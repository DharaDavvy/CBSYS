"""
Tests for the RAG service — mocks embeddings and LLM to test orchestration logic.
"""

import pytest
from unittest.mock import patch, AsyncMock
from app.services.rag import ask, generate_roadmap, _format_context
from app.services.embeddings import Document


class TestFormatContext:
    def test_empty_docs(self):
        context, sources = _format_context([])
        assert context == ""
        assert sources == []

    def test_single_doc_with_metadata(self):
        doc = Document(
            page_content="CSC 301 covers algorithm design.",
            metadata={
                "page": 42,
                "source": "Computing-CCMAS 2023-FINAL.pdf",
                "course_code": "CSC 301",
                "section": "3.2.1",
                "level": 300,
                "semester": 1,
                "units": 3,
                "prerequisites": ["CSC 201"],
            },
        )
        context, sources = _format_context([doc])
        assert "CSC 301" in context
        assert "Level: 300" in context
        assert "Prerequisites: CSC 201" in context
        assert len(sources) == 1
        assert "Section 3.2.1" in sources[0]

    def test_deduplicates_sources(self):
        docs = [
            Document(
                page_content="Chunk 1",
                metadata={"page": 1, "source": "CCMAS.pdf", "course_code": "CSC 101"},
            ),
            Document(
                page_content="Chunk 2",
                metadata={"page": 1, "source": "CCMAS.pdf", "course_code": "CSC 101"},
            ),
        ]
        _, sources = _format_context(docs)
        assert len(sources) == 1


class TestAsk:
    @pytest.mark.asyncio
    async def test_no_docs_returns_fallback(self):
        with patch("app.services.rag.emb") as mock_emb:
            mock_emb.search.return_value = []
            result = await ask("Anything?")
            assert "don't have enough information" in result["response"]
            assert result["sources"] == []

    @pytest.mark.asyncio
    async def test_returns_answer_with_sources(self):
        doc = Document(
            page_content="CSC 301 requires CSC 201.",
            metadata={"page": 5, "source": "CCMAS.pdf", "course_code": "CSC 301"},
        )
        with (
            patch("app.services.rag.emb") as mock_emb,
            patch("app.services.rag.llm_service") as mock_llm,
        ):
            mock_emb.search.return_value = [doc]
            mock_llm.generate = AsyncMock(
                return_value="CSC 301 requires CSC 201 [Source: CCMAS.pdf, Page 5]"
            )
            result = await ask("What are prerequisites for CSC 301?")
            assert "CSC 301" in result["response"]
            assert len(result["sources"]) > 0

    @pytest.mark.asyncio
    async def test_appends_citation_if_llm_forgot(self):
        doc = Document(
            page_content="Test content",
            metadata={"page": 1, "source": "CCMAS.pdf"},
        )
        with (
            patch("app.services.rag.emb") as mock_emb,
            patch("app.services.rag.llm_service") as mock_llm,
        ):
            mock_emb.search.return_value = [doc]
            mock_llm.generate = AsyncMock(return_value="Plain answer without citation")
            result = await ask("Test question")
            assert "[Source:" in result["response"]


class TestGenerateRoadmap:
    @pytest.mark.asyncio
    async def test_returns_roadmap_structure(self):
        import json

        doc = Document(
            page_content="Year 1 courses include CSC 101.",
            metadata={"page": 1, "source": "CCMAS.pdf", "course_code": "CSC 101"},
        )
        roadmap_json = json.dumps([
            {"semester": "Year 1 – Semester 1", "courses": ["CSC 101 (2 units)"]},
        ])
        with (
            patch("app.services.rag.emb") as mock_emb,
            patch("app.services.rag.llm_service") as mock_llm,
        ):
            mock_emb.search.return_value = [doc]
            mock_llm.generate = AsyncMock(return_value=roadmap_json)
            result = await generate_roadmap(
                level=100, interests=["AI"], completed_courses=[]
            )
            assert len(result["roadmap"]) == 1
            assert result["roadmap"][0]["semester"] == "Year 1 – Semester 1"

    @pytest.mark.asyncio
    async def test_empty_docs_returns_stub_roadmap(self):
        with (
            patch("app.services.rag.emb") as mock_emb,
            patch("app.services.rag.llm_service") as mock_llm,
        ):
            mock_emb.search.return_value = []
            mock_llm.generate = AsyncMock(return_value="[]")
            result = await generate_roadmap(
                level=100, interests=[], completed_courses=[]
            )
            assert isinstance(result["roadmap"], list)
            assert result["sources"] == []
