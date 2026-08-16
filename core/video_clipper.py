import os
import subprocess
import uuid

_ffmpeg_path = None


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


def _cut_clip(video_path: str, start: float, end: float, out_path: str) -> None:
    """Cut one [start, end] slice out of the source video."""
    start_pos = max(0.0, start - PAD_SECONDS)
    duration = max(0.4, (end - start) + (2 * PAD_SECONDS))

    cmd = [
        get_ffmpeg_path(),
        "-y",
        "-ss",
        f"{start_pos:.2f}",
        "-i",
        video_path,
        "-t",
        f"{duration:.2f}",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
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

    subprocess.run(cmd, check=True, capture_output=True)


def _concat_clips(clip_paths: list[str], out_path: str) -> None:
    """Join clips with ffmpeg's concat demuxer. Safe to stream-copy here since
    every clip was just re-encoded above with the same codec settings."""
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
    """
    Cut `video_path` at each selected segment's [start, end] and merge the
    pieces, in order, into one output video.

    selected_segments: the list returned by
    script_generator.select_segments_for_request() — each item must have
    "start" and "end" (seconds, relative to the full source video).

    Returns the path to the final reel video (.mp4).
    """
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
