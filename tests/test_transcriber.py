"""Unit tests for core/transcriber.py."""

from unittest.mock import patch

from core.transcriber import segments_to_text, transcribe_all, unload_transcribers


def test_segments_to_text_concatenation(sample_segments):
    """Verify that segments_to_text correctly merges segment text in order."""
    text = segments_to_text(sample_segments)
    assert "Welcome to Relent AI." in text
    assert "You can also cut AI highlight reels" in text
    assert text.startswith("Welcome to Relent AI.")


def test_segments_to_text_empty():
    """Verify handling of empty segment list."""
    assert segments_to_text([]) == ""


def test_unload_transcribers():
    """Verify that unloading transcribers executes cleanly without errors."""
    unload_transcribers()


@patch("core.transcriber.transcribe_chunk")
def test_transcribe_all(mock_transcribe):
    """Verify transcribe_all loops through all wav chunks and collects segments."""
    mock_transcribe.return_value = [{"start": 0.0, "end": 10.0, "text": "Segment 1"}]

    wav_chunks = [
        {"path": "chunk_0.wav", "offset": 0.0},
        {"path": "chunk_1.wav", "offset": 600.0},
    ]

    segments = transcribe_all(wav_chunks, language="english")
    assert len(segments) == 2
    assert mock_transcribe.call_count == 2
