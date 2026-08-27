"""Unit tests for core/video_clipper.py."""

import os
from unittest.mock import MagicMock, patch

import pytest

from core.video_clipper import (
    CLIP_DIR,
    REEL_DIR,
    _concat_clips,
    _cut_clip,
    _validate_output_path,
    _validate_video_input_path,
    build_reel,
    get_ffmpeg_path,
)


def test_clipper_directories_exist():
    """Verify clips and reels directories are configured and valid."""
    assert os.path.exists(CLIP_DIR)
    assert os.path.exists(REEL_DIR)


def test_get_ffmpeg_path():
    """Verify that get_ffmpeg_path resolves a non-empty string path."""
    path = get_ffmpeg_path()
    assert isinstance(path, str)
    assert len(path) > 0


def test_validate_video_input_path():
    """Verify input path sanitization and edge cases."""
    with patch("os.path.isfile", return_value=True):
        valid = _validate_video_input_path("sample.mp4")
        assert os.path.isabs(valid)

    # Empty string or non-string
    with pytest.raises(ValueError):
        _validate_video_input_path("")
    with pytest.raises(ValueError):
        _validate_video_input_path(None)

    # Option-like argument injection starting with dash
    with pytest.raises(ValueError):
        _validate_video_input_path("-option.mp4")

    # Control characters
    with pytest.raises(ValueError):
        _validate_video_input_path("sample\x00.mp4")

    # Non-existent file
    with patch("os.path.isfile", return_value=False):
        with pytest.raises(FileNotFoundError):
            _validate_video_input_path("non_existent_file.mp4")


def test_validate_output_path():
    """Verify output path sanitization."""
    valid = _validate_output_path("output.mp4")
    assert os.path.isabs(valid)

    with pytest.raises(ValueError):
        _validate_output_path("")
    with pytest.raises(ValueError):
        _validate_output_path("-dash_output.mp4")
    with pytest.raises(ValueError):
        _validate_output_path("out\n.mp4")


def test_build_reel_missing_video():
    """Verify FileNotFoundError when source video does not exist."""
    try:
        build_reel("non_existent_video_path.mp4", [{"start": 0, "end": 10}])
        raise AssertionError("Expected FileNotFoundError")
    except FileNotFoundError:
        pass


def test_build_reel_empty_segments():
    """Verify ValueError when selected segments list is empty."""
    with patch("os.path.isfile", return_value=True):
        try:
            build_reel("fake_video.mp4", [])
            raise AssertionError("Expected ValueError")
        except ValueError:
            pass


@patch("os.path.getsize", return_value=1024)
@patch("os.path.exists", return_value=True)
@patch("os.path.isfile", return_value=True)
@patch("subprocess.run")
def test_cut_clip_stream_copy_mode(mock_subprocess, mock_isfile, mock_exists, mock_getsize):
    """Verify _cut_clip attempts high-speed stream-copy (-c copy)."""
    mock_subprocess.return_value = MagicMock(returncode=0)

    _cut_clip("input.mp4", start=10.0, end=25.0, out_path="out.mp4")

    mock_subprocess.assert_called_once()
    args, kwargs = mock_subprocess.call_args
    cmd = args[0]
    assert "-ss" in cmd
    assert "-i" in cmd
    assert "copy" in cmd
    assert any("input.mp4" in part for part in cmd)
    assert any("out.mp4" in part for part in cmd)


@patch("os.path.isfile", return_value=True)
@patch("subprocess.run")
def test_cut_clip_ultrafast_fallback(mock_subprocess, mock_isfile):
    """Verify _cut_clip falls back to -preset ultrafast on copy failure."""
    # First call (copy) fails, second call (ultrafast) succeeds
    mock_subprocess.side_effect = [
        Exception("Non-aligned keyframes"),
        MagicMock(returncode=0),
    ]

    _cut_clip("input.mp4", start=10.0, end=25.0, out_path="out.mp4")

    assert mock_subprocess.call_count == 2
    args2, _ = mock_subprocess.call_args_list[1]
    cmd2 = args2[0]
    assert "ultrafast" in cmd2
    assert "libx264" in cmd2


@patch("os.path.isfile", return_value=True)
@patch("subprocess.run")
def test_concat_clips_mock(mock_subprocess, mock_isfile):
    """Verify _concat_clips builds concat demuxer command with -c copy."""
    mock_subprocess.return_value = MagicMock(returncode=0)

    _concat_clips(["clip1.mp4", "clip2.mp4"], out_path="final_reel.mp4")

    mock_subprocess.assert_called_once()
    args, kwargs = mock_subprocess.call_args
    cmd = args[0]
    assert "-f" in cmd
    assert "concat" in cmd
    assert "copy" in cmd
    assert any("final_reel.mp4" in part for part in cmd)
