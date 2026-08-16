import asyncio
import os
import sys
import tempfile
import uuid
from io import BytesIO

# Ensure UTF-8 output on Windows consoles
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

from dotenv import load_dotenv
load_dotenv()

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

from core.rag_engine import ask_question
from main import run_pipeline, run_reel_pipeline

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

# In-memory storage for active video session
session_state = {
    "result": None,
    "chat_history": [],
    "last_reel": None,
}

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def clean_pdf_text(text: str) -> str:
    """Make text safe for ReportLab Paragraph rendering."""
    if text is None:
        return ""
    safe = (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )
    return safe.encode("latin-1", "replace").decode("latin-1")


def add_pdf_section(elements, styles, heading: str, content: str) -> None:
    elements.append(Paragraph(clean_pdf_text(heading), styles["Heading2"]))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(clean_pdf_text(content), styles["BodyText"]))
    elements.append(Spacer(1, 14))


def build_meeting_pdf(result: dict, chat_history: list[dict]) -> bytes:
    buffer = BytesIO()
    try:
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("AI Video Intelligence Report", styles["Title"]))
        elements.append(Spacer(1, 16))

        add_pdf_section(elements, styles, "Video Title", result.get("title", ""))
        add_pdf_section(elements, styles, "Subtitle", result.get("subtitle", ""))
        add_pdf_section(elements, styles, "Executive Summary", result.get("summary", ""))
        add_pdf_section(elements, styles, "Action Items", result.get("action_items", ""))
        add_pdf_section(elements, styles, "Key Decisions", result.get("key_decisions", ""))
        add_pdf_section(elements, styles, "Open Questions", result.get("open_questions", ""))

        elements.append(PageBreak())
        add_pdf_section(elements, styles, "Full Transcript", result.get("transcript", ""))

        elements.append(PageBreak())
        elements.append(Paragraph("Chat Conversation", styles["Heading2"]))
        elements.append(Spacer(1, 8))

        if chat_history:
            for index, chat in enumerate(chat_history, start=1):
                question = chat.get("question", "")
                answer = chat.get("answer", "")
                elements.append(Paragraph(f"Question {index}", styles["Heading3"]))
                elements.append(Paragraph(clean_pdf_text(question), styles["BodyText"]))
                elements.append(Spacer(1, 6))
                elements.append(Paragraph("Answer", styles["Heading3"]))
                elements.append(Paragraph(clean_pdf_text(answer), styles["BodyText"]))
                elements.append(Spacer(1, 12))
        else:
            elements.append(Paragraph("No chat conversation recorded.", styles["BodyText"]))

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
    except Exception as e:
        pdf_bytes = b""
    finally:
        buffer.close()

    return pdf_bytes


# ----------------------------------------------------
# API Route Handlers
# ----------------------------------------------------

async def api_health(request):
    return JSONResponse({
        "status": "online",
        "model": OLLAMA_MODEL,
        "base_url": OLLAMA_BASE_URL,
        "has_active_video": session_state["result"] is not None,
    })


async def api_process(request):
    """Process YouTube URL, local file, or multipart file upload."""
    content_type = request.headers.get("content-type", "")
    source = ""
    language = "english"

    if "multipart/form-data" in content_type:
        form = await request.form()
        uploaded_file = form.get("file")
        language = form.get("language", "english")

        if uploaded_file is None:
            return JSONResponse({"error": "No file uploaded"}, status_code=400)

        suffix = os.path.splitext(uploaded_file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            content = await uploaded_file.read()
            tmp_file.write(content)
            source = tmp_file.name
    else:
        try:
            body = await request.json()
            source = body.get("source", "").strip()
            language = body.get("language", "english")
        except Exception:
            return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    if not source:
        return JSONResponse({"error": "Source URL or file path is required."}, status_code=400)

    try:
        # Run blocking video pipeline in worker thread
        result = await asyncio.to_thread(run_pipeline, source, language)
        session_state["result"] = result
        session_state["chat_history"] = []
        session_state["last_reel"] = None

        # Build media URL if video file exists
        video_url = None
        if result.get("video_path") and os.path.exists(result["video_path"]):
            video_name = os.path.basename(result["video_path"])
            video_url = f"/api/media/downloads/{video_name}"

        return JSONResponse({
            "success": True,
            "title": result.get("title", ""),
            "subtitle": result.get("subtitle", ""),
            "summary": result.get("summary", ""),
            "action_items": result.get("action_items", ""),
            "key_decisions": result.get("key_decisions", ""),
            "open_questions": result.get("open_questions", ""),
            "transcript": result.get("transcript", ""),
            "video_url": video_url,
            "segments_count": len(result.get("segments", [])),
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def api_chat(request):
    if not session_state.get("result") or not session_state["result"].get("rag_chain"):
        return JSONResponse({"error": "No video has been processed yet. Please process a video first."}, status_code=400)

    try:
        body = await request.json()
        question = body.get("question", "").strip()
        if not question:
            return JSONResponse({"error": "Question cannot be empty"}, status_code=400)

        rag_chain = session_state["result"]["rag_chain"]
        answer = await asyncio.to_thread(ask_question, rag_chain, question)

        session_state["chat_history"].append({
            "question": question,
            "answer": answer,
        })

        return JSONResponse({
            "question": question,
            "answer": answer,
            "history": session_state["chat_history"],
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def api_reel(request):
    if not session_state.get("result"):
        return JSONResponse({"error": "No video available. Process a video first."}, status_code=400)

    try:
        body = await request.json()
        user_request = body.get("request", "").strip()
        if not user_request:
            return JSONResponse({"error": "Reel prompt description is required."}, status_code=400)

        reel_result = await asyncio.to_thread(run_reel_pipeline, session_state["result"], user_request)

        reel_url = None
        if reel_result.get("reel_path") and os.path.exists(reel_result["reel_path"]):
            filename = os.path.basename(reel_result["reel_path"])
            reel_url = f"/api/media/reels/{filename}"

        session_state["last_reel"] = reel_result

        return JSONResponse({
            "script": reel_result.get("script", ""),
            "reel_url": reel_url,
            "selected_segments": reel_result.get("selected_segments", []),
            "error": reel_result.get("error"),
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def api_download(request):
    format_type = request.path_params.get("format", "summary")
    result = session_state.get("result")

    if not result:
        return JSONResponse({"error": "No processed video found."}, status_code=404)

    if format_type == "summary":
        content = result.get("summary", "")
        return Response(
            content=content,
            media_type="text/plain",
            headers={"Content-Disposition": 'attachment; filename="video_summary.txt"'}
        )
    elif format_type == "transcript":
        content = result.get("transcript", "")
        return Response(
            content=content,
            media_type="text/plain",
            headers={"Content-Disposition": 'attachment; filename="transcript.txt"'}
        )
    elif format_type == "markdown":
        md = f"""# {result.get('title', 'Video Report')}

**{result.get('subtitle', '')}**

## Executive Summary
{result.get('summary', '')}

## Action Items
{result.get('action_items', '')}

## Key Decisions
{result.get('key_decisions', '')}

## Open Questions
{result.get('open_questions', '')}

## Full Transcript
{result.get('transcript', '')}
"""
        return Response(
            content=md,
            media_type="text/markdown",
            headers={"Content-Disposition": 'attachment; filename="video_intelligence_report.md"'}
        )
    elif format_type == "pdf":
        pdf_bytes = build_meeting_pdf(result, session_state.get("chat_history", []))
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="video_intelligence_report.pdf"'}
        )
    else:
        return JSONResponse({"error": f"Unknown format {format_type}"}, status_code=400)


async def api_serve_media(request):
    folder = request.path_params.get("folder")
    filename = request.path_params.get("filename")

    allowed_folders = {"downloads": "downloads", "reels": "reels", "clips": "clips"}
    if folder not in allowed_folders:
        return JSONResponse({"error": "Forbidden"}, status_code=403)

    filepath = os.path.join(allowed_folders[folder], filename)
    if not os.path.exists(filepath):
        return JSONResponse({"error": "File not found"}, status_code=404)

    return FileResponse(filepath, media_type="video/mp4")


# ----------------------------------------------------
# Application Setup
# ----------------------------------------------------

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

routes = [
    Route("/api/health", api_health, methods=["GET"]),
    Route("/api/process", api_process, methods=["POST"]),
    Route("/api/chat", api_chat, methods=["POST"]),
    Route("/api/reel", api_reel, methods=["POST"]),
    Route("/api/download/{format}", api_download, methods=["GET"]),
    Route("/api/media/{folder}/{filename}", api_serve_media, methods=["GET"]),
]

app = Starlette(debug=True, routes=routes, middleware=middleware)


def main():
    """Launch the Relent AI API server."""
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() in ("true", "1")

    print(f"🚀 Relent AI Backend Server starting on http://{host}:{port}")
    uvicorn.run("server:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    main()
