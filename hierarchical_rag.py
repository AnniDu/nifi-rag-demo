from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from google.genai import types

from prompts import DECOMPOSITION_SYSTEM_PROMPT, EVIDENCE_EXTRACTION_SYSTEM_PROMPT, FINAL_ANSWER_SYSTEM_PROMPT
from rag_config import DEFAULT_CHROMA_DIR, embed_texts, get_chroma_collection, get_gemini_client, get_gemini_model


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    text: str
    metadata: dict[str, Any]
    distance: float | None


@dataclass(frozen=True)
class EvidenceSummary:
    subquery: str
    supported: bool
    evidence: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class HierarchicalRagResult:
    question: str
    subqueries: list[str]
    retrievals: dict[str, list[RetrievedChunk]]
    evidence_summaries: list[EvidenceSummary]
    final_prompt: str
    answer: str


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
    client = get_gemini_client()
    response = client.models.generate_content(
        model=get_gemini_model(),
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.1,
            response_mime_type="application/json",
        ),
        contents=contents,
    )
    return parse_json_object(response.text or "{}")


def generate_text(system_prompt: str, contents: str) -> str:
    client = get_gemini_client()
    response = client.models.generate_content(
        model=get_gemini_model(),
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.2,
        ),
        contents=contents,
    )
    return response.text or ""


def decompose_question(question: str) -> list[str]:
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


def build_evidence_extraction_prompt(subquery: str, chunks: list[RetrievedChunk]) -> str:
    chunk_blocks = []
    for i, chunk in enumerate(chunks, start=1):
        distance = f"{chunk.distance:.4f}" if chunk.distance is not None else "n/a"
        chunk_blocks.append(
            f"[chunk {i}]\n"
            f"chunk_id: {chunk.chunk_id}\n"
            f"source_file: {source_file(chunk.metadata)}\n"
            f"distance: {distance}\n"
            f"text:\n{chunk.text}"
        )

    valid_source_ids = ", ".join(chunk.chunk_id for chunk in chunks)
    return (
        f"Subquery:\n{subquery}\n\n"
        f"Valid source chunk ids:\n{valid_source_ids}\n\n"
        "Retrieved chunks:\n"
        + "\n\n---\n\n".join(chunk_blocks)
    )


def extract_evidence(subquery: str, chunks: list[RetrievedChunk]) -> EvidenceSummary:
    if not chunks:
        return EvidenceSummary(subquery=subquery, supported=False)

    payload = generate_json(
        EVIDENCE_EXTRACTION_SYSTEM_PROMPT,
        build_evidence_extraction_prompt(subquery, chunks),
    )
    evidence = [str(item).strip() for item in payload.get("evidence", []) if str(item).strip()]
    allowed_sources = {chunk.chunk_id for chunk in chunks}
    sources = []
    for item in payload.get("sources", []):
        source = str(item).strip()
        if source in allowed_sources and source not in sources:
            sources.append(source)
    supported = bool(payload.get("supported")) and bool(evidence) and bool(sources)
    return EvidenceSummary(
        subquery=str(payload.get("subquery") or subquery),
        supported=supported,
        evidence=evidence if supported else [],
        sources=sources if supported else [],
    )


def format_evidence_lines(summary: EvidenceSummary) -> str:
    if not summary.evidence:
        return "- unsupported by indexed docs"
    return "\n".join(f"- {item}" for item in summary.evidence)


def build_final_prompt(question: str, evidence_summaries: list[EvidenceSummary]) -> str:
    blocks = []
    for i, summary in enumerate(evidence_summaries, start=1):
        blocks.append(
            f"Evidence summary {i}\n"
            f"Subquery: {summary.subquery}\n"
            f"Supported: {summary.supported}\n"
            f"Evidence:\n{format_evidence_lines(summary)}\n"
            f"Sources: {', '.join(summary.sources) if summary.sources else 'none'}"
        )

    return (
        f"User question:\n{question}\n\n"
        "Evidence summaries:\n"
        + "\n\n---\n\n".join(blocks)
    )


def generate_final_answer(question: str, evidence_summaries: list[EvidenceSummary]) -> tuple[str, str]:
    final_prompt = build_final_prompt(question, evidence_summaries)
    answer = generate_text(FINAL_ANSWER_SYSTEM_PROMPT, final_prompt)
    return answer, final_prompt


def answer_hierarchical(question: str, chroma_dir: Path = DEFAULT_CHROMA_DIR, top_k: int = 5) -> HierarchicalRagResult:
    subqueries = decompose_question(question)
    collection = get_chroma_collection(chroma_dir)

    retrievals: dict[str, list[RetrievedChunk]] = {}
    evidence_summaries = []
    for subquery in subqueries:
        chunks = retrieve_for_subquery(collection, subquery, top_k)
        retrievals[subquery] = chunks
        evidence_summaries.append(extract_evidence(subquery, chunks))

    answer, final_prompt = generate_final_answer(question, evidence_summaries)
    return HierarchicalRagResult(
        question=question,
        subqueries=subqueries,
        retrievals=retrievals,
        evidence_summaries=evidence_summaries,
        final_prompt=final_prompt,
        answer=answer,
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
        print(f"\n=== Evidence: subquery {i} ===")
        print(f"subquery: {summary.subquery}")
        print(f"supported: {summary.supported}")
        print(f"sources: {', '.join(summary.sources) if summary.sources else 'none'}")
        print("evidence:")
        for item in summary.evidence:
            print(f"- {item}")
        if not summary.evidence:
            print("- unsupported by indexed docs")

    print("\n=== Final Answer Prompt ===")
    print(result.final_prompt)
    print()
