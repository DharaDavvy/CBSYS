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
from app.services.sql_roadmap import build_sql_roadmap, build_sql_knowledge_graph


def _format_context(docs) -> tuple[str, list[str]]:
    """Join retrieved documents into a single context string.

    Returns (context_text, source_labels).
    """
    context_parts: list[str] = []
    sources: list[str] = []

    for i, doc in enumerate(docs, 1):
        meta = doc.metadata
        page = meta.get("page", "?")
        source_file = meta.get("source", "NUC CCMAS Computing")
        course_code = meta.get("course_code", "")
        section = meta.get("section", "")
        level = meta.get("level", "")
        semester = meta.get("semester", "")
        units = meta.get("units", "")
        prerequisites = meta.get("prerequisites", [])

        # Rich source label for citations
        label_parts = [source_file]
        if section:
            label_parts.append(f"Section {section}")
        else:
            label_parts.append(f"Page {page}")
        if course_code:
            label_parts.append(course_code)
        source_label = ", ".join(label_parts)

        # Rich context header for LLM
        header_parts = [f"[{i}]"]
        if course_code:
            header_parts.append(f"Course: {course_code}")
        if level:
            header_parts.append(f"Level: {level}")
        if semester:
            header_parts.append(f"Semester: {semester}")
        if units:
            header_parts.append(f"Units: {units}")
        if prerequisites:
            header_parts.append(f"Prerequisites: {', '.join(prerequisites)}")
        header_parts.append(f"Page: {page}")

        context_parts.append(f"{' | '.join(header_parts)}\n{doc.page_content}")
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
    """Generate a structured academic roadmap from the SQL curriculum seeds.

    Returns {"roadmap": list[dict], "sources": list[str]}
    """
    if skills is None:
        skills = []

    return build_sql_roadmap(
        level=level,
        interests=interests,
        completed_courses=completed_courses,
        target_career=target_career,
        skills=skills,
        department=department,
    )


async def generate_knowledge_graph(
    career_sector: str,
    department: str = "Computer Science",
    k: int = 10,
) -> dict:
    """Generate a knowledge pillar dependency graph from the SQL curriculum.

    Returns {"pillars": list[dict], "dependencies": list[dict], "sources": list[str]}
    Each dependency dict has keys "from_pillar" and "to_pillar".
    """
    return build_sql_knowledge_graph(
        career_sector=career_sector,
        department=department,
    )
