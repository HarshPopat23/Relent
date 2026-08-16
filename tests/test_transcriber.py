"""Unit tests for core/transcriber.py."""

from unittest.mock import MagicMock, patch

from core.transcriber import (
    get_device_and_compute_type,
    segments_to_text,
    transcribe_all,
    transcribe_chunk_indicwhisper,
    transcribe_chunk_whisper,
    unload_transcribers,
)


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


def test_get_device_and_compute_type_cpu():
    """Verify CPU fallback produces cpu device and int8 compute type by default."""
    with patch("torch.cuda.is_available", return_value=False):
        device, compute_type = get_device_and_compute_type()
        assert device == "cpu"
        assert compute_type in ("int8", "")


def test_get_device_and_compute_type_cuda():
    """Verify CUDA auto-detection produces cuda device and float16 compute type."""
    with patch("torch.cuda.is_available", return_value=True):
        device, compute_type = get_device_and_compute_type()
        assert device == "cuda"
        assert compute_type in ("float16", "int8_float16")


@patch("core.transcriber.load_model")
def test_transcribe_chunk_whisper_faster_whisper(mock_load_model):
    """Verify faster_whisper generator output parsing with timestamp offsets."""

    class MockSegment:
        def __init__(self, start, end, text):
            self.start = start
            self.end = end
            self.text = text

    mock_fw_model = MagicMock()
    mock_fw_model.transcribe.return_value = (
        [
            MockSegment(0.5, 3.2, "Faster Whisper test transcription."),
            MockSegment(3.5, 6.0, "Second chunk segment."),
        ],
        MagicMock(),
    )
    mock_load_model.return_value = ("faster_whisper", mock_fw_model, "cpu")

    segments = transcribe_chunk_whisper("test_chunk.wav", chunk_offset=100.0)
    assert len(segments) == 2
    assert segments[0]["start"] == 100.5
    assert segments[0]["end"] == 103.2
    assert segments[0]["text"] == "Faster Whisper test transcription."
    assert segments[1]["start"] == 103.5


@patch("core.transcriber.load_model")
def test_transcribe_chunk_whisper_standard_fallback(mock_load_model):
    """Verify standard whisper dictionary output parsing with timestamp offsets."""
    mock_whisper_model = MagicMock()
    mock_whisper_model.transcribe.return_value = {
        "segments": [
            {"start": 1.0, "end": 4.0, "text": "Standard Whisper fallback."},
        ]
    }
    mock_load_model.return_value = ("whisper", mock_whisper_model, "cpu")

    segments = transcribe_chunk_whisper("test_chunk.wav", chunk_offset=50.0)
    assert len(segments) == 1
    assert segments[0]["start"] == 51.0
    assert segments[0]["end"] == 54.0
    assert segments[0]["text"] == "Standard Whisper fallback."


@patch("core.transcriber.load_indicwhisper")
def test_transcribe_chunk_indicwhisper(mock_load_indic):
    """Verify IndicWhisper output parsing for Hinglish / Indian languages."""
    mock_pipe = MagicMock()
    mock_pipe.return_value = {
        "chunks": [
            {"timestamp": (0.0, 5.0), "text": "Hinglish meeting recording chalu hai."},
        ]
    }
    mock_load_indic.return_value = mock_pipe

    segments = transcribe_chunk_indicwhisper("test_hinglish.wav", chunk_offset=20.0)
    assert len(segments) == 1
    assert segments[0]["start"] == 20.0
    assert segments[0]["end"] == 25.0
    assert "Hinglish meeting" in segments[0]["text"]


@patch("os.path.exists", return_value=False)
@patch("builtins.open", create=True)
@patch("core.transcriber.transcribe_chunk")
def test_transcribe_all(mock_transcribe, mock_open, mock_exists):
    """Verify transcribe_all loops through all wav chunks and collects segments."""
    mock_transcribe.return_value = [{"start": 0.0, "end": 10.0, "text": "Segment 1"}]

    wav_chunks = [
        {"path": "dummy_test_chunk_0.wav", "offset": 0.0},
        {"path": "dummy_test_chunk_1.wav", "offset": 600.0},
    ]

    segments = transcribe_all(wav_chunks, language="english")
    assert len(segments) == 2
    assert mock_transcribe.call_count == 2
