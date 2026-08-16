"""Unit tests for core/extractor.py."""

from unittest.mock import MagicMock, patch

from core.extractor import extract_action_items, extract_key_decisions, extract_questions


def test_extractor_empty_guards():
    """Verify fallback messages when transcript is empty."""
    assert extract_action_items("") == "No action items found."
    assert extract_action_items("   ") == "No action items found."
    assert extract_key_decisions("") == "No key decisions found."
    assert extract_questions("") == "No open questions found."


@patch("core.extractor.build_chain")
def test_extract_action_items_mock(mock_build):
    """Verify action item extraction invokes chain."""
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "1. Deploy to staging (Owner: Sarah, Deadline: Tomorrow)"
    mock_build.return_value = mock_chain

    result = extract_action_items("Sarah agreed to deploy the staging app by tomorrow.")
    assert "Deploy to staging" in result
    assert "Sarah" in result


@patch("core.extractor.build_chain")
def test_extract_key_decisions_mock(mock_build):
    """Verify key decision extraction invokes chain."""
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "1. Standardize on Python 3.10+"
    mock_build.return_value = mock_chain

    result = extract_key_decisions("The team decided to standardize on Python 3.10+.")
    assert "Standardize on Python 3.10+" in result


@patch("core.extractor.build_chain")
def test_extract_questions_mock(mock_build):
    """Verify questions extraction invokes chain."""
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "1. When is the release date?"
    mock_build.return_value = mock_chain

    result = extract_questions("Someone asked what the release date would be.")
    assert "release date" in result
