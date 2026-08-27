"""Unit tests for utils/audio_processor.py."""

import os
from unittest.mock import MagicMock, patch

from utils.audio_processor import (
    AUDIO_ONLY_EXTS,
    DOWNLOAD_DIR,
    _ensure_ffmpeg,
    chunk_audio_with_offsets,
    convert_to_wav,
    process_input,
)


def test_audio_only_extensions():
    """Verify that common audio extensions are properly categorized."""
    assert ".mp3" in AUDIO_ONLY_EXTS
    assert ".wav" in AUDIO_ONLY_EXTS
    assert ".m4a" in AUDIO_ONLY_EXTS
    assert ".aac" in AUDIO_ONLY_EXTS
    assert ".flac" in AUDIO_ONLY_EXTS
    assert ".mp4" not in AUDIO_ONLY_EXTS
    assert ".mov" not in AUDIO_ONLY_EXTS


def test_download_dir_exists():
    """Verify that DOWNLOAD_DIR is created and valid."""
    assert os.path.exists(DOWNLOAD_DIR)
    assert isinstance(DOWNLOAD_DIR, str)


def test_ensure_ffmpeg():
    """Verify that _ensure_ffmpeg resolves without crashing."""
    ffmpeg_p, ffprobe_p = _ensure_ffmpeg()
    assert isinstance(ffmpeg_p, str)
    assert isinstance(ffprobe_p, str)


def test_convert_to_wav_missing_file():
    """Verify FileNotFoundError when input file does not exist."""
    try:
        convert_to_wav("non_existent_file_12345.mp4")
        raise AssertionError("Expected FileNotFoundError")
    except FileNotFoundError:
        pass


def test_chunk_audio_with_offsets():
    """Verify chunk calculation and offset mathematics."""
    mock_segment = MagicMock()
    # Mock audio length of 25 minutes (25 * 60 * 1000 ms)
    mock_segment.__len__.return_value = 25 * 60 * 1000
    mock_audio_segment = MagicMock()
    mock_audio_segment.from_wav.return_value = mock_segment

    with patch("os.path.isfile", side_effect=lambda p: str(p).endswith("fake_path.wav")):
        with patch.dict("sys.modules", {"pydub": MagicMock(AudioSegment=mock_audio_segment)}):
            with patch("utils.audio_processor.AudioSegment", mock_audio_segment, create=True):
                chunks = chunk_audio_with_offsets("fake_path.wav", chunk_minutes=10)

    # 25 minutes with 10 min chunks should yield 3 chunks (0-10m, 10-20m, 20-25m)
    assert len(chunks) == 3
    assert chunks[0]["offset"] == 0.0
    assert chunks[1]["offset"] == 600.0  # 10 minutes = 600 seconds
    assert chunks[2]["offset"] == 1200.0  # 20 minutes = 1200 seconds


@patch("utils.audio_processor.download_youtube_video")
@patch("utils.audio_processor.convert_to_wav")
@patch("utils.audio_processor.chunk_audio_with_offsets")
def test_process_input_youtube_url(mock_chunk, mock_convert, mock_download):
    """Verify handling of YouTube URLs."""
    mock_download.return_value = "downloads/sample.mp4"
    mock_convert.return_value = "downloads/sample_converted.wav"
    mock_chunk.return_value = [{"path": "chunk_0.wav", "offset": 0.0}]

    res = process_input("https://youtu.be/sample123")

    assert res["video_path"] == "downloads/sample.mp4"
    assert len(res["wav_chunks"]) == 1
    mock_download.assert_called_once_with("https://youtu.be/sample123")
