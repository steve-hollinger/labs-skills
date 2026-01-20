"""Exercise 3: Test an SQS Message Processor

Your task is to implement tests for the MessageProcessor class using moto.
The processor handles receiving, processing, and acknowledging SQS messages.

Instructions:
1. Create a pytest fixture that provides a mocked SQS queue
2. Implement tests for all MessageProcessor methods
3. Test error handling and batch processing

Expected Tests:
- test_send_message: Send a message and verify it's in the queue
- test_receive_messages: Receive messages from queue
- test_process_messages: Process messages with a handler
- test_batch_send: Send batch of messages
- test_dead_letter_handling: Test error handling
- test_message_attributes: Test sending/receiving attributes

Hints:
- Use @mock_aws decorator or context manager
- Create the queue in the fixture
- Use WaitTimeSeconds=0 for immediate responses in tests

Run your tests with:
    pytest exercises/exercise_3.py -v
"""

import json
from dataclasses import dataclass
from typing import Any, Callable

import boto3
import pytest  # noqa: F401
from moto import mock_aws  # noqa: F401


@dataclass
class Message:
    """Represents an SQS message."""

    message_id: str
    body: dict[str, Any]
    receipt_handle: str
    attributes: dict[str, str]


class MessageProcessor:
    """SQS message processor."""

    def __init__(self, queue_url: str) -> None:
        self.sqs = boto3.client("sqs", region_name="us-east-1")
        self.queue_url = queue_url

    def send(
        self,
        body: dict[str, Any],
        attributes: dict[str, str] | None = None,
    ) -> str:
        """Send a message to the queue.

        Returns the message ID.
        """
        message_attributes = {}
        if attributes:
            for key, value in attributes.items():
                message_attributes[key] = {
                    "DataType": "String",
                    "StringValue": value,
                }

        response = self.sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(body),
            MessageAttributes=message_attributes,
        )

        return response["MessageId"]

    def send_batch(self, messages: list[dict[str, Any]]) -> list[str]:
        """Send a batch of messages.

        Returns list of message IDs.
        """
        entries = [
            {"Id": str(i), "MessageBody": json.dumps(msg)}
            for i, msg in enumerate(messages)
        ]

        response = self.sqs.send_message_batch(
            QueueUrl=self.queue_url,
            Entries=entries,
        )

        return [msg["MessageId"] for msg in response["Successful"]]

    def receive(self, max_messages: int = 10) -> list[Message]:
        """Receive messages from the queue."""
        response = self.sqs.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=max_messages,
            MessageAttributeNames=["All"],
            WaitTimeSeconds=0,
        )

        if "Messages" not in response:
            return []

        messages = []
        for msg in response["Messages"]:
            attributes = {}
            if "MessageAttributes" in msg:
                for key, value in msg["MessageAttributes"].items():
                    attributes[key] = value["StringValue"]

            messages.append(
                Message(
                    message_id=msg["MessageId"],
                    body=json.loads(msg["Body"]),
                    receipt_handle=msg["ReceiptHandle"],
                    attributes=attributes,
                )
            )

        return messages

    def acknowledge(self, receipt_handle: str) -> None:
        """Acknowledge (delete) a processed message."""
        self.sqs.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle,
        )

    def process(
        self,
        handler: Callable[[dict[str, Any]], bool],
        max_messages: int = 10,
    ) -> tuple[int, int]:
        """Process messages with a handler function.

        Handler should return True on success, False on failure.
        Returns (success_count, failure_count).
        """
        messages = self.receive(max_messages)

        success_count = 0
        failure_count = 0

        for message in messages:
            try:
                if handler(message.body):
                    self.acknowledge(message.receipt_handle)
                    success_count += 1
                else:
                    failure_count += 1
            except Exception:
                failure_count += 1

        return success_count, failure_count

    def get_queue_depth(self) -> int:
        """Get approximate number of messages in queue."""
        response = self.sqs.get_queue_attributes(
            QueueUrl=self.queue_url,
            AttributeNames=["ApproximateNumberOfMessages"],
        )
        return int(response["Attributes"]["ApproximateNumberOfMessages"])


# =============================================================================
# TODO: Implement the fixture and tests below
# =============================================================================


@pytest.fixture
def message_processor():
    """Create a mocked SQS queue and MessageProcessor.

    TODO:
    1. Use mock_aws context manager
    2. Create SQS client
    3. Create a queue
    4. Yield MessageProcessor instance with queue_url
    """
    pass


def test_send_message(message_processor) -> None:
    """Test sending a message.

    TODO:
    1. Send a message with body {"type": "test", "data": "hello"}
    2. Verify message ID is returned
    3. Verify queue depth is 1
    """
    pass


def test_receive_messages(message_processor) -> None:
    """Test receiving messages.

    TODO:
    1. Send multiple messages
    2. Receive messages
    3. Verify message bodies are correct
    """
    pass


def test_process_messages(message_processor) -> None:
    """Test processing messages with handler.

    TODO:
    1. Send some messages
    2. Process with a handler that returns True
    3. Verify success count
    4. Verify queue is empty (messages acknowledged)
    """
    pass


def test_batch_send(message_processor) -> None:
    """Test sending batch of messages.

    TODO:
    1. Create list of 5 messages
    2. Send as batch
    3. Verify all message IDs returned
    4. Verify queue depth
    """
    pass


def test_handler_failure(message_processor) -> None:
    """Test handling of failed message processing.

    TODO:
    1. Send a message
    2. Process with handler that returns False
    3. Verify failure count
    4. Verify message is NOT deleted (still in queue)
    """
    pass


def test_message_attributes(message_processor) -> None:
    """Test message attributes.

    TODO:
    1. Send message with attributes {"priority": "high", "type": "order"}
    2. Receive message
    3. Verify attributes are present
    """
    pass


def test_queue_depth(message_processor) -> None:
    """Test queue depth reporting.

    TODO:
    1. Verify empty queue has depth 0
    2. Send 5 messages
    3. Verify depth is 5
    4. Receive and acknowledge 2
    5. Verify depth is 3
    """
    pass


def test_process_empty_queue(message_processor) -> None:
    """Test processing empty queue.

    TODO:
    1. Process empty queue
    2. Verify returns (0, 0)
    """
    pass


if __name__ == "__main__":
    import subprocess

    subprocess.run(["pytest", __file__, "-v"])
