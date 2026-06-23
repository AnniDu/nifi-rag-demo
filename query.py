from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex
from openai import OpenAI

from rag_config import DEFAULT_CHROMA_DIR, PROJECT_ROOT, get_chroma_vector_store, get_embedding_model


SYSTEM_PROMPT = """You answer questions about Apache NiFi Processor documentation.
Use only the provided context. If the context does not contain the answer, say you do not know.
Be concise and cite relevant source labels in the answer."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query the local NiFi RAG index.")
    parser.add_argument("question", nargs="+", help="Question to ask.")
    parser.add_argument("--chroma-dir", type=Path, default=DEFAULT_CHROMA_DIR, help="Directory containing the persisted ChromaDB index.")
    parser.add_argument("--top-k", type=int, default=5, help="Number of chunks to retrieve.")
    return parser.parse_args()


def build_context(nodes) -> tuple[str, list[dict[str, str]]]:
    context_blocks = []
    sources = []

    for i, node_with_score in enumerate(nodes, start=1):
        node = node_with_score.node
        metadata = node.metadata or {}
        file_name = metadata.get("file_name") or metadata.get("filename") or metadata.get("file_path") or "unknown"
        chunk_id = node.node_id
        label = f"source {i}: {file_name} / {chunk_id}"

        context_blocks.append(f"[{label}]\n{node.get_content(metadata_mode='none')}")
        sources.append(
            {
                "label": f"source {i}",
                "file_name": str(file_name),
                "chunk_id": str(chunk_id),
                "score": f"{node_with_score.score:.4f}" if node_with_score.score is not None else "n/a",
            }
        )

    return "\n\n---\n\n".join(context_blocks), sources


def call_llm(question: str, context: str) -> str:
    load_dotenv(PROJECT_ROOT / ".env")
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL") or None,
    )
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}",
            },
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or ""


def main() -> None:
    args = parse_args()
    question = " ".join(args.question)

    Settings.embed_model = get_embedding_model()
    vector_store = get_chroma_vector_store(args.chroma_dir)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    retriever = index.as_retriever(similarity_top_k=args.top_k)
    retrieved_nodes = retriever.retrieve(question)

    if not retrieved_nodes:
        print("No relevant chunks found. Run ingest.py first or add documents to ./docs.")
        return

    context, sources = build_context(retrieved_nodes)
    answer = call_llm(question, context)

    print(answer.strip())
    print("\nSources:")
    for source in sources:
        print(f"- {source['label']}: {source['file_name']} | chunk_id={source['chunk_id']} | score={source['score']}")


if __name__ == "__main__":
    main()
