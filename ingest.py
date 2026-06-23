from __future__ import annotations

import argparse
from pathlib import Path

from llama_index.core import Settings, SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter

from rag_config import (
    DEFAULT_CHROMA_DIR,
    DEFAULT_DOCS_DIR,
    SUPPORTED_EXTENSIONS,
    get_chroma_vector_store,
    get_embedding_model,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest NiFi docs into a local ChromaDB index.")
    parser.add_argument("--docs-dir", type=Path, default=DEFAULT_DOCS_DIR, help="Directory containing .md, .txt, and .java files.")
    parser.add_argument("--chroma-dir", type=Path, default=DEFAULT_CHROMA_DIR, help="Directory where ChromaDB persists data.")
    parser.add_argument("--chunk-size", type=int, default=1024, help="Target chunk size in tokens.")
    parser.add_argument("--chunk-overlap", type=int, default=150, help="Chunk overlap in tokens.")
    return parser.parse_args()


def load_documents(docs_dir: Path):
    if not docs_dir.exists():
        raise FileNotFoundError(f"Docs directory does not exist: {docs_dir}")

    documents = SimpleDirectoryReader(
        input_dir=str(docs_dir),
        recursive=True,
        required_exts=sorted(SUPPORTED_EXTENSIONS),
        filename_as_id=True,
    ).load_data()

    if not documents:
        raise ValueError(f"No supported documents found in {docs_dir}")

    return documents


def main() -> None:
    args = parse_args()

    Settings.embed_model = get_embedding_model()
    Settings.node_parser = SentenceSplitter(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    documents = load_documents(args.docs_dir)
    vector_store = get_chroma_vector_store(args.chroma_dir)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True,
    )

    nodes = len(index.docstore.docs)
    print(f"Ingested {len(documents)} documents into {args.chroma_dir}")
    print(f"Created {nodes} chunks in ChromaDB")


if __name__ == "__main__":
    main()
