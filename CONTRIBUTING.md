# Contributing to Relent AI

First off, thank you for considering contributing to **Relent AI**! 🎉

Whether you are fixing a bug, adding support for a new speech model, writing documentation, or improving UI styling, your contributions are welcome.

---

## 📜 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
  - [Fork & Clone](#1-fork--clone)
  - [Backend Setup](#2-backend-setup)
  - [Frontend Setup](#3-frontend-setup)
- [Development Workflow](#development-workflow)
  - [Branch Naming](#branch-naming)
  - [Running Linters & Formatters](#running-linters--formatters)
  - [Running Automated Tests](#running-automated-tests)
  - [Pre-commit Hooks](#pre-commit-hooks)
- [Commit Conventions](#commit-conventions)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Adding New Capabilities](#adding-new-capabilities)

---

## Code of Conduct

All contributors and maintainers agree to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please report any unacceptable behavior to `community@relent.ai`.

---

## Getting Started

### 1. Fork & Clone

Fork the repository to your GitHub account and clone it locally:

```bash
git clone https://github.com/HarshPopat23/Relent.git
cd Relent
```

### 2. Backend Setup

Relent AI requires **Python 3.10+** and [Ollama](https://ollama.com).

```bash
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate virtual environment
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies in editable mode
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ".[dev]"

# 4. Copy environment template
cp .env.example .env

# 5. Pull local Ollama model
ollama pull qwen2.5-coder:3b
```

### 3. Frontend Setup

The frontend is built with **React 19** and **Vite**:

```bash
cd frontend
npm install
npm run dev
```

---

## Development Workflow

### Branch Naming

Create a topic branch with a meaningful prefix:
- `feat/add-indic-whisper-streaming`
- `fix/ffmpeg-padding-overflow`
- `docs/update-troubleshooting-guide`
- `refactor/lazy-import-embeddings`
- `test/add-video-clipper-mock-tests`

### Running Linters & Formatters

We use **Ruff** for high-speed Python linting and code formatting:

```bash
# Check for lint issues
ruff check .

# Automatically fix lint issues
ruff check --fix .

# Check formatting
ruff format --check .

# Auto-format all code
ruff format .
```

### Running Automated Tests

Run the complete test suite locally using `pytest`:

```bash
# Run all unit tests
pytest tests/ -v

# Run with test coverage analysis
pytest tests/ --cov=core --cov=utils

# Run standalone test runner
python run_tests.py
```

### Pre-commit Hooks

Install pre-commit hooks to automatically format and lint files before each commit:

```bash
pre-commit install
```

---

## Commit Conventions

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat(transcriber): add support for whisper-large-v3-turbo`
- `fix(clipper): prevent audio sync drift during concat demux`
- `docs(api): document streaming SSE response format`
- `test(rag): add similarity threshold verification tests`
- `refactor(audio): make static_ffmpeg loader lazy`

---

## Submitting a Pull Request

1. Push your branch to your GitHub fork:
   ```bash
   git push origin feat/your-feature-name
   ```
2. Open a Pull Request on the main repository targeting the `main` branch.
3. Fill out the **[Pull Request Template](.github/pull_request_template.md)** completely.
4. Ensure all CI checks (linting, tests, frontend build) pass green.
5. Maintainers will review your PR and provide constructive feedback!

---

## Adding New Capabilities

### Adding a New Speech-to-Text Engine
1. Implement the transcription wrapper in `core/transcriber.py`.
2. Ensure timestamp normalization outputs `start` and `end` in global seconds.
3. Add corresponding unit tests in `tests/test_transcriber.py`.

### Adding a New LLM Backend
1. Update `get_llm()` in `core/summarizer.py`, `core/extractor.py`, `core/rag_engine.py`, and `core/script_generator.py`.
2. Add environment variable options to `.env.example` and `docs/CONFIGURATION.md`.
