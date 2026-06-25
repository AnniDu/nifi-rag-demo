from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from hierarchical_rag import HierarchicalRagResult, answer_hierarchical, source_file, structured_evidence_to_dict
from rag_config import DEFAULT_CHROMA_DIR, get_embed_model, get_embed_provider, get_llm_model, get_llm_provider

EVALUATION_DIR = Path(__file__).resolve().parent
DEFAULT_QUESTIONS_FILE = EVALUATION_DIR / "questions.yaml"
DEFAULT_RUNS_DIR = EVALUATION_DIR / "runs"
REFUSAL_PHRASES = [
    "not found in the retrieved documents",
    "retrieved documents do not contain",
    "not enough information",
    "cannot determine from the provided context",
    "i don't know based on the provided documents",
    "the provided documents do not mention",
    "not supported by the retrieved context",
]


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


def classify_observed_behavior(answer: str) -> str:
    answer_text = answer.strip().lower()
    if not answer_text:
        return "unclear"
    if any(phrase in answer_text for phrase in REFUSAL_PHRASES):
        return "refuse"
    return "answer"


def chunk_to_dict(chunk) -> dict[str, Any]:
    return {
        "chunk_id": chunk.chunk_id,
        "source_file": source_file(chunk.metadata),
        "metadata": chunk.metadata,
        "distance": chunk.distance,
    }


def retrieval_distance_analysis(retrievals: list[dict[str, Any]]) -> dict[str, Any]:
    distance_rows = []
    for retrieval in retrievals:
        for chunk in retrieval["chunks"]:
            distance = chunk.get("distance")
            if distance is None:
                continue
            distance_rows.append(
                {
                    "distance": float(distance),
                    "source_file": chunk.get("source_file") or "unknown",
                    "chunk_id": chunk.get("chunk_id"),
                }
            )

    if not distance_rows:
        return {
            "best_distance": None,
            "median_distance": None,
            "worst_distance": None,
            "top_source_file": None,
        }

    distances = [row["distance"] for row in distance_rows]
    best_row = min(distance_rows, key=lambda row: row["distance"])
    return {
        "best_distance": min(distances),
        "median_distance": median(distances),
        "worst_distance": max(distances),
        "top_source_file": best_row["source_file"],
    }


def behavior_pass(expected_behavior: Any, observed_behavior: str) -> bool | None:
    if expected_behavior is None:
        return None
    expected = str(expected_behavior).strip().lower()
    if not expected:
        return None
    return observed_behavior == expected


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

    observed_behavior = classify_observed_behavior(result.answer)
    expected_behavior = question_config.get("expected_behavior")
    pass_value = behavior_pass(expected_behavior, observed_behavior)

    record = {
        "id": question_config.get("id"),
        "question": question_config.get("question"),
        "category": question_config.get("category"),
        "expected_topics": question_config.get("expected_topics", []),
        "notes": question_config.get("notes", ""),
        "timestamp": timestamp,
        "subqueries": result.subqueries,
        "retrievals": retrievals,
        "retrieval_distance_analysis": retrieval_distance_analysis(retrievals),
        "evidence": [structured_evidence_to_dict(summary) for summary in result.evidence_summaries],
        "final_answer": result.answer,
        "observed_behavior": observed_behavior,
    }
    if expected_behavior is not None:
        record["expected_behavior"] = expected_behavior
        record["behavior_pass"] = pass_value
    return record


def error_record(question_config: dict[str, Any], error: Exception) -> dict[str, Any]:
    expected_behavior = question_config.get("expected_behavior")
    record = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "id": question_config.get("id"),
        "question": question_config.get("question"),
        "category": question_config.get("category"),
        "expected_topics": question_config.get("expected_topics", []),
        "notes": question_config.get("notes", ""),
        "retrieval_distance_analysis": {
            "best_distance": None,
            "median_distance": None,
            "worst_distance": None,
            "top_source_file": None,
        },
        "observed_behavior": "unclear",
        "error": {
            "type": type(error).__name__,
            "message": str(error),
        },
    }
    if expected_behavior is not None:
        record["expected_behavior"] = expected_behavior
        record["behavior_pass"] = behavior_pass(expected_behavior, "unclear")
    return record


def average(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def build_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    behavior_counts = {"answer": 0, "refuse": 0, "unclear": 0}
    expected_results = []
    answer_best_distances = []
    refuse_best_distances = []

    for result in results:
        observed = result.get("observed_behavior", "unclear")
        if observed not in behavior_counts:
            observed = "unclear"
        behavior_counts[observed] += 1

        if "behavior_pass" in result and result["behavior_pass"] is not None:
            expected_results.append(bool(result["behavior_pass"]))

        best_distance = result.get("retrieval_distance_analysis", {}).get("best_distance")
        if best_distance is not None and observed == "answer":
            answer_best_distances.append(float(best_distance))
        elif best_distance is not None and observed == "refuse":
            refuse_best_distances.append(float(best_distance))

    pass_rate = None
    if expected_results:
        pass_rate = sum(1 for value in expected_results if value) / len(expected_results)

    return {
        "total_cases": len(results),
        "answer_count": behavior_counts["answer"],
        "refuse_count": behavior_counts["refuse"],
        "unclear_count": behavior_counts["unclear"],
        "pass_rate": pass_rate,
        "expected_behavior_cases": len(expected_results),
        "average_best_distance_answer_cases": average(answer_best_distances),
        "average_best_distance_refuse_cases": average(refuse_best_distances),
    }


def format_distance(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.4f}"


def print_summary_table(results: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    print("\nEvaluation summary")
    print("==================")
    headers = ["case", "expected", "observed", "pass", "best", "median", "top_source_file"]
    print(" | ".join(headers))
    print(" | ".join("-" * len(header) for header in headers))
    for result in results:
        analysis = result.get("retrieval_distance_analysis", {})
        expected = result.get("expected_behavior", "n/a")
        pass_value = result.get("behavior_pass")
        pass_text = "n/a" if pass_value is None else ("pass" if pass_value else "fail")
        row = [
            str(result.get("id", "n/a")),
            str(expected),
            str(result.get("observed_behavior", "unclear")),
            pass_text,
            format_distance(analysis.get("best_distance")),
            format_distance(analysis.get("median_distance")),
            str(analysis.get("top_source_file") or "n/a"),
        ]
        print(" | ".join(row))

    print("\nAggregate stats")
    print("===============")
    print(f"total cases: {summary['total_cases']}")
    print(f"answer count: {summary['answer_count']}")
    print(f"refuse count: {summary['refuse_count']}")
    print(f"unclear count: {summary['unclear_count']}")
    if summary["pass_rate"] is None:
        print("pass rate: n/a")
    else:
        print(f"pass rate: {summary['pass_rate']:.2%} ({summary['expected_behavior_cases']} expected cases)")
    print(f"average best distance for answer cases: {format_distance(summary['average_best_distance_answer_cases'])}")
    print(f"average best distance for refuse cases: {format_distance(summary['average_best_distance_refuse_cases'])}")
    print()


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
                "llm_provider": get_llm_provider(),
                "llm_model": get_llm_model(),
                "embed_provider": get_embed_provider(),
                "embedding_model": get_embed_model(),
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

    summary = build_summary(run["results"])
    run["summary"] = summary
    print_summary_table(run["results"], summary)

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
