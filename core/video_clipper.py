"""Relent AI - Video Clipper & Highlight Reel Engine.

Cuts timestamped video clips and merges them into high-energy reels
using high-speed stream-copy (-c copy) and -preset ultrafast encoding.
"""

import os
import subprocess
import uuid

_ffmpeg_path = None

REEL_CLIP_MODE = os.getenv("REEL_CLIP_MODE", "copy").lower()  # "copy", "ultrafast"


def get_ffmpeg_path() -> str:
    """Resolve ffmpeg binary path lazily from static_ffmpeg or system PATH."""
    global _ffmpeg_path
    if _ffmpeg_path is None:
        try:
            import static_ffmpeg

            ffmpeg_path, _ = static_ffmpeg.run.get_or_fetch_platform_executables_else_raise()
            _ffmpeg_path = ffmpeg_path
        except Exception:
            _ffmpeg_path = "ffmpeg"
    return _ffmpeg_path


CLIP_DIR = "clips"
REEL_DIR = "reels"
os.makedirs(CLIP_DIR, exist_ok=True)
os.makedirs(REEL_DIR, exist_ok=True)

# Small padding so clips don't feel abruptly cut off mid-word.
PAD_SECONDS = 0.15


def _sanitize_input_media_path(video_path: str) -> str:
    """Validate and normalize local media path before passing it to ffmpeg."""
    if not isinstance(video_path, str):
        raise ValueError("Invalid video path type.")

    normalized = os.path.abspath(video_path.strip())
    if not normalized or not os.path.isfile(normalized):
        raise FileNotFoundError(f"Invalid source video path: {video_path}")

    # Prevent ffmpeg option-style argument confusion via crafted filenames.
    if os.path.basename(normalized).startswith("-"):
        raise ValueError("Invalid source video filename.")

    return normalized


def _cut_clip(video_path: str, start: float, end: float, out_path: str) -> None:
    """Cut one [start, end] slice out of the source video using fast stream-copy or ultrafast encoding."""
    start_pos = max(0.0, start - PAD_SECONDS)
    duration = max(0.4, (end - start) + (2 * PAD_SECONDS))
    ffmpeg_bin = get_ffmpeg_path()
    safe_video_path = _sanitize_input_media_path(video_path)

    # 1. Attempt instantaneous stream copy (-c copy) if enabled
    if REEL_CLIP_MODE in ("copy", "auto", "stream_copy"):
        copy_cmd = [
            ffmpeg_bin,
            "-y",
            "-ss",
            f"{start_pos:.2f}",
            "-i",
            safe_video_path,
            "-t",
            f"{duration:.2f}",
            "-c",
            "copy",
            "-avoid_negative_ts",
            "make_zero",
            out_path,
        ]
        try:
            result = subprocess.run(copy_cmd, check=True, capture_output=True)
            if (
                result.returncode == 0
                and os.path.exists(out_path)
                and os.path.getsize(out_path) > 0
            ):
                return
        except Exception:
            # Seamless fallback to ultrafast re-encoding on keyframe alignment / container errors
            pass

    # 2. Fallback / Precise ultrafast re-encoding
    encode_cmd = [
        ffmpeg_bin,
        "-y",
        "-ss",
        f"{start_pos:.2f}",
        "-i",
        safe_video_path,
        "-t",
        f"{duration:.2f}",
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-crf",
        "22",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-ar",
        "44100",
        "-ac",
        "2",
        "-avoid_negative_ts",
        "make_zero",
        out_path,
    ]

    subprocess.run(encode_cmd, check=True, capture_output=True)


def _concat_clips(clip_paths: list[str], out_path: str) -> None:
    """Join clips with ffmpeg's concat demuxer via instant stream copy."""
    list_file = os.path.join(CLIP_DIR, f"concat_{uuid.uuid4().hex}.txt")

    with open(list_file, "w", encoding="utf-8") as f:
        for path in clip_paths:
            normalized_path = os.path.abspath(path).replace("\\", "/")
            f.write(f"file '{normalized_path}'\n")

    cmd = [
        get_ffmpeg_path(),
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        list_file,
        "-c",
        "copy",
        out_path,
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    finally:
        if os.path.exists(list_file):
            os.remove(list_file)


def build_reel(
    video_path: str, selected_segments: list[dict], output_name: str | None = None
) -> str:
    """Cut `video_path` at each selected segment's [start, end] and merge into a high-energy reel."""
    if not video_path or not os.path.exists(video_path):
        raise FileNotFoundError(
            "No source video available to clip (the source may have been audio-only)."
        )

    if not selected_segments:
        raise ValueError("No segments were selected — nothing to clip.")

    clip_paths = []

    try:
        for i, seg in enumerate(selected_segments):
            clip_path = os.path.join(CLIP_DIR, f"clip_{uuid.uuid4().hex}_{i}.mp4")
            _cut_clip(video_path, seg["start"], seg["end"], clip_path)
            clip_paths.append(clip_path)

        output_name = output_name or f"reel_{uuid.uuid4().hex}.mp4"
        output_path = os.path.join(REEL_DIR, output_name)

        _concat_clips(clip_paths, output_path)
    finally:
        for path in clip_paths:
            if os.path.exists(path):
                os.remove(path)

    return output_path
