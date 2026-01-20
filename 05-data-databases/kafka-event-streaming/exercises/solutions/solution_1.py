"""Solution 1: Event Logger Implementation.

This is the solution for Exercise 1: Build an Event Logger.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from confluent_kafka import Producer
from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Event severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ApplicationEvent(BaseModel):
    """Schema for application events."""

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    service_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    severity: Severity
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class EventLogger:
    """Logger that produces events to Kafka."""

    def __init__(
        self,
        service_name: str,
        topic: str = "application-logs",
        bootstrap_servers: str = "localhost:9092",
    ) -> None:
        """Initialize the event logger."""
        self.service_name = service_name
        self.topic = topic
        self.events_logged = 0

        self.producer = Producer({
            "bootstrap.servers": bootstrap_servers,
            "acks": "all",
        })

    def _delivery_callback(self, err: Exception | None, msg: Any) -> None:
        """Handle delivery confirmation."""
        if err is not None:
            print(f"  [ERROR] Delivery failed: {err}")
        else:
            print(f"  [OK] Logged to {msg.topic()}[{msg.partition()}]")

    def log(
        self,
        event_type: str,
        message: str,
        severity: Severity = Severity.INFO,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log an event to Kafka."""
        event = ApplicationEvent(
            event_type=event_type,
            service_name=self.service_name,
            severity=severity,
            message=message,
            metadata=metadata or {},
        )

        self.producer.produce(
            topic=self.topic,
            key=event_type.encode("utf-8"),
            value=event.model_dump_json().encode("utf-8"),
            callback=self._delivery_callback,
        )
        self.producer.poll(0)
        self.events_logged += 1

    def info(
        self,
        event_type: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log an INFO level event."""
        self.log(event_type, message, Severity.INFO, metadata)

    def warning(
        self,
        event_type: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log a WARNING level event."""
        self.log(event_type, message, Severity.WARNING, metadata)

    def error(
        self,
        event_type: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log an ERROR level event."""
        self.log(event_type, message, Severity.ERROR, metadata)

    def flush(self) -> None:
        """Flush all pending events."""
        self.producer.flush(timeout=10)


def main() -> None:
    """Demonstrate the event logger."""
    print("Solution 1: Event Logger")
    print("=" * 40)

    # Create logger for user-service
    logger = EventLogger(service_name="user-service")

    print("\n  Logging events...")

    # Log INFO events
    logger.info(
        "user.login",
        "User logged in successfully",
        metadata={"user_id": "user-123", "ip": "192.168.1.1"},
    )

    logger.info(
        "user.profile_updated",
        "User updated profile",
        metadata={"user_id": "user-123", "fields": ["email", "name"]},
    )

    # Log WARNING event
    logger.warning(
        "user.rate_limit",
        "User approaching rate limit",
        metadata={"user_id": "user-456", "requests": 95, "limit": 100},
    )

    # Log ERROR event
    logger.error(
        "user.auth_failed",
        "Authentication failed",
        metadata={"user_id": "unknown", "reason": "invalid_token"},
    )

    # Flush and summarize
    print("\n  Flushing...")
    logger.flush()

    print(f"\n  Summary: Logged {logger.events_logged} events")
    print("  - 2 INFO events")
    print("  - 1 WARNING event")
    print("  - 1 ERROR event")


if __name__ == "__main__":
    main()
