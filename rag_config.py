from __future__ import annotations

import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DOCS_DIR = PROJECT_ROOT / "docs"
DEFAULT_CHROMA_DIR = PROJECT_ROOT / "chroma_db"
COLLECTION_NAME = "nifi_processor_docs"
SUPPORTED_EXTENSIONS = {".md", ".txt", ".java"}


def load_environment() -> None:
    load_dotenv(PROJECT_ROOT / ".env")


def get_embedding_model() -> OpenAIEmbedding:
    load_environment()
    return OpenAIEmbedding(
        model=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small"),
        api_key=os.getenv("OPENAI_API_KEY"),
        api_base=os.getenv("OPENAI_BASE_URL"),
    )


def get_chroma_vector_store(chroma_dir: Path = DEFAULT_CHROMA_DIR) -> ChromaVectorStore:
    client = chromadb.PersistentClient(path=str(chroma_dir))
    collection = client.get_or_create_collection(COLLECTION_NAME)
    return ChromaVectorStore(chroma_collection=collection)
