"""
RAG service — ties together embeddings retrieval and LLM generation.

Flow:
  1. Embed the user query → retrieve top-k chunks from FAISS
  2. Build a prompt with the system instruction + context + question
  3. Call the LLM → post-process to attach citations
  4. Return (answer, sources)
"""

from app.services import embeddings as emb
from app.services import llm as llm_service
from app.prompts.advisor import ADVISOR_SYSTEM_PROMPT
from app.prompts.roadmap import ROADMAP_SYSTEM_PROMPT


def _format_context(docs) -> tuple[str, list[str]]:
    """Join retrieved documents into a single context string.

    Returns (context_text, source_labels).
    """
    context_parts: list[str] = []
    sources: list[str] = []

    for i, doc in enumerate(docs, 1):
        page = doc.metadata.get("page", "?")
        source_label = f"NUC CCMAS Computing, Page {page}"
        context_parts.append(f"[{i}] (Page {page})\n{doc.page_content}")
        if source_label not in sources:
            sources.append(source_label)

    return "\n\n".join(context_parts), sources


async def ask(question: str, k: int = 5) -> dict:
    """Answer a curriculum question using RAG.

    Returns {"response": str, "sources": list[str]}
    """
    # 1. Retrieve relevant chunks
    docs = emb.search(question, k=k)

    if not docs:
        return {
            "response": (
                "I don't have enough information in the curriculum data "
                "to answer that."
            ),
            "sources": [],
        }

    # 2. Build prompt
    context_text, sources = _format_context(docs)
    prompt = ADVISOR_SYSTEM_PROMPT.format(context=context_text, question=question)

    # 3. Generate answer
    answer = await llm_service.generate(prompt)

    # 4. Ensure citation footer if LLM forgot
    if sources and "[Source:" not in answer:
        citation_line = " | ".join(f"[Source: {s}]" for s in sources)
        answer = f"{answer}\n\n{citation_line}"

    return {"response": answer, "sources": sources}


async def generate_roadmap(
    level: int,
    interests: list[str],
    completed_courses: list[str],
    k: int = 8,
) -> dict:
    """Generate a structured academic roadmap using RAG.

    Returns {"roadmap": list[dict], "sources": list[str]}
    """
    # Build a composite query to pull the most relevant programme-structure chunks
    query_parts = [f"programme structure level {level}"]
    if interests:
        query_parts.append("courses related to " + ", ".join(interests))
    query = ". ".join(query_parts)

    docs = emb.search(query, k=k)
    context_text, sources = _format_context(docs)

    prompt = ROADMAP_SYSTEM_PROMPT.format(
        level=level,
        interests=", ".join(interests) if interests else "none specified",
        completed_courses=", ".join(completed_courses) if completed_courses else "none",
        context=context_text,
    )

    raw = await llm_service.generate(prompt)

    # Try to parse the JSON from the LLM output
    import json

    roadmap: list[dict] = []
    try:
        # The LLM should return pure JSON, but sometimes wraps it in markdown
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            # Strip markdown code fences
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        roadmap = json.loads(cleaned)
    except (json.JSONDecodeError, IndexError):
        # Return the raw text so the caller can still display something
        roadmap = [{"semester": "Raw response", "courses": [raw]}]

    return {"roadmap": roadmap, "sources": sources}
