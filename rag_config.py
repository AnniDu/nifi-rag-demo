from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

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
DEFAULT_LLM_PROVIDER = "ollama"
DEFAULT_EMBED_PROVIDER = "ollama"
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "qwen2.5:1.5b"
DEFAULT_OLLAMA_EMBED_MODEL = "nomic-embed-text"
DEFAULT_OLLAMA_NUM_PREDICT = 128
DEFAULT_OLLAMA_NUM_THREAD = 16
DEFAULT_OLLAMA_KEEP_ALIVE = "10m"
DEFAULT_OLLAMA_TIMEOUT_SECONDS = 30
DEFAULT_RAG_MAX_CHARS_PER_CHUNK = 1000
DEFAULT_RAG_EVIDENCE_MODE = "llm"


def load_environment() -> None:
    load_dotenv(PROJECT_ROOT / ".env")


def get_llm_provider() -> str:
    load_environment()
    return os.getenv("RAG_LLM_PROVIDER", DEFAULT_LLM_PROVIDER).strip().lower()


def get_embed_provider() -> str:
    load_environment()
    return os.getenv("RAG_EMBED_PROVIDER", DEFAULT_EMBED_PROVIDER).strip().lower()


def get_ollama_base_url() -> str:
    load_environment()
    return os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).rstrip("/")


def get_ollama_model() -> str:
    load_environment()
    return os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)


def get_ollama_embed_model() -> str:
    load_environment()
    return os.getenv("OLLAMA_EMBED_MODEL", DEFAULT_OLLAMA_EMBED_MODEL)


def get_int_env(name: str, default: int) -> int:
    load_environment()
    raw_value = os.getenv(name)
    if not raw_value:
        return default
    try:
        return int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw_value!r}") from exc


def get_ollama_num_predict() -> int:
    return get_int_env("OLLAMA_NUM_PREDICT", DEFAULT_OLLAMA_NUM_PREDICT)


def get_ollama_num_thread() -> int:
    return get_int_env("OLLAMA_NUM_THREAD", DEFAULT_OLLAMA_NUM_THREAD)


def get_ollama_keep_alive() -> str:
    load_environment()
    return os.getenv("OLLAMA_KEEP_ALIVE", DEFAULT_OLLAMA_KEEP_ALIVE)


def get_ollama_timeout_seconds() -> int:
    return get_int_env("OLLAMA_TIMEOUT_SECONDS", DEFAULT_OLLAMA_TIMEOUT_SECONDS)


def get_max_chars_per_chunk() -> int:
    return get_int_env("RAG_MAX_CHARS_PER_CHUNK", DEFAULT_RAG_MAX_CHARS_PER_CHUNK)


def get_evidence_mode() -> str:
    load_environment()
    return os.getenv("RAG_EVIDENCE_MODE", DEFAULT_RAG_EVIDENCE_MODE).strip().lower()


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


def get_llm_model() -> str:
    provider = get_llm_provider()
    if provider == "gemini":
        return get_gemini_model()
    if provider == "ollama":
        return get_ollama_model()
    raise ValueError(f"Unsupported RAG_LLM_PROVIDER: {provider}")


def get_embed_model() -> str:
    provider = get_embed_provider()
    if provider == "gemini":
        return get_gemini_embed_model()
    if provider == "ollama":
        return get_ollama_embed_model()
    raise ValueError(f"Unsupported RAG_EMBED_PROVIDER: {provider}")


def get_chroma_collection(chroma_dir: Path = DEFAULT_CHROMA_DIR, reset: bool = False):
    client = chromadb.PersistentClient(path=str(chroma_dir))
    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except ValueError:
            pass
    return client.get_or_create_collection(COLLECTION_NAME)


def post_ollama(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = f"{get_ollama_base_url()}{path}"
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=get_ollama_timeout_seconds()) as response:
            return json.loads(response.read().decode("utf-8"))
    except (OSError, TimeoutError, urllib.error.URLError) as exc:
        raise RuntimeError(
            f"Ollama request failed at {get_ollama_base_url()}{path}: {exc}"
        ) from exc


def generate_with_ollama(system_prompt: str, contents: str, *, json_output: bool = False) -> str:
    payload: dict[str, Any] = {
        "model": get_ollama_model(),
        "system": system_prompt,
        "prompt": contents,
        "stream": False,
        "keep_alive": get_ollama_keep_alive(),
        "options": {
            "temperature": 0.1 if json_output else 0.2,
            "num_predict": get_ollama_num_predict(),
            "num_thread": get_ollama_num_thread(),
        },
    }
    if json_output:
        payload["format"] = "json"
    response = post_ollama("/api/generate", payload)
    return str(response.get("response") or "")


def generate_with_gemini(system_prompt: str, contents: str, *, json_output: bool = False) -> str:
    client = get_gemini_client()
    config_kwargs: dict[str, Any] = {
        "system_instruction": system_prompt,
        "temperature": 0.1 if json_output else 0.2,
    }
    if json_output:
        config_kwargs["response_mime_type"] = "application/json"
    response = client.models.generate_content(
        model=get_gemini_model(),
        config=types.GenerateContentConfig(**config_kwargs),
        contents=contents,
    )
    return response.text or ""


def generate_text(system_prompt: str, contents: str, *, json_output: bool = False) -> str:
    provider = get_llm_provider()
    if provider == "ollama":
        return generate_with_ollama(system_prompt, contents, json_output=json_output)
    if provider == "gemini":
        return generate_with_gemini(system_prompt, contents, json_output=json_output)
    raise ValueError(f"Unsupported RAG_LLM_PROVIDER: {provider}")


def embed_texts(texts: list[str], task_type: str) -> list[list[float]]:
    provider = get_embed_provider()
    if provider == "ollama":
        return embed_texts_ollama(texts)
    if provider == "gemini":
        return embed_texts_gemini(texts, task_type=task_type)
    raise ValueError(f"Unsupported RAG_EMBED_PROVIDER: {provider}")


def embed_texts_ollama(texts: list[str]) -> list[list[float]]:
    embeddings: list[list[float]] = []
    model = get_ollama_embed_model()
    for start in range(0, len(texts), 100):
        batch = texts[start : start + 100]
        response = post_ollama("/api/embed", {"model": model, "input": batch})
        batch_embeddings = response.get("embeddings")
        if not isinstance(batch_embeddings, list):
            raise RuntimeError("Ollama /api/embed response did not include embeddings.")
        embeddings.extend(batch_embeddings)
    return embeddings


def embed_texts_gemini(texts: list[str], task_type: str) -> list[list[float]]:
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
