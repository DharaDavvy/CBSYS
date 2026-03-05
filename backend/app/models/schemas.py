"""
Pydantic schemas for request/response bodies.
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
    level: int | None = None           # 100–500; fetched from Firestore if omitted
    interests: list[str] = []
    completed_courses: list[str] = []  # course codes


class SemesterNode(BaseModel):
    semester: str                      # e.g. "Year 1 – Semester 1"
    courses: list[str]


class RoadmapResponse(BaseModel):
    roadmap: list[SemesterNode] = []
    sources: list[str] = []


# ── User Profile ─────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str
    matricNumber: str                  # e.g. "CSC/2024/001"
    level: int                         # 100–500
    department: str = "Computer Science"


class UserResponse(BaseModel):
    name: str
    matricNumber: str
    level: int
    department: str


class ProfileUpdate(BaseModel):
    interests: list[str] = []
    skills: list[str] = []
    targetCareer: str = ""


class ProfileResponse(BaseModel):
    interests: list[str] = []
    skills: list[str] = []
    targetCareer: str = ""


# ── Transcript ───────────────────────────────────────────────────────

class CourseEntry(BaseModel):
    code: str
    title: str
    units: int
    grade: str
    semester: str


class TranscriptUpdate(BaseModel):
    courses: list[CourseEntry]


class TranscriptResponse(BaseModel):
    courses: list[CourseEntry] = []


# ── Chat History ─────────────────────────────────────────────────────

class ChatMessageOut(BaseModel):
    role: str
    content: str
    sources: list[str] = []
    timestamp: str = ""


class ChatHistoryResponse(BaseModel):
    messages: list[ChatMessageOut] = []
