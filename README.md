# nifi-rag-demo

A minimal local RAG demo for Apache NiFi Processor documentation using LlamaIndex, ChromaDB, and local Ollama models by default.

## What it does

- Loads `.md`, `.txt`, and `.java` files from `./docs`
- Chunks the files with LlamaIndex
- Stores embeddings, chunks, and metadata in a local persistent ChromaDB collection
- Retrieves relevant chunks for a question
- Builds grounded prompts and sends them to a local Ollama model by default
- Prints the answer and the source file names / chunk IDs used

## Setup

```bash
cd nifi-rag-demo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` for local Ollama defaults:

```bash
RAG_LLM_PROVIDER=ollama
RAG_EMBED_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:1.5b
OLLAMA_EMBED_MODEL=nomic-embed-text
OLLAMA_NUM_PREDICT=128
OLLAMA_NUM_THREAD=16
OLLAMA_KEEP_ALIVE=10m
OLLAMA_TIMEOUT_SECONDS=30
RAG_MAX_CHARS_PER_CHUNK=1000
RAG_EVIDENCE_MODE=llm
```

Install Ollama separately, start it, then pull the recommended CPU-friendly models for this machine:

```bash
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text
```

This machine has 32 CPU threads and 503 GiB RAM, but no detected NVIDIA GPU. `qwen2.5:1.5b` is the current CPU-friendly default for faster local iteration; `qwen2.5:3b` or `qwen2.5:7b` may improve answer quality but is noticeably slower on CPU-only hardware. `nomic-embed-text` keeps retrieval local too.

Ollama performance knobs:

- `OLLAMA_NUM_PREDICT` caps generated tokens per model call. Lower values are faster.
- `OLLAMA_NUM_THREAD` controls CPU threads used by Ollama. Start with `16` on this host.
- `OLLAMA_KEEP_ALIVE` keeps the model warm between calls.
- `RAG_MAX_CHARS_PER_CHUNK` caps retrieved chunk text sent into evidence extraction. Use `0` to disable truncation.

Optional Gemini fallback is still supported:

```bash
RAG_LLM_PROVIDER=gemini
RAG_EMBED_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash
GEMINI_EMBED_MODEL=gemini-embedding-001
```

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

Each ingest run clears the existing local ChromaDB collection, then rebuilds the index from all supported files under `./docs` recursively. The local ChromaDB data is persisted in `./chroma_db`. Re-run ingest after switching embedding providers or embedding models, because Chroma collections must use one embedding dimensionality.

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

The JSON captures the question metadata, decomposed subqueries, retrieved chunk ids, source files, distances, structured evidence, final answer, timestamp, `top_k`, LLM provider/model, and embedding provider/model.

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
