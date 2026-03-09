"""
Tests for FastAPI endpoints — uses TestClient with mocked services.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a TestClient that skips the real lifespan (FAISS/LLM/Firebase)."""
    # Patch startup services so they don't run
    with (
        patch("app.services.embeddings.init_vectorstore"),
        patch("app.services.llm.init_llm", new_callable=AsyncMock),
        patch("app.models.firebase.init_firebase"),
    ):
        from app.main import app
        with TestClient(app) as c:
            yield c


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestChatEndpoint:
    def test_chat_requires_auth(self, client):
        resp = client.post("/chat", json={"message": "hello"})
        assert resp.status_code in (401, 403)

    def test_chat_success_with_dev_token(self, client):
        """In dev mode (Firebase not ready), Bearer token = UID passthrough."""
        with (
            patch("app.routers.auth.firebase_is_ready", return_value=False),
            patch("app.services.rag.ask", new_callable=AsyncMock) as mock_ask,
            patch("app.models.firebase.append_chat_message"),
        ):
            mock_ask.return_value = {
                "response": "Test answer",
                "sources": ["CCMAS.pdf, Page 1"],
            }
            resp = client.post(
                "/chat",
                json={"message": "test question"},
                headers={"Authorization": "Bearer test-uid"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["response"] == "Test answer"
            assert len(data["sources"]) == 1


class TestRoadmapEndpoint:
    def test_roadmap_requires_auth(self, client):
        resp = client.post("/generate-roadmap", json={})
        assert resp.status_code in (401, 403)


class TestUserEndpoints:
    def test_get_me_requires_auth(self, client):
        resp = client.get("/users/me")
        assert resp.status_code in (401, 403)
