"""Episode and message data structures."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4


class EpisodeStatus(Enum):
    """Status of an episode."""

    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"


@dataclass
class Message:
    """A single message in a conversation.

    Attributes:
        role: The sender role (user, assistant, system).
        content: The message text content.
        timestamp: When the message was created.
        metadata: Additional message metadata.
    """

    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def token_estimate(self) -> int:
        """Estimate token count (rough approximation).

        Returns:
            Approximate token count based on word count.
        """
        # Rough estimate: ~4 characters per token
        return len(self.content) // 4

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Message":
        """Create from dictionary.

        Args:
            data: Dictionary with message data.

        Returns:
            New Message instance.
        """
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Episode:
    """A bounded segment of conversation.

    Attributes:
        id: Unique episode identifier.
        topic: Topic or title for this episode.
        messages: List of messages in this episode.
        summary: Compressed summary (set when closed).
        status: Current episode status.
        created_at: When the episode started.
        closed_at: When the episode was closed (None if active).
        metadata: Additional episode metadata.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    topic: str = "general"
    messages: list[Message] = field(default_factory=list)
    summary: str | None = None
    status: EpisodeStatus = EpisodeStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    closed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        """Check if episode is active."""
        return self.status == EpisodeStatus.ACTIVE

    @property
    def is_closed(self) -> bool:
        """Check if episode is closed."""
        return self.status in (EpisodeStatus.CLOSED, EpisodeStatus.ARCHIVED)

    @property
    def message_count(self) -> int:
        """Get number of messages."""
        return len(self.messages)

    @property
    def age(self) -> timedelta:
        """Get episode age."""
        return datetime.now() - self.created_at

    @property
    def duration(self) -> timedelta | None:
        """Get episode duration (None if still active)."""
        if not self.closed_at:
            return None
        return self.closed_at - self.created_at

    @property
    def last_message_time(self) -> datetime | None:
        """Get timestamp of last message."""
        if not self.messages:
            return None
        return self.messages[-1].timestamp

    @property
    def time_since_last_message(self) -> timedelta | None:
        """Get time since last message."""
        last_time = self.last_message_time
        if not last_time:
            return None
        return datetime.now() - last_time

    @property
    def total_tokens(self) -> int:
        """Estimate total tokens in episode."""
        return sum(m.token_estimate for m in self.messages)

    def add_message(self, message: Message) -> None:
        """Add a message to the episode.

        Args:
            message: Message to add.

        Raises:
            ValueError: If episode is not active.
        """
        if not self.is_active:
            raise ValueError("Cannot add message to closed episode")
        self.messages.append(message)

    def close(self, summary: str | None = None) -> None:
        """Close the episode.

        Args:
            summary: Optional summary to set.
        """
        self.status = EpisodeStatus.CLOSED
        self.closed_at = datetime.now()
        if summary:
            self.summary = summary

    def archive(self) -> None:
        """Archive the episode."""
        if self.status != EpisodeStatus.CLOSED:
            self.close()
        self.status = EpisodeStatus.ARCHIVED

    def get_context_string(self, use_summary: bool = True) -> str:
        """Get episode content as context string.

        Args:
            use_summary: If True and summary exists, use summary.

        Returns:
            Formatted context string.
        """
        if use_summary and self.summary and self.is_closed:
            return f"[Previous conversation about {self.topic}]: {self.summary}"

        lines = [f"[Conversation: {self.topic}]"]
        for msg in self.messages:
            lines.append(f"{msg.role}: {msg.content}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "id": self.id,
            "topic": self.topic,
            "messages": [m.to_dict() for m in self.messages],
            "summary": self.summary,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Episode":
        """Create from dictionary.

        Args:
            data: Dictionary with episode data.

        Returns:
            New Episode instance.
        """
        return cls(
            id=data["id"],
            topic=data["topic"],
            messages=[Message.from_dict(m) for m in data["messages"]],
            summary=data.get("summary"),
            status=EpisodeStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            closed_at=datetime.fromisoformat(data["closed_at"]) if data.get("closed_at") else None,
            metadata=data.get("metadata", {}),
        )
