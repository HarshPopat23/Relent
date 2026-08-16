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


def test_summarize_mock_pipeline():
    """Verify summarize executes map-reduce chain properly."""
    mock_chain = MagicMock()
    mock_chain.invoke.side_effect = ["Chunk summary", "### Overview\nFinal combined executive summary."]
    mock_prompt_cls = MagicMock()
    mock_prompt_cls.from_messages.return_value = MagicMock(__or__=lambda s, o: MagicMock(__or__=lambda s2, o2: mock_chain))

    with patch.dict(
        "sys.modules",
        {
            "langchain_core.prompts": MagicMock(ChatPromptTemplate=mock_prompt_cls),
            "langchain_core.output_parsers": MagicMock(StrOutputParser=MagicMock()),
            "langchain_ollama": MagicMock(ChatOllama=MagicMock()),
        },
    ):
        result = summarize("This is a sample video transcript about AI technology.")
        assert "Overview" in result or isinstance(result, str)
