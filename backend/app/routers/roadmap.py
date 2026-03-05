"""
Roadmap endpoint — POST /generate-roadmap

Generates a structured semester-by-semester academic plan
using the student's profile and the RAG pipeline.
"""

from fastapi import APIRouter, Depends
from app.models.schemas import RoadmapRequest, RoadmapResponse, SemesterNode
from app.services import rag
from app.routers.auth import verify_token

router = APIRouter(prefix="/generate-roadmap", tags=["Roadmap"])


@router.post("", response_model=RoadmapResponse)
async def generate_roadmap(
    body: RoadmapRequest,
    uid: str = Depends(verify_token),
):
    """Generate a personalised academic roadmap.

    Respects the student's current level, interests, and
    already-completed courses.
    """
    result = await rag.generate_roadmap(
        level=body.level,
        interests=body.interests,
        completed_courses=body.completed_courses,
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
