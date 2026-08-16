import os
import sys

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def safe_print(text: str = "") -> None:
    try:
        print(text)
    except Exception:
        try:
            encoding = sys.stdout.encoding or "utf-8"
            print(str(text).encode(encoding, errors="replace").decode(encoding, errors="replace"))
        except Exception:
            pass


_ffmpeg_configured = False
_ffmpeg_dir = ""


def _ensure_ffmpeg() -> tuple[str, str]:
    """Ensure ffmpeg and ffprobe are resolved and configured for pydub."""
    global _ffmpeg_configured, _ffmpeg_dir
    if not _ffmpeg_configured:
        try:
            import static_ffmpeg

            ffmpeg_path, ffprobe_path = (
                static_ffmpeg.run.get_or_fetch_platform_executables_else_raise()
            )
            _ffmpeg_dir = os.path.dirname(ffmpeg_path)
            if _ffmpeg_dir not in os.environ.get("PATH", ""):
                os.environ["PATH"] += os.pathsep + _ffmpeg_dir

            from pydub import AudioSegment

            AudioSegment.converter = ffmpeg_path
            AudioSegment.ffprobe = ffprobe_path
            _ffmpeg_configured = True
            return ffmpeg_path, ffprobe_path
        except Exception:
            _ffmpeg_configured = True
            return "ffmpeg", "ffprobe"
    return "ffmpeg", "ffprobe"


DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Extensions that have no video track — reels can't be cut from these.
AUDIO_ONLY_EXTS = {".mp3", ".wav", ".m4a", ".aac", ".flac"}


def download_youtube_video(url: str) -> str:
    """Download the best video+audio MP4 for a YouTube URL.

    NOTE: this replaces the old download_youtube_audio(), which only kept the
    audio track and threw the video away — we need the video for clipping.
    """
    import yt_dlp

    _ensure_ffmpeg()
    output_path = os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": output_path,
        "merge_output_format": "mp4",
        "quiet": True,
        "windowsfilenames": True,
        "noplaylist": True,
        "extractor_args": {"youtube": {"player_client": ["android", "ios", "web"]}},
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
    }
    if _ffmpeg_dir:
        ydl_opts["ffmpeg_location"] = _ffmpeg_dir

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_path = ydl.prepare_filename(info)

        # After yt-dlp merges video+audio, the extension becomes .mp4
        base, _ = os.path.splitext(video_path)
        merged_path = base + ".mp4"
        if os.path.exists(merged_path):
            video_path = merged_path

    return video_path


MEDIA_ROOT = os.path.realpath(os.path.abspath(os.getenv("RELENT_MEDIA_ROOT", os.getcwd())))


def _sanitize_audio_path(file_path: str) -> str:
    """Validate and normalize local media path to prevent path traversal / injection."""
    if not isinstance(file_path, str) or not file_path.strip():
        raise ValueError("Invalid file path.")
    candidate = file_path.strip()
    if candidate.startswith("-"):
        raise ValueError("Invalid file path.")
    if any(ch in candidate for ch in ("\x00", "\n", "\r")):
        raise ValueError("Invalid file path.")
    resolved_path = os.path.realpath(os.path.abspath(candidate))
    if os.path.commonpath([MEDIA_ROOT, resolved_path]) != MEDIA_ROOT:
        raise ValueError("File path is outside the allowed media directory.")
    return resolved_path


def convert_to_wav(input_path: str) -> str:
    """Convert any local audio/video file to mono 16 kHz WAV (for transcription only)."""
    safe_input_path = _sanitize_audio_path(input_path)
    if not os.path.isfile(safe_input_path):
        raise FileNotFoundError(f"Local file not found: {input_path}")

    base_no_ext = os.path.splitext(safe_input_path)[0]
    output_path = f"{base_no_ext}_converted.wav"
    if os.path.isfile(output_path) and os.path.getsize(output_path) > 0:
        return output_path

    _ensure_ffmpeg()
    from pydub import AudioSegment

    audio = AudioSegment.from_file(safe_input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_path, format="wav")

    return output_path


def chunk_audio_with_offsets(wav_path: str, chunk_minutes: int = 10) -> list[dict]:
    """Split a WAV file into chunks, tracking each chunk's start offset (in seconds)
    within the FULL audio. This offset is what lets us convert a Whisper timestamp
    (which is relative to the chunk) back into a timestamp relative to the whole video.
    """
    safe_wav_path = _sanitize_audio_path(wav_path)
    if not os.path.isfile(safe_wav_path):
        raise FileNotFoundError(f"WAV file not found: {wav_path}")

    _ensure_ffmpeg()
    from pydub import AudioSegment

    audio = AudioSegment.from_wav(safe_wav_path)
    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk_path = f"{safe_wav_path}_chunk_{i}.wav"
        if not (os.path.isfile(chunk_path) and os.path.getsize(chunk_path) > 0):
            chunk = audio[start : start + chunk_ms]
            chunk.export(chunk_path, format="wav")
        chunks.append({"path": chunk_path, "offset": start / 1000.0})

    return chunks


def process_input(source: str) -> dict:
    """Accept a YouTube URL, local audio path, or local video path.

    Returns:
        {
            "video_path": str | None,   # None when the source has no video track
            "wav_chunks": [{"path": str, "offset": float}, ...],
        }

    BREAKING CHANGE from the old version: this used to return `list[str]` (just
    chunk paths). It now returns a dict, because reel-building needs both the
    original video file and each chunk's time offset. main.py has been updated
    to match.
    """
    source = source.strip()
    video_path = None

    if source.startswith("http://") or source.startswith("https://"):
        safe_print("Detected YouTube URL. Downloading video...")
        video_path = download_youtube_video(source)
        wav_path = convert_to_wav(video_path)
    else:
        ext = os.path.splitext(source)[1].lower()
        if ext in AUDIO_ONLY_EXTS:
            safe_print("Detected local audio-only file. No video track available for reels.")
            wav_path = convert_to_wav(source)
        else:
            safe_print("Detected local video file. Converting audio for transcription...")
            video_path = source
            wav_path = convert_to_wav(source)

    safe_print("Chunking audio...")
    wav_chunks = chunk_audio_with_offsets(wav_path)
    safe_print(f"Audio ready - {len(wav_chunks)} chunk(s) created.")

    return {"video_path": video_path, "wav_chunks": wav_chunks}
