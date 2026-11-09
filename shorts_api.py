"""Local-only Shorts Studio endpoints."""

import asyncio
import logging
import os
from pathlib import Path
from threading import Lock
from urllib.parse import urlsplit
from uuid import uuid4

from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Route

from core.shorts import SHORT_COUNT, ShortsError, generate_shorts, youtube_url

SHORTS_DIR = Path("shorts_output")
_STUDIO_LOCK = Lock()
_LOGGER = logging.getLogger(__name__)
_LOOPBACK = {"localhost", "127.0.0.1", "::1"}


def _local_request(request) -> bool:
    origin = request.headers.get("origin")
    try:
        host = request.url.hostname
        return host in _LOOPBACK and (not origin or urlsplit(origin).hostname in _LOOPBACK)
    except ValueError:
        return False


def _error(message, status):
    return JSONResponse({"error": message}, status_code=status)


def _run_batch(url, key):
    if not _STUDIO_LOCK.acquire(blocking=False):
        return _error("A shorts batch is already running. Wait for it to finish.", 409)
    try:
        return JSONResponse(generate_shorts(url, key, SHORTS_DIR, str(uuid4())), status_code=201)
    except ShortsError as exc:
        return _error(str(exc), 422)
    except OSError:
        _LOGGER.exception("Could not read or write Shorts Studio files")
        return _error("Check disk space and write access to the Shorts Studio output folder.", 500)
    finally:
        _STUDIO_LOCK.release()


async def create_shorts(request):
    if not _local_request(request):
        return _error("The Shorts Studio is available on localhost.", 403)
    if request.headers.get("content-type", "").split(";")[0] != "application/json":
        return _error("Send the YouTube link as JSON.", 415)
    try:
        body = await request.json()
        url = youtube_url(body["url"])
    except (AttributeError, KeyError, TypeError, ValueError):
        return _error("Paste an HTTPS link to one YouTube video.", 400)
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        return _error("Set GROQ_API_KEY in the backend .env file and restart Relent.", 503)
    return await asyncio.to_thread(_run_batch, url, key)


async def short_file(request):
    if not _local_request(request):
        return _error("The Shorts Studio is available on localhost.", 403)
    batch = SHORTS_DIR / str(request.path_params["batch"])
    index = request.path_params.get("index")
    if index is None:
        path = batch / "metadata.json"
        options = {"media_type": "application/json", "filename": "shorts-metadata.json"}
    elif 1 <= index <= SHORT_COUNT:
        path = batch / f"short-{index:02}.mp4"
        options = {"media_type": "video/mp4"}
        if request.query_params.get("download") == "1":
            options["filename"] = path.name
    else:
        return _error("Short not found.", 404)
    if not path.is_file():
        return _error("Short not found.", 404)
    return FileResponse(path, **options)


shorts_routes = [
    Route("/api/shorts", create_shorts, methods=["POST"]),
    Route("/api/shorts/{batch:uuid}/metadata", short_file),
    Route("/api/shorts/{batch:uuid}/{index:int}", short_file),
]
