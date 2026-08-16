# Changelog

All notable changes to **Relent AI** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Standardized open-source packaging with PEP 518/621 `pyproject.toml`.
- CLI script entry points (`relent-ai`, `relent-ai-server`).
- Advanced non-interactive CLI flags (`--source`, `--language`, `--reel`, `--output`, `--json`).
- Pre-commit configuration and developer `Makefile`.
- Multi-OS GitHub Actions CI workflow (Ubuntu, Windows) across Python 3.10-3.13.
- Automated Docker build test and CodeQL security analysis workflows.
- Structured YAML GitHub issue forms and PR templates.
- Comprehensive technical documentation suite (`CLI_REFERENCE.md`, `DEVELOPMENT.md`, `TROUBLESHOOTING.md`).

### Changed
- Refactored ML dependency loading (`torch`, `whisper`, `transformers`) to be lazy for instant startup and offline testing.
- Improved FFmpeg binary resolution with graceful fallback.
- Standardized test suite with fast offline mock fixtures.

---

## [0.1.0] - 2026-08-16

### Added
- **Universal Video Ingestion**: Ingest YouTube URLs or local media files via `yt-dlp` and `pydub`.
- **Speech-to-Text Pipeline**: High-precision transcription with OpenAI Whisper and AI4Bharat IndicWhisper with global timestamp preservation.
- **Hierarchical Map-Reduce Summarizer**: LangChain-powered chunk summarization with dynamic category headers and executive takeaways.
- **Structured Intelligence Extraction**: Automated action items with assignees & deadlines, key decisions, and open questions.
- **Semantic RAG Engine**: Chroma vector store indexing with `all-MiniLM-L6-v2` embeddings for natural language transcript querying.
- **AI Highlight Reel Studio**: Automated prompt-directed segment selection and lossless FFmpeg clipping & concatenation.
- **Multi-Format Export**: One-click intelligence export to PDF, Markdown, and plain text formats.
- **Modern User Interfaces**: Cyberpunk/Glassmorphic React 19 + Vite frontend and standalone Streamlit dashboard.
- **Local Privacy**: 100% on-device AI inference via local Ollama LLMs and local Whisper speech models.
