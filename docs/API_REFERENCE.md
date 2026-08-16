# Relent AI REST API Reference

The backend exposes a high-performance asynchronous REST API powered by **Starlette** and **Uvicorn** on `http://127.0.0.1:8000`.

---

## 1. Health & Status

### `GET /api/health`
Checks backend status, connected LLM model, and active video state.

#### Response `200 OK`
```json
{
  "status": "online",
  "model": "qwen2.5:3b-instruct",
  "base_url": "http://localhost:11434",
  "has_active_video": true
}
```

---

## 2. Video Processing

### `POST /api/process`
Ingests and processes a video from a YouTube URL, local path, or file upload.

#### Request (JSON)
```json
{
  "source": "https://youtu.be/11Y3B33oCLE",
  "language": "english"
}
```

#### Request (Multipart Form Data)
- `file`: File blob (`.mp4`, `.mov`, `.wav`, `.mp3`)
- `language`: `"english"` or `"hinglish"`

#### Response `200 OK`
```json
{
  "success": true,
  "title": "NVIDIA Keynote 2026",
  "subtitle": "Overview of Next-Gen Accelerated Computing and AI Infrastructure",
  "summary": "### Overview\nJensen Huang presented...",
  "action_items": "1. Deploy NIM microservices...",
  "key_decisions": "1. Transition data centers to Blackwell architecture...",
  "open_questions": "1. Expected timeline for quantum acceleration...",
  "transcript": "Full text transcript...",
  "video_url": "/api/media/downloads/11Y3B33oCLE.mp4",
  "segments_count": 142
}
```

#### Response `400 / 500 Error`
```json
{
  "error": "Source URL or file path is required."
}
```

---

## 3. Interactive RAG Chat

### `POST /api/chat`
Ask questions against the currently indexed video transcript.

#### Request (JSON)
```json
{
  "question": "What is the key takeaway regarding AI inference performance?"
}
```

#### Response `200 OK`
```json
{
  "question": "What is the key takeaway regarding AI inference performance?",
  "answer": "The speaker emphasized a 30x increase in real-time inference throughput using FP4 tensor cores...",
  "history": [
    {
      "question": "...",
      "answer": "..."
    }
  ]
}
```

---

## 4. AI Reel Generation

### `POST /api/reel`
Generate a tailored highlight reel from the video based on a prompt.

#### Request (JSON)
```json
{
  "request": "Generate a 2-minute reel focusing on the product announcement"
}
```

#### Response `200 OK`
```json
{
  "script": "00:00:15 - 00:01:05: Today we introduce the new platform...\n00:04:20 - 00:05:30: Here are the benchmark metrics...",
  "reel_url": "/api/media/reels/reel_a8d3e2f9.mp4",
  "selected_segments": [
    {
      "id": 4,
      "start": 15.0,
      "end": 65.0,
      "text": "Today we introduce..."
    }
  ],
  "error": null
}
```

---

## 5. Intelligence Report Export

### `GET /api/download/{format}`
Download intelligence output in various file formats.

#### Path Parameters
- `format`: `pdf` | `markdown` | `summary` | `transcript`

#### Response
- `Content-Type`: `application/pdf`, `text/markdown`, or `text/plain`
- `Content-Disposition`: `attachment; filename="video_intelligence_report.pdf"`

---

## 6. Media Streaming

### `GET /api/media/{folder}/{filename}`
Streams video and clip assets directly to the web player.

#### Path Parameters
- `folder`: `downloads` | `clips` | `reels`
- `filename`: e.g. `11Y3B33oCLE.mp4`, `reel_abc123.mp4`

#### Response
- `Content-Type`: `video/mp4`
