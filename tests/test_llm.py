"""Unit tests for core/llm.py."""

import os
from unittest.mock import MagicMock, patch

from core.llm import (
    FALLBACK_MODEL,
    PRIMARY_MODEL,
    FallbackChatOllama,
    create_ollama_instance,
    get_llm,
    is_indic_language,
)


def test_default_models():
    """Verify default model names are set to Qwen2.5-72B (4-bit) and Sarvam-M."""
    assert "72b" in PRIMARY_MODEL.lower()
    assert "sarvam" in FALLBACK_MODEL.lower()


def test_is_indic_language():
    """Verify Indic language detection."""
    assert is_indic_language("hindi") is True
    assert is_indic_language("hinglish") is True
    assert is_indic_language("bengali") is True
    assert is_indic_language("english") is False
    assert is_indic_language("french") is False
    assert is_indic_language(None) is False


def test_get_llm_primary_success():
    """Verify get_llm returns working runnable that invokes primary model."""
    mock_primary = MagicMock()
    mock_primary.invoke.return_value = "Primary response"
    mock_fallback = MagicMock()

    runner = FallbackChatOllama(
        primary_llm=mock_primary,
        fallback_llm=mock_fallback,
        prefer_fallback=False,
    )

    result = runner.invoke("test prompt")
    assert result == "Primary response"
    mock_primary.invoke.assert_called_once()
    mock_fallback.invoke.assert_not_called()


def test_get_llm_fallback_on_primary_failure():
    """Verify automatic failover to Sarvam-M fallback when primary model raises an exception."""
    mock_primary = MagicMock()
    mock_primary.invoke.side_effect = RuntimeError("CUDA OOM or model unreachable")
    mock_fallback = MagicMock()
    mock_fallback.invoke.return_value = "Fallback response"

    runner = FallbackChatOllama(
        primary_llm=mock_primary,
        fallback_llm=mock_fallback,
        prefer_fallback=False,
    )

    result = runner.invoke("test prompt")
    assert result == "Fallback response"
    mock_primary.invoke.assert_called_once()
    mock_fallback.invoke.assert_called_once()


def test_get_llm_hindi_specialization():
    """Verify Hindi language routing prefers Sarvam-M first."""
    mock_primary = MagicMock()
    mock_primary.invoke.return_value = "Primary response"
    mock_fallback = MagicMock()
    mock_fallback.invoke.return_value = "Sarvam Hindi response"

    runner = FallbackChatOllama(
        primary_llm=mock_primary,
        fallback_llm=mock_fallback,
        prefer_fallback=True,
    )

    result = runner.invoke("हिंदी में सारांश")
    assert result == "Sarvam Hindi response"
    mock_fallback.invoke.assert_called_once()
    mock_primary.invoke.assert_not_called()


def test_create_ollama_instance_gpu_detection():
    """Verify create_ollama_instance respects OLLAMA_NUM_GPU."""
    mock_chat_ollama = MagicMock()
    with patch.dict("sys.modules", {"langchain_ollama": MagicMock(ChatOllama=mock_chat_ollama)}):
        with patch.dict(os.environ, {"OLLAMA_NUM_GPU": "0"}):
            create_ollama_instance("qwen2.5:72b-instruct-q4_K_M")
            mock_chat_ollama.assert_called_once()
            kwargs = mock_chat_ollama.call_args.kwargs
            assert kwargs.get("num_gpu") == 0
            assert "72b" in kwargs.get("model", "")
