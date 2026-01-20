"""Exercise 1 Solution: Episode Manager Implementation."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from episode_history.episode import Episode, Message, EpisodeStatus


@dataclass
class ManagerStats:
    """Statistics about the conversation manager."""

    total_episodes: int
    total_messages: int
    active_episode_messages: int
    oldest_episode_age: timedelta | None
    average_episode_length: float


class ConversationManager:
    """Manager for conversation episodes."""

    def __init__(
        self,
        max_messages: int = 20,
        time_gap_minutes: int = 60,
    ) -> None:
        """Initialize the manager."""
        self.max_messages = max_messages
        self.time_gap = timedelta(minutes=time_gap_minutes)
        self.episodes: list[Episode] = []
        self.current: Episode | None = None

    def send_message(self, role: str, content: str) -> tuple[Message, bool]:
        """Send a message, creating new episode if needed."""
        message = Message(role=role, content=content)
        is_new_episode = False

        # Check if we need a new episode
        if self._should_create_episode(message):
            self._close_current()
            self.current = Episode(topic=self._extract_topic(content))
            is_new_episode = True

        self.current.add_message(message)
        return message, is_new_episode

    def _should_create_episode(self, message: Message) -> bool:
        """Check if a new episode should be created."""
        if self.current is None:
            return True

        # Size boundary
        if self.current.message_count >= self.max_messages:
            return True

        # Time boundary
        if self.current.messages:
            last_time = self.current.messages[-1].timestamp
            if message.timestamp - last_time > self.time_gap:
                return True

        return False

    def _close_current(self) -> None:
        """Close the current episode if exists."""
        if self.current and self.current.messages:
            self.current.close(summary=self._generate_summary(self.current))
            self.episodes.append(self.current)
            self.current = None

    def _extract_topic(self, content: str) -> str:
        """Extract topic from message content."""
        # Simple: use first few words
        words = content.split()[:5]
        return " ".join(words) if words else "general"

    def _generate_summary(self, episode: Episode) -> str:
        """Generate a simple summary for an episode."""
        if not episode.messages:
            return "Empty conversation"

        first_user = None
        for msg in episode.messages:
            if msg.role == "user":
                first_user = msg.content
                break

        if first_user:
            return f"Discussion about: {first_user[:100]}"
        return f"Conversation with {episode.message_count} messages"

    def get_history(self, max_episodes: int = 10) -> list[Episode]:
        """Get recent conversation history."""
        all_episodes = self.episodes.copy()
        if self.current:
            all_episodes.append(self.current)

        return all_episodes[-max_episodes:]

    def search(self, query: str) -> list[Episode]:
        """Search episodes by content."""
        query_lower = query.lower()
        results = []

        for episode in self.get_history(100):  # Search all
            # Search in topic
            if query_lower in episode.topic.lower():
                results.append(episode)
                continue

            # Search in summary
            if episode.summary and query_lower in episode.summary.lower():
                results.append(episode)
                continue

            # Search in messages
            for msg in episode.messages:
                if query_lower in msg.content.lower():
                    results.append(episode)
                    break

        return results

    def get_stats(self) -> ManagerStats:
        """Get conversation statistics."""
        all_episodes = self.get_history(1000)

        total_messages = sum(ep.message_count for ep in all_episodes)
        active_messages = self.current.message_count if self.current else 0

        oldest_age = None
        if all_episodes:
            oldest_age = datetime.now() - all_episodes[0].created_at

        avg_length = total_messages / len(all_episodes) if all_episodes else 0.0

        return ManagerStats(
            total_episodes=len(all_episodes),
            total_messages=total_messages,
            active_episode_messages=active_messages,
            oldest_episode_age=oldest_age,
            average_episode_length=avg_length,
        )


# Test cases
def test_basic_usage() -> None:
    """Test basic manager usage."""
    manager = ConversationManager(max_messages=5)

    msg1, new1 = manager.send_message("user", "Hello!")
    msg2, new2 = manager.send_message("assistant", "Hi there!")

    assert msg1.content == "Hello!"
    assert new1 is True
    assert new2 is False

    history = manager.get_history()
    assert len(history) == 1
    print("Basic usage test passed!")


def test_size_boundary() -> None:
    """Test that size boundary creates new episode."""
    manager = ConversationManager(max_messages=3)

    for i in range(3):
        manager.send_message("user", f"Message {i}")

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
