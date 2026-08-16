"""Unit tests for core/rag_engine.py and core/vector_store.py."""

import os
from unittest.mock import MagicMock, patch

from core.rag_engine import ask_question, format_docs, get_llm

try:
    from langchain_core.documents import Document
except ImportError:

    class Document:
        def __init__(self, page_content="", metadata=None):
            self.page_content = page_content
            self.metadata = metadata or {}


def test_format_docs():
    """Verify format_docs concatenates document page contents."""
    docs = [
        Document(page_content="First chunk of transcript."),
        Document(page_content="Second chunk of transcript."),
    ]
    result = format_docs(docs)
    assert "First chunk" in result
    assert "Second chunk" in result
    assert "\n\n" in result


def test_rag_engine_get_llm_auto_gpu_offloading():
    """Verify rag_engine get_llm enables Auto GPU Offloading by default."""
    mock_chat_ollama = MagicMock()
    with patch.dict("sys.modules", {"langchain_ollama": MagicMock(ChatOllama=mock_chat_ollama)}):
        with patch.dict(os.environ, {}, clear=True):
            get_llm()
            mock_chat_ollama.assert_called_once()
            call_kwargs = mock_chat_ollama.call_args.kwargs
            assert "num_gpu" not in call_kwargs


def test_rag_engine_get_llm_manual_num_gpu_override():
    """Verify rag_engine get_llm accepts manual OLLAMA_NUM_GPU override."""
    mock_chat_ollama = MagicMock()
    with patch.dict("sys.modules", {"langchain_ollama": MagicMock(ChatOllama=mock_chat_ollama)}):
        with patch.dict(os.environ, {"OLLAMA_NUM_GPU": "33"}):
            get_llm()
            mock_chat_ollama.assert_called_once()
            call_kwargs = mock_chat_ollama.call_args.kwargs
            assert call_kwargs.get("num_gpu") == 33


def test_ask_question_mock():
    """Verify ask_question invokes chain with user question."""
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "The model was trained on speech audio."

    ans = ask_question(mock_chain, "What was the model trained on?")
    assert ans == "The model was trained on speech audio."
    mock_chain.invoke.assert_called_once_with("What was the model trained on?")


def test_vector_store_build_mock():
    """Verify build_vector_store splits transcript into documents."""
    import core.vector_store as vs

    mock_chroma_class = MagicMock()
    mock_chroma_class.from_documents.return_value = MagicMock()

    with patch.object(vs, "get_embeddings", return_value=MagicMock()):
        with patch.dict(
            "sys.modules",
            {
                "langchain_chroma": MagicMock(Chroma=mock_chroma_class),
                "langchain_core.documents": MagicMock(Document=MagicMock),
                "langchain_text_splitters": MagicMock(RecursiveCharacterTextSplitter=MagicMock()),
            },
        ):
            transcript = "Relent AI is a local neural video assistant. " * 50
            vector_store = vs.build_vector_store(transcript)
            assert vector_store is not None
