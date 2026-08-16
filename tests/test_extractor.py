"""Unit tests for core/extractor.py."""

from unittest.mock import patch
from core.extractor import extract_action_items, extract_key_decisions, extract_questions


def test_extractor_empty_guards():
    """Verify fallback messages when transcript is empty."""
    assert extract_action_items("") == "No action items found."
    assert extract_action_items("   ") == "No action items found."
    assert extract_key_decisions("") == "No key decisions found."
    assert extract_questions("") == "No open questions found."


@patch("langchain_core.runnables.base.RunnableSequence.invoke")
def test_extract_action_items_mock(mock_invoke):
    """Verify action item extraction invokes chain."""
    mock_invoke.return_value = "1. Deploy to staging (Owner: Sarah, Deadline: Tomorrow)"
    result = extract_action_items("Sarah agreed to deploy the staging app by tomorrow.")
    assert "Deploy to staging" in result
    assert "Sarah" in result


@patch("langchain_core.runnables.base.RunnableSequence.invoke")
def test_extract_key_decisions_mock(mock_invoke):
    """Verify key decision extraction invokes chain."""
    mock_invoke.return_value = "1. Standardize on Python 3.10+"
    result = extract_key_decisions("The team decided to standardize on Python 3.10+.")
    assert "Standardize on Python 3.10+" in result


@patch("langchain_core.runnables.base.RunnableSequence.invoke")
def test_extract_questions_mock(mock_invoke):
    """Verify questions extraction invokes chain."""
    mock_invoke.return_value = "1. When is the release date?"
    result = extract_questions("Someone asked what the release date would be.")
    assert "release date" in result
