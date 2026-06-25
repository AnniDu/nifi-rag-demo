from __future__ import annotations

import json
import contextlib
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from prompts import DECOMPOSITION_SYSTEM_PROMPT, EVIDENCE_EXTRACTION_SYSTEM_PROMPT, FINAL_ANSWER_SYSTEM_PROMPT
from rag_config import DEFAULT_CHROMA_DIR, PROJECT_ROOT, embed_texts, generate_text as generate_model_text, get_chroma_collection, get_evidence_mode, get_max_chars_per_chunk


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    text: str
    metadata: dict[str, Any]
    distance: float | None


@dataclass(frozen=True)
class EvidenceItem:
    name: str = ""
    description: str = ""
    step: str = ""
    source_chunk: str = ""


@dataclass(frozen=True)
class StructuredEvidence:
    subquery: str
    topic: str = ""
    purpose: str = ""
    processor_names: list[str] = field(default_factory=list)
    required_properties: list[EvidenceItem] = field(default_factory=list)
    optional_properties: list[EvidenceItem] = field(default_factory=list)
    relationships: list[str] = field(default_factory=list)
    configuration_steps: list[EvidenceItem] = field(default_factory=list)
    warnings_or_constraints: list[str] = field(default_factory=list)
    unsupported_or_missing_details: list[str] = field(default_factory=list)

    @property
    def supported(self) -> bool:
        return any(
            [
                self.purpose,
                self.processor_names,
                self.required_properties,
                self.optional_properties,
                self.relationships,
                self.configuration_steps,
                self.warnings_or_constraints,
            ]
        )

    @property
    def sources(self) -> list[str]:
        sources = []
        for item in self.required_properties + self.optional_properties + self.configuration_steps:
            if item.source_chunk and item.source_chunk not in sources:
                sources.append(item.source_chunk)
        return sources


@dataclass(frozen=True)
class HierarchicalRagResult:
    question: str
    subqueries: list[str]
    retrievals: dict[str, list[RetrievedChunk]]
    evidence_summaries: list[StructuredEvidence]
    final_prompt: str
    answer: str
    timing_checkpoints: list[dict[str, Any]] = field(default_factory=list)


def source_file(metadata: dict[str, Any]) -> str:
    return str(metadata.get("file_name") or metadata.get("filename") or metadata.get("file_path") or "unknown")


def parse_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(cleaned[start : end + 1])


def generate_json(system_prompt: str, contents: str) -> dict[str, Any]:
    return parse_json_object(generate_model_text(system_prompt, contents, json_output=True) or "{}")


def generate_text(system_prompt: str, contents: str) -> str:
    return generate_model_text(system_prompt, contents)


def now_timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def emit_timing_checkpoint(
    checkpoints: list[dict[str, Any]],
    label: str,
    started_at: float,
    *,
    detail: str = "",
    live: bool = False,
) -> None:
    elapsed_seconds = time.perf_counter() - started_at
    checkpoint = {
        "timestamp": now_timestamp(),
        "elapsed_seconds": round(elapsed_seconds, 3),
        "label": label,
        "detail": detail,
    }
    checkpoints.append(checkpoint)
    if live:
        detail_suffix = f" | {detail}" if detail else ""
        print(
            f"[rag timing] {checkpoint['timestamp']} +{checkpoint['elapsed_seconds']:.3f}s "
            f"{label}{detail_suffix}",
            file=sys.stderr,
            flush=True,
        )


def load_retrieval_topics() -> list[dict[str, Any]]:
    config_path = PROJECT_ROOT / "retrieval_topics.yaml"
    if not config_path.exists():
        return []
    with config_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    topics = payload.get("topics")
    return topics if isinstance(topics, list) else []


def decompose_question_from_topics(question: str) -> list[str]:
    question_lower = question.lower()
    subqueries = []

    if "kafka" in question_lower and any(word in question_lower for word in ["read", "consume", "consumer"]):
        subqueries.append(f"ConsumeKafka processor configuration for reading messages from Kafka in NiFi: {question}")
    elif "kafka" in question_lower and any(word in question_lower for word in ["write", "publish", "produce", "producer"]):
        subqueries.append(f"PublishKafka processor configuration for writing messages to Kafka in NiFi: {question}")

    if "hdfs" in question_lower and any(word in question_lower for word in ["write", "put", "store", "send"]):
        subqueries.append(f"PutHDFS processor configuration for writing FlowFiles to HDFS in NiFi: {question}")
    elif "hdfs" in question_lower and any(word in question_lower for word in ["read", "get", "fetch", "list", "ingest"]):
        subqueries.append(f"GetHDFS FetchHDFS ListHDFS processor configuration for reading from HDFS in NiFi: {question}")

    if len(subqueries) > 1:
        return subqueries

    for topic in load_retrieval_topics():
        if not isinstance(topic, dict):
            continue
        keywords = topic.get("keywords") or []
        if not any(str(keyword).lower() in question_lower for keyword in keywords):
            continue
        template = str(topic.get("subquery_template") or "{question}")
        subquery = template.format(question=question).strip()
        if subquery and subquery not in subqueries:
            subqueries.append(subquery)

    return subqueries if len(subqueries) > 1 else []


def decompose_question(question: str) -> list[str]:
    topic_subqueries = decompose_question_from_topics(question)
    if topic_subqueries:
        return topic_subqueries

    with contextlib.suppress(json.JSONDecodeError, RuntimeError):
        payload = generate_json(
            DECOMPOSITION_SYSTEM_PROMPT,
            f"Question:\n{question}",
        )
        subqueries = []
        seen = set()
        for item in payload.get("subqueries", []):
            subquery = str(item).strip()
            subquery_key = subquery.lower()
            if subquery and subquery_key not in seen:
                subqueries.append(subquery)
                seen.add(subquery_key)
        return subqueries or [question]

    return [question]


def get_first_result_list(results: dict[str, Any], key: str) -> list[Any]:
    values = results.get(key) or []
    if not values:
        return []
    return values[0] or []


def retrieve_for_subquery(collection, subquery: str, top_k: int) -> list[RetrievedChunk]:
    embedding = embed_texts([subquery], task_type="RETRIEVAL_QUERY")[0]
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    ids = get_first_result_list(results, "ids")
    documents = get_first_result_list(results, "documents")
    metadatas = get_first_result_list(results, "metadatas")
    distances = get_first_result_list(results, "distances")
    for chunk_id, document, metadata, distance in zip(ids, documents, metadatas, distances):
        chunks.append(
            RetrievedChunk(
                chunk_id=str(chunk_id),
                text=str(document),
                metadata=dict(metadata or {}),
                distance=distance,
            )
        )
    return chunks


def truncate_chunk_text(text: str) -> str:
    max_chars = get_max_chars_per_chunk()
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + f"\n...[truncated to {max_chars} chars]"


def build_evidence_extraction_prompt(subquery: str, chunks: list[RetrievedChunk]) -> str:
    chunk_blocks = []
    for i, chunk in enumerate(chunks, start=1):
        distance = f"{chunk.distance:.4f}" if chunk.distance is not None else "n/a"
        chunk_blocks.append(
            f"[chunk {i}]\n"
            f"chunk_id: {chunk.chunk_id}\n"
            f"source_file: {source_file(chunk.metadata)}\n"
            f"distance: {distance}\n"
            f"text:\n{truncate_chunk_text(chunk.text)}"
        )

    valid_source_ids = ", ".join(chunk.chunk_id for chunk in chunks)
    return (
        f"Subquery:\n{subquery}\n\n"
        f"Valid source chunk ids:\n{valid_source_ids}\n\n"
        "Retrieved chunks:\n"
        + "\n\n---\n\n".join(chunk_blocks)
    )


def as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def parse_evidence_items(value: Any, allowed_sources: set[str], *, step_mode: bool = False) -> list[EvidenceItem]:
    if not isinstance(value, list):
        return []

    items = []
    for raw_item in value:
        if not isinstance(raw_item, dict):
            continue
        source_chunk = str(raw_item.get("source_chunk") or "").strip()
        if source_chunk not in allowed_sources:
            continue
        item = EvidenceItem(
            name=str(raw_item.get("name") or "").strip(),
            description=str(raw_item.get("description") or "").strip(),
            step=str(raw_item.get("step") or "").strip(),
            source_chunk=source_chunk,
        )
        if step_mode and item.step:
            items.append(item)
        elif not step_mode and item.name:
            items.append(item)
    return items


def extract_evidence(subquery: str, chunks: list[RetrievedChunk]) -> StructuredEvidence:
    if get_evidence_mode() == "skip":
        return StructuredEvidence(
            subquery=subquery,
            topic=subquery,
            unsupported_or_missing_details=[
                "LLM evidence extraction is disabled for this run; retrieved chunks were not converted into structured evidence."
            ],
        )

    if not chunks:
        return StructuredEvidence(
            subquery=subquery,
            topic=subquery,
            unsupported_or_missing_details=["No chunks were retrieved for this subquery."],
        )

    try:
        payload = generate_json(
            EVIDENCE_EXTRACTION_SYSTEM_PROMPT,
            build_evidence_extraction_prompt(subquery, chunks),
        )
    except (json.JSONDecodeError, RuntimeError):
        return StructuredEvidence(
            subquery=subquery,
            topic=subquery,
            unsupported_or_missing_details=[
                "The local model did not return valid structured evidence JSON for this subquery."
            ],
        )
    allowed_sources = {chunk.chunk_id for chunk in chunks}
    unsupported = as_string_list(payload.get("unsupported_or_missing_details"))
    if not unsupported and not any(
        [
            payload.get("purpose"),
            payload.get("processor_names"),
            payload.get("required_properties"),
            payload.get("optional_properties"),
            payload.get("relationships"),
            payload.get("configuration_steps"),
            payload.get("warnings_or_constraints"),
        ]
    ):
        unsupported = ["No directly relevant structured evidence was found in the retrieved chunks."]

    return StructuredEvidence(
        subquery=subquery,
        topic=str(payload.get("topic") or subquery).strip(),
        purpose=str(payload.get("purpose") or "").strip(),
        processor_names=as_string_list(payload.get("processor_names")),
        required_properties=parse_evidence_items(payload.get("required_properties"), allowed_sources),
        optional_properties=parse_evidence_items(payload.get("optional_properties"), allowed_sources),
        relationships=as_string_list(payload.get("relationships")),
        configuration_steps=parse_evidence_items(payload.get("configuration_steps"), allowed_sources, step_mode=True),
        warnings_or_constraints=as_string_list(payload.get("warnings_or_constraints")),
        unsupported_or_missing_details=unsupported,
    )


def evidence_item_to_dict(item: EvidenceItem, *, step_mode: bool = False) -> dict[str, str]:
    if step_mode:
        return {"step": item.step, "source_chunk": item.source_chunk}
    return {
        "name": item.name,
        "description": item.description,
        "source_chunk": item.source_chunk,
    }


def structured_evidence_to_dict(summary: StructuredEvidence) -> dict[str, Any]:
    return {
        "subquery": summary.subquery,
        "topic": summary.topic,
        "purpose": summary.purpose,
        "processor_names": summary.processor_names,
        "required_properties": [evidence_item_to_dict(item) for item in summary.required_properties],
        "optional_properties": [evidence_item_to_dict(item) for item in summary.optional_properties],
        "relationships": summary.relationships,
        "configuration_steps": [evidence_item_to_dict(item, step_mode=True) for item in summary.configuration_steps],
        "warnings_or_constraints": summary.warnings_or_constraints,
        "unsupported_or_missing_details": summary.unsupported_or_missing_details,
    }


def build_final_prompt(question: str, evidence_summaries: list[StructuredEvidence]) -> str:
    evidence_payload = [structured_evidence_to_dict(summary) for summary in evidence_summaries]
    return (
        f"User question:\n{question}\n\n"
        "Structured evidence JSON:\n"
        + json.dumps(evidence_payload, indent=2)
    )


def build_unsupported_answer(question: str, evidence_summaries: list[StructuredEvidence]) -> str:
    lines = [
        "I cannot answer this from the indexed documents because structured evidence extraction did not produce supported evidence.",
        "",
        "Unsupported parts:",
    ]
    for summary in evidence_summaries:
        details = summary.unsupported_or_missing_details or ["No supported evidence was extracted."]
        lines.append(f"- {summary.subquery}: {'; '.join(details)}")
    return "\n".join(lines)


def all_evidence_unsupported(evidence_summaries: list[StructuredEvidence]) -> bool:
    return bool(evidence_summaries) and all(not summary.supported for summary in evidence_summaries)


def generate_final_answer(question: str, evidence_summaries: list[StructuredEvidence]) -> tuple[str, str]:
    final_prompt = build_final_prompt(question, evidence_summaries)
    if all_evidence_unsupported(evidence_summaries):
        return build_unsupported_answer(question, evidence_summaries), final_prompt
    answer = generate_text(FINAL_ANSWER_SYSTEM_PROMPT, final_prompt)
    return answer, final_prompt


def answer_hierarchical(
    question: str,
    chroma_dir: Path = DEFAULT_CHROMA_DIR,
    top_k: int = 5,
    *,
    timing: bool = False,
) -> HierarchicalRagResult:
    started_at = time.perf_counter()
    timing_checkpoints: list[dict[str, Any]] = []
    emit_timing_checkpoint(timing_checkpoints, "start", started_at, detail=f"top_k={top_k}", live=timing)

    emit_timing_checkpoint(timing_checkpoints, "decomposition:start", started_at, live=timing)
    subqueries = decompose_question(question)
    emit_timing_checkpoint(
        timing_checkpoints,
        "decomposition:end",
        started_at,
        detail=f"subqueries={len(subqueries)}",
        live=timing,
    )

    emit_timing_checkpoint(timing_checkpoints, "chroma_collection:start", started_at, detail=str(chroma_dir), live=timing)
    collection = get_chroma_collection(chroma_dir)
    emit_timing_checkpoint(timing_checkpoints, "chroma_collection:end", started_at, live=timing)

    retrievals: dict[str, list[RetrievedChunk]] = {}
    evidence_summaries = []
    for i, subquery in enumerate(subqueries, start=1):
        step_detail = f"subquery={i}/{len(subqueries)}"
        emit_timing_checkpoint(
            timing_checkpoints,
            "retrieval:start",
            started_at,
            detail=f"{step_detail}: {subquery}",
            live=timing,
        )
        chunks = retrieve_for_subquery(collection, subquery, top_k)
        retrievals[subquery] = chunks
        emit_timing_checkpoint(
            timing_checkpoints,
            "retrieval:end",
            started_at,
            detail=f"{step_detail} chunks={len(chunks)}",
            live=timing,
        )

        emit_timing_checkpoint(
            timing_checkpoints,
            "evidence_extraction:start",
            started_at,
            detail=f"{step_detail}: {subquery}",
            live=timing,
        )
        evidence_summaries.append(extract_evidence(subquery, chunks))
        emit_timing_checkpoint(
            timing_checkpoints,
            "evidence_extraction:end",
            started_at,
            detail=step_detail,
            live=timing,
        )

    emit_timing_checkpoint(timing_checkpoints, "final_answer:start", started_at, live=timing)
    answer, final_prompt = generate_final_answer(question, evidence_summaries)
    emit_timing_checkpoint(timing_checkpoints, "final_answer:end", started_at, live=timing)
    emit_timing_checkpoint(timing_checkpoints, "done", started_at, live=timing)
    return HierarchicalRagResult(
        question=question,
        subqueries=subqueries,
        retrievals=retrievals,
        evidence_summaries=evidence_summaries,
        final_prompt=final_prompt,
        answer=answer,
        timing_checkpoints=timing_checkpoints,
    )


def print_debug_result(result: HierarchicalRagResult) -> None:
    print("=== Query Decomposition ===")
    for i, subquery in enumerate(result.subqueries, start=1):
        print(f"{i}. {subquery}")

    for i, subquery in enumerate(result.subqueries, start=1):
        print(f"\n=== Retrieval: subquery {i} ===")
        print(subquery)
        chunks = result.retrievals.get(subquery, [])
        if not chunks:
            print("- no chunks retrieved")
            continue
        for chunk in chunks:
            distance = f"{chunk.distance:.4f}" if chunk.distance is not None else "n/a"
            print(f"- chunk_id={chunk.chunk_id} source_file={source_file(chunk.metadata)} distance={distance}")

    for i, summary in enumerate(result.evidence_summaries, start=1):
        print(f"\n=== Structured Evidence: subquery {i} ===")
        print(json.dumps(structured_evidence_to_dict(summary), indent=2))

    print("\n=== Final Answer Prompt ===")
    print(result.final_prompt)
    print()
