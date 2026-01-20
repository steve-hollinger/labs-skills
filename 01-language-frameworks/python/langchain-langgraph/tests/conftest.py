"""Pytest configuration and fixtures for LangChain/LangGraph tests."""

import os
import pytest


@pytest.fixture(autouse=True)
def mock_openai_key(monkeypatch):
    """Ensure OPENAI_API_KEY is not set during tests to use mock implementations."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


@pytest.fixture
def sample_documents():
    """Provide sample documents for testing."""
    return {
        "technical": """
            The new software architecture uses microservices and containerization.
            Our programming team implemented the algorithm using Python code.
            The system processes data through multiple pipeline stages.
        """,
        "business": """
            Q3 revenue exceeded expectations with strong market performance.
            Sales grew 15% and profit margins improved significantly.
            The company plans to expand into new markets next quarter.
        """,
        "general": """
            The weather today was beautiful with clear blue skies.
            Many people enjoyed walking in the park and having picnics.
            It was a perfect day for outdoor activities.
        """,
        "short": "Hello",
        "empty": "   ",
    }


@pytest.fixture
def sample_messages():
    """Provide sample messages for conversation tests."""
    return [
        "Hello! My name is Alice.",
        "I like programming and coffee.",
        "What's my name?",
    ]
