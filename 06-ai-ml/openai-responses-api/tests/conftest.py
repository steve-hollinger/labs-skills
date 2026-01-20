"""Pytest configuration for OpenAI Responses API tests."""

import pytest


@pytest.fixture(autouse=True)
def mock_openai_key(monkeypatch):
    """Ensure OPENAI_API_KEY is not set during tests."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


@pytest.fixture
def sample_messages():
    """Sample messages for testing."""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
