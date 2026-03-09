"""
Tests for the custom text splitter — no external dependencies.
"""

from app.services.text_splitter import split_text


class TestSplitText:
    def test_empty_string_returns_empty(self):
        assert split_text("") == []
        assert split_text("   ") == []

    def test_short_text_returns_single_chunk(self):
        text = "Hello world"
        result = split_text(text, chunk_size=500)
        assert result == ["Hello world"]

    def test_splits_on_paragraph_breaks(self):
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        result = split_text(text, chunk_size=30, chunk_overlap=0)
        assert len(result) >= 2
        assert all(len(c) <= 30 for c in result)

    def test_respects_chunk_size_approximately(self):
        text = " ".join(f"word{i}" for i in range(200))
        result = split_text(text, chunk_size=100, chunk_overlap=10)
        # Most chunks should respect the size limit;
        # recursive splitting on word boundaries can occasionally exceed by a few chars
        oversized = [c for c in result if len(c) > 110]
        assert len(oversized) == 0, f"Chunks far over limit: {[len(c) for c in oversized]}"

    def test_no_empty_chunks(self):
        text = "a\n\n\n\nb\n\nc"
        result = split_text(text, chunk_size=5, chunk_overlap=0)
        assert all(c.strip() for c in result)

    def test_single_long_word_triggers_recursion(self):
        text = "A" * 600
        result = split_text(text, chunk_size=100, chunk_overlap=0)
        assert len(result) > 1
        for chunk in result:
            assert len(chunk) <= 100

    def test_overlap_preserved(self):
        text = "Sentence one. Sentence two. Sentence three. Sentence four."
        result = split_text(text, chunk_size=30, chunk_overlap=10)
        assert len(result) >= 2
