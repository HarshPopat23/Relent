# Relent AI Configuration & Tuning Guide

This document details hardware acceleration, model selection, and performance optimization for **Relent AI**.

---

## 1. LLM Model Selection & Performance

Relent AI connects to any model hosted on your local [Ollama](https://ollama.com) instance with **automatic GPU layer offloading**.

| Model | Size | Recommended RAM/VRAM | Strengths | Speed |
| :--- | :--- | :--- | :--- | :--- |
| **`qwen2.5:3b-instruct`** *(Recommended)* | 1.9 GB | 4 GB | High instruction following, fast summarization, minimal memory footprint | ⚡⚡⚡⚡⚡ (Fastest) |
| **`qwen2.5:7b-instruct`** | 4.7 GB | 8 GB | Superior reasoning, detailed meeting summaries, nuanced question answering | ⚡⚡⚡⚡ (High Quality) |
| **`llama3.2:3b`** | 2.0 GB | 4 GB | Lightweight, concise summaries, 128k context support | ⚡⚡⚡⚡⚡ |
| **`llama3.1:8b`** | 4.9 GB | 8 GB | Robust semantic understanding and complex multi-turn RAG chat | ⚡⚡⚡ |
| **`mistral:7b`** | 4.1 GB | 8 GB | Strong general reasoning and action extraction | ⚡⚡⚡ |

To switch models, set `OLLAMA_MODEL` in `.env`:
```ini
OLLAMA_MODEL=qwen2.5:3b-instruct
```

---

## 2. Faster-Whisper Speech-to-Text & Quantization

Relent AI defaults to **Faster-Whisper (CTranslate2)** with 8-bit `int8` quantization for up to **6x faster transcription** and ~50% reduced RAM footprint compared to standard PyTorch Whisper.

| Model Checkpoint | Parameters | Required VRAM / RAM | Relative Speed | Word Error Rate (WER) |
| :--- | :--- | :--- | :--- | :--- |
| `tiny` | 39 M | ~0.5 GB | ~15x | Moderate |
| `base` | 74 M | ~0.7 GB | ~10x | Good |
| **`small`** *(Default)* | 244 M | ~1.0 GB | **~6x (int8)** | **Optimal Balance** |
| `medium` | 769 M | ~2.5 GB | ~3x | High Accuracy |
| `large-v3-turbo` | 808 M | ~2.0 GB | ~4x | Maximum Accuracy |
| `large-v3` | 1550 M | ~4.5 GB | 1x | Highest Precision |

Configure backend and compute quantization in `.env`:
```ini
WHISPER_MODEL=small
WHISPER_BACKEND=auto         # Options: auto, faster-whisper, whisper
WHISPER_COMPUTE_TYPE=int8    # Options: int8 (CPU default), float16 (CUDA default), int8_float16
```

---

## 3. Hardware Acceleration & Dynamic GPU Auto-Detection

### GPU Acceleration (NVIDIA CUDA)
If an NVIDIA GPU is present, Relent AI automatically detects CUDA and assigns:
- **Whisper**: Uses `device="cuda"` with `float16` or `int8_float16` compute type.
- **IndicWhisper**: Uses `device="cuda:0"`.
- **Ollama**: Automatically offloads 100% of LLM transformer layers to GPU VRAM.

### CPU Fallback & Low-Memory Environments
If running on systems with shared GPU memory or limited VRAM:
1. Prevent CUDA out-of-memory errors by forcing CPU mode in `.env`:
   ```ini
   OLLAMA_NUM_GPU=0
   WHISPER_COMPUTE_TYPE=int8
   ```
2. Or start Ollama with CPU mode:
   ```bash
   # Windows PowerShell
   $env:OLLAMA_NUM_GPU="0"; ollama serve

   # Linux / macOS
   OLLAMA_NUM_GPU=0 ollama serve
   ```

---

## 4. Vector Store & Embedding Tuning

Relent AI defaults to `sentence-transformers/all-MiniLM-L6-v2` for generating embeddings.

- **Chunk Size**: 500 characters
- **Chunk Overlap**: 50 characters
- **Top-k Retrieval**: 4 documents
- **Distance Metric**: Cosine similarity

To customize vector database storage directory:
```ini
CHROMA_PERSIST_DIR=vector_db
```

---

## 5. Video Reel Clipping Acceleration

Relent AI uses zero-reencoding **stream-copy (`-c copy`)** and **`-preset ultrafast`** for near-instant highlight clip cutting and stitching.

| Mode | Speed | Re-encoding | Behavior |
| :--- | :--- | :--- | :--- |
| **`copy`** *(Default)* | ⚡⚡⚡⚡⚡ (< 0.1s/clip) | None (Stream Copy) | Instant zero-CPU copy with automatic fallback to ultrafast on non-aligned keyframes |
| **`ultrafast`** | ⚡⚡⚡⚡ (~ 1s/clip) | Fast libx264 | Frame-accurate cut with ultrafast CPU/GPU encoder preset |

Configure clipping mode in `.env`:
```ini
REEL_CLIP_MODE=copy    # Options: copy (default), ultrafast
```
