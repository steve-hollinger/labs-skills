"""Tests demonstrating SQS mocking with moto."""

import json
from typing import Any

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws


# =============================================================================
# Basic Message Operations
# =============================================================================


def test_send_and_receive_message(sqs_client: tuple[Any, str]) -> None:
    """Test basic send and receive operations."""
    sqs, queue_url = sqs_client

    # Send message
    sqs.send_message(QueueUrl=queue_url, MessageBody="Hello, World!")

    # Receive message
    response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)

    assert len(response["Messages"]) == 1
    assert response["Messages"][0]["Body"] == "Hello, World!"


def test_send_json_message(sqs_client: tuple[Any, str]) -> None:
    """Test sending and receiving JSON messages."""
    sqs, queue_url = sqs_client

    event = {"event_type": "user_created", "user_id": "123", "timestamp": "2024-01-15"}

    sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(event))

    response = sqs.receive_message(QueueUrl=queue_url)
    received = json.loads(response["Messages"][0]["Body"])

    assert received["event_type"] == "user_created"
    assert received["user_id"] == "123"


def test_delete_message(sqs_client: tuple[Any, str]) -> None:
    """Test deleting a message after processing."""
    sqs, queue_url = sqs_client

    # Send message
    sqs.send_message(QueueUrl=queue_url, MessageBody="To be deleted")

    # Receive message
    response = sqs.receive_message(QueueUrl=queue_url)
    receipt_handle = response["Messages"][0]["ReceiptHandle"]

    # Delete message
    sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)

    # Verify queue is empty
    response = sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=0)
    assert "Messages" not in response or len(response["Messages"]) == 0


# =============================================================================
# Message Attributes
# =============================================================================


def test_message_attributes(sqs_client: tuple[Any, str]) -> None:
    """Test sending messages with attributes."""
    sqs, queue_url = sqs_client

    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody="Order notification",
        MessageAttributes={
            "priority": {"DataType": "String", "StringValue": "high"},
            "order_id": {"DataType": "Number", "StringValue": "12345"},
            "urgent": {"DataType": "String", "StringValue": "true"},
        },
    )

    response = sqs.receive_message(
        QueueUrl=queue_url,
        MessageAttributeNames=["All"],
    )

    attrs = response["Messages"][0]["MessageAttributes"]
    assert attrs["priority"]["StringValue"] == "high"
    assert attrs["order_id"]["StringValue"] == "12345"


def test_selective_message_attributes(sqs_client: tuple[Any, str]) -> None:
    """Test receiving specific message attributes."""
    sqs, queue_url = sqs_client

    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody="Test",
        MessageAttributes={
            "attr1": {"DataType": "String", "StringValue": "value1"},
            "attr2": {"DataType": "String", "StringValue": "value2"},
            "attr3": {"DataType": "String", "StringValue": "value3"},
        },
    )

    # Only request attr1
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MessageAttributeNames=["attr1"],
    )

    attrs = response["Messages"][0]["MessageAttributes"]
    assert "attr1" in attrs
    assert "attr2" not in attrs


# =============================================================================
# Batch Operations
# =============================================================================


def test_send_message_batch(sqs_client: tuple[Any, str]) -> None:
    """Test sending batch of messages."""
    sqs, queue_url = sqs_client

    entries = [{"Id": str(i), "MessageBody": f"Message {i}"} for i in range(10)]

    response = sqs.send_message_batch(QueueUrl=queue_url, Entries=entries)

    assert len(response["Successful"]) == 10
    assert "Failed" not in response or len(response["Failed"]) == 0


def test_receive_multiple_messages(sqs_client: tuple[Any, str]) -> None:
    """Test receiving multiple messages."""
    sqs, queue_url = sqs_client

    # Send multiple messages
    for i in range(5):
        sqs.send_message(QueueUrl=queue_url, MessageBody=f"Message {i}")

    # Receive all messages
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=0,
    )

    assert len(response["Messages"]) == 5


def test_delete_message_batch(sqs_client: tuple[Any, str]) -> None:
    """Test deleting batch of messages."""
    sqs, queue_url = sqs_client

    # Send messages
    for i in range(5):
        sqs.send_message(QueueUrl=queue_url, MessageBody=f"Message {i}")

    # Receive messages
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
    )

    # Delete all messages
    entries = [
        {"Id": str(i), "ReceiptHandle": msg["ReceiptHandle"]}
        for i, msg in enumerate(response["Messages"])
    ]

    delete_response = sqs.delete_message_batch(QueueUrl=queue_url, Entries=entries)

    assert len(delete_response["Successful"]) == 5


# =============================================================================
# Queue Attributes
# =============================================================================


def test_get_queue_attributes(sqs_client: tuple[Any, str]) -> None:
    """Test getting queue attributes."""
    sqs, queue_url = sqs_client

    # Send some messages
    for i in range(3):
        sqs.send_message(QueueUrl=queue_url, MessageBody=f"Message {i}")

    response = sqs.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=["ApproximateNumberOfMessages", "QueueArn"],
    )

    assert int(response["Attributes"]["ApproximateNumberOfMessages"]) == 3
    assert "arn:aws:sqs" in response["Attributes"]["QueueArn"]


@mock_aws
def test_create_queue_with_attributes() -> None:
    """Test creating queue with custom attributes."""
    sqs = boto3.client("sqs", region_name="us-east-1")

    response = sqs.create_queue(
        QueueName="custom-queue",
        Attributes={
            "VisibilityTimeout": "60",
            "MessageRetentionPeriod": "86400",
            "MaximumMessageSize": "1024",
        },
    )

    queue_url = response["QueueUrl"]

    attrs = sqs.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=["VisibilityTimeout", "MessageRetentionPeriod"],
    )

    assert attrs["Attributes"]["VisibilityTimeout"] == "60"
    assert attrs["Attributes"]["MessageRetentionPeriod"] == "86400"


# =============================================================================
# Visibility Timeout
# =============================================================================


def test_change_message_visibility(sqs_client: tuple[Any, str]) -> None:
    """Test changing message visibility timeout."""
    sqs, queue_url = sqs_client

    sqs.send_message(QueueUrl=queue_url, MessageBody="Test")

    # Receive message
    response = sqs.receive_message(QueueUrl=queue_url)
    receipt_handle = response["Messages"][0]["ReceiptHandle"]

    # Change visibility to 0 (make immediately visible)
    sqs.change_message_visibility(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle,
        VisibilityTimeout=0,
    )

    # Should be able to receive again
    response = sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=0)
    assert len(response.get("Messages", [])) == 1


# =============================================================================
# Queue Operations
# =============================================================================


@mock_aws
def test_list_queues() -> None:
    """Test listing queues."""
    sqs = boto3.client("sqs", region_name="us-east-1")

    # Create queues
    sqs.create_queue(QueueName="queue-1")
    sqs.create_queue(QueueName="queue-2")
    sqs.create_queue(QueueName="other-queue")

    # List all queues
    response = sqs.list_queues()
    assert len(response["QueueUrls"]) == 3

    # List with prefix
    response = sqs.list_queues(QueueNamePrefix="queue-")
    assert len(response["QueueUrls"]) == 2


@mock_aws
def test_delete_queue() -> None:
    """Test deleting a queue."""
    sqs = boto3.client("sqs", region_name="us-east-1")

    response = sqs.create_queue(QueueName="to-delete")
    queue_url = response["QueueUrl"]

    sqs.delete_queue(QueueUrl=queue_url)

    response = sqs.list_queues()
    assert "QueueUrls" not in response or len(response["QueueUrls"]) == 0


@mock_aws
def test_purge_queue() -> None:
    """Test purging all messages from a queue."""
    sqs = boto3.client("sqs", region_name="us-east-1")

    response = sqs.create_queue(QueueName="to-purge")
    queue_url = response["QueueUrl"]

    # Send messages
    for i in range(10):
        sqs.send_message(QueueUrl=queue_url, MessageBody=f"Message {i}")

    # Purge queue
    sqs.purge_queue(QueueUrl=queue_url)

    # Verify empty
    attrs = sqs.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=["ApproximateNumberOfMessages"],
    )
    assert int(attrs["Attributes"]["ApproximateNumberOfMessages"]) == 0


# =============================================================================
# Error Handling
# =============================================================================


@mock_aws
def test_receive_from_nonexistent_queue() -> None:
    """Test error when receiving from nonexistent queue."""
    sqs = boto3.client("sqs", region_name="us-east-1")

    with pytest.raises(ClientError) as exc_info:
        sqs.receive_message(
            QueueUrl="https://sqs.us-east-1.amazonaws.com/123456789/nonexistent"
        )

    assert "NonExistentQueue" in exc_info.value.response["Error"]["Code"]


# =============================================================================
# Message Processing Pattern
# =============================================================================


def test_message_processing_loop(sqs_client: tuple[Any, str]) -> None:
    """Test typical message processing pattern."""
    sqs, queue_url = sqs_client

    # Send test messages
    expected_events = [
        {"type": "order", "id": "001"},
        {"type": "order", "id": "002"},
        {"type": "payment", "id": "003"},
    ]

    for event in expected_events:
        sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(event))

    # Process messages
    processed = []

    while True:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=0,
        )

        if "Messages" not in response:
            break

        for message in response["Messages"]:
            event = json.loads(message["Body"])
            processed.append(event)

            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message["ReceiptHandle"],
            )

    assert len(processed) == 3
    assert all(e in processed for e in expected_events)
