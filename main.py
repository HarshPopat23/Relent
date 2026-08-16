"""Relent AI - CLI Entry Point & Pipeline Orchestrator.

Processes YouTube videos or local media files to generate summaries, action items,
decisions, open questions, semantic RAG search, and automated highlight reels.
"""

import argparse
import json
import sys

# Ensure UTF-8 output on Windows consoles to prevent charmap encoding crashes
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def safe_print(text: str = "") -> None:
    """Print safely without failing on Windows console codepage limitations."""
    try:
        print(text)
    except Exception:
        try:
            encoding = sys.stdout.encoding or "utf-8"
            print(str(text).encode(encoding, errors="replace").decode(encoding, errors="replace"))
        except Exception:
            pass


from dotenv import load_dotenv

# IMPORTANT: load_dotenv() must run BEFORE the core.* imports below.
load_dotenv()

from core import __version__
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import ask_question, build_rag_chain
from core.script_generator import build_script_text, select_segments_for_request
from core.summarizer import generate_subtitle, generate_title, summarize
from core.transcriber import segments_to_text, transcribe_all
from core.video_clipper import build_reel
from utils.audio_processor import process_input


def run_pipeline(source: str, language: str = "english") -> dict:
    """Execute the end-to-end video intelligence ingestion & analysis pipeline."""
    safe_print(f"🎬 Starting Relent AI pipeline for: {source}")

    inputs = process_input(source)  # {"video_path": ..., "wav_chunks": [...]}

    segments = transcribe_all(inputs["wav_chunks"], language=language)
    transcript = segments_to_text(segments)

    safe_print(f"Transcript generated ({len(transcript)} chars, {len(segments)} segments).")

    title = generate_title(transcript)
    subtitle = generate_subtitle(transcript)
    summary = summarize(transcript)
    action_items = extract_action_items(transcript)
    decisions = extract_key_decisions(transcript)
    questions = extract_questions(transcript)
    rag_chain = build_rag_chain(transcript)

    return {
        "title": title,
        "subtitle": subtitle,
        "transcript": transcript,
        "segments": segments,  # kept for reel generation
        "video_path": inputs["video_path"],  # kept for reel generation
        "summary": summary,
        "action_items": action_items,
        "key_decisions": decisions,
        "open_questions": questions,
        "rag_chain": rag_chain,
    }


def run_reel_pipeline(result: dict, user_request: str) -> dict:
    """Build a highlight reel from an already-processed video result."""
    segments = result.get("segments", [])

    if not segments:
        return {
            "script": "",
            "selected_segments": [],
            "reel_path": None,
            "error": "No transcript segments available to build a reel.",
        }

    selected = select_segments_for_request(segments, user_request)

    if not selected:
        return {
            "script": "",
            "selected_segments": [],
            "reel_path": None,
            "error": "No matching content was found in the transcript for that request.",
        }

    script_text = build_script_text(selected)
    reel_path = build_reel(result["video_path"], selected)

    return {
        "script": script_text,
        "selected_segments": selected,
        "reel_path": reel_path,
        "error": None,
    }


def format_markdown_report(res: dict) -> str:
    """Format pipeline results into a markdown intelligence report."""
    return f"""# {res.get("title", "Video Report")}

**{res.get("subtitle", "")}**

---

## 📋 Executive Summary
{res.get("summary", "No summary available.")}

---

## ✅ Action Items
{res.get("action_items", "No action items recorded.")}

---

## 🔑 Key Decisions
{res.get("key_decisions", "No key decisions recorded.")}

---

## ❓ Open Questions / Follow-ups
{res.get("open_questions", "No open questions.")}

---

## 📝 Full Transcript
{res.get("transcript", "")}
"""


def interactive_mode(source: str | None = None, language: str = "english"):
    """Interactive CLI terminal session."""
    if not source:
        source = input("Enter YouTube URL or local audio/video file path: ").strip()
    if not source:
        safe_print("No input provided. Exiting.")
        return

    result = run_pipeline(source, language)

    safe_print("\n" + "=" * 60)
    safe_print(f"📌 Title: {result['title']}")
    safe_print(f"📝 {result['subtitle']}")
    safe_print(f"\n📋 Summary:\n{result['summary']}")
    safe_print(f"\n✅ Action Items:\n{result['action_items']}")
    safe_print(f"\n🔑 Key Decisions:\n{result['key_decisions']}")
    safe_print(f"\n❓ Open Questions:\n{result['open_questions']}")
    safe_print("=" * 60)

    safe_print("\n💬 Interactive Q&A Terminal (type 'exit' to quit, or 'reel' to build a reel)\n")
    rag_chain = result["rag_chain"]

    while True:
        try:
            question = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            safe_print("\n👋 Goodbye!")
            break

        if question.lower() in ["exit", "quit", "q"]:
            safe_print("👋 Goodbye!")
            break

        if not question:
            continue

        if question.lower() == "reel":
            try:
                reel_request = input(
                    "Describe the reel you want (e.g. '2 minute summary of main announcement'): "
                ).strip()
            except (KeyboardInterrupt, EOFError):
                break
            reel_result = run_reel_pipeline(result, reel_request)
            if reel_result["error"]:
                safe_print(f"⚠️ {reel_result['error']}")
            else:
                safe_print(f"\n🎬 Script:\n{reel_result['script']}")
                safe_print(f"\n✅ Reel saved to: {reel_result['reel_path']}\n")
            continue

        answer = ask_question(rag_chain, question)
        safe_print(f"\n🤖 Assistant: {answer}\n")


def main():
    """Main CLI entrypoint supporting both argument flags and interactive prompts."""
    parser = argparse.ArgumentParser(
        prog="relent-ai",
        description="Relent AI - Local Neural Video Intelligence & AI Reel Studio",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"Relent AI v{__version__}",
    )
    parser.add_argument(
        "--source",
        "-s",
        type=str,
        help="YouTube URL or local path to audio/video file",
    )
    parser.add_argument(
        "--language",
        "-l",
        type=str,
        default="english",
        choices=["english", "hinglish"],
        help="Transcription speech engine language (default: english)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Path to save markdown report (e.g., report.md)",
    )
    parser.add_argument(
        "--reel",
        "-r",
        type=str,
        help="Automatically generate a highlight reel with the given prompt (e.g. '2 minutes overview')",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON to stdout (non-interactive)",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Force interactive Q&A mode after processing",
    )

    args = parser.parse_args()

    # If no source was provided and not explicit JSON request, launch interactive mode
    if not args.source and not args.json:
        interactive_mode()
        return

    if not args.source:
        parser.error("--source is required when running in non-interactive mode")

    result = run_pipeline(args.source, language=args.language)

    reel_result = None
    if args.reel:
        safe_print(f"\n🎬 Generating reel: '{args.reel}'...")
        reel_result = run_reel_pipeline(result, args.reel)

    if args.output:
        md_content = format_markdown_report(result)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(md_content)
        safe_print(f"✅ Intelligence report written to: {args.output}")

    if args.json:
        output_data = {
            "title": result["title"],
            "subtitle": result["subtitle"],
            "summary": result["summary"],
            "action_items": result["action_items"],
            "key_decisions": result["key_decisions"],
            "open_questions": result["open_questions"],
            "transcript": result["transcript"],
            "video_path": result["video_path"],
            "segments_count": len(result["segments"]),
        }
        if reel_result:
            output_data["reel"] = {
                "script": reel_result["script"],
                "reel_path": reel_result["reel_path"],
                "error": reel_result["error"],
            }
        print(json.dumps(output_data, indent=2, ensure_ascii=False))
        return

    if args.interactive:
        safe_print("\n💬 Entering interactive Q&A mode...")
        rag_chain = result["rag_chain"]
        while True:
            try:
                question = input("\nYou: ").strip()
            except (KeyboardInterrupt, EOFError):
                break
            if question.lower() in ["exit", "quit", "q"]:
                break
            if not question:
                continue
            answer = ask_question(rag_chain, question)
            safe_print(f"\n🤖 Assistant: {answer}")


if __name__ == "__main__":
    main()
