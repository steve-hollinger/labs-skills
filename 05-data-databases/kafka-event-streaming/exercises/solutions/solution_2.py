"""Solution 2: Message Processor with Retry Logic.

This is the solution for Exercise 2: Implement a Message Processor with Retry Logic.
"""

from __future__ import annotations

import json
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

from confluent_kafka import Consumer, KafkaError, Producer


@dataclass
class ProcessingResult:
    """Track processing statistics."""

    success_count: int = 0
    retry_count: int = 0
    dlq_count: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass
class DeadLetterMessage:
    """Message sent to dead letter queue."""

    original_topic: str
    original_partition: int
    original_offset: int
    original_key: str | None
    original_value: str
    error_message: str
    error_traceback: str
    retry_count: int
    timestamp: datetime

    def to_json(self) -> str:
        """Serialize to JSON."""
        data = {
            "original_topic": self.original_topic,
            "original_partition": self.original_partition,
            "original_offset": self.original_offset,
            "original_key": self.original_key,
            "original_value": self.original_value,
            "error_message": self.error_message,
            "error_traceback": self.error_traceback,
            "retry_count": self.retry_count,
            "timestamp": self.timestamp.isoformat(),
        }
        return json.dumps(data)


class MessageProcessor:
    """Consumer with retry logic and DLQ handling."""

    def __init__(
        self,
        topic: str,
        dlq_topic: str = "dead-letter-queue",
        group_id: str = "processor-group",
        max_retries: int = 3,
        bootstrap_servers: str = "localhost:9092",
    ) -> None:
        """Initialize the message processor."""
        self.topic = topic
        self.dlq_topic = dlq_topic
        self.max_retries = max_retries

        self.consumer = Consumer({
            "bootstrap.servers": bootstrap_servers,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        })
        self.consumer.subscribe([topic])

        self.producer = Producer({
            "bootstrap.servers": bootstrap_servers,
        })

        # Track retry counts by message ID (topic-partition-offset)
        self.retry_counts: dict[str, int] = {}

    def process(
        self,
        handler: Callable[[dict[str, Any]], None],
        max_messages: int | None = None,
        timeout: float = 30.0,
    ) -> ProcessingResult:
        """Process messages with retry logic."""
        result = ProcessingResult()
        start_time = time.time()
        processed = 0
        empty_polls = 0

        while (time.time() - start_time) < timeout:
            if max_messages is not None and processed >= max_messages:
                break

            msg = self.consumer.poll(timeout=1.0)

            if msg is None:
                empty_polls += 1
                if empty_polls >= 5:
                    break
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    empty_polls += 1
                    if empty_polls >= 5:
                        break
                    continue
                result.errors.append(f"Consumer error: {msg.error()}")
                continue

            empty_polls = 0
            message_id = f"{msg.topic()}-{msg.partition()}-{msg.offset()}"

            try:
                # Parse and process message
                value = json.loads(msg.value().decode("utf-8"))
                handler(value)

                # Success - commit and clear retry count
                self.consumer.commit(asynchronous=False)
                self.retry_counts.pop(message_id, None)
                result.success_count += 1
                processed += 1

            except Exception as e:
                # Increment retry count
                retry_count = self.retry_counts.get(message_id, 0) + 1
                self.retry_counts[message_id] = retry_count
                result.retry_count += 1

                print(f"  [RETRY {retry_count}/{self.max_retries}] {message_id}: {e}")

                if retry_count >= self.max_retries:
                    # Send to DLQ
                    self._send_to_dlq(msg, e, retry_count)
                    self.consumer.commit(asynchronous=False)
                    self.retry_counts.pop(message_id, None)
                    result.dlq_count += 1
                    result.errors.append(f"Sent to DLQ: {e}")
                    processed += 1
                else:
                    # Wait with backoff before retry
                    backoff = self._calculate_backoff(retry_count)
                    print(f"  [BACKOFF] Waiting {backoff:.2f}s before retry")
                    time.sleep(backoff)
                    # Don't commit - message will be redelivered

        return result

    def _send_to_dlq(
        self,
        msg: Any,
        error: Exception,
        retry_count: int,
    ) -> None:
        """Send a message to the dead letter queue."""
        dlq_message = DeadLetterMessage(
            original_topic=msg.topic(),
            original_partition=msg.partition(),
            original_offset=msg.offset(),
            original_key=msg.key().decode("utf-8") if msg.key() else None,
            original_value=msg.value().decode("utf-8"),
            error_message=str(error),
            error_traceback=traceback.format_exc(),
            retry_count=retry_count,
            timestamp=datetime.utcnow(),
        )

        self.producer.produce(
            topic=self.dlq_topic,
            key=msg.key(),
            value=dlq_message.to_json().encode("utf-8"),
        )
        self.producer.flush(timeout=10)
        print(f"  [DLQ] Sent message to {self.dlq_topic}")

    def _calculate_backoff(self, retry_count: int) -> float:
        """Calculate exponential backoff delay."""
        base_delay = 0.1
        max_delay = 5.0
        delay = min(base_delay * (2**retry_count), max_delay)
        return delay

    def close(self) -> None:
        """Close consumer and producer."""
        self.producer.flush()
        self.consumer.close()


def produce_test_messages(topic: str, count: int = 10) -> None:
    """Produce test messages, some that will fail."""
    producer = Producer({"bootstrap.servers": "localhost:9092"})

    for i in range(count):
        message = {
            "id": i + 1,
            "data": f"Message {i + 1}",
            "should_fail": i % 4 == 3,  # Every 4th message fails
        }

        producer.produce(
            topic=topic,
            key=f"msg-{i}".encode("utf-8"),
            value=json.dumps(message).encode("utf-8"),
        )

    producer.flush(timeout=10)
    print(f"  Produced {count} test messages ({count // 4} will fail)")


def main() -> None:
    """Demonstrate the message processor."""
    print("Solution 2: Message Processor with Retry Logic")
    print("=" * 50)

    topic = "messages-to-process"

    # Produce test messages
    print("\n  Producing test messages...")
    produce_test_messages(topic, count=8)

    # Define handler that fails for some messages
    def handler(message: dict[str, Any]) -> None:
        if message.get("should_fail"):
            raise ValueError(f"Intentional failure for message {message['id']}")
        print(f"  [OK] Processed message {message['id']}")

    # Process messages
    print("\n  Processing messages...")
    processor = MessageProcessor(
        topic=topic,
        dlq_topic="messages-dlq",
        group_id=f"processor-{time.time()}",  # Unique group for demo
        max_retries=2,
    )

    try:
        result = processor.process(handler, max_messages=8, timeout=30.0)

        print("\n  Results:")
        print(f"    Success: {result.success_count}")
        print(f"    Retries: {result.retry_count}")
        print(f"    Sent to DLQ: {result.dlq_count}")
        if result.errors:
            print("    Errors:")
            for error in result.errors:
                print(f"      - {error}")

    finally:
        processor.close()


if __name__ == "__main__":
    main()
