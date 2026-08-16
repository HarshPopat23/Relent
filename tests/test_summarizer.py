"""Unit tests for core/summarizer.py."""

from unittest.mock import MagicMock, patch

from core.summarizer import generate_subtitle, generate_title, split_transcript, summarize


def test_split_transcript():
    """Verify recursive character text splitting behavior."""
    long_text = "Relent AI is an open source video intelligence tool. " * 200
    chunks = split_transcript(long_text)
    assert len(chunks) > 1
    assert all(isinstance(c, str) for c in chunks)


def test_summarizer_empty_guards():
    """Verify safe fallback strings on empty transcripts."""
    assert summarize("") == "No transcript content available to summarize."
    assert summarize("   ") == "No transcript content available to summarize."
    assert generate_title("") == "Untitled Video"
    assert generate_subtitle("") == "No description available"


@patch("core.summarizer.ChatOllama")
def test_summarize_mock_pipeline(mock_ollama_class):
    """Verify summarize executes map-reduce chain properly."""
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content="Mock summary bullet point")
    mock_ollama_class.return_value = mock_llm

    # Test with short input
    with patch("langchain_core.runnables.base.RunnableSequence.invoke") as mock_invoke:
        mock_invoke.return_value = "### Overview\nExecutive summary generated."
        result = summarize("This is a sample video transcript about AI technology.")
        assert "Overview" in result
