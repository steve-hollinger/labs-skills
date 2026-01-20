"""Kafka producer utilities for event publishing."""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Protocol

from confluent_kafka import Producer
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class DeliveryCallback(Protocol):
    """Protocol for delivery callback functions."""

    def __call__(self, err: Exception | None, msg: Any) -> None:
        """Handle delivery result."""
        ...


def default_delivery_callback(err: Exception | None, msg: Any) -> None:
    """Default delivery callback that logs results."""
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(
            f"Message delivered to {msg.topic()}[{msg.partition()}] @ offset {msg.offset()}"
        )


class KafkaEventProducer:
    """High-level Kafka producer for event publishing.

    Provides a simplified interface for producing events to Kafka with
    automatic serialization and delivery tracking.

    Example:
        >>> producer = KafkaEventProducer(bootstrap_servers="localhost:9092")
        >>> producer.produce("events", key="user-123", value={"action": "login"})
        >>> producer.flush()
    """

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        config: dict[str, Any] | None = None,
        delivery_callback: DeliveryCallback | None = None,
    ) -> None:
        """Initialize the Kafka producer.

        Args:
            bootstrap_servers: Kafka bootstrap servers address.
            config: Additional Kafka producer configuration.
            delivery_callback: Callback for delivery reports.
        """
        self._config = {
            "bootstrap.servers": bootstrap_servers,
            "acks": "all",  # Wait for all replicas
            "retries": 3,
            "retry.backoff.ms": 100,
            "linger.ms": 5,  # Batch for 5ms
        }

        if config:
            self._config.update(config)

        self._producer = Producer(self._config)
        self._delivery_callback = delivery_callback or default_delivery_callback

    def produce(
        self,
        topic: str,
        value: dict[str, Any] | BaseModel | str | bytes,
        key: str | bytes | None = None,
        headers: dict[str, str] | None = None,
        callback: DeliveryCallback | None = None,
    ) -> None:
        """Produce a message to a Kafka topic.

        Args:
            topic: Target topic name.
            value: Message value (dict, Pydantic model, string, or bytes).
            key: Optional message key for partitioning.
            headers: Optional message headers.
            callback: Optional per-message delivery callback.
        """
        # Serialize value
        if isinstance(value, BaseModel):
            serialized_value = value.model_dump_json().encode("utf-8")
        elif isinstance(value, dict):
            serialized_value = json.dumps(value).encode("utf-8")
        elif isinstance(value, str):
            serialized_value = value.encode("utf-8")
        else:
            serialized_value = value

        # Serialize key
        serialized_key = None
        if key is not None:
            serialized_key = key.encode("utf-8") if isinstance(key, str) else key

        # Prepare headers
        kafka_headers = None
        if headers:
            kafka_headers = [(k, v.encode("utf-8")) for k, v in headers.items()]

        # Produce message
        self._producer.produce(
            topic=topic,
            value=serialized_value,
            key=serialized_key,
            headers=kafka_headers,
            callback=callback or self._delivery_callback,
        )

        # Poll for callbacks
        self._producer.poll(0)

    def produce_batch(
        self,
        topic: str,
        messages: list[tuple[str | None, dict[str, Any] | BaseModel]],
    ) -> None:
        """Produce multiple messages in a batch.

        Args:
            topic: Target topic name.
            messages: List of (key, value) tuples.
        """
        for key, value in messages:
            self.produce(topic, value=value, key=key)

    def flush(self, timeout: float = 10.0) -> int:
        """Flush all buffered messages.

        Args:
            timeout: Maximum time to wait in seconds.

        Returns:
            Number of messages still in queue after flush.
        """
        return self._producer.flush(timeout)

    def poll(self, timeout: float = 0) -> int:
        """Poll for delivery callbacks.

        Args:
            timeout: Maximum time to wait in seconds.

        Returns:
            Number of events processed.
        """
        return self._producer.poll(timeout)

    def __enter__(self) -> KafkaEventProducer:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with flush."""
        self.flush()
