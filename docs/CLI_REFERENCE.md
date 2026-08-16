# Relent AI Command-Line Interface (CLI) Reference

Relent AI provides a powerful command-line interface via `main.py` or the `relent-ai` entrypoint script. It supports interactive terminal chat sessions, scripted pipeline executions, automated highlight reel cuts, and machine-readable JSON exports.

---

## 🚀 Quick Usage

```bash
# Launch interactive terminal mode
relent-ai

# Or with python directly:
python main.py
```

---

## 🛠️ CLI Flags & Options

```
usage: relent-ai [-h] [--version] [--source SOURCE] [--language {english,hinglish}]
                 [--output OUTPUT] [--reel REEL] [--json] [--interactive]

Relent AI - Local Neural Video Intelligence & AI Reel Studio

options:
  -h, --help            show this help message and exit
  --version, -v         show program's version number and exit
  --source SOURCE, -s SOURCE
                        YouTube URL or local path to audio/video file
  --language {english,hinglish}, -l {english,hinglish}
                        Transcription speech engine language (default: english)
  --output OUTPUT, -o OUTPUT
                        Path to save markdown report (e.g., report.md)
  --reel REEL, -r REEL  Automatically generate a highlight reel with the given prompt
                        (e.g. '2 minutes overview')
  --json                Output results as JSON to stdout (non-interactive)
  --interactive, -i     Force interactive Q&A mode after processing
```

---

## 📋 Common CLI Workflows

### 1. Process YouTube Video & Save Markdown Report
```bash
python main.py \
  --source "https://youtu.be/11Y3B33oCLE" \
  --output "reports/nvidia_keynote_summary.md"
```

### 2. Transcribe Hinglish Video & Generate a 2-Minute Reel
```bash
python main.py \
  --source "downloads/podcast_episode_42.mp4" \
  --language "hinglish" \
  --reel "2 minute highlight reel of the most impactful tips" \
  --output "podcast_notes.md"
```

### 3. Pipeline JSON Output for Automation / CI
```bash
python main.py \
  --source "https://youtu.be/11Y3B33oCLE" \
  --json > result.json
```

**JSON Output Schema:**
```json
{
  "title": "NVIDIA AI Keynote 2026",
  "subtitle": "Overview of Accelerated Computing Platforms",
  "summary": "### Overview\n...",
  "action_items": "1. Deploy NIM microservices...",
  "key_decisions": "1. Standardize on Blackwell clusters...",
  "open_questions": "1. General availability dates...",
  "transcript": "Full text...",
  "video_path": "downloads/11Y3B33oCLE.mp4",
  "segments_count": 142
}
```

### 4. Direct Processing with Interactive Terminal Q&A
```bash
python main.py --source "https://youtu.be/11Y3B33oCLE" --interactive
```
Once processing finishes, you can ask questions directly against the video transcript:
```
You: What was said about energy efficiency?
🤖 Assistant: The speaker noted a 25x reduction in power consumption...

You: reel
Describe the reel you want: 1 minute clip on hardware specs
🎬 Script: 00:02:10 - 00:03:10: Here are the specs...
✅ Reel saved to: reels/reel_3f82a1b9.mp4
```

---

## ⚙️ Exit Codes

- `0`: Successful execution.
- `1`: Processing or validation failure (e.g., invalid URL, network error, missing dependencies).
- `2`: Invalid command-line arguments.
