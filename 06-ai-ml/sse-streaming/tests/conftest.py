"""Pytest configuration for SSE Streaming tests."""

import pytest


@pytest.fixture(autouse=True)
def mock_openai_key(monkeypatch):
    """Ensure OPENAI_API_KEY is not set during tests."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
