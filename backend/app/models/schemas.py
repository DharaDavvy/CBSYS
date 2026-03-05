"""
Pydantic schemas for request/response bodies.
Populated in Phase 2; placeholder keeps imports clean.
"""

from pydantic import BaseModel
from typing import Optional


# ── Chat ─────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    sources: list[str] = []


# ── Roadmap ──────────────────────────────────────────────────────────

class RoadmapRequest(BaseModel):
    user_id: str
    level: int                         # 100–500
    interests: list[str] = []
    completed_courses: list[str] = []  # course codes


class SemesterNode(BaseModel):
    semester: str                      # e.g. "Year 1 – Semester 1"
    courses: list[str]


class RoadmapResponse(BaseModel):
    roadmap: list[SemesterNode] = []
    sources: list[str] = []
