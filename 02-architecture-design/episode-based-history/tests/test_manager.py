"""Tests for episode manager."""

import pytest
from datetime import timedelta

from episode_history.episode import EpisodeStatus
from episode_history.manager import (
    EpisodeManager,
    BoundaryConfig,
    EpisodeBoundary,
)


class TestEpisodeManager:
    """Tests for EpisodeManager class."""

    def test_create_manager(self) -> None:
        """Test manager creation."""
        manager = EpisodeManager()

        assert manager.current is None
        assert len(manager.episodes) == 0

    def test_start_episode(self) -> None:
        """Test starting a new episode."""
        manager = EpisodeManager()

        ep = manager.start_episode("Test Topic")

        assert manager.current is not None
        assert manager.current.topic == "Test Topic"
        assert ep.is_active

    def test_add_message_creates_episode(self) -> None:
        """Test that add_message creates episode if none exists."""
        manager = EpisodeManager()

        msg, boundary = manager.add_message("user", "Hello")

        assert manager.current is not None
        assert manager.current.message_count == 1
        assert boundary is None  # No boundary crossed

    def test_add_message_triggers_size_boundary(self) -> None:
        """Test size-based episode boundary."""
        config = BoundaryConfig(max_messages=3)
        manager = EpisodeManager(config=config)

        # Add messages up to limit
        manager.add_message("user", "Message 1")
        manager.add_message("assistant", "Response 1")
        manager.add_message("user", "Message 2")

        # This should trigger boundary
        msg, boundary = manager.add_message("assistant", "Response 2")

        assert boundary == EpisodeBoundary.SIZE
        assert len(manager.episodes) == 1  # One closed episode

    def test_close_current(self) -> None:
        """Test explicit episode closure."""
        manager = EpisodeManager()
        manager.add_message("user", "Hello")

        ep = manager.close_current(summary="Test summary")

        assert ep is not None
        assert ep.is_closed
        assert ep.summary == "Test summary"
        assert manager.current is None

    def test_close_current_no_episode(self) -> None:
        """Test closing when no current episode."""
        manager = EpisodeManager()

        result = manager.close_current()

        assert result is None

    def test_get_all_episodes(self) -> None:
        """Test getting all episodes including current."""
        manager = EpisodeManager()

        manager.add_message("user", "First")
        manager.close_current()
        manager.add_message("user", "Second")

        all_eps = manager.get_all_episodes()

        assert len(all_eps) == 2
        assert all_eps[0].is_closed
        assert all_eps[1].is_active

    def test_get_recent_episodes(self) -> None:
        """Test getting recent episodes."""
        manager = EpisodeManager()

        for i in range(5):
            manager.start_episode(f"Topic {i}")
            manager.add_message("user", f"Message {i}")
            if i < 4:  # Keep last one open
                manager.close_current()

        recent = manager.get_recent_episodes(3)

        assert len(recent) == 3
        assert recent[-1].topic == "Topic 4"  # Most recent

    def test_get_episodes_by_status(self) -> None:
        """Test filtering by status."""
        manager = EpisodeManager()

        manager.add_message("user", "Msg 1")
        manager.close_current()
        manager.add_message("user", "Msg 2")
        manager.close_current()
        manager.add_message("user", "Msg 3")  # Still active

        closed = manager.get_episodes_by_status(EpisodeStatus.CLOSED)
        active = manager.get_episodes_by_status(EpisodeStatus.ACTIVE)

        assert len(closed) == 2
        assert len(active) == 1

    def test_find_episodes_by_topic(self) -> None:
        """Test topic search."""
        manager = EpisodeManager()

        manager.start_episode("Python Basics")
        manager.add_message("user", "test")
        manager.close_current()

        manager.start_episode("Database Design")
        manager.add_message("user", "test")
        manager.close_current()

        manager.start_episode("Python Advanced")
        manager.add_message("user", "test")

        results = manager.find_episodes_by_topic("Python")

        assert len(results) == 2

    def test_on_episode_closed_callback(self) -> None:
        """Test closure callback."""
        manager = EpisodeManager()
        closed_topics = []

        def callback(ep):
            closed_topics.append(ep.topic)

        manager.on_episode_closed(callback)

        manager.start_episode("Test")
        manager.add_message("user", "Hello")
        manager.close_current()

        assert "Test" in closed_topics

    def test_total_messages(self) -> None:
        """Test total message count."""
        manager = EpisodeManager()

        manager.add_message("user", "1")
        manager.add_message("assistant", "2")
        manager.close_current()
        manager.add_message("user", "3")

        assert manager.get_total_messages() == 3

    def test_topic_extractor(self) -> None:
        """Test topic extraction on episode creation."""
        def extract_topic(content: str) -> str:
            """Simple topic extractor."""
            return content.split()[0] if content else "general"

        manager = EpisodeManager(topic_extractor=extract_topic)

        manager.add_message("user", "Python help needed")

        assert manager.current.topic == "Python"
