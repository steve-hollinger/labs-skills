"""Solution for Exercise 3: Test an SQS Message Processor"""

import json
import os
from dataclasses import dataclass
from typing import Any, Callable

import boto3
import pytest
from moto import mock_aws


# Set up credentials
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


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
        """Send a message to the queue."""
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
        """Send a batch of messages."""
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
        """Process messages with a handler function."""
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
# Fixtures and Tests (Solutions)
# =============================================================================


@pytest.fixture
def message_processor():
    """Create a mocked SQS queue and MessageProcessor."""
    with mock_aws():
        sqs = boto3.client("sqs", region_name="us-east-1")
        response = sqs.create_queue(QueueName="test-queue")
        queue_url = response["QueueUrl"]
        yield MessageProcessor(queue_url)


def test_send_message(message_processor: MessageProcessor) -> None:
    """Test sending a message."""
    message_id = message_processor.send({"type": "test", "data": "hello"})

    assert message_id is not None
    assert len(message_id) > 0

    # Verify queue depth
    depth = message_processor.get_queue_depth()
    assert depth == 1


def test_receive_messages(message_processor: MessageProcessor) -> None:
    """Test receiving messages."""
    # Send messages
    message_processor.send({"id": 1, "value": "first"})
    message_processor.send({"id": 2, "value": "second"})
    message_processor.send({"id": 3, "value": "third"})

    # Receive messages
    messages = message_processor.receive()

    assert len(messages) == 3

    bodies = [m.body for m in messages]
    ids = [b["id"] for b in bodies]
    assert sorted(ids) == [1, 2, 3]


def test_process_messages(message_processor: MessageProcessor) -> None:
    """Test processing messages with handler."""
    # Send messages
    for i in range(5):
        message_processor.send({"index": i})

    # Process with success handler
    processed_items: list[int] = []

    def handler(body: dict[str, Any]) -> bool:
        processed_items.append(body["index"])
        return True

    success, failure = message_processor.process(handler)

    assert success == 5
    assert failure == 0
    assert sorted(processed_items) == [0, 1, 2, 3, 4]

    # Verify queue is empty
    assert message_processor.get_queue_depth() == 0


def test_batch_send(message_processor: MessageProcessor) -> None:
    """Test sending batch of messages."""
    messages = [{"id": i, "content": f"message {i}"} for i in range(5)]

    message_ids = message_processor.send_batch(messages)

    assert len(message_ids) == 5
    assert message_processor.get_queue_depth() == 5


def test_handler_failure(message_processor: MessageProcessor) -> None:
    """Test handling of failed message processing."""
    message_processor.send({"should": "fail"})

    # Handler returns False
    def failing_handler(body: dict[str, Any]) -> bool:
        return False

    success, failure = message_processor.process(failing_handler)

    assert success == 0
    assert failure == 1

    # Message should still be in queue (not acknowledged)
    # Note: In real SQS it would be invisible, but after visibility timeout
    # it would reappear. moto simulates this behavior.


def test_message_attributes(message_processor: MessageProcessor) -> None:
    """Test message attributes."""
    message_processor.send(
        {"order_id": "12345"},
        attributes={"priority": "high", "type": "order"},
    )

    messages = message_processor.receive()

    assert len(messages) == 1
    assert messages[0].attributes["priority"] == "high"
    assert messages[0].attributes["type"] == "order"


def test_queue_depth(message_processor: MessageProcessor) -> None:
    """Test queue depth reporting."""
    # Empty queue
    assert message_processor.get_queue_depth() == 0

    # Add messages
    for i in range(5):
        message_processor.send({"index": i})

    assert message_processor.get_queue_depth() == 5

    # Receive and acknowledge 2 messages
    messages = message_processor.receive(2)
    for msg in messages:
        message_processor.acknowledge(msg.receipt_handle)

    assert message_processor.get_queue_depth() == 3


def test_process_empty_queue(message_processor: MessageProcessor) -> None:
    """Test processing empty queue."""

    def handler(body: dict[str, Any]) -> bool:
        return True

    success, failure = message_processor.process(handler)

    assert success == 0
    assert failure == 0


def test_handler_exception(message_processor: MessageProcessor) -> None:
    """Test handler that raises exception."""
    message_processor.send({"data": "test"})

    def exception_handler(body: dict[str, Any]) -> bool:
        raise ValueError("Handler crashed!")

    success, failure = message_processor.process(exception_handler)

    assert success == 0
    assert failure == 1


def test_partial_batch_success(message_processor: MessageProcessor) -> None:
    """Test batch where some messages succeed and some fail."""
    for i in range(5):
        message_processor.send({"index": i, "should_fail": i % 2 == 0})

    def selective_handler(body: dict[str, Any]) -> bool:
        return not body["should_fail"]

    success, failure = message_processor.process(selective_handler)

    # Indices 0, 2, 4 should fail (even numbers)
    # Indices 1, 3 should succeed (odd numbers)
    assert success == 2
    assert failure == 3


if __name__ == "__main__":
    import subprocess

    subprocess.run(["pytest", __file__, "-v"])
