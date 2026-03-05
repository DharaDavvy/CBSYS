"""
Roadmap endpoint — POST /generate-roadmap

Generates a structured semester-by-semester academic plan
using the student's profile and the RAG pipeline.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import RoadmapRequest, RoadmapResponse, SemesterNode
from app.services import rag
from app.routers.auth import verify_token
from app.models import firebase as fb

router = APIRouter(prefix="/generate-roadmap", tags=["Roadmap"])

# Grades that count as a passed course
_PASSING_GRADES = {"A", "B", "C", "D", "Pass", "P"}


@router.post("", response_model=RoadmapResponse)
async def generate_roadmap(
    body: RoadmapRequest,
    uid: str = Depends(verify_token),
):
    """Generate a personalised academic roadmap.

    Pulls level, interests, target career, department, and transcript
    directly from Firestore so the client only needs to supply a user_id.
    Any fields passed in the request body override the stored values.
    Only courses with a passing grade are treated as completed.
    """
    # ── Fetch stored data ────────────────────────────────────────────
    user = fb.get_user(uid) or {}
    profile = fb.get_profile(uid) or {}
    transcript_rows = fb.get_transcript(uid)

    # ── Resolve level ────────────────────────────────────────────────
    level = body.level or user.get("level")
    if not level:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Level could not be determined — please complete your profile.",
        )

    # ── Resolve interests (body overrides stored) ────────────────────
    interests: list[str] = body.interests or profile.get("interests", [])

    # ── Derive completed courses from passing grades only ────────────
    passed_codes: list[str] = [
        row["code"]
        for row in transcript_rows
        if row.get("grade", "").strip().upper() in {g.upper() for g in _PASSING_GRADES}
    ]
    # Allow request body to supplement (union, no duplicates)
    completed_courses: list[str] = list(
        dict.fromkeys(passed_codes + list(body.completed_courses))
    )

    # ── Extra context signals ────────────────────────────────────────
    target_career: str = profile.get("targetCareer", "")
    skills: list[str] = profile.get("skills", [])
    department: str = user.get("department", "Computer Science")

    result = await rag.generate_roadmap(
        level=level,
        interests=interests,
        completed_courses=completed_courses,
        target_career=target_career,
        skills=skills,
        department=department,
    )

    # Normalise the raw dicts into SemesterNode models
    roadmap_nodes = []
    for item in result["roadmap"]:
        if isinstance(item, dict):
            roadmap_nodes.append(
                SemesterNode(
                    semester=item.get("semester", "Unknown"),
                    courses=item.get("courses", []),
                )
            )

    return RoadmapResponse(
        roadmap=roadmap_nodes,
        sources=result["sources"],
    )
