"""Unit tests for core/script_generator.py."""

import os
from unittest.mock import MagicMock, patch

from core.script_generator import (
    _extract_id_list_ordered,
    _find_int_list_anywhere,
    _format_segments_for_prompt,
    _parse_target_seconds,
    _trim_to_duration,
    build_script_text,
    get_llm,
)


def test_script_generator_get_llm_auto_gpu_offloading():
    """Verify script_generator get_llm enables Auto GPU Offloading by default."""
    mock_chat_ollama = MagicMock()
    with patch.dict("sys.modules", {"langchain_ollama": MagicMock(ChatOllama=mock_chat_ollama)}):
        with patch.dict(os.environ, {}, clear=True):
            get_llm()
            mock_chat_ollama.assert_called_once()
            call_kwargs = mock_chat_ollama.call_args.kwargs
            assert "num_gpu" not in call_kwargs
            assert call_kwargs.get("format") == "json"


def test_script_generator_get_llm_manual_num_gpu_override():
    """Verify script_generator get_llm accepts manual OLLAMA_NUM_GPU override."""
    mock_chat_ollama = MagicMock()
    with patch.dict("sys.modules", {"langchain_ollama": MagicMock(ChatOllama=mock_chat_ollama)}):
        with patch.dict(os.environ, {"OLLAMA_NUM_GPU": "0"}):
            get_llm()
            mock_chat_ollama.assert_called_once()
            call_kwargs = mock_chat_ollama.call_args.kwargs
            assert call_kwargs.get("num_gpu") == 0


def test_parse_target_seconds():
    """Verify natural language duration parsing."""
    assert _parse_target_seconds("create a 2 minute reel") == 120.0
    assert _parse_target_seconds("generate a 90 second clip") == 90.0
    assert _parse_target_seconds("1.5 min summary") == 90.0
    assert _parse_target_seconds("make a short reel") is None


def test_find_int_list_anywhere():
    """Verify parsing integer arrays from diverse JSON structures."""
    assert _find_int_list_anywhere({"segment_ids": [1, 2, 3]}) == [1, 2, 3]
    assert _find_int_list_anywhere([4, 5, 6]) == [4, 5, 6]
    assert _find_int_list_anywhere({"custom_key": [7, 8]}) == [7, 8]
    assert _find_int_list_anywhere("not a list") is None


def test_extract_id_list_ordered():
    """Verify JSON parsing and out-of-range / duplicate dropping."""
    raw_json = '{"segment_ids": [2, 0, 2, 99, 1]}'
    ids = _extract_id_list_ordered(raw_json, max_id=3)
    # 2 kept, 0 kept, duplicate 2 dropped, 99 (out of range > 3) dropped, 1 kept
    assert ids == [2, 0, 1]


def test_trim_to_duration(sample_segments):
    """Verify greedy duration trimming respects target duration."""
    # Segments durations: seg0: 14.8s, seg1: 30.2s, seg2: 44.5s, seg3: 29.5s
    # Total for seg0 + seg1 = 45s
    trimmed = _trim_to_duration(sample_segments, target_seconds=40.0)
    assert len(trimmed) >= 1
    total_dur = sum(s["end"] - s["start"] for s in trimmed)
    assert total_dur >= 40.0 or len(trimmed) == len(sample_segments)


def test_build_script_text(sample_segments):
    """Verify joining verbatim transcript segments into script text."""
    script = build_script_text(sample_segments[:2])
    assert script.startswith("Welcome to Relent AI.")
    assert "Map-Reduce summarization." in script


def test_format_segments_for_prompt(sample_segments):
    """Verify formatting segments for LLM prompt context."""
    formatted = _format_segments_for_prompt(sample_segments)
    assert "[0]" in formatted
    assert "[1]" in formatted
    assert "(14.8s)" in formatted
