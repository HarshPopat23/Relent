"""Unit tests for core/video_clipper.py."""

import os
from unittest.mock import MagicMock, patch

from core.video_clipper import (
    CLIP_DIR,
    REEL_DIR,
    _concat_clips,
    _cut_clip,
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


def test_build_reel_missing_video():
    """Verify FileNotFoundError when source video does not exist."""
    try:
        build_reel("non_existent_video_path.mp4", [{"start": 0, "end": 10}])
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_build_reel_empty_segments():
    """Verify ValueError when selected segments list is empty."""
    # Use existing directory or test with dummy path
    with patch("os.path.exists", return_value=True):
        try:
            build_reel("fake_video.mp4", [])
            assert False, "Expected ValueError"
        except ValueError:
            pass


@patch("subprocess.run")
def test_cut_clip_mock(mock_subprocess):
    """Verify _cut_clip builds expected ffmpeg command."""
    mock_subprocess.return_value = MagicMock(returncode=0)

    _cut_clip("input.mp4", start=10.0, end=25.0, out_path="out.mp4")

    mock_subprocess.assert_called_once()
    args, kwargs = mock_subprocess.call_args
    cmd = args[0]
    assert "-ss" in cmd
    assert "-i" in cmd
    assert "input.mp4" in cmd
    assert "out.mp4" in cmd


@patch("subprocess.run")
def test_concat_clips_mock(mock_subprocess):
    """Verify _concat_clips builds concat demuxer command."""
    mock_subprocess.return_value = MagicMock(returncode=0)

    _concat_clips(["clip1.mp4", "clip2.mp4"], out_path="final_reel.mp4")

    mock_subprocess.assert_called_once()
    args, kwargs = mock_subprocess.call_args
    cmd = args[0]
    assert "-f" in cmd
    assert "concat" in cmd
    assert "final_reel.mp4" in cmd
