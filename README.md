<div align="center">

# 🎬 Relent AI

### **Open-Source Neural Video Intelligence & AI Highlight Reel Studio**
*Transform YouTube videos or local recordings into executive summaries, action items, semantic RAG search, and automated highlight reels — 100% locally with Ollama, Whisper & FFmpeg.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![React: 19](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![FastAPI / Starlette](https://img.shields.io/badge/Backend-Starlette%20%2F%20FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Ollama: Local AI](https://img.shields.io/badge/Ollama-Local%20LLM-black?logo=ollama)](https://ollama.com)
[![OpenAI Whisper](https://img.shields.io/badge/Whisper-Speech%20to%20Text-412991?logo=openai)](https://github.com/openai/whisper)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Video%20Clipping-007808?logo=ffmpeg)](https://ffmpeg.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[Quickstart](#-quickstart) • [Architecture](#-architecture) • [Features](#-key-features) • [CLI Reference](docs/CLI_REFERENCE.md) • [API Reference](docs/API_REFERENCE.md) • [Documentation](docs/) • [Contributing](CONTRIBUTING.md)

</div>

---

## 🌟 Overview

**Relent AI** is an end-to-end, privacy-first AI video intelligence platform designed for developers, creators, researchers, and enterprise teams. It ingests video from YouTube URLs or local media, transcribes the speech using OpenAI Whisper or AI4Bharat IndicWhisper, summarizes and extracts structured intelligence using local Ollama LLMs, indexes the content into a Chroma vector store for semantic RAG Q&A, and automatically clips targeted video reels using FFmpeg based on plain natural language instructions.

---

## ⚡ Key Features

| Capability | Description |
| :--- | :--- |
| 📥 **Universal Ingestion** | One-click processing for **YouTube links**, local audio/video files (`.mp4`, `.mov`, `.mkv`, `.mp3`, `.wav`), or drag-and-drop web uploads. |
| 🎙️ **Multi-Engine Transcription** | Language-routed transcription powered by **Whisper Large-v3** and **AI4Bharat IndicWhisper** for Hindi / Hinglish / Indic languages. |
| 🧠 **Hierarchical Intelligence** | Reasoning and tone-matching powered by **Qwen2.5-72B (4-bit)** as primary LLM, backed by **Sarvam-M** as Hindi-specialized fallback. |
| 💬 **Interactive RAG Terminal** | Ask questions and chat directly with your video using semantic vector retrieval without hallucination. |
| 🎬 **AI Reel Studio** | Automatically cuts, trims, and concatenates exact video segments matching user prompt duration (e.g. *"2-minute product summary reel"*). |
| 📄 **Multi-Format Export** | Download intelligence reports in **PDF**, **Markdown**, or plain text formats. |
| 🎨 **Dual User Interfaces** | Modern Cyberpunk/Glassmorphic **React + Vite App** (`http://127.0.0.1:5173`) and a standalone **Streamlit Dashboard** (`http://127.0.0.1:8501`). |
| 💻 **Scriptable CLI** | Fully scriptable command-line interface (`relent-ai`) with JSON export for CI/CD and automation pipelines. |
| 🔒 **100% Local & Private** | Runs entirely on your own hardware via Ollama and local Whisper models without sending data to third-party cloud APIs. |

---

## 🏗️ Architecture

```mermaid
flowchart TD
    subgraph INGESTION["1. Ingestion Layer"]
        A[YouTube URL / Local Video / File Upload] --> B[yt-dlp Video Downloader]
        B --> C[static_ffmpeg Audio Converter]
        C --> D[10-min Audio Chunker with Time Offsets]
    end

    subgraph TRANSCRIPTION["2. Speech-to-Text Engine"]
        D --> E{Language Selector}
        E -->|English| F[OpenAI Whisper Engine]
        E -->|Hinglish| G[AI4Bharat IndicWhisper]
        F --> H[Timestamped Segments JSON]
        G --> H
    end

    subgraph INTELLIGENCE["3. LLM Intelligence & Map-Reduce"]
        H --> I[Map-Reduce Summarizer]
        H --> J[Action Items & Decision Extractor]
        H --> K[Chroma Vector Store Indexer]
        I --> L[Executive Summary]
        J --> M[Tasks & Decisions]
    end

    subgraph CREATIVE["4. Reel Studio & Delivery"]
        H --> N[LLM Segment Selector]
        N --> O[FFmpeg Subclip Cutter]
        O --> P[Seamless Video Reel Assembly]
        K --> Q[RAG Q&A Chat Terminal]
    end

    subgraph UI["5. Presentation Layer"]
        L --> R[React 19 Frontend :5173 / Streamlit App :8501 / CLI :relent-ai]
        M --> R
        P --> R
        Q --> R
        R --> S[PDF / Markdown / TXT Exporter]
    end
```

---

## Local YouTube Shorts Studio

Paste a YouTube link to generate up to ten distinct **9:16 MP4s** with a headline overlay, synchronized burned-in captions, and the video's original voice. The original picture is kept in view against a blurred background. Each short includes a title, description, hashtags, and its time range in the source. The ranking favors a strong opening and a self-contained moment.

### Run without Docker

1. Install Python 3.10+, Node.js 22.12+, and FFmpeg/FFprobe with `libass` and `libx264` on your PATH. Relent enables the installed Node.js runtime for yt-dlp's YouTube downloads.
2. From the repository root, create and activate a virtual environment. On Windows PowerShell use `.\.venv\Scripts\Activate.ps1`; on macOS/Linux use `source .venv/bin/activate`.

   ```bash
   python -m venv .venv
   # Activate .venv before running the remaining commands.
   python -m pip install -r requirements-shorts.txt
   npm --prefix frontend ci
   npm --prefix frontend run build
   ```

3. Create a `.env` in the repository root and set `GROQ_API_KEY` to your own [Groq API key](https://console.groq.com/keys). The default models are `whisper-large-v3-turbo` and `openai/gpt-oss-20b`. To override them, set `GROQ_TRANSCRIPTION_MODEL` or `GROQ_CHAT_MODEL`.
4. Run `python server.py` from the repository root and open [Shorts Studio](http://127.0.0.1:8000/shorts). Paste a link to a finished YouTube video you can reuse, then download each MP4 and the batch metadata. Outputs are saved under `shorts_output/`.

The Shorts Studio uses your Groq account's [free-tier limits](https://console.groq.com/docs/rate-limits). Groq receives audio and transcript excerpts for inference, while FFmpeg renders the video locally. Use a source up to 30 minutes long. Short or quiet videos can yield fewer than ten clips. Captions use local fonts, so install a font for the source language if glyphs are missing. YouTube downloads require access to the video page and its media servers. If your network uses a trusted custom CA, set `SSL_CERT_FILE` to your CA bundle before starting Relent so the downloader can verify that connection.

---

## 🚀 Quickstart

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & **npm** (for modern React UI)
- **Ollama**: [Download & Install Ollama](https://ollama.com)

### 1. Clone & Setup Environment
```bash
git clone https://github.com/HarshPopat23/Relent.git
cd Relent

# Create and activate Python virtual environment
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies in editable mode
pip install -r requirements.txt
pip install -e ".[dev]"
```

### 2. Configure Local LLM & Ollama
```bash
# Pull the recommended model in Ollama
ollama pull qwen2.5:3b-instruct

# Copy the environment file template
cp .env.example .env
```

### 3. Launch Development Stack
#### On Windows:
```cmd
scripts\run_dev.bat
```
#### On Linux / macOS:
```bash
chmod +x scripts/run_dev.sh
./scripts/run_dev.sh
```

Open your browser at:
- 🌐 **Modern React App**: [http://127.0.0.1:5173](http://127.0.0.1:5173)
- 📊 **Streamlit Dashboard**: [http://127.0.0.1:8501](http://127.0.0.1:8501)
- 🔌 **API Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## 💻 CLI Usage

Relent AI includes a powerful command-line interface:

```bash
# Process a video and save markdown intelligence report
python main.py --source "https://youtu.be/11Y3B33oCLE" --output "report.md"

# Generate a 2-minute highlight reel directly from terminal
python main.py --source "video.mp4" --reel "2 minute product summary"

# Output structured JSON for automation scripts
python main.py --source "https://youtu.be/11Y3B33oCLE" --json

# Launch interactive Q&A terminal
python main.py
```

👉 See the complete [CLI Reference Guide](docs/CLI_REFERENCE.md) for all options and flags.

---

## 🧪 Running Automated Tests

Run the test suite locally using `pytest`:

```bash
# Run all unit tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=core --cov=utils

# Run standalone test runner
python run_tests.py
```

---

## 🐳 Docker Deployment

Run the complete stack inside Docker containers:

```bash
docker-compose up --build
```

---

## 📖 In-Depth Guides & Documentation

- 📘 [System Architecture & Pipeline Flow](docs/ARCHITECTURE.md)
- 🔌 [REST API Reference](docs/API_REFERENCE.md)
- 💻 [Command-Line Interface (CLI) Manual](docs/CLI_REFERENCE.md)
- ⚙️ [Hardware & Model Configuration Guide](docs/CONFIGURATION.md)
- 💡 [Real-World Use Cases & Practical Workflows](docs/USE_CASES.md)
- 🛠️ [Developer Guide & Architecture Extension](docs/DEVELOPMENT.md)
- 🔧 [Troubleshooting & Common Errors](docs/TROUBLESHOOTING.md)

---

## 🤝 Contributing

Contributions are what make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

Please review our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before submitting a pull request.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

<div align="center">
Built with ❤️ by the <b>Relent AI</b> Community
</div>
