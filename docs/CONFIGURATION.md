# Relent AI Configuration & Tuning Guide

This document details hardware acceleration, model selection, and performance optimization for **Relent AI**.

---

## 1. LLM Model Selection & Performance

Relent AI connects to any model hosted on your local [Ollama](https://ollama.com) instance.

| Model | Size | Recommended RAM/VRAM | Strengths | Speed |
| :--- | :--- | :--- | :--- | :--- |
| **`qwen2.5-coder:3b`** *(Default)* | 1.9 GB | 4 GB | High instruction following, fast summarization, minimal memory footprint | ⚡⚡⚡⚡⚡ (Fastest) |
| **`qwen2.5:7b-instruct`** | 4.7 GB | 8 GB | Superior reasoning, detailed meeting summaries, nuanced question answering | ⚡⚡⚡⚡ (High Quality) |
| **`llama3.2:3b`** | 2.0 GB | 4 GB | Lightweight, concise summaries | ⚡⚡⚡⚡⚡ |
| **`llama3.1:8b`** | 4.9 GB | 8 GB | Robust semantic understanding and complex multi-turn RAG chat | ⚡⚡⚡ |
| **`mistral:7b`** | 4.1 GB | 8 GB | Strong general reasoning and action extraction | ⚡⚡⚡ |

To switch models, set `OLLAMA_MODEL` in `.env`:
```ini
OLLAMA_MODEL=qwen2.5:7b-instruct
```

---

## 2. Whisper Model Options

The speech-to-text engine supports all OpenAI Whisper checkpoints:

| Model | Parameters | Required VRAM / RAM | Relative Speed | Word Error Rate (WER) |
| :--- | :--- | :--- | :--- | :--- |
| `tiny` | 39 M | ~1 GB | ~10x | Moderate |
| `base` | 74 M | ~1 GB | ~7x | Good |
| **`small`** *(Default)* | 244 M | ~2 GB | ~4x | **Optimal Balance** |
| `medium` | 769 M | ~5 GB | ~2x | High Accuracy |
| `large-v3` | 1550 M | ~10 GB | 1x | Maximum Accuracy |

Configure model size in `.env`:
```ini
WHISPER_MODEL=small
```

---

## 3. Hardware Acceleration & Memory Management

### GPU Acceleration (NVIDIA CUDA)
If an NVIDIA GPU with sufficient VRAM (6 GB+) is available, Whisper and Ollama will automatically leverage CUDA.

### CPU Fallback & Low-Memory Environments
If running on systems with shared GPU memory or limited VRAM:
1. Prevent CUDA out-of-memory errors in Ollama by starting Ollama with CPU mode:
   ```bash
   # Windows PowerShell
   $env:OLLAMA_NUM_GPU="0"; ollama serve

   # Linux / macOS
   OLLAMA_NUM_GPU=0 ollama serve
   ```
2. In `.env`, ensure Whisper uses CPU if VRAM is constrained:
   ```ini
   WHISPER_MODEL=small
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
