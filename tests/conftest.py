"""Pytest shared test fixtures and mock objects for Relent AI."""

import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    import pytest

    fixture_decorator = pytest.fixture
except ImportError:

    def fixture_decorator(func):
        return func


def get_sample_segments():
    """Return a mock list of timestamped video segments."""
    return [
        {
            "start": 0.0,
            "end": 14.8,
            "text": "Welcome to Relent AI. Today we demonstrate open-source neural video intelligence.",
        },
        {
            "start": 15.0,
            "end": 45.2,
            "text": "We support universal ingestion, speech transcription, and Map-Reduce summarization.",
        },
        {
            "start": 45.5,
            "end": 90.0,
            "text": "You can also cut AI highlight reels using plain natural language instructions.",
        },
        {
            "start": 90.5,
            "end": 120.0,
            "text": "Action item: Deploy the updated container by Friday and verify GPU acceleration.",
        },
    ]


def get_sample_transcript(sample_segments=None):
    """Return merged text transcript of sample segments."""
    if sample_segments is None:
        sample_segments = get_sample_segments()
    return " ".join(s["text"] for s in sample_segments)


def get_sample_pipeline_result(sample_segments=None, sample_transcript=None):
    """Return a full mock pipeline result dictionary."""
    if sample_segments is None:
        sample_segments = get_sample_segments()
    if sample_transcript is None:
        sample_transcript = get_sample_transcript(sample_segments)

    return {
        "title": "Relent AI Launch & Demo",
        "subtitle": "Overview of Neural Video Intelligence Platform",
        "summary": "### Overview\nRelent AI provides on-device video intelligence.\n\n### Key Takeaways\n- 100% Local\n- Fast transcription\n- Automatic reel clipping",
        "action_items": "1. Deploy the updated container by Friday (Owner: DevOps Team, Deadline: Friday)",
        "key_decisions": "1. Standardize on Ollama for local LLM inference",
        "open_questions": "1. What is the target timeline for multi-GPU streaming?",
        "transcript": sample_transcript,
        "segments": sample_segments,
        "video_path": "downloads/sample_video.mp4",
        "rag_chain": None,
    }


@fixture_decorator
def sample_segments():
    return get_sample_segments()


@fixture_decorator
def sample_transcript(sample_segments):
    return get_sample_transcript(sample_segments)


@fixture_decorator
def sample_pipeline_result(sample_segments, sample_transcript):
    return get_sample_pipeline_result(sample_segments, sample_transcript)
