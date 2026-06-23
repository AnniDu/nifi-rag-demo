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

Use `--debug` to print each retrieved chunk id, source file, distance, and the first 300 characters before the answer.

The answer is grounded only in retrieved chunks. If the retrieved context does not contain the answer, the model is instructed to say it does not know.

## Project Layout

```text
nifi-rag-demo/
  docs/
  ingest.py
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
