"""Unit tests for core/extractor.py."""

import os
from unittest.mock import MagicMock, patch

from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions,
    get_llm,
)


def test_extractor_empty_guards():
    """Verify fallback messages when transcript is empty."""
    assert extract_action_items("") == "No action items found."
    assert extract_action_items("   ") == "No action items found."
    assert extract_key_decisions("") == "No key decisions found."
    assert extract_questions("") == "No open questions found."


def test_extractor_get_llm_auto_gpu_offloading():
    """Verify extractor get_llm enables Auto GPU Offloading by default."""
    mock_chat_ollama = MagicMock()
    with patch.dict("sys.modules", {"langchain_ollama": MagicMock(ChatOllama=mock_chat_ollama)}):
        with patch.dict(os.environ, {}, clear=True):
            get_llm()
            mock_chat_ollama.assert_called_once()
            call_kwargs = mock_chat_ollama.call_args.kwargs
            assert "num_gpu" not in call_kwargs


def test_extractor_get_llm_manual_num_gpu_override():
    """Verify extractor get_llm accepts manual OLLAMA_NUM_GPU override."""
    mock_chat_ollama = MagicMock()
    with patch.dict("sys.modules", {"langchain_ollama": MagicMock(ChatOllama=mock_chat_ollama)}):
        with patch.dict(os.environ, {"OLLAMA_NUM_GPU": "16"}):
            get_llm()
            mock_chat_ollama.assert_called_once()
            call_kwargs = mock_chat_ollama.call_args.kwargs
            assert call_kwargs.get("num_gpu") == 16


@patch("core.extractor.build_chain")
def test_extract_action_items_mock(mock_build):
    """Verify action item extraction invokes chain."""
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "1. Deploy to staging (Owner: Sarah, Deadline: Tomorrow)"
    mock_build.return_value = mock_chain

    result = extract_action_items("Sarah agreed to deploy the staging app by tomorrow.")
    assert "Deploy to staging" in result
    assert "Sarah" in result


@patch("core.extractor.build_chain")
def test_extract_key_decisions_mock(mock_build):
    """Verify key decision extraction invokes chain."""
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "1. Standardize on Python 3.10+"
    mock_build.return_value = mock_chain

    result = extract_key_decisions("The team decided to standardize on Python 3.10+.")
    assert "Standardize on Python 3.10+" in result


@patch("core.extractor.build_chain")
def test_extract_questions_mock(mock_build):
    """Verify questions extraction invokes chain."""
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "1. When is the release date?"
    mock_build.return_value = mock_chain

    result = extract_questions("Someone asked what the release date would be.")
    assert "release date" in result
