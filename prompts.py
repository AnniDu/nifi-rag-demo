from __future__ import annotations


DECOMPOSITION_SYSTEM_PROMPT = """You decompose Apache NiFi documentation questions into retrieval subqueries.
Return only valid JSON.
Use this schema:
{
  "subqueries": ["..."]
}
Rules:
- Always return at least one subquery.
- If the question is simple, return one subquery close to the original question.
- If the question mentions multiple systems, processors, destinations, formats, or concepts, split them into separate subqueries.
- Make each subquery specific, standalone, and retrieval-oriented.
- Keep each subquery about Apache NiFi.
- Do not answer the question."""


EVIDENCE_EXTRACTION_SYSTEM_PROMPT = """You extract evidence from Apache NiFi documentation chunks.
Use only the provided chunks.
Return only valid JSON.
Use this schema:
{
  "subquery": "...",
  "supported": true,
  "evidence": ["..."],
  "sources": ["chunk_id"]
}
Rules:
- Summarize only evidence relevant to the subquery.
- Keep evidence concise.
- Cite chunk ids in sources.
- If the chunks do not support the subquery, set supported to false, evidence to [], and sources to [].
- Do not include raw chunk text in the evidence."""


FINAL_ANSWER_SYSTEM_PROMPT = """You answer questions about Apache NiFi Processor documentation.
Use only the provided evidence summaries.
If evidence for part of the question is unsupported, say that part is unsupported by the indexed docs.
Be concise and cite relevant chunk ids from the evidence summaries.
Do not invent details not supported by the evidence."""
