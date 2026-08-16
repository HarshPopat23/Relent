# Relent AI Troubleshooting & FAQ

This guide provides solutions to common issues encountered during setup, video ingestion, transcription, and reel generation.

---

## 🛠️ Common Issues & Resolutions

### 1. `Ollama connection refused` or `Model 'qwen2.5-coder:3b' not found`

**Symptoms:**
- Error trace showing `HTTPConnectionPool(host='localhost', port=11434): Max retries exceeded`.
- `ollama._types.ResponseError: model not found`.

**Resolution:**
1. Ensure the Ollama daemon is actively running:
   ```bash
   ollama serve
   ```
2. Pull the required model:
   ```bash
   ollama pull qwen2.5-coder:3b
   ```
3. Check that your `.env` file specifies `OLLAMA_MODEL=qwen2.5-coder:3b` and `OLLAMA_BASE_URL=http://localhost:11434`.

---

### 2. `FFmpeg not found` or `Executable not found`

**Symptoms:**
- Error trace in `pydub` or `video_clipper.py` mentioning `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`.

**Resolution:**
1. Relent AI bundles `static-ffmpeg` which automatically downloads platform binaries on first run. If your network restricts automated binary downloads:
   - **Windows**: Install via Chocolatey `choco install ffmpeg` or winget `winget install Gyan.FFmpeg`.
   - **Linux (Ubuntu/Debian)**: `sudo apt-get update && sudo apt-get install -y ffmpeg`.
   - **macOS**: `brew install ffmpeg`.
2. Verify by running `ffmpeg -version` in your terminal.

---

### 3. `yt-dlp HTTP Error 429: Too Many Requests` or `Sign in to confirm you’re not a bot`

**Symptoms:**
- YouTube blocks video download requests with HTTP 429 or bot verification prompts.

**Resolution:**
1. Upgrade `yt-dlp` to the latest release:
   ```bash
   pip install --upgrade yt-dlp
   ```
2. Relent AI automatically rotates player clients (`android`, `ios`, `web`). If an IP block persists, download the `.mp4` video locally and pass the local path to Relent AI:
   ```bash
   python main.py --source "path/to/downloaded_video.mp4"
   ```

---

### 4. CUDA Out-of-Memory (OOM) Errors

**Symptoms:**
- `torch.cuda.OutOfMemoryError: CUDA out of memory`.

**Resolution:**
1. Reduce the Whisper model size in `.env`:
   ```dotenv
   WHISPER_MODEL=base
   ```
2. For Ollama LLMs, select a smaller quantized model:
   ```dotenv
   OLLAMA_MODEL=qwen2.5-coder:1.5b
   ```
3. Set CPU fallback in `.env`:
   ```dotenv
   INDICWHISPER_DEVICE=cpu
   ```

---

### 5. Windows Unicode / Character Encoding Errors (`Charmap codec can't encode character`)

**Symptoms:**
- Traceback ending with `UnicodeEncodeError: 'charmap' codec can't encode characters in position ...`.

**Resolution:**
- Relent AI includes `safe_print()` guards and UTF-8 console reconfiguring. Ensure your Windows PowerShell / Command Prompt uses UTF-8:
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  $env:PYTHONIOENCODING = "utf-8"
  ```

---

## ❓ Frequently Asked Questions (FAQ)

### Q: Does Relent AI send my videos to third-party cloud servers?
**A:** No! All transcription (Whisper), embedding generation (`all-MiniLM-L6-v2`), vector indexing (Chroma), and LLM reasoning (Ollama) run 100% locally on your hardware.

### Q: Can I run Relent AI without a GPU?
**A:** Yes. Whisper `small` or `base` and Ollama models like `qwen2.5-coder:3b` or `llama3.2:3b` run efficiently on modern multi-core CPUs.

### Q: How do I export intelligence reports?
**A:** Via the CLI using `--output report.md`, via the React UI export toolbar (PDF, Markdown, TXT), or via the REST endpoint `/api/download/pdf`.
