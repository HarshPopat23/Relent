"""Integration and unit tests for server.py Starlette REST API endpoints."""

from starlette.testclient import TestClient
from server import app, clean_pdf_text, session_state

try:
    import pytest
    fixture_dec = pytest.fixture
except ImportError:
    def fixture_dec(func):
        return func


@fixture_dec
def client():
    return TestClient(app)


def test_clean_pdf_text():
    """Verify clean_pdf_text escapes XML entities and formats line breaks."""
    assert clean_pdf_text(None) == ""
    assert clean_pdf_text("a & b < c > d\ne") == "a &amp; b &lt; c &gt; d<br/>e"


def test_api_health(client=None):
    """Verify health endpoint response structure."""
    if client is None:
        client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "model" in data


def test_api_process_missing_source(client=None):
    """Verify validation error when no source is supplied."""
    if client is None:
        client = TestClient(app)
    response = client.post("/api/process", json={})
    assert response.status_code == 400
    assert "error" in response.json()


def test_api_chat_no_active_video(client=None):
    """Verify chat returns error when no video is indexed."""
    if client is None:
        client = TestClient(app)
    session_state["result"] = None
    response = client.post("/api/chat", json={"question": "Summarize this"})
    assert response.status_code == 400
    assert "error" in response.json()


def test_api_reel_no_active_video(client=None):
    """Verify reel generation returns error when no video is processed."""
    if client is None:
        client = TestClient(app)
    session_state["result"] = None
    response = client.post("/api/reel", json={"request": "2 min reel"})
    assert response.status_code == 400
    assert "error" in response.json()


def test_api_download_endpoints(client=None, sample_pipeline_result=None):
    """Verify download endpoints for various formats."""
    if client is None:
        client = TestClient(app)
    if sample_pipeline_result is None:
        from tests.conftest import sample_pipeline_result as spr
        sample_pipeline_result = spr()

    # Temporarily set mock result in session
    session_state["result"] = sample_pipeline_result

    # 1. Summary
    res_summary = client.get("/api/download/summary")
    assert res_summary.status_code == 200
    assert "Overview" in res_summary.text

    # 2. Transcript
    res_trans = client.get("/api/download/transcript")
    assert res_trans.status_code == 200
    assert "Welcome to Relent AI" in res_trans.text

    # 3. Markdown
    res_md = client.get("/api/download/markdown")
    assert res_md.status_code == 200
    assert "# Relent AI Launch & Demo" in res_md.text

    # 4. Unknown format
    res_unknown = client.get("/api/download/unknown_format")
    assert res_unknown.status_code == 400

    # Reset
    session_state["result"] = None


def test_api_serve_media_forbidden_and_not_found(client=None):
    """Verify security forbidden and not found handlers on media endpoint."""
    if client is None:
        client = TestClient(app)
    res_forbidden = client.get("/api/media/forbidden_folder/test.mp4")
    assert res_forbidden.status_code == 403

    res_not_found = client.get("/api/media/downloads/non_existent_file_999.mp4")
    assert res_not_found.status_code == 404
