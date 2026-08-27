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
MEDIA_ROOT = os.getenv("RELENT_MEDIA_ROOT", os.getcwd())
os.makedirs(CLIP_DIR, exist_ok=True)
os.makedirs(REEL_DIR, exist_ok=True)

# Small padding so clips don't feel abruptly cut off mid-word.
PAD_SECONDS = 0.15


def _get_media_root() -> str:
    """Return validated absolute media root configured via RELENT_MEDIA_ROOT."""
    raw_root = os.getenv("RELENT_MEDIA_ROOT", os.getcwd())
    if not raw_root or not raw_root.strip():
        raise ValueError("RELENT_MEDIA_ROOT must be configured for local file paths.")
    root = os.path.realpath(os.path.abspath(raw_root.strip()))
    if not os.path.isdir(root):
        raise ValueError("RELENT_MEDIA_ROOT does not exist or is not a directory.")
    return root


def _validate_video_input_path(video_path: str) -> str:
    """Validate and normalize user-influenced video paths before passing to ffmpeg."""
    if not isinstance(video_path, str) or not video_path.strip():
        raise ValueError("Invalid source video path.")

    candidate = video_path.strip()
    if candidate.startswith("-"):
        raise ValueError("Invalid source video path.")

    if any(ch in candidate for ch in ("\x00", "\n", "\r")):
        raise ValueError("Invalid source video path.")

    media_root = _get_media_root()
    resolved = os.path.realpath(os.path.abspath(candidate))
    try:
        if os.path.commonpath([media_root, resolved]) != media_root:
            raise ValueError("Source video path is outside the allowed media directory.")
    except ValueError as err:
        raise ValueError("Source video path is outside the allowed media directory.") from err

    if not os.path.isfile(resolved):
        raise FileNotFoundError(
            "No source video available to clip (the source may have been audio-only)."
        )

    return resolved


def _validate_output_path(out_path: str) -> str:
    """Validate and normalize output paths before passing to ffmpeg."""
    if not isinstance(out_path, str) or not out_path.strip():
        raise ValueError("Invalid output path.")

    candidate = out_path.strip()
    if candidate.startswith("-"):
        raise ValueError("Invalid output path.")

    if any(ch in candidate for ch in ("\x00", "\n", "\r")):
        raise ValueError("Invalid output path.")

    media_root = _get_media_root()
    resolved = os.path.realpath(os.path.abspath(candidate))
    try:
        if os.path.commonpath([media_root, resolved]) != media_root:
            raise ValueError("Output path is outside the allowed media directory.")
    except ValueError as err:
        raise ValueError("Output path is outside the allowed media directory.") from err

    return resolved


def _cut_clip(video_path: str, start: float, end: float, out_path: str) -> None:
    """Cut one [start, end] slice out of the source video using fast stream-copy or ultrafast encoding."""
    safe_video_path = _validate_video_input_path(video_path)
    safe_out_path = _validate_output_path(out_path)

    start_pos = max(0.0, float(start) - PAD_SECONDS)
    duration = max(0.4, float(end - start) + (2 * PAD_SECONDS))
    ffmpeg_bin = get_ffmpeg_path()

    # 1. Attempt instantaneous stream copy (-c copy) if enabled
    if REEL_CLIP_MODE in ("copy", "auto", "stream_copy"):
        copy_cmd = [
            ffmpeg_bin,
            "-y",
            "-ss",
            f"{start_pos:.2f}",
            "-i",
            f"file:{safe_video_path}",
            "-t",
            f"{duration:.2f}",
            "-c",
            "copy",
            "-avoid_negative_ts",
            "make_zero",
            safe_out_path,
        ]
        try:
            result = subprocess.run(copy_cmd, check=True, capture_output=True)
            if (
                result.returncode == 0
                and os.path.exists(safe_out_path)
                and os.path.getsize(safe_out_path) > 0
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
        f"file:{safe_video_path}",
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
        safe_out_path,
    ]

    subprocess.run(encode_cmd, check=True, capture_output=True)


def _concat_clips(clip_paths: list[str], out_path: str) -> None:
    """Join clips with ffmpeg's concat demuxer via instant stream copy."""
    safe_out_path = _validate_output_path(out_path)
    list_file = os.path.join(CLIP_DIR, f"concat_{uuid.uuid4().hex}.txt")

    with open(list_file, "w", encoding="utf-8") as f:
        for path in clip_paths:
            safe_clip = _validate_video_input_path(path)
            normalized_path = safe_clip.replace("\\", "/")
            f.write(f"file '{normalized_path}'\n")

    cmd = [
        get_ffmpeg_path(),
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        f"file:{list_file}",
        "-c",
        "copy",
        safe_out_path,
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
    validated_video_path = _validate_video_input_path(video_path)

    if not selected_segments:
        raise ValueError("No segments were selected — nothing to clip.")

    clip_paths = []

    try:
        for i, seg in enumerate(selected_segments):
            clip_path = os.path.join(CLIP_DIR, f"clip_{uuid.uuid4().hex}_{i}.mp4")
            _cut_clip(validated_video_path, seg["start"], seg["end"], clip_path)
            clip_paths.append(clip_path)

        output_name = output_name or f"reel_{uuid.uuid4().hex}.mp4"
        output_path = os.path.join(REEL_DIR, output_name)

        _concat_clips(clip_paths, output_path)
    finally:
        for path in clip_paths:
            if os.path.exists(path):
                os.remove(path)

    return output_path
