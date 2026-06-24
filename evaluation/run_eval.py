from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from hierarchical_rag import HierarchicalRagResult, source_file, structured_evidence_to_dict, answer_hierarchical
from rag_config import DEFAULT_CHROMA_DIR, get_gemini_embed_model, get_gemini_model

EVALUATION_DIR = Path(__file__).resolve().parent
DEFAULT_QUESTIONS_FILE = EVALUATION_DIR / "questions.yaml"
DEFAULT_RUNS_DIR = EVALUATION_DIR / "runs"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run inspection evals for the NiFi hierarchical RAG pipeline.")
    parser.add_argument("--questions-file", type=Path, default=DEFAULT_QUESTIONS_FILE, help="YAML file containing evaluation questions.")
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS_DIR, help="Directory where timestamped eval JSON files are written.")
    parser.add_argument("--chroma-dir", type=Path, default=DEFAULT_CHROMA_DIR, help="Directory containing the persisted ChromaDB index.")
    parser.add_argument("--top-k", type=int, default=5, help="Chunks to retrieve per decomposed subquery.")
    parser.add_argument("--limit", type=int, default=None, help="Only run the first N questions.")
    parser.add_argument("--tag", default=None, help="Optional label included in the output file and run metadata.")
    return parser.parse_args()


def load_questions(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        questions = yaml.safe_load(file) or []
    if not isinstance(questions, list):
        raise ValueError(f"Expected a list of questions in {path}")
    return questions


def safe_tag(tag: str | None) -> str:
    if not tag:
        return ""
    cleaned = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in tag.strip())
    return cleaned.strip("_")


def output_path(runs_dir: Path, timestamp: datetime, tag: str | None) -> Path:
    stamp = timestamp.strftime("%Y_%m_%d_%H%M%S")
    cleaned_tag = safe_tag(tag)
    filename = f"run_{stamp}.json" if not cleaned_tag else f"run_{stamp}_{cleaned_tag}.json"
    return runs_dir / filename


def chunk_to_dict(chunk) -> dict[str, Any]:
    return {
        "chunk_id": chunk.chunk_id,
        "source_file": source_file(chunk.metadata),
        "metadata": chunk.metadata,
        "distance": chunk.distance,
    }


def result_to_record(question_config: dict[str, Any], result: HierarchicalRagResult) -> dict[str, Any]:
    timestamp = datetime.now().astimezone().isoformat()
    retrievals = []
    for subquery in result.subqueries:
        chunks = result.retrievals.get(subquery, [])
        retrievals.append(
            {
                "subquery": subquery,
                "chunks": [chunk_to_dict(chunk) for chunk in chunks],
            }
        )

    return {
        "id": question_config.get("id"),
        "question": question_config.get("question"),
        "category": question_config.get("category"),
        "expected_topics": question_config.get("expected_topics", []),
        "notes": question_config.get("notes", ""),
        "timestamp": timestamp,
        "subqueries": result.subqueries,
        "retrievals": retrievals,
        "evidence": [structured_evidence_to_dict(summary) for summary in result.evidence_summaries],
        "final_answer": result.answer,
    }


def error_record(question_config: dict[str, Any], error: Exception) -> dict[str, Any]:
    return {
        "timestamp": datetime.now().astimezone().isoformat(),
        "id": question_config.get("id"),
        "question": question_config.get("question"),
        "category": question_config.get("category"),
        "expected_topics": question_config.get("expected_topics", []),
        "notes": question_config.get("notes", ""),
        "error": {
            "type": type(error).__name__,
            "message": str(error),
        },
    }


def run_eval(args: argparse.Namespace) -> Path:
    started_at = datetime.now().astimezone()
    questions = load_questions(args.questions_file)
    if args.limit is not None:
        questions = questions[: args.limit]

    run = {
        "run": {
            "timestamp": started_at.isoformat(),
            "tag": args.tag,
            "questions_file": str(args.questions_file),
            "chroma_dir": str(args.chroma_dir),
            "config": {
                "top_k": args.top_k,
                "model": get_gemini_model(),
                "embedding_model": get_gemini_embed_model(),
            },
        },
        "results": [],
    }

    for index, question_config in enumerate(questions, start=1):
        question_id = question_config.get("id", f"question_{index}")
        question_text = str(question_config.get("question", "")).strip()
        if not question_text:
            run["results"].append(error_record(question_config, ValueError("Missing question text.")))
            continue

        print(f"[{index}/{len(questions)}] {question_id}: {question_text}")
        try:
            result = answer_hierarchical(question_text, chroma_dir=args.chroma_dir, top_k=args.top_k)
            run["results"].append(result_to_record(question_config, result))
        except Exception as exc:
            run["results"].append(error_record(question_config, exc))
            print(f"  error: {type(exc).__name__}: {exc}")

    args.runs_dir.mkdir(parents=True, exist_ok=True)
    path = output_path(args.runs_dir, started_at, args.tag)
    with path.open("w", encoding="utf-8") as file:
        json.dump(run, file, indent=2)
        file.write("\n")
    return path


def main() -> None:
    args = parse_args()
    path = run_eval(args)
    print(f"Saved eval results to {path}")


if __name__ == "__main__":
    main()
