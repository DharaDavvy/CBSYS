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
        source_file = doc.metadata.get("source", "NUC CCMAS Computing")
        source_label = f"{source_file}, Page {page}"
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
    target_career: str = "",
    skills: list[str] | None = None,
    department: str = "Computer Science",
    k: int = 8,
) -> dict:
    """Generate a structured academic roadmap using RAG.

    Returns {"roadmap": list[dict], "sources": list[str]}
    """
    if skills is None:
        skills = []

    # Build a composite query anchored to the student's remaining years,
    # their target career, and their interests so we retrieve the most
    # relevant curriculum chunks.
    year = level // 100  # e.g. 300 → 3
    level_terms = " ".join(
        f"year {y} level {y * 100}" for y in range(year, 6)
    )
    query_parts = [f"{department} programme structure {level_terms}"]
    if target_career:
        query_parts.append(f"courses for career in {target_career}")
    if interests:
        query_parts.append("courses related to " + ", ".join(interests))
    query = ". ".join(query_parts)

    docs = emb.search(query, k=k)
    context_text, sources = _format_context(docs)

    prompt = ROADMAP_SYSTEM_PROMPT.format(
        level=level,
        department=department,
        target_career=target_career or "not specified",
        interests=", ".join(interests) if interests else "none specified",
        skills=", ".join(skills) if skills else "none listed",
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
