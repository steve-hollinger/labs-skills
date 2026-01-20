"""Exercise 1: Implement Episode Manager.

Build a class to manage the complete episode lifecycle including
creation, boundaries, and archival.

Requirements:
1. Create a ConversationManager class that:
   - Tracks the current active episode
   - Maintains a list of closed episodes
   - Automatically creates new episodes when boundaries are crossed
   - Supports both time and size boundaries
   - Provides methods to query history

Methods to implement:
- __init__(max_messages, time_gap_minutes)
- send_message(role, content) -> tuple[Message, bool]  # Returns (msg, is_new_episode)
- get_history(max_episodes) -> list[Episode]
- search(query) -> list[Episode]
- get_stats() -> dict  # Total messages, episodes, etc.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from episode_history.episode import Episode, Message


@dataclass
class ManagerStats:
    """Statistics about the conversation manager."""

    total_episodes: int
    total_messages: int
    active_episode_messages: int
    oldest_episode_age: timedelta | None
    average_episode_length: float


class ConversationManager:
    """Manager for conversation episodes.

    TODO: Implement this class

    The manager should:
    - Create new episodes automatically based on boundaries
    - Track both size (max_messages) and time (gap between messages) boundaries
    - Provide query methods for history
    - Calculate statistics
    """

    def __init__(
        self,
        max_messages: int = 20,
        time_gap_minutes: int = 60,
    ) -> None:
        """Initialize the manager.

        Args:
            max_messages: Maximum messages per episode.
            time_gap_minutes: Time gap (minutes) that triggers new episode.
        """
        # Your implementation here
        raise NotImplementedError("Implement __init__")

    def send_message(self, role: str, content: str) -> tuple[Message, bool]:
        """Send a message, creating new episode if needed.

        Args:
            role: Message role (user/assistant).
            content: Message content.

        Returns:
            Tuple of (message, is_new_episode).

        Hints:
        - Check if current episode exists
        - Check size boundary
        - Check time boundary (time since last message)
        - Create new episode if any boundary crossed
        """
        # Your implementation here
        raise NotImplementedError("Implement send_message")

    def get_history(self, max_episodes: int = 10) -> list[Episode]:
        """Get recent conversation history.

        Args:
            max_episodes: Maximum episodes to return.

        Returns:
            List of recent episodes (newest last).
        """
        # Your implementation here
        raise NotImplementedError("Implement get_history")

    def search(self, query: str) -> list[Episode]:
        """Search episodes by content.

        Args:
            query: Search query.

        Returns:
            Episodes matching the query.

        Hints:
        - Search in topic
        - Search in message content
        - Search in summary (if exists)
        """
        # Your implementation here
        raise NotImplementedError("Implement search")

    def get_stats(self) -> ManagerStats:
        """Get conversation statistics.

        Returns:
            ManagerStats with various metrics.
        """
        # Your implementation here
        raise NotImplementedError("Implement get_stats")


# Test cases
def test_basic_usage() -> None:
    """Test basic manager usage."""
    manager = ConversationManager(max_messages=5)

    # Send some messages
    msg1, new1 = manager.send_message("user", "Hello!")
    msg2, new2 = manager.send_message("assistant", "Hi there!")

    assert msg1.content == "Hello!"
    assert new1 is True  # First message creates episode
    assert new2 is False  # Same episode

    history = manager.get_history()
    assert len(history) == 1
    print("Basic usage test passed!")


def test_size_boundary() -> None:
    """Test that size boundary creates new episode."""
    manager = ConversationManager(max_messages=3)

    # Fill first episode
    for i in range(3):
        manager.send_message("user", f"Message {i}")

    # This should create new episode
    _, is_new = manager.send_message("user", "New episode message")
    assert is_new is True

    history = manager.get_history()
    assert len(history) == 2
    print("Size boundary test passed!")


def test_search() -> None:
    """Test episode search."""
    manager = ConversationManager()

    manager.send_message("user", "Tell me about Python")
    manager.send_message("assistant", "Python is a programming language")

    results = manager.search("Python")
    assert len(results) == 1
    print("Search test passed!")


def test_stats() -> None:
    """Test statistics calculation."""
    manager = ConversationManager()

    manager.send_message("user", "Hello")
    manager.send_message("assistant", "Hi")
    manager.send_message("user", "Goodbye")

    stats = manager.get_stats()
    assert stats.total_messages == 3
    assert stats.total_episodes == 1
    print("Stats test passed!")


if __name__ == "__main__":
    test_basic_usage()
    test_size_boundary()
    test_search()
    test_stats()
    print("\nAll tests passed!")
