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


WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")

# Path or HF repo id of your installed IndicWhisper checkpoint, e.g.
# "ai4bharat/indicwhisper" or a local folder path if you downloaded it manually.
INDICWHISPER_MODEL = os.getenv("INDICWHISPER_MODEL", "ai4bharat/indicwhisper")
INDICWHISPER_DEVICE = os.getenv("INDICWHISPER_DEVICE", "cpu")  # "cuda" if you have a GPU

_model = None
_indicwhisper_pipe = None


def load_model():
    """Load the Whisper model once and reuse it (used for the 'english' path)."""
    global _model

    if _model is None:
        import whisper

        safe_print(f"Loading Whisper model: {WHISPER_MODEL}...")

        model_dir = os.getenv("WHISPER_MODEL_DIR", os.path.join(os.getcwd(), "whisper_models"))
        os.makedirs(model_dir, exist_ok=True)

        model_path = os.path.join(model_dir, f"{WHISPER_MODEL}.pt")
        target = model_path if os.path.exists(model_path) else WHISPER_MODEL
        _model = whisper.load_model(target, download_root=model_dir, in_memory=False, device="cpu")

        safe_print("Whisper model loaded.")

    return _model


def load_indicwhisper():
    """Load AI4Bharat IndicWhisper once and reuse it (used for the 'hinglish' path).
    This replaces Sarvam entirely — no more paid API call, and unlike Sarvam it
    gives us real segment-level timestamps, which is why the hinglish reel
    clipping used to be stuck at ~25s granularity."""
    global _indicwhisper_pipe

    if _indicwhisper_pipe is None:
        from transformers import pipeline

        safe_print(f"Loading IndicWhisper model: {INDICWHISPER_MODEL}...")

        _indicwhisper_pipe = pipeline(
            task="automatic-speech-recognition",
            model=INDICWHISPER_MODEL,
            device=INDICWHISPER_DEVICE,
            chunk_length_s=25,
            return_timestamps=True,
        )

        safe_print("IndicWhisper model loaded.")

    return _indicwhisper_pipe


def transcribe_chunk_whisper(chunk_path: str, chunk_offset: float) -> list[dict]:
    """Transcribe one audio chunk with Whisper and return timestamped segments.

    Whisper timestamps are relative to the chunk, so we add chunk_offset to make
    them relative to the full original video — this is what makes clipping possible.
    """
    model = load_model()

    try:
        import torch

        use_fp16 = torch.cuda.is_available()
    except Exception:
        use_fp16 = False

    result = model.transcribe(chunk_path, task="transcribe", fp16=use_fp16)

    segments = []
    for seg in result.get("segments", []):
        text = seg["text"].strip()
        if not text:
            continue
        segments.append(
            {
                "start": round(chunk_offset + seg["start"], 2),
                "end": round(chunk_offset + seg["end"], 2),
                "text": text,
            }
        )

    return segments


def transcribe_chunk_indicwhisper(chunk_path: str, chunk_offset: float) -> list[dict]:
    """Transcribe one audio chunk with IndicWhisper and return timestamped
    segments, converted to full-video time using chunk_offset — same as the
    Whisper path. Unlike Sarvam, this gives per-segment timestamps directly
    from the model instead of one flat 25s block."""

    pipe = load_indicwhisper()

    result = pipe(chunk_path)

    segments = []
    for chunk in result.get("chunks", []):
        text = chunk["text"].strip()
        if not text:
            continue

        start_rel, end_rel = chunk["timestamp"]
        if start_rel is None:
            continue
        if end_rel is None:
            end_rel = start_rel  # last chunk sometimes has an open end

        segments.append(
            {
                "start": round(chunk_offset + start_rel, 2),
                "end": round(chunk_offset + end_rel, 2),
                "text": text,
            }
        )

    return segments


def transcribe_chunk(
    chunk_path: str,
    chunk_offset: float,
    language: str = "english",
) -> list[dict]:
    """
    Route transcription to the appropriate engine.

    english  -> Whisper (small)
    hinglish -> IndicWhisper (local, replaces Sarvam)
    """

    if language.lower() == "hinglish":
        return transcribe_chunk_indicwhisper(chunk_path, chunk_offset)

    return transcribe_chunk_whisper(chunk_path, chunk_offset)


def unload_transcribers():
    global _model, _indicwhisper_pipe
    _model = None
    _indicwhisper_pipe = None
    import gc

    gc.collect()
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except Exception:
        pass


def transcribe_all(
    wav_chunks: list[dict],
    language: str = "english",
) -> list[dict]:
    """Transcribe all audio chunks and return one flat, time-ordered list of
    segments across the whole video:

        [{"start": float, "end": float, "text": str}, ...]

    wav_chunks must be the list produced by
    utils.audio_processor.process_input()["wav_chunks"], i.e.
    [{"path": str, "offset": float}, ...].
    """
    import json

    engine = "IndicWhisper" if language.lower() == "hinglish" else "Whisper"

    safe_print(f"Using {engine} for transcription.")

    all_segments = []
    total_chunks = len(wav_chunks)

    for i, chunk in enumerate(wav_chunks, start=1):
        cache_file = f"{chunk['path']}.{language}.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, encoding="utf-8") as f:
                    segments = json.load(f)
                safe_print(f"Loaded cached transcript for chunk {i}/{total_chunks}.")
                all_segments.extend(segments)
                continue
            except Exception:
                pass

        safe_print(f"Transcribing chunk {i}/{total_chunks}...")

        segments = transcribe_chunk(
            chunk["path"],
            chunk["offset"],
            language=language,
        )

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(segments, f, ensure_ascii=False)
        except Exception:
            pass

        all_segments.extend(segments)

    # Free Whisper model from RAM so Ollama has full memory for LLM generation
    unload_transcribers()

    safe_print("Transcription completed.")

    return all_segments


def segments_to_text(segments: list[dict]) -> str:
    """Join segment texts into one plain transcript string, for the
    summarizer/extractor prompts that only need plain text."""
    return " ".join(s["text"] for s in segments).strip()
