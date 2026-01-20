"""Exercise 1: Build an Event Logger.

In this exercise, you will create a producer that logs application events
to Kafka. This simulates a common use case where application events are
captured for monitoring, analytics, or debugging.

Requirements:
1. Create an ApplicationEvent schema with:
   - event_id (auto-generated UUID)
   - event_type (string)
   - service_name (string)
   - timestamp (datetime)
   - severity (enum: INFO, WARNING, ERROR)
   - message (string)
   - metadata (dict, optional)

2. Create an EventLogger class that:
   - Produces events to a configurable topic
   - Supports different severity levels
   - Includes delivery confirmation
   - Batches events for efficiency

3. Write a main function that demonstrates:
   - Logging INFO events for successful operations
   - Logging WARNING events for potential issues
   - Logging ERROR events for failures
   - Include metadata in events

Run with: python exercises/exercise_1.py
Test with: pytest tests/test_exercises.py -k exercise_1
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

# TODO: Implement the following


class Severity(str, Enum):
    """Event severity levels."""
    # TODO: Define INFO, WARNING, ERROR levels
    pass


class ApplicationEvent(BaseModel):
    """Schema for application events.

    TODO: Implement fields:
    - event_id: str (default factory to generate UUID)
    - event_type: str
    - service_name: str
    - timestamp: datetime (default to now)
    - severity: Severity
    - message: str
    - metadata: dict[str, Any] (default empty dict)
    """

    pass


class EventLogger:
    """Logger that produces events to Kafka.

    TODO: Implement methods:
    - __init__(self, service_name, topic, bootstrap_servers)
    - log(self, event_type, message, severity, metadata)
    - info(self, event_type, message, metadata)
    - warning(self, event_type, message, metadata)
    - error(self, event_type, message, metadata)
    - flush(self)
    """

    def __init__(
        self,
        service_name: str,
        topic: str = "application-logs",
        bootstrap_servers: str = "localhost:9092",
    ) -> None:
        """Initialize the event logger.

        TODO:
        1. Store service_name and topic
        2. Create a Kafka Producer
        3. Track events logged count
        """
        pass

    def log(
        self,
        event_type: str,
        message: str,
        severity: Severity = Severity.INFO,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log an event to Kafka.

        TODO:
        1. Create ApplicationEvent with provided data
        2. Serialize to JSON
        3. Produce to topic with event_type as key
        4. Implement delivery callback
        """
        pass

    def info(
        self,
        event_type: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log an INFO level event."""
        # TODO: Call log with INFO severity
        pass

    def warning(
        self,
        event_type: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log a WARNING level event."""
        # TODO: Call log with WARNING severity
        pass

    def error(
        self,
        event_type: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log an ERROR level event."""
        # TODO: Call log with ERROR severity
        pass

    def flush(self) -> None:
        """Flush all pending events."""
        # TODO: Flush the producer
        pass


def main() -> None:
    """Demonstrate the event logger."""
    print("Exercise 1: Event Logger")
    print("=" * 40)

    # TODO: Implement the demonstration
    #
    # 1. Create an EventLogger for "user-service"
    # 2. Log these events:
    #    - INFO: "user.login" - "User logged in successfully"
    #      metadata: {"user_id": "user-123", "ip": "192.168.1.1"}
    #    - INFO: "user.profile_updated" - "User updated profile"
    #      metadata: {"user_id": "user-123", "fields": ["email", "name"]}
    #    - WARNING: "user.rate_limit" - "User approaching rate limit"
    #      metadata: {"user_id": "user-456", "requests": 95, "limit": 100}
    #    - ERROR: "user.auth_failed" - "Authentication failed"
    #      metadata: {"user_id": "unknown", "reason": "invalid_token"}
    # 3. Flush and print summary

    print("\nNot implemented yet. See TODO comments.")


if __name__ == "__main__":
    main()
