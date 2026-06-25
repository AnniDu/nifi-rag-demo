from __future__ import annotations

import argparse
from pathlib import Path

from hierarchical_rag import answer_hierarchical, print_debug_result
from rag_config import DEFAULT_CHROMA_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query the local NiFi RAG index with hierarchical RAG.")
    parser.add_argument("question", nargs="*", help="Question to ask.")
    parser.add_argument("--chroma-dir", type=Path, default=DEFAULT_CHROMA_DIR, help="Directory containing the persisted ChromaDB index.")
    parser.add_argument("--top-k", type=int, default=1, help="Number of chunks to retrieve per decomposed subquery.")
    parser.add_argument("--debug", action="store_true", help="Print decomposition, retrieval, evidence, final prompt, and timing diagnostics.")
    parser.add_argument("--timing", action="store_true", help="Print live timestamp checkpoints while the query runs.")
    parser.add_argument("--examples", action="store_true", help="Print Hierarchical RAG CLI examples and exit.")
    return parser.parse_args()


def print_cli_examples() -> None:
    print("Hierarchical RAG examples:")
    print()
    print("Basic query:")
    print('  .venv/bin/python query.py "How do I consume from Kafka and write to HDFS?"')
    print()
    print("Show decomposition, retrieval, evidence, final prompt, and timing:")
    print('  .venv/bin/python query.py --debug "How do I consume from Kafka and write to HDFS and Iceberg?"')
    print()
    print("Show live timing checkpoints only:")
    print('  .venv/bin/python query.py --timing "How do I consume from Kafka and write to HDFS?"')
    print()
    print("Change chunks retrieved per decomposed subquery:")
    print('  .venv/bin/python query.py --top-k 3 "How do I consume from Kafka and write to HDFS?"')
    print()
    print("Use a custom Chroma index directory:")
    print('  .venv/bin/python query.py --chroma-dir ./chroma_db "Which processor writes to HDFS?"')


def main() -> None:
    args = parse_args()
    if args.examples:
        print_cli_examples()
        return
    if not args.question:
        raise SystemExit("Question is required unless --examples is used.")

    question = " ".join(args.question)

    result = answer_hierarchical(question, chroma_dir=args.chroma_dir, top_k=args.top_k, timing=args.timing or args.debug)
    if args.debug:
        print_debug_result(result)

    print(result.answer.strip())
    print("\nSources:")
    seen_sources = []
    for summary in result.evidence_summaries:
        for source in summary.sources:
            if source not in seen_sources:
                seen_sources.append(source)
    if not seen_sources:
        print("- none")
        return
    for source in seen_sources:
        print(f"- {source}")


if __name__ == "__main__":
    main()
