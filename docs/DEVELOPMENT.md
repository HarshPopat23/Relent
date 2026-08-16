# Relent AI Developer Guide

This document is for developers who want to modify, extend, or contribute to **Relent AI**.

---

## 🛠️ Project Structure

```
relent-ai/
├── core/                       # Core AI pipeline algorithms
│   ├── extractor.py            # Action items, key decisions, questions extraction
│   ├── rag_engine.py           # Chroma retrieval & LangChain LCEL RAG chains
│   ├── script_generator.py     # Prompt-driven segment selection & duration constraints
│   ├── summarizer.py           # Map-Reduce chunking & hierarchical summarization
│   ├── transcriber.py          # OpenAI Whisper & AI4Bharat IndicWhisper routers
│   ├── vector_store.py         # Chroma database management & embeddings
│   └── video_clipper.py        # FFmpeg loss-free trimming & concat demuxing
├── utils/                      # Helper libraries & media processors
│   └── audio_processor.py      # yt-dlp downloader, 16kHz WAV converter, audio chunker
├── frontend/                   # Modern React 19 + Vite web interface
│   ├── src/components/         # UI sections (HUD, VideoPlayer, ReelStudio, Chat)
│   └── src/index.css           # Glassmorphism & Cyberpunk CSS design system
├── tests/                      # Automated test suite
│   ├── conftest.py             # Mock fixtures for offline test execution
│   └── test_*.py               # Unit and integration test files
├── docs/                       # Technical documentation
├── examples/                   # Standalone runnable example scripts
├── scripts/                    # Convenience launch and setup scripts
├── main.py                     # CLI pipeline entry point
├── server.py                   # Starlette / Uvicorn REST backend API
└── pyproject.toml              # Modern Python build & packaging metadata
```

---

## 💻 Local Environment Setup

1. **Python 3.10+ Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
   pip install -e ".[dev]"
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   ```

3. **Running the Dual Development Servers**:
   ```bash
   # Terminal 1: Backend
   python server.py

   # Terminal 2: Frontend
   cd frontend && npm run dev
   ```

---

## 🧪 Testing Guidelines

We write unit tests with **pytest**. Automated tests should run fast and execute completely offline without requiring external network connectivity or running Ollama/Whisper models.

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_script_generator.py -v

# Run with test coverage
pytest tests/ --cov=core --cov=utils
```

### Writing Mock Fixtures
Use `unittest.mock.patch` or `pytest` fixtures in `tests/conftest.py` when testing functions that invoke LLM chains or run FFmpeg subprocesses.

---

## 🎨 Code Style & Quality

- **Linter & Formatter**: [Ruff](https://docs.astral.sh/ruff/)
  ```bash
  ruff check --fix .
  ruff format .
  ```
- **Type Annotations**: Add type hints to public function signatures (`source: str, language: str = "english" -> dict`).
- **Docstrings**: Use clear Google/Sphinx style docstrings explaining inputs and return structures.

---

## 🧩 Extending Relent AI

### Adding a New Transcription Model
1. Open `core/transcriber.py`.
2. Define your engine function: `transcribe_chunk_yourmodel(chunk_path: str, chunk_offset: float) -> list[dict]`.
3. Ensure timestamps are returned relative to the global video:
   ```python
   {"start": round(chunk_offset + s["start"], 2), "end": round(chunk_offset + s["end"], 2), "text": s["text"]}
   ```
4. Register the engine in `transcribe_chunk()`.

### Adding a Custom Export Format
1. Open `server.py`.
2. Add an endpoint handler in `api_download()`.
3. Support the format in `frontend/src/components/ExportBar.jsx`.
