"""
Tests for the Pydantic request/response schemas.
"""

import pytest
from pydantic import ValidationError
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    RoadmapRequest,
    SemesterNode,
    RoadmapResponse,
    UserCreate,
    UserResponse,
    ProfileUpdate,
    ProfileResponse,
    CourseEntry,
    TranscriptUpdate,
    TranscriptResponse,
    ChatMessageOut,
    ChatHistoryResponse,
)


class TestChatSchemas:
    def test_chat_request_valid(self):
        req = ChatRequest(message="What are the prerequisites for CSC 301?")
        assert req.message == "What are the prerequisites for CSC 301?"

    def test_chat_request_missing_message_raises(self):
        with pytest.raises(ValidationError):
            ChatRequest()

    def test_chat_response_defaults(self):
        resp = ChatResponse(response="Answer text")
        assert resp.response == "Answer text"
        assert resp.sources == []

    def test_chat_response_with_sources(self):
        resp = ChatResponse(response="text", sources=["NUC CCMAS, Page 5"])
        assert len(resp.sources) == 1


class TestRoadmapSchemas:
    def test_roadmap_request_minimal(self):
        req = RoadmapRequest()
        assert req.level is None
        assert req.interests == []
        assert req.completed_courses == []

    def test_roadmap_request_full(self):
        req = RoadmapRequest(level=300, interests=["AI"], completed_courses=["CSC 101"])
        assert req.level == 300

    def test_semester_node(self):
        node = SemesterNode(semester="Year 1 – Semester 1", courses=["CSC 101", "MTH 101"])
        assert len(node.courses) == 2

    def test_roadmap_response_defaults(self):
        resp = RoadmapResponse()
        assert resp.roadmap == []
        assert resp.sources == []


class TestUserSchemas:
    def test_user_create_valid(self):
        user = UserCreate(name="John", matricNumber="CSC/2024/001", level=300)
        assert user.department == "Computer Science"

    def test_user_create_missing_fields_raises(self):
        with pytest.raises(ValidationError):
            UserCreate(name="John")

    def test_user_response(self):
        resp = UserResponse(name="John", matricNumber="CSC/2024/001", level=300, department="CS")
        assert resp.level == 300


class TestProfileSchemas:
    def test_profile_update_defaults(self):
        profile = ProfileUpdate()
        assert profile.interests == []
        assert profile.skills == []
        assert profile.targetCareer == ""

    def test_profile_response_with_data(self):
        profile = ProfileResponse(interests=["AI", "Web Dev"], targetCareer="ML Engineer")
        assert len(profile.interests) == 2


class TestTranscriptSchemas:
    def test_course_entry(self):
        entry = CourseEntry(code="CSC 301", title="Algo", units=3, grade="A", semester="1st")
        assert entry.units == 3

    def test_transcript_update(self):
        courses = [CourseEntry(code="CSC 101", title="Intro", units=2, grade="B", semester="1st")]
        t = TranscriptUpdate(courses=courses)
        assert len(t.courses) == 1

    def test_transcript_response_defaults(self):
        resp = TranscriptResponse()
        assert resp.courses == []


class TestChatHistorySchemas:
    def test_chat_message_out(self):
        msg = ChatMessageOut(role="assistant", content="Hello")
        assert msg.sources == []
        assert msg.timestamp == ""

    def test_chat_history_response(self):
        resp = ChatHistoryResponse()
        assert resp.messages == []
