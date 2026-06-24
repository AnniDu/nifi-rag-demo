from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from google.genai import types

from rag_config import DEFAULT_CHROMA_DIR, PROJECT_ROOT, embed_texts, get_chroma_collection, get_gemini_client, get_gemini_model


SYSTEM_PROMPT = """You answer questions about Apache NiFi Processor documentation.
Use only the provided context. If the context does not contain the answer, say you do not know.
If the context says a topic is unsupported by the indexed docs, say that part is unsupported by the indexed docs.
Be concise and cite relevant source labels in the answer."""

DEFAULT_TOPICS_FILE = PROJECT_ROOT / "retrieval_topics.yaml"


@dataclass(frozen=True)
class RetrievalTopic:
    name: str
    keywords: list[str]
    subquery_template: str
    top_k: int | None = None


@dataclass(frozen=True)
class RetrievalQuery:
    topic: str
    text: str
    top_k: int
    is_original: bool = False


@dataclass
class RetrievedChunk:
    chunk_id: str
    document: str
    metadata: dict[str, Any]
    best_distance: float | None
    matched_subqueries: list[str] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query the local NiFi RAG index.")
    parser.add_argument("question", nargs="+", help="Question to ask.")
    parser.add_argument("--chroma-dir", type=Path, default=DEFAULT_CHROMA_DIR, help="Directory containing the persisted ChromaDB index.")
    parser.add_argument("--top-k", type=int, default=5, help="Default number of chunks to retrieve per query.")
    parser.add_argument("--topics-file", type=Path, default=DEFAULT_TOPICS_FILE, help="YAML file containing retrieval topic definitions.")
    parser.add_argument("--debug", action="store_true", help="Print the full retrieval pipeline before answering.")
    return parser.parse_args()


def load_retrieval_topics(path: Path) -> list[RetrievalTopic]:
    if not path.exists():
        raise FileNotFoundError(f"Retrieval topics file does not exist: {path}")

    with path.open("r", encoding="utf-8") as file:
        raw_config = yaml.safe_load(file) or {}

    topics = []
    for raw_topic in raw_config.get("topics", []):
        name = str(raw_topic["name"])
        keywords = [str(keyword).lower() for keyword in raw_topic.get("keywords", [])]
        subquery_template = str(raw_topic["subquery_template"])
        top_k = raw_topic.get("top_k")
        topics.append(
            RetrievalTopic(
                name=name,
                keywords=keywords,
                subquery_template=subquery_template,
                top_k=int(top_k) if top_k is not None else None,
            )
        )
    return topics


def matched_keywords(question: str, topic: RetrievalTopic) -> list[str]:
    question_lower = question.lower()
    return [keyword for keyword in topic.keywords if keyword in question_lower]


def find_matched_topics(question: str, topics: list[RetrievalTopic]) -> list[RetrievalTopic]:
    return [topic for topic in topics if matched_keywords(question, topic)]


def build_retrieval_queries(question: str, matched_topics: list[RetrievalTopic], default_top_k: int) -> list[RetrievalQuery]:
    queries = [
        RetrievalQuery(
            topic="original_question",
            text=question,
            top_k=default_top_k,
            is_original=True,
        )
    ]

    for topic in matched_topics:
        subquery = topic.subquery_template.format(
            question=question,
            topic_name=topic.name,
            keywords=", ".join(topic.keywords),
        )
        queries.append(
            RetrievalQuery(
                topic=topic.name,
                text=subquery,
                top_k=topic.top_k or default_top_k,
            )
        )

    return queries


def query_collection(collection, retrieval_query: RetrievalQuery) -> dict[str, Any]:
    embedding = embed_texts([retrieval_query.text], task_type="RETRIEVAL_QUERY")[0]
    return collection.query(
        query_embeddings=[embedding],
        n_results=retrieval_query.top_k,
        include=["documents", "metadatas", "distances"],
    )


def get_first_result_list(results: dict[str, Any], key: str) -> list[Any]:
    values = results.get(key) or []
    if not values:
        return []
    return values[0] or []


def is_better_distance(candidate: float | None, current: float | None) -> bool:
    if candidate is None:
        return False
    if current is None:
        return True
    return candidate < current


def merge_retrieval_results(
    query_results: list[tuple[RetrievalQuery, dict[str, Any]]],
) -> tuple[dict[str, RetrievedChunk], dict[str, list[str]]]:
    chunks_by_id: dict[str, RetrievedChunk] = {}
    query_chunk_ids: dict[str, list[str]] = {}

    for retrieval_query, results in query_results:
        ids = get_first_result_list(results, "ids")
        documents = get_first_result_list(results, "documents")
        metadatas = get_first_result_list(results, "metadatas")
        distances = get_first_result_list(results, "distances")
        query_chunk_ids[retrieval_query.text] = []

        for chunk_id, document, metadata, distance in zip(ids, documents, metadatas, distances):
            chunk_key = str(chunk_id)
            query_chunk_ids[retrieval_query.text].append(chunk_key)
            if chunk_key not in chunks_by_id:
                chunks_by_id[chunk_key] = RetrievedChunk(
                    chunk_id=chunk_key,
                    document=str(document),
                    metadata=dict(metadata or {}),
                    best_distance=distance,
                    matched_subqueries=[retrieval_query.text],
                )
                continue

            chunk = chunks_by_id[chunk_key]
            if is_better_distance(distance, chunk.best_distance):
                chunk.best_distance = distance
            if retrieval_query.text not in chunk.matched_subqueries:
                chunk.matched_subqueries.append(retrieval_query.text)

    return chunks_by_id, query_chunk_ids


def source_file(metadata: dict[str, Any]) -> str:
    return str(metadata.get("file_name") or metadata.get("filename") or metadata.get("file_path") or "unknown")


def build_context(
    retrieval_queries: list[RetrievalQuery],
    chunks_by_id: dict[str, RetrievedChunk],
    query_chunk_ids: dict[str, list[str]],
    unsupported_topics: list[str],
) -> tuple[str, list[dict[str, str]]]:
    context_blocks = []
    sources = []
    source_labels = {}

    for i, chunk in enumerate(chunks_by_id.values(), start=1):
        file_name = source_file(chunk.metadata)
        source_labels[chunk.chunk_id] = f"source {i}: {file_name} / {chunk.chunk_id}"
        sources.append(
            {
                "label": f"source {i}",
                "file_name": file_name,
                "chunk_id": chunk.chunk_id,
                "best_distance": f"{chunk.best_distance:.4f}" if chunk.best_distance is not None else "n/a",
                "matched_subqueries": " | ".join(chunk.matched_subqueries),
            }
        )

    if unsupported_topics:
        context_blocks.append(
            "Unsupported by indexed docs:\n"
            + "\n".join(f"- {topic}" for topic in unsupported_topics)
        )

    for retrieval_query in retrieval_queries:
        query_chunk_keys = query_chunk_ids.get(retrieval_query.text, [])
        heading = f"Topic/query: {retrieval_query.topic}\nRetrieval query: {retrieval_query.text}"
        if not query_chunk_keys:
            context_blocks.append(f"{heading}\nNo retrieved chunks for this query.")
            continue

        chunk_blocks = []
        for chunk_key in query_chunk_keys:
            chunk = chunks_by_id[chunk_key]
            chunk_blocks.append(f"[{source_labels[chunk.chunk_id]}]\n{chunk.document}")
        context_blocks.append(f"{heading}\n\n" + "\n\n".join(chunk_blocks))

    return "\n\n---\n\n".join(context_blocks), sources


def chunk_preview(text: str, limit: int = 300) -> str:
    preview = " ".join(text.split())
    if len(preview) <= limit:
        return preview
    return preview[:limit].rstrip() + "..."


def print_debug_retrieval_plan(
    question: str,
    topics_file: Path,
    topics: list[RetrievalTopic],
    matched_topics: list[RetrievalTopic],
    retrieval_queries: list[RetrievalQuery],
) -> None:
    print("Retrieval debug")
    print("===============")
    print(f"Question: {question}")
    print(f"Topics file: {topics_file}")
    print(f"Configured topics: {len(topics)}")
    for topic in topics:
        top_k = topic.top_k if topic.top_k is not None else "default"
        print(f"- {topic.name}: top_k={top_k}; keywords={', '.join(topic.keywords)}")

    print("\nMatched topics:")
    if not matched_topics:
        print("- none")
    for topic in matched_topics:
        print(f"- {topic.name}: matched_keywords={', '.join(matched_keywords(question, topic))}")

    print("\nRetrieval queries to execute:")
    for i, retrieval_query in enumerate(retrieval_queries, start=1):
        query_type = "original question" if retrieval_query.is_original else "topic subquery"
        print(f"- query {i}: topic={retrieval_query.topic}; type={query_type}; top_k={retrieval_query.top_k}")
        print(f"  text: {retrieval_query.text}")
    print()


def print_debug_chunks(query_results: list[tuple[RetrievalQuery, dict[str, Any]]]) -> None:
    print("Retrieved chunks by query:")
    for retrieval_query, results in query_results:
        print(f"\n[{retrieval_query.topic}] {retrieval_query.text}")
        ids = get_first_result_list(results, "ids")
        documents = get_first_result_list(results, "documents")
        metadatas = get_first_result_list(results, "metadatas")
        distances = get_first_result_list(results, "distances")

        if not ids:
            print("- no chunks retrieved")
            continue

        for i, (chunk_id, document, metadata, distance) in enumerate(zip(ids, documents, metadatas, distances), start=1):
            distance_text = f"{distance:.4f}" if distance is not None else "n/a"
            print(f"- result {i}")
            print(f"  chunk_id: {chunk_id}")
            print(f"  source_file: {source_file(metadata or {})}")
            print(f"  distance: {distance_text}")
    print()


def print_debug_merge_summary(
    chunks_by_id: dict[str, RetrievedChunk],
    query_chunk_ids: dict[str, list[str]],
    unsupported_topics: list[str],
) -> None:
    print("Merged retrieval results:")
    print(f"- unique_chunks: {len(chunks_by_id)}")
    for query_text, chunk_ids in query_chunk_ids.items():
        duplicate_count = len(chunk_ids) - len(set(chunk_ids))
        print(f"- query: {query_text}")
        print(f"  returned_chunks: {len(chunk_ids)}")
        print(f"  duplicate_chunk_ids_in_query: {duplicate_count}")
        print(f"  chunk_ids: {', '.join(chunk_ids) if chunk_ids else 'none'}")

    print("\nChunks after de-duplication:")
    if not chunks_by_id:
        print("- none")
    for chunk in chunks_by_id.values():
        best_distance = f"{chunk.best_distance:.4f}" if chunk.best_distance is not None else "n/a"
        print(f"- chunk_id: {chunk.chunk_id}")
        print(f"  source_file: {source_file(chunk.metadata)}")
        print(f"  best_distance: {best_distance}")
        print(f"  matched_subqueries: {' | '.join(chunk.matched_subqueries)}")

    print("\nUnsupported matched topics:")
    if not unsupported_topics:
        print("- none")
    for topic in unsupported_topics:
        print(f"- {topic}")
    print()


def print_debug_context_summary(
    retrieval_queries: list[RetrievalQuery],
    query_chunk_ids: dict[str, list[str]],
) -> None:
    print("Final grouped context sent to LLM:")
    print("----------------------------------")
    for retrieval_query in retrieval_queries:
        chunk_ids = query_chunk_ids.get(retrieval_query.text, [])
        print(f"- topic={retrieval_query.topic}")
        print(f"  query: {retrieval_query.text}")
        print(f"  chunk_ids: {', '.join(chunk_ids) if chunk_ids else 'none'}")
    print("----------------------------------")
    print()


def call_llm(question: str, context: str) -> str:
    client = get_gemini_client()
    response = client.models.generate_content(
        model=get_gemini_model(),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,
        ),
        contents=f"Context:\n{context}\n\nQuestion: {question}",
    )
    return response.text or ""


def main() -> None:
    args = parse_args()
    question = " ".join(args.question)

    topics = load_retrieval_topics(args.topics_file)
    matched_topics = find_matched_topics(question, topics)
    retrieval_queries = build_retrieval_queries(question, matched_topics, args.top_k)

    if args.debug:
        print_debug_retrieval_plan(question, args.topics_file, topics, matched_topics, retrieval_queries)

    collection = get_chroma_collection(args.chroma_dir)
    query_results = [(retrieval_query, query_collection(collection, retrieval_query)) for retrieval_query in retrieval_queries]
    chunks_by_id, query_chunk_ids = merge_retrieval_results(query_results)
    unsupported_topics = [
        retrieval_query.topic
        for retrieval_query in retrieval_queries
        if not retrieval_query.is_original and not query_chunk_ids.get(retrieval_query.text)
    ]

    if args.debug:
        print_debug_chunks(query_results)
        print_debug_merge_summary(chunks_by_id, query_chunk_ids, unsupported_topics)

    if not chunks_by_id:
        print("No relevant chunks found. Run ingest.py first or add documents to ./docs.")
        return

    context, sources = build_context(retrieval_queries, chunks_by_id, query_chunk_ids, unsupported_topics)
    if args.debug:
        print_debug_context_summary(retrieval_queries, query_chunk_ids)

    answer = call_llm(question, context)

    print(answer.strip())
    if unsupported_topics:
        print("\nUnsupported by indexed docs:")
        for topic in unsupported_topics:
            print(f"- {topic}")
    print("\nSources:")
    for source in sources:
        print(
            f"- {source['label']}: {source['file_name']} | chunk_id={source['chunk_id']} "
            f"| best_distance={source['best_distance']} | matched_subqueries={source['matched_subqueries']}"
        )


if __name__ == "__main__":
    main()
