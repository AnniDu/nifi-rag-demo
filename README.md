# nifi-rag-demo

A minimal local RAG demo for Apache NiFi Processor documentation using LlamaIndex, ChromaDB, and an OpenAI-compatible chat endpoint.

## What it does

- Loads `.md`, `.txt`, and `.java` files from `./docs`
- Chunks the files with LlamaIndex
- Stores embeddings, chunks, and metadata in a local persistent ChromaDB collection
- Retrieves relevant chunks for a question
- Builds a grounded prompt and sends it to an OpenAI-compatible LLM endpoint
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
OPENAI_API_KEY=sk-your-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBED_MODEL=text-embedding-3-small
```

For another OpenAI-compatible provider, set `OPENAI_BASE_URL`, `OPENAI_MODEL`, and `OPENAI_EMBED_MODEL` to values supported by that provider.

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

The local ChromaDB data is persisted in `./chroma_db`.

## Query

```bash
python3 query.py "Which processor should I use to write records to a database?"
```

Optional arguments:

```bash
python3 query.py "How does ExecuteScript handle processor properties?" --top-k 8 --chroma-dir ./chroma_db
```

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
