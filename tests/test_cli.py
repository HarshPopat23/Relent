"""Unit tests for CLI interface (main.py)."""

from unittest.mock import MagicMock, patch

from core import __version__
from main import format_markdown_report, main


def test_format_markdown_report(sample_pipeline_result=None):
    """Verify markdown intelligence report structure."""
    if sample_pipeline_result is None:
        from tests.conftest import sample_pipeline_result as spr
        sample_pipeline_result = spr()

    report = format_markdown_report(sample_pipeline_result)
    assert "# Relent AI Launch & Demo" in report
    assert "## 📋 Executive Summary" in report
    assert "## ✅ Action Items" in report
    assert "## 🔑 Key Decisions" in report
    assert "## ❓ Open Questions" in report
    assert "## 📝 Full Transcript" in report


def test_cli_version():
    """Verify --version flag output."""
    with patch("sys.argv", ["main.py", "--version"]):
        try:
            main()
        except SystemExit as exc:
            assert exc.code == 0


@patch("main.run_pipeline")
def test_cli_json_mode(mock_run):
    """Verify non-interactive --json execution."""
    from tests.conftest import sample_pipeline_result
    mock_run.return_value = sample_pipeline_result()

    with patch("sys.argv", ["main.py", "--source", "https://youtu.be/test", "--json"]):
        main()

    mock_run.assert_called_once()
