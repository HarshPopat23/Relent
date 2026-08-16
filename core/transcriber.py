"""Relent AI - Speech-to-Text Engine.

High-efficiency neural transcription powered by Faster-Whisper (int8/float16)
with dynamic GPU auto-detection and fallback to standard Whisper and IndicWhisper.
"""

import gc
import json
import os
import re
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
WHISPER_BACKEND = os.getenv(
    "WHISPER_BACKEND", "auto"
).lower()  # "auto", "faster-whisper", "whisper"
WHISPER_COMPUTE_TYPE = os.getenv(
    "WHISPER_COMPUTE_TYPE", ""
)  # e.g., "int8", "float16", "int8_float16"

# Path or HF repo id of your installed IndicWhisper checkpoint
INDICWHISPER_MODEL = os.getenv("INDICWHISPER_MODEL", "ai4bharat/indicwhisper")
INDICWHISPER_DEVICE = os.getenv("INDICWHISPER_DEVICE", "")

_model_entry = None
_indicwhisper_pipe = None


def get_device_and_compute_type() -> tuple[str, str]:
    """Detect available hardware (CUDA GPU vs CPU) and optimal quantization compute type."""
    try:
        import torch

        cuda_available = torch.cuda.is_available()
    except Exception:
        cuda_available = False

    if cuda_available:
        device = "cuda"
        compute_type = WHISPER_COMPUTE_TYPE or "float16"
    else:
        device = "cpu"
        compute_type = WHISPER_COMPUTE_TYPE or "int8"

    return device, compute_type


def load_model():
    """Load Faster-Whisper or fallback to standard Whisper with dynamic GPU auto-detection."""
    global _model_entry

    if _model_entry is None:
        device, compute_type = get_device_and_compute_type()
        model_dir = os.getenv("WHISPER_MODEL_DIR", os.path.join(os.getcwd(), "whisper_models"))
        os.makedirs(model_dir, exist_ok=True)

        loaded = False

        # 1. Attempt Faster-Whisper (CTranslate2 int8 / float16)
        if WHISPER_BACKEND in ("auto", "faster-whisper", "faster_whisper"):
            try:
                from faster_whisper import WhisperModel

                safe_print(
                    f"Loading Faster-Whisper model: '{WHISPER_MODEL}' on {device.upper()} (compute_type={compute_type})..."
                )
                model = WhisperModel(
                    WHISPER_MODEL,
                    device=device,
                    compute_type=compute_type,
                    download_root=model_dir,
                )
                _model_entry = ("faster_whisper", model, device)
                loaded = True
                safe_print("Faster-Whisper model loaded successfully.")
            except Exception as e:
                if WHISPER_BACKEND in ("faster-whisper", "faster_whisper"):
                    safe_print(f"Faster-Whisper load failed: {e}")
                    raise
                safe_print(
                    f"Faster-Whisper not available ({e}). Falling back to standard Whisper..."
                )

        # 2. Fallback to standard OpenAI Whisper
        if not loaded:
            import whisper

            safe_print(f"Loading standard Whisper model: '{WHISPER_MODEL}' on {device.upper()}...")
            model_path = os.path.join(model_dir, f"{WHISPER_MODEL}.pt")
            target = model_path if os.path.exists(model_path) else WHISPER_MODEL
            model = whisper.load_model(
                target,
                download_root=model_dir,
                in_memory=False,
                device=device,
            )
            _model_entry = ("whisper", model, device)
            safe_print("Standard Whisper model loaded.")

    return _model_entry


def load_indicwhisper():
    """Load AI4Bharat IndicWhisper with GPU auto-detection for Hinglish transcripts."""
    global _indicwhisper_pipe

    if _indicwhisper_pipe is None:
        from transformers import pipeline

        device_setting = INDICWHISPER_DEVICE
        if not device_setting:
            try:
                import torch

                device_setting = "cuda:0" if torch.cuda.is_available() else "cpu"
            except Exception:
                device_setting = "cpu"

        safe_print(
            f"Loading IndicWhisper model: '{INDICWHISPER_MODEL}' on {str(device_setting).upper()}..."
        )

        _indicwhisper_pipe = pipeline(
            task="automatic-speech-recognition",
            model=INDICWHISPER_MODEL,
            device=device_setting,
            chunk_length_s=25,
            return_timestamps=True,
        )

        safe_print("IndicWhisper model loaded.")

    return _indicwhisper_pipe


def transcribe_chunk_whisper(chunk_path: str, chunk_offset: float) -> list[dict]:
    """Transcribe one audio chunk with Faster-Whisper or standard Whisper."""
    engine_type, model, device = load_model()
    segments = []

    if engine_type == "faster_whisper":
        segments_iter, _ = model.transcribe(
            chunk_path,
            task="transcribe",
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
        )
        for seg in segments_iter:
            text = (
                seg.text.strip()
                if hasattr(seg, "text")
                else getattr(seg, "get", lambda k, d="": "")("text", "").strip()
            )
            if not text:
                continue
            start_time = seg.start if hasattr(seg, "start") else seg.get("start", 0.0)
            end_time = seg.end if hasattr(seg, "end") else seg.get("end", start_time)
            segments.append(
                {
                    "start": round(chunk_offset + float(start_time), 2),
                    "end": round(chunk_offset + float(end_time), 2),
                    "text": text,
                }
            )
    else:
        use_fp16 = device == "cuda"
        result = model.transcribe(chunk_path, task="transcribe", fp16=use_fp16)
        for seg in result.get("segments", []):
            text = seg.get("text", "").strip()
            if not text:
                continue
            segments.append(
                {
                    "start": round(chunk_offset + float(seg["start"]), 2),
                    "end": round(chunk_offset + float(seg["end"]), 2),
                    "text": text,
                }
            )

    return segments


def transcribe_chunk_indicwhisper(chunk_path: str, chunk_offset: float) -> list[dict]:
    """Transcribe one audio chunk with IndicWhisper for Hinglish / Indian languages."""
    pipe = load_indicwhisper()
    result = pipe(chunk_path)

    segments = []
    for chunk in result.get("chunks", []):
        text = chunk.get("text", "").strip()
        if not text:
            continue

        start_rel, end_rel = chunk.get("timestamp", (None, None))
        if start_rel is None:
            continue
        if end_rel is None:
            end_rel = start_rel

        segments.append(
            {
                "start": round(chunk_offset + float(start_rel), 2),
                "end": round(chunk_offset + float(end_rel), 2),
                "text": text,
            }
        )

    return segments


def transcribe_chunk(
    chunk_path: str,
    chunk_offset: float,
    language: str = "english",
) -> list[dict]:
    """Route transcription to Faster-Whisper or IndicWhisper based on selected language."""
    if language.lower() == "hinglish":
        return transcribe_chunk_indicwhisper(chunk_path, chunk_offset)

    return transcribe_chunk_whisper(chunk_path, chunk_offset)


def unload_transcribers():
    """Release Whisper models from memory so Ollama has full RAM/VRAM for LLM generation."""
    global _model_entry, _indicwhisper_pipe
    _model_entry = None
    _indicwhisper_pipe = None

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
    """Transcribe all audio chunks and return one flat, time-ordered list of segments."""
    engine = "IndicWhisper" if language.lower() == "hinglish" else "Faster-Whisper"

    safe_print(f"Using {engine} for transcription.")

    all_segments = []
    total_chunks = len(wav_chunks)

    safe_lang = re.sub(r"[^a-zA-Z0-9_-]", "", str(language)) or "default"

    for i, chunk in enumerate(wav_chunks, start=1):
        raw_chunk_path = str(chunk.get("path", "")).strip()
        if not raw_chunk_path:
            continue
        safe_chunk_path = os.path.abspath(raw_chunk_path)
        cache_file = f"{safe_chunk_path}.{safe_lang}.json"

        if os.path.isfile(cache_file):
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
            safe_chunk_path,
            chunk["offset"],
            language=language,
        )

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(segments, f, ensure_ascii=False)
        except Exception:
            pass

        all_segments.extend(segments)

    # Free model from RAM/VRAM so Ollama has full memory for LLM generation
    unload_transcribers()

    safe_print("Transcription completed.")
    return all_segments


def segments_to_text(segments: list[dict]) -> str:
    """Join segment texts into one plain transcript string."""
    return " ".join(s["text"] for s in segments).strip()
