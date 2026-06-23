from __future__ import annotations

import os
import sys
from pathlib import Path

import pysqlite3

sys.modules["sqlite3"] = pysqlite3

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DOCS_DIR = PROJECT_ROOT / "docs"
DEFAULT_CHROMA_DIR = PROJECT_ROOT / "chroma_db"
COLLECTION_NAME = "nifi_processor_docs"
SUPPORTED_EXTENSIONS = {".md", ".txt", ".java"}


def load_environment() -> None:
    load_dotenv(PROJECT_ROOT / ".env")


def get_gemini_client() -> genai.Client:
    load_environment()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY. Add it to .env or export it in your shell.")
    return genai.Client(api_key=api_key)


def get_gemini_model() -> str:
    load_environment()
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def get_gemini_embed_model() -> str:
    load_environment()
    return os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")


def get_chroma_collection(chroma_dir: Path = DEFAULT_CHROMA_DIR, reset: bool = False):
    client = chromadb.PersistentClient(path=str(chroma_dir))
    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except ValueError:
            pass
    return client.get_or_create_collection(COLLECTION_NAME)


def embed_texts(texts: list[str], task_type: str) -> list[list[float]]:
    client = get_gemini_client()
    model = get_gemini_embed_model()
    embeddings: list[list[float]] = []

    for start in range(0, len(texts), 100):
        batch = texts[start : start + 100]
        response = client.models.embed_content(
            model=model,
            contents=batch,
            config=types.EmbedContentConfig(task_type=task_type),
        )
        embeddings.extend([embedding.values for embedding in response.embeddings])

    return embeddings
