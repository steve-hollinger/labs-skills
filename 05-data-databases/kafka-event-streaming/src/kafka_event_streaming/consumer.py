"""Kafka consumer utilities for event consumption."""

from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

from confluent_kafka import Consumer, KafkaError, KafkaException, Message
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


@dataclass
class ConsumedMessage:
    """Wrapper for consumed Kafka messages with parsed data."""

    topic: str
    partition: int
    offset: int
    key: str | None
    value: dict[str, Any]
    headers: dict[str, str]
    timestamp: tuple[int, int]  # (timestamp_type, timestamp)

    @classmethod
    def from_kafka_message(cls, msg: Message) -> ConsumedMessage:
        """Create from a Kafka message."""
        # Parse value
        raw_value = msg.value()
        if raw_value is None:
            value = {}
        else:
            try:
                value = json.loads(raw_value.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                value = {"raw": raw_value.decode("utf-8", errors="replace")}

        # Parse key
        raw_key = msg.key()
        key = raw_key.decode("utf-8") if raw_key else None

        # Parse headers
        headers = {}
        if msg.headers():
            for header_key, header_value in msg.headers():
                if header_value:
                    headers[header_key] = header_value.decode("utf-8")

        return cls(
            topic=msg.topic(),
            partition=msg.partition(),
            offset=msg.offset(),
            key=key,
            value=value,
            headers=headers,
            timestamp=msg.timestamp(),
        )


class KafkaEventConsumer:
    """High-level Kafka consumer for event consumption.

    Provides a simplified interface for consuming events from Kafka with
    automatic deserialization and error handling.

    Example:
        >>> consumer = KafkaEventConsumer(
        ...     bootstrap_servers="localhost:9092",
        ...     group_id="my-service",
        ...     topics=["events"]
        ... )
        >>> for message in consumer.consume():
        ...     print(f"Received: {message.value}")
        ...     consumer.commit()
    """

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        group_id: str = "default-group",
        topics: list[str] | None = None,
        config: dict[str, Any] | None = None,
        auto_commit: bool = False,
    ) -> None:
        """Initialize the Kafka consumer.

        Args:
            bootstrap_servers: Kafka bootstrap servers address.
            group_id: Consumer group ID.
            topics: List of topics to subscribe to.
            config: Additional Kafka consumer configuration.
            auto_commit: Whether to enable auto-commit.
        """
        self._config = {
            "bootstrap.servers": bootstrap_servers,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": auto_commit,
        }

        if config:
            self._config.update(config)

        self._consumer = Consumer(self._config)
        self._topics = topics or []
        self._running = False

        if self._topics:
            self.subscribe(self._topics)

    def subscribe(
        self,
        topics: list[str],
        on_assign: Callable[[Any, list[Any]], None] | None = None,
        on_revoke: Callable[[Any, list[Any]], None] | None = None,
    ) -> None:
        """Subscribe to topics.

        Args:
            topics: List of topic names.
            on_assign: Callback when partitions are assigned.
            on_revoke: Callback when partitions are revoked.
        """
        self._topics = topics
        self._consumer.subscribe(
            topics,
            on_assign=on_assign,
            on_revoke=on_revoke,
        )
        logger.info(f"Subscribed to topics: {topics}")

    def poll(self, timeout: float = 1.0) -> ConsumedMessage | None:
        """Poll for a single message.

        Args:
            timeout: Maximum time to wait in seconds.

        Returns:
            Consumed message or None if no message available.

        Raises:
            KafkaException: If a non-recoverable error occurs.
        """
        msg = self._consumer.poll(timeout)

        if msg is None:
            return None

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition - not an error
                logger.debug(
                    f"Reached end of partition: {msg.topic()}[{msg.partition()}]"
                )
                return None
            else:
                raise KafkaException(msg.error())

        return ConsumedMessage.from_kafka_message(msg)

    def consume(
        self,
        timeout: float = 1.0,
        max_messages: int | None = None,
    ) -> Iterator[ConsumedMessage]:
        """Iterate over messages from subscribed topics.

        Args:
            timeout: Maximum time to wait for each poll.
            max_messages: Maximum number of messages to consume (None for unlimited).

        Yields:
            Consumed messages.
        """
        self._running = True
        messages_consumed = 0

        try:
            while self._running:
                if max_messages is not None and messages_consumed >= max_messages:
                    break

                message = self.poll(timeout)
                if message is not None:
                    messages_consumed += 1
                    yield message

        finally:
            self._running = False

    def commit(self, asynchronous: bool = False) -> None:
        """Commit current offsets.

        Args:
            asynchronous: Whether to commit asynchronously.
        """
        self._consumer.commit(asynchronous=asynchronous)

    def stop(self) -> None:
        """Stop consuming messages."""
        self._running = False

    def close(self) -> None:
        """Close the consumer connection."""
        self._consumer.close()
        logger.info("Consumer closed")

    def __enter__(self) -> KafkaEventConsumer:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with cleanup."""
        self.close()


class TypedEventConsumer(Generic[T]):
    """Consumer that deserializes messages to a specific Pydantic model.

    Example:
        >>> consumer = TypedEventConsumer(
        ...     OrderEvent,
        ...     bootstrap_servers="localhost:9092",
        ...     group_id="order-processors",
        ...     topics=["orders"]
        ... )
        >>> for event in consumer.consume():
        ...     print(f"Order ID: {event.order_id}")
    """

    def __init__(
        self,
        event_type: type[T],
        bootstrap_servers: str = "localhost:9092",
        group_id: str = "default-group",
        topics: list[str] | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the typed consumer.

        Args:
            event_type: Pydantic model class for deserialization.
            bootstrap_servers: Kafka bootstrap servers address.
            group_id: Consumer group ID.
            topics: List of topics to subscribe to.
            config: Additional Kafka consumer configuration.
        """
        self._event_type = event_type
        self._consumer = KafkaEventConsumer(
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            topics=topics,
            config=config,
        )

    def consume(
        self,
        timeout: float = 1.0,
        max_messages: int | None = None,
    ) -> Iterator[T]:
        """Iterate over typed messages.

        Args:
            timeout: Maximum time to wait for each poll.
            max_messages: Maximum number of messages to consume.

        Yields:
            Deserialized event objects.
        """
        for message in self._consumer.consume(timeout, max_messages):
            try:
                yield self._event_type.model_validate(message.value)
            except Exception as e:
                logger.error(f"Failed to deserialize message: {e}")
                raise

    def commit(self, asynchronous: bool = False) -> None:
        """Commit current offsets."""
        self._consumer.commit(asynchronous)

    def close(self) -> None:
        """Close the consumer connection."""
        self._consumer.close()

    def __enter__(self) -> TypedEventConsumer[T]:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with cleanup."""
        self.close()
