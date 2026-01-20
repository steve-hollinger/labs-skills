"""Episode lifecycle management."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Callable

from episode_history.episode import Episode, Message, EpisodeStatus


class EpisodeBoundary(Enum):
    """Types of episode boundaries."""

    SIZE = auto()  # Maximum messages reached
    TIME = auto()  # Time gap exceeded
    TOPIC = auto()  # Topic changed
    EXPLICIT = auto()  # Explicitly closed


@dataclass
class BoundaryConfig:
    """Configuration for episode boundaries.

    Attributes:
        max_messages: Maximum messages per episode.
        max_tokens: Maximum tokens per episode.
        time_gap: Maximum time between messages.
        topic_similarity_threshold: Minimum similarity to stay in same topic.
    """

    max_messages: int = 20
    max_tokens: int = 3000
    time_gap: timedelta = field(default_factory=lambda: timedelta(hours=1))
    topic_similarity_threshold: float = 0.7


TopicExtractor = Callable[[str], str]
SimilarityChecker = Callable[[str, str], float]


class EpisodeManager:
    """Manages episode lifecycle including creation, boundaries, and closure.

    Attributes:
        config: Boundary configuration.
        episodes: List of all episodes (including closed).
        current: Currently active episode (if any).
    """

    def __init__(
        self,
        config: BoundaryConfig | None = None,
        topic_extractor: TopicExtractor | None = None,
        similarity_checker: SimilarityChecker | None = None,
    ) -> None:
        """Initialize the episode manager.

        Args:
            config: Boundary configuration.
            topic_extractor: Function to extract topic from message.
            similarity_checker: Function to check topic similarity.
        """
        self.config = config or BoundaryConfig()
        self._topic_extractor = topic_extractor
        self._similarity_checker = similarity_checker
        self.episodes: list[Episode] = []
        self.current: Episode | None = None
        self._on_episode_closed: list[Callable[[Episode], None]] = []

    def on_episode_closed(self, callback: Callable[[Episode], None]) -> None:
        """Register callback for when episodes close.

        Args:
            callback: Function to call with closed episode.
        """
        self._on_episode_closed.append(callback)

    def start_episode(self, topic: str = "general") -> Episode:
        """Start a new episode.

        Args:
            topic: Topic for the new episode.

        Returns:
            The newly created episode.
        """
        self.current = Episode(topic=topic)
        return self.current

    def add_message(
        self,
        role: str,
        content: str,
        metadata: dict | None = None,
    ) -> tuple[Message, EpisodeBoundary | None]:
        """Add a message, handling boundaries automatically.

        Args:
            role: Message role (user/assistant).
            content: Message content.
            metadata: Optional message metadata.

        Returns:
            Tuple of (added message, boundary type if new episode created).
        """
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {},
        )

        # Check if we need a new episode
        boundary = self._check_boundaries(message)

        if boundary or not self.current:
            if self.current:
                self._close_current(boundary or EpisodeBoundary.EXPLICIT)

            # Extract topic for new episode
            topic = "general"
            if self._topic_extractor:
                topic = self._topic_extractor(content)
            self.start_episode(topic)

        self.current.add_message(message)
        return message, boundary

    def close_current(self, summary: str | None = None) -> Episode | None:
        """Explicitly close the current episode.

        Args:
            summary: Optional summary for the episode.

        Returns:
            The closed episode, or None if no active episode.
        """
        if not self.current:
            return None
        return self._close_current(EpisodeBoundary.EXPLICIT, summary)

    def _close_current(
        self,
        boundary: EpisodeBoundary,
        summary: str | None = None,
    ) -> Episode:
        """Internal method to close current episode.

        Args:
            boundary: Type of boundary that triggered closure.
            summary: Optional summary.

        Returns:
            The closed episode.
        """
        episode = self.current
        episode.close(summary)
        episode.metadata["closed_by"] = boundary.name
        self.episodes.append(episode)
        self.current = None

        # Notify callbacks
        for callback in self._on_episode_closed:
            try:
                callback(episode)
            except Exception:
                pass  # Don't let callbacks break the flow

        return episode

    def _check_boundaries(self, message: Message) -> EpisodeBoundary | None:
        """Check if any boundary conditions are met.

        Args:
            message: The new message being added.

        Returns:
            Boundary type if triggered, None otherwise.
        """
        if not self.current:
            return None

        # Size boundary
        if self.current.message_count >= self.config.max_messages:
            return EpisodeBoundary.SIZE

        if self.current.total_tokens >= self.config.max_tokens:
            return EpisodeBoundary.SIZE

        # Time boundary
        time_since = self.current.time_since_last_message
        if time_since and time_since > self.config.time_gap:
            return EpisodeBoundary.TIME

        # Topic boundary
        if self._topic_extractor and self._similarity_checker:
            new_topic = self._topic_extractor(message.content)
            similarity = self._similarity_checker(self.current.topic, new_topic)
            if similarity < self.config.topic_similarity_threshold:
                return EpisodeBoundary.TOPIC

        return None

    def get_all_episodes(self) -> list[Episode]:
        """Get all episodes including current.

        Returns:
            List of all episodes.
        """
        result = self.episodes.copy()
        if self.current:
            result.append(self.current)
        return result

    def get_recent_episodes(self, count: int) -> list[Episode]:
        """Get most recent episodes.

        Args:
            count: Maximum number of episodes to return.

        Returns:
            List of recent episodes (newest last).
        """
        all_episodes = self.get_all_episodes()
        return all_episodes[-count:]

    def get_episodes_by_status(self, status: EpisodeStatus) -> list[Episode]:
        """Get episodes with a specific status.

        Args:
            status: Status to filter by.

        Returns:
            List of matching episodes.
        """
        result = [e for e in self.episodes if e.status == status]
        if self.current and self.current.status == status:
            result.append(self.current)
        return result

    def find_episodes_by_topic(self, topic: str) -> list[Episode]:
        """Find episodes matching a topic.

        Args:
            topic: Topic to search for.

        Returns:
            List of matching episodes.
        """
        topic_lower = topic.lower()
        result = []

        for episode in self.get_all_episodes():
            if topic_lower in episode.topic.lower():
                result.append(episode)

        return result

    def get_total_messages(self) -> int:
        """Get total message count across all episodes.

        Returns:
            Total number of messages.
        """
        return sum(e.message_count for e in self.get_all_episodes())

    def clear_archived(self) -> int:
        """Remove archived episodes from memory.

        Returns:
            Number of episodes removed.
        """
        original_count = len(self.episodes)
        self.episodes = [
            e for e in self.episodes
            if e.status != EpisodeStatus.ARCHIVED
        ]
        return original_count - len(self.episodes)
