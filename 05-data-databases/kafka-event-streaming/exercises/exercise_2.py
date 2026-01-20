"""Exercise 2: Implement a Message Processor with Retry Logic.

In this exercise, you will create a robust consumer that processes
messages with retry logic and dead letter queue handling.

Requirements:
1. Create a MessageProcessor class that:
   - Consumes from a configured topic
   - Retries failed processing up to max_retries
   - Sends permanently failed messages to a DLQ
   - Commits offsets only after successful processing
   - Handles rebalances gracefully

2. Implement exponential backoff for retries

3. Create a ProcessingResult dataclass to track:
   - success count
   - retry count
   - dlq count
   - error messages

Run with: python exercises/exercise_2.py
Test with: pytest tests/test_exercises.py -k exercise_2
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

from confluent_kafka import Consumer, KafkaError, Producer

# TODO: Implement the following


@dataclass
class ProcessingResult:
    """Track processing statistics.

    TODO: Add fields:
    - success_count: int
    - retry_count: int
    - dlq_count: int
    - errors: list[str]
    """

    pass


@dataclass
class DeadLetterMessage:
    """Message sent to dead letter queue.

    TODO: Add fields:
    - original_topic: str
    - original_partition: int
    - original_offset: int
    - original_key: str | None
    - original_value: str
    - error_message: str
    - retry_count: int
    - timestamp: datetime
    """

    pass


class MessageProcessor:
    """Consumer with retry logic and DLQ handling.

    TODO: Implement methods:
    - __init__(self, topic, dlq_topic, group_id, max_retries, bootstrap_servers)
    - process(self, handler, max_messages) -> ProcessingResult
    - _send_to_dlq(self, msg, error, retry_count)
    - _calculate_backoff(self, retry_count) -> float
    - close(self)
    """

    def __init__(
        self,
        topic: str,
        dlq_topic: str = "dead-letter-queue",
        group_id: str = "processor-group",
        max_retries: int = 3,
        bootstrap_servers: str = "localhost:9092",
    ) -> None:
        """Initialize the message processor.

        TODO:
        1. Store configuration
        2. Create Consumer with manual commit
        3. Create Producer for DLQ
        4. Subscribe to topic
        5. Initialize retry tracking dict
        """
        pass

    def process(
        self,
        handler: Callable[[dict[str, Any]], None],
        max_messages: int | None = None,
        timeout: float = 30.0,
    ) -> ProcessingResult:
        """Process messages with retry logic.

        TODO:
        1. Poll for messages
        2. For each message:
           a. Try to process with handler
           b. On success: commit and clear retry count
           c. On failure:
              - Increment retry count
              - If retries exhausted: send to DLQ and commit
              - Otherwise: wait with backoff (don't commit)
        3. Return ProcessingResult
        """
        pass

    def _send_to_dlq(
        self,
        msg: Any,
        error: Exception,
        retry_count: int,
    ) -> None:
        """Send a message to the dead letter queue.

        TODO:
        1. Create DeadLetterMessage with original message info
        2. Serialize to JSON
        3. Produce to DLQ topic
        4. Flush producer
        """
        pass

    def _calculate_backoff(self, retry_count: int) -> float:
        """Calculate exponential backoff delay.

        TODO: Implement exponential backoff
        - Base delay: 0.1 seconds
        - Max delay: 5 seconds
        - Formula: min(base * 2^retry_count, max)
        """
        pass

    def close(self) -> None:
        """Close consumer and producer."""
        # TODO: Close both consumer and producer
        pass


def main() -> None:
    """Demonstrate the message processor."""
    print("Exercise 2: Message Processor with Retry Logic")
    print("=" * 50)

    # TODO: Implement the demonstration
    #
    # 1. Produce test messages (some that will fail processing)
    #    - Use a topic like "messages-to-process"
    #    - Include a "should_fail" field in some messages
    #
    # 2. Create a handler function that:
    #    - Raises an exception if message["should_fail"] is True
    #    - Otherwise prints "Processed: {message}"
    #
    # 3. Create a MessageProcessor
    #
    # 4. Process messages and print results:
    #    - Success count
    #    - Retry count
    #    - DLQ count
    #    - Any errors
    #
    # 5. Optionally: Consume from DLQ to show failed messages

    print("\nNot implemented yet. See TODO comments.")


if __name__ == "__main__":
    main()
