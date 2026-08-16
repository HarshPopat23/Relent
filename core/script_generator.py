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


OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b-instruct")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def get_llm():
    from langchain_ollama import ChatOllama

    # temperature=0 for maximum consistency picking IDs; format="json" forces
    # Ollama to constrain output to valid JSON instead of hoping the model
    # follows the "only a JSON array" instruction on its own.
    kwargs = {
        "model": OLLAMA_MODEL,
        "base_url": OLLAMA_BASE_URL,
        "temperature": 0,
        "format": "json",
    }
    num_gpu = os.getenv("OLLAMA_NUM_GPU")
    if num_gpu is not None and num_gpu != "":
        try:
            kwargs["num_gpu"] = int(num_gpu)
        except ValueError:
            pass

    return ChatOllama(**kwargs)


# The LLM never writes new text — it only picks segment IDs. This is what
# guarantees "all words must be from the video": the script text is built
# later by literally joining the chosen segments' original text.
SELECTOR_SYSTEM_PROMPT = """You are selecting exact sentences from a video transcript to build a short reel/script.

You will be given a numbered list of transcript segments. Each line looks like:
[ID] (duration_seconds) text

Rules:
- You must choose ONLY from the given segment IDs. Never invent text.
- Choose segments that are relevant to the user's requested topic.
- Order the IDs by RELEVANCE, most important/on-topic first — NOT by video order (the code will re-sort them into video order afterward, and will cut your list off once it hits the requested duration, so put your best picks first).
- If nothing in the transcript matches the topic, return an empty list.

Respond with ONLY a JSON object of this exact shape, nothing else:
{{"segment_ids": [7, 2, 8, 3]}}
"""

# How much over the requested duration we allow before we stop adding segments.
DURATION_TOLERANCE = 0.15

# Split the transcript into chunks of at most this many segments per LLM call.
# Smaller/coder models lose instruction-following over long inputs, and a
# 15-20 min video can easily produce 150+ segments in one prompt.
MAX_SEGMENTS_PER_CALL = 60


def _format_segments_for_prompt(segments: list[dict]) -> str:
    lines = []
    for i, seg in enumerate(segments):
        duration = round(seg["end"] - seg["start"], 1)
        lines.append(f"[{i}] ({duration}s) {seg['text']}")
    return "\n".join(lines)


def _parse_target_seconds(user_request: str) -> float | None:
    """Safely parse requested duration from user query with length bounding."""
    if not isinstance(user_request, str) or not user_request.strip():
        return None
    bounded_text = user_request[:300].strip().lower()
    match = re.search(r"\b(\d{1,6}(?:\.\d{1,4})?)\s*(second|sec|minute|min)", bounded_text)
    if not match:
        return None
    value, unit = match.groups()
    unit_seconds = 60 if "min" in unit else 1
    return float(value) * unit_seconds


def _duration_hint(target_seconds: float | None) -> str:
    if target_seconds is None:
        return "No specific duration requested — pick a concise set covering the topic."
    return f"Target total duration: approximately {int(target_seconds)} seconds."


def _trim_to_duration(
    segments_in_relevance_order: list[dict], target_seconds: float | None
) -> list[dict]:
    """Greedily keep adding segments (in the order given) until the total
    duration reaches the target, then stop — this is what actually enforces
    the requested length, since the LLM alone won't reliably self-limit."""
    if target_seconds is None:
        return segments_in_relevance_order

    max_allowed = target_seconds * (1 + DURATION_TOLERANCE)
    total = 0.0
    kept = []

    for seg in segments_in_relevance_order:
        dur = seg["end"] - seg["start"]
        if kept and total + dur > max_allowed:
            continue  # skip this one, but keep looking — a shorter later pick might still fit
        kept.append(seg)
        total += dur
        if total >= target_seconds:
            break

    return kept


def _find_int_list_anywhere(parsed) -> list[int] | None:
    """Small/coder models don't always use the exact key name we asked for
    (segment_ids). Instead of failing silently, walk the parsed JSON and use
    the first list made up entirely of ints, wherever it is."""
    if isinstance(parsed, list) and all(isinstance(x, int) for x in parsed):
        return parsed

    if isinstance(parsed, dict):
        # Prefer the exact key first.
        if "segment_ids" in parsed and isinstance(parsed["segment_ids"], list):
            candidate = parsed["segment_ids"]
            if all(isinstance(x, int) for x in candidate):
                return candidate
        # Otherwise take the first list-of-ints value, whatever it's called.
        for value in parsed.values():
            if isinstance(value, list) and value and all(isinstance(x, int) for x in value):
                return value

    return None


def _extract_id_list_ordered(raw: str, max_id: int) -> list[int]:
    """Parse the LLM's JSON output, keeping ID order (relevance order) and
    dropping any invalid/duplicate/out-of-range IDs."""
    ids = None

    try:
        parsed = json.loads(raw)
        ids = _find_int_list_anywhere(parsed)
    except json.JSONDecodeError:
        pass

    if ids is None:
        # Last-resort fallback: pull the first [...] looking array out of the
        # raw text, in case the model wrapped valid JSON in prose despite
        # format="json" (some models still do this).
        match = re.search(r"\[[\s\d,]*\]", raw)
        if match:
            try:
                candidate = json.loads(match.group(0))
                if all(isinstance(x, int) for x in candidate):
                    ids = candidate
            except json.JSONDecodeError:
                pass

    if ids is None:
        safe_print(
            f"⚠️ Reel selector: could not extract any segment IDs. Raw model output was:\n{raw[:500]}"
        )
        return []

    seen = set()
    clean_ids = []
    for i in ids:
        if isinstance(i, int) and 0 <= i <= max_id and i not in seen:
            seen.add(i)
            clean_ids.append(i)

    return clean_ids


def _select_from_batch(
    segments: list[dict], user_request: str, target_seconds: float | None
) -> list[dict]:
    """Run one LLM selection call over a single batch of segments (<= MAX_SEGMENTS_PER_CALL)."""
    if not segments:
        return []

    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SELECTOR_SYSTEM_PROMPT),
            (
                "human",
                "User request: {user_request}\n{duration_hint}\n\nTranscript segments:\n{segments}",
            ),
        ]
    )

    chain = prompt | llm | StrOutputParser()

    raw = chain.invoke(
        {
            "user_request": user_request,
            "duration_hint": _duration_hint(target_seconds),
            "segments": _format_segments_for_prompt(segments),
        }
    )

    relevance_ids = _extract_id_list_ordered(raw, max_id=len(segments) - 1)
    return [segments[i] for i in relevance_ids]


def select_segments_for_request(segments: list[dict], user_request: str) -> list[dict]:
    """
    Ask the LLM to pick transcript segment IDs (verbatim, in video order) that
    satisfy the user's request (e.g. "script about GSoC, 2 minutes").

    Returns the selected segments UNMODIFIED, in their original video order —
    each still carrying its "start"/"end" timestamps, ready to hand to
    video_clipper.build_reel().

    Long transcripts are split into batches of MAX_SEGMENTS_PER_CALL segments
    each, selected independently, then merged — this keeps the prompt small
    enough for smaller/coder models to follow the instructions reliably.
    """
    if not segments:
        return []

    target_seconds = _parse_target_seconds(user_request)

    relevance_ordered = []
    for start in range(0, len(segments), MAX_SEGMENTS_PER_CALL):
        batch = segments[start : start + MAX_SEGMENTS_PER_CALL]
        relevance_ordered.extend(_select_from_batch(batch, user_request, target_seconds))

    if not relevance_ordered:
        safe_print(
            "⚠️ Reel selector: no segments matched LLM filter, selecting representative segments."
        )
        # Fallback: take segments spread across the video
        step = max(1, len(segments) // 25)
        relevance_ordered = segments[::step]

    # Enforce the requested duration in code, then sort back into video order.
    trimmed = _trim_to_duration(relevance_ordered, target_seconds)
    trimmed.sort(key=lambda seg: seg["start"])

    return trimmed


def build_script_text(selected_segments: list[dict]) -> str:
    """The script is just the verbatim, in-order text of the selected segments —
    every single word necessarily comes from the transcript, because nothing
    here is generated."""
    return " ".join(seg["text"].strip() for seg in selected_segments).strip()
