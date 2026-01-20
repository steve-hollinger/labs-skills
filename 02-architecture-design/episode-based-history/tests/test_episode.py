"""Tests for episode data structures."""

import pytest
from datetime import datetime, timedelta

from episode_history.episode import Message, Episode, EpisodeStatus


class TestMessage:
    """Tests for Message class."""

    def test_create_message(self) -> None:
        """Test basic message creation."""
        msg = Message(role="user", content="Hello")

        assert msg.role == "user"
        assert msg.content == "Hello"
        assert isinstance(msg.timestamp, datetime)

    def test_message_token_estimate(self) -> None:
        """Test token estimation."""
        msg = Message(role="user", content="a" * 100)  # 100 chars

        # Rough estimate: ~4 chars per token
        assert msg.token_estimate == 25

    def test_message_to_dict(self) -> None:
        """Test message serialization."""
        msg = Message(
            role="assistant",
            content="Hello",
            metadata={"tokens": 10},
        )

        data = msg.to_dict()

        assert data["role"] == "assistant"
        assert data["content"] == "Hello"
        assert data["metadata"]["tokens"] == 10
        assert "timestamp" in data

    def test_message_from_dict(self) -> None:
        """Test message deserialization."""
        data = {
            "role": "user",
            "content": "Test",
            "timestamp": "2024-01-01T10:00:00",
            "metadata": {},
        }

        msg = Message.from_dict(data)

        assert msg.role == "user"
        assert msg.content == "Test"


class TestEpisode:
    """Tests for Episode class."""

    def test_create_episode(self) -> None:
        """Test basic episode creation."""
        ep = Episode(topic="Test Topic")

        assert ep.topic == "Test Topic"
        assert ep.is_active
        assert not ep.is_closed
        assert ep.message_count == 0

    def test_add_message(self) -> None:
        """Test adding messages to episode."""
        ep = Episode()

        ep.add_message(Message(role="user", content="Hello"))
        ep.add_message(Message(role="assistant", content="Hi there"))

        assert ep.message_count == 2
        assert ep.messages[0].content == "Hello"

    def test_add_message_to_closed_raises(self) -> None:
        """Test that adding to closed episode raises."""
        ep = Episode()
        ep.close()

        with pytest.raises(ValueError, match="closed"):
            ep.add_message(Message(role="user", content="test"))

    def test_close_episode(self) -> None:
        """Test closing an episode."""
        ep = Episode()
        ep.add_message(Message(role="user", content="Hello"))

        ep.close(summary="Test summary")

        assert ep.is_closed
        assert not ep.is_active
        assert ep.status == EpisodeStatus.CLOSED
        assert ep.closed_at is not None
        assert ep.summary == "Test summary"

    def test_archive_episode(self) -> None:
        """Test archiving an episode."""
        ep = Episode()
        ep.close()
        ep.archive()

        assert ep.status == EpisodeStatus.ARCHIVED

    def test_episode_age(self) -> None:
        """Test episode age calculation."""
        ep = Episode()

        # Age should be very small (just created)
        assert ep.age < timedelta(seconds=1)

    def test_total_tokens(self) -> None:
        """Test total token calculation."""
        ep = Episode()
        ep.add_message(Message(role="user", content="a" * 40))  # ~10 tokens
        ep.add_message(Message(role="assistant", content="b" * 80))  # ~20 tokens

        assert ep.total_tokens == 30

    def test_get_context_string_active(self) -> None:
        """Test context string for active episode."""
        ep = Episode(topic="Test")
        ep.add_message(Message(role="user", content="Hello"))
        ep.add_message(Message(role="assistant", content="Hi"))

        context = ep.get_context_string()

        assert "Test" in context
        assert "user: Hello" in context
        assert "assistant: Hi" in context

    def test_get_context_string_with_summary(self) -> None:
        """Test context string uses summary for closed."""
        ep = Episode(topic="Test")
        ep.add_message(Message(role="user", content="Hello"))
        ep.close(summary="Short summary")

        context = ep.get_context_string(use_summary=True)

        assert "Previous conversation" in context
        assert "Short summary" in context
        assert "Hello" not in context

    def test_episode_serialization(self) -> None:
        """Test episode to_dict and from_dict."""
        ep = Episode(topic="Test", metadata={"key": "value"})
        ep.add_message(Message(role="user", content="Hello"))
        ep.close(summary="Summary")

        data = ep.to_dict()
        restored = Episode.from_dict(data)

        assert restored.id == ep.id
        assert restored.topic == ep.topic
        assert restored.message_count == 1
        assert restored.summary == "Summary"
        assert restored.metadata["key"] == "value"
        assert restored.status == EpisodeStatus.CLOSED
