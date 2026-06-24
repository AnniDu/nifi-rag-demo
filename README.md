# nifi-rag-demo

A minimal local RAG demo for Apache NiFi Processor documentation using LlamaIndex, ChromaDB, and the Gemini API.

## What it does

- Loads `.md`, `.txt`, and `.java` files from `./docs`
- Chunks the files with LlamaIndex
- Stores embeddings, chunks, and metadata in a local persistent ChromaDB collection
- Retrieves relevant chunks for a question
- Builds a grounded prompt and sends it to the Gemini API
- Prints the answer and the source file names / chunk IDs used

## Setup

```bash
cd nifi-rag-demo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

```bash
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash
GEMINI_EMBED_MODEL=gemini-embedding-001
```

Create a Gemini API key in Google AI Studio, then set `GEMINI_API_KEY` in `.env`.

## Add Documents

Put NiFi Processor documentation or source files in `./docs`:

```text
docs/
  PutDatabaseRecord.md
  QueryDatabaseTable.txt
  ExecuteScript.java
```

Nested directories are supported.

## Ingest

```bash
python3 ingest.py
```

Optional arguments:

```bash
python3 ingest.py --docs-dir ./docs --chroma-dir ./chroma_db --chunk-size 1024 --chunk-overlap 150
```

Each ingest run clears the existing local ChromaDB collection, then rebuilds the index from all supported files under `./docs` recursively. The local ChromaDB data is persisted in `./chroma_db`.

## Query

```bash
python3 query.py "Which processor should I use to write records to a database?"
```

Optional arguments:

```bash
python3 query.py "How does ExecuteScript handle processor properties?" --top-k 8 --chroma-dir ./chroma_db
python3 query.py "How do I consume Kafka messages?" --debug
```

Use `--debug` to print decomposition, per-subquery retrieved chunk ids, structured evidence, and the final answer prompt.

The hierarchical answer is grounded in structured evidence extracted from retrieved chunks. Raw chunks are used for evidence extraction, but the final answer model receives only the user question and structured evidence.

## Evaluation

This project includes a lightweight inspection/regression harness under `evaluation/`.

Evaluation questions live in `evaluation/questions.yaml`. Add a new question as a YAML list item:

```yaml
- id: q011
  question: "How do I configure a NiFi processor property?"
  category: property_descriptor
  expected_topics:
    - PropertyDescriptor
    - required
  notes: "What you expect retrieval/evidence to include."
```

Run the first three questions with a tag:

```bash
python3 evaluation/run_eval.py --limit 3 --tag baseline
```

Useful options:

```bash
python3 evaluation/run_eval.py --top-k 3 --tag top3
python3 evaluation/run_eval.py --questions-file evaluation/questions.yaml --chroma-dir ./chroma_db
```

Each run writes a timestamped JSON file under `evaluation/runs/`, for example:

```text
evaluation/runs/run_2026_06_24_153000_baseline.json
```

The JSON captures the question metadata, decomposed subqueries, retrieved chunk ids, source files, distances, structured evidence, final answer, timestamp, `top_k`, Gemini model, and embedding model.

To compare results manually, run the same question set with different tags, then inspect or diff the JSON files:

```bash
python3 evaluation/run_eval.py --limit 3 --top-k 5 --tag baseline_top5
python3 evaluation/run_eval.py --limit 3 --top-k 8 --tag top8
ls evaluation/runs/
diff -u evaluation/runs/<baseline>.json evaluation/runs/<candidate>.json
```

There is no automatic LLM grading yet. Treat these outputs as inspection artifacts for retrieval and answer regression checks.

## Project Layout

```text
nifi-rag-demo/
  docs/
  evaluation/
    questions.yaml
    run_eval.py
    runs/
  hierarchical_rag.py
  ingest.py
  prompts.py
  query.py
  rag_config.py
  requirements.txt
  .env.example
  README.md
```

## Notes

- This project intentionally avoids LangGraph, agents, and complex orchestration.
- Re-run `python3 ingest.py` after adding or changing documents.
- To reset the local index, stop any running process and delete `./chroma_db`.
