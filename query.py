from __future__ import annotations

import argparse
from pathlib import Path

from google.genai import types

from rag_config import DEFAULT_CHROMA_DIR, embed_texts, get_chroma_collection, get_gemini_client, get_gemini_model


SYSTEM_PROMPT = """You answer questions about Apache NiFi Processor documentation.
Use only the provided context. If the context does not contain the answer, say you do not know.
Be concise and cite relevant source labels in the answer."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query the local NiFi RAG index.")
    parser.add_argument("question", nargs="+", help="Question to ask.")
    parser.add_argument("--chroma-dir", type=Path, default=DEFAULT_CHROMA_DIR, help="Directory containing the persisted ChromaDB index.")
    parser.add_argument("--top-k", type=int, default=5, help="Number of chunks to retrieve.")
    return parser.parse_args()


def build_context(results) -> tuple[str, list[dict[str, str]]]:
    context_blocks = []
    sources = []
    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for i, (chunk_id, document, metadata, distance) in enumerate(zip(ids, documents, metadatas, distances), start=1):
        file_name = metadata.get("file_name") or metadata.get("filename") or metadata.get("file_path") or "unknown"
        label = f"source {i}: {file_name} / {chunk_id}"

        context_blocks.append(f"[{label}]\n{document}")
        sources.append(
            {
                "label": f"source {i}",
                "file_name": str(file_name),
                "chunk_id": str(chunk_id),
                "distance": f"{distance:.4f}" if distance is not None else "n/a",
            }
        )

    return "\n\n---\n\n".join(context_blocks), sources


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

    question_embedding = embed_texts([question], task_type="RETRIEVAL_QUERY")[0]
    collection = get_chroma_collection(args.chroma_dir)
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=args.top_k,
        include=["documents", "metadatas", "distances"],
    )

    if not results["ids"] or not results["ids"][0]:
        print("No relevant chunks found. Run ingest.py first or add documents to ./docs.")
        return

    context, sources = build_context(results)
    answer = call_llm(question, context)

    print(answer.strip())
    print("\nSources:")
    for source in sources:
        print(f"- {source['label']}: {source['file_name']} | chunk_id={source['chunk_id']} | distance={source['distance']}")


if __name__ == "__main__":
    main()
