"""Example 3: SQS Mocking with moto

This example demonstrates how to mock SQS operations using moto,
including queue creation, message sending/receiving, and visibility handling.
"""

import json
import os


def setup_aws_credentials() -> None:
    """Set up fake AWS credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


def main() -> None:
    """Demonstrate SQS mocking with moto."""
    print("Example 3: SQS Mocking with moto")
    print("=" * 50)
    print()

    # Show basic operations
    print("1. Basic SQS Operations")
    print("-" * 40)
    print("""
    import boto3
    from moto import mock_aws

    @mock_aws
    def test_sqs_basic():
        sqs = boto3.client("sqs", region_name="us-east-1")

        # Create queue
        response = sqs.create_queue(QueueName="my-queue")
        queue_url = response["QueueUrl"]

        # Send message
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody="Hello, World!",
        )

        # Receive message
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
        )

        message = response["Messages"][0]
        assert message["Body"] == "Hello, World!"

        # Delete message
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=message["ReceiptHandle"],
        )
    """)

    # Show JSON messages
    print("2. JSON Message Handling")
    print("-" * 40)
    print("""
    import json

    @mock_aws
    def test_json_messages():
        sqs = boto3.client("sqs", region_name="us-east-1")
        response = sqs.create_queue(QueueName="events-queue")
        queue_url = response["QueueUrl"]

        # Send JSON message
        event = {
            "event_type": "user_created",
            "user_id": "123",
            "timestamp": "2024-01-15T10:30:00Z",
        }
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(event),
        )

        # Receive and parse
        response = sqs.receive_message(QueueUrl=queue_url)
        message = response["Messages"][0]
        received_event = json.loads(message["Body"])

        assert received_event["event_type"] == "user_created"
        assert received_event["user_id"] == "123"
    """)

    # Show batch operations
    print("3. Batch Operations")
    print("-" * 40)
    print("""
    @mock_aws
    def test_batch_operations():
        sqs = boto3.client("sqs", region_name="us-east-1")
        response = sqs.create_queue(QueueName="batch-queue")
        queue_url = response["QueueUrl"]

        # Send batch of messages
        entries = [
            {"Id": str(i), "MessageBody": f"Message {i}"}
            for i in range(10)
        ]
        sqs.send_message_batch(QueueUrl=queue_url, Entries=entries)

        # Receive multiple messages
        all_messages = []
        while True:
            response = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=0,
            )
            if "Messages" not in response:
                break
            all_messages.extend(response["Messages"])

        assert len(all_messages) == 10
    """)

    # Show message attributes
    print("4. Message Attributes")
    print("-" * 40)
    print("""
    @mock_aws
    def test_message_attributes():
        sqs = boto3.client("sqs", region_name="us-east-1")
        response = sqs.create_queue(QueueName="attr-queue")
        queue_url = response["QueueUrl"]

        # Send with attributes
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody="Order notification",
            MessageAttributes={
                "priority": {
                    "DataType": "String",
                    "StringValue": "high",
                },
                "order_id": {
                    "DataType": "Number",
                    "StringValue": "12345",
                },
            },
        )

        # Receive with attributes
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MessageAttributeNames=["All"],
        )

        message = response["Messages"][0]
        attrs = message["MessageAttributes"]
        assert attrs["priority"]["StringValue"] == "high"
    """)

    # Show visibility timeout
    print("5. Visibility Timeout")
    print("-" * 40)
    print("""
    @mock_aws
    def test_visibility_timeout():
        sqs = boto3.client("sqs", region_name="us-east-1")
        response = sqs.create_queue(
            QueueName="timeout-queue",
            Attributes={"VisibilityTimeout": "30"},
        )
        queue_url = response["QueueUrl"]

        sqs.send_message(QueueUrl=queue_url, MessageBody="Test")

        # First receive - message becomes invisible
        response = sqs.receive_message(QueueUrl=queue_url)
        message = response["Messages"][0]

        # Change visibility timeout
        sqs.change_message_visibility(
            QueueUrl=queue_url,
            ReceiptHandle=message["ReceiptHandle"],
            VisibilityTimeout=0,  # Make immediately visible again
        )

        # Can receive again
        response = sqs.receive_message(QueueUrl=queue_url)
        assert "Messages" in response
    """)

    # Run actual demo
    print("6. Live Demo")
    print("-" * 40)

    setup_aws_credentials()

    import boto3
    from moto import mock_aws

    with mock_aws():
        sqs = boto3.client("sqs", region_name="us-east-1")

        # Create queue
        response = sqs.create_queue(QueueName="demo-queue")
        queue_url = response["QueueUrl"]
        print(f"Created queue: {queue_url}")

        # Send messages
        events = [
            {"type": "order_created", "order_id": "001", "amount": 99.99},
            {"type": "order_shipped", "order_id": "001", "carrier": "FedEx"},
            {"type": "order_created", "order_id": "002", "amount": 149.99},
        ]

        for event in events:
            sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(event),
                MessageAttributes={
                    "event_type": {
                        "DataType": "String",
                        "StringValue": event["type"],
                    }
                },
            )
            print(f"Sent: {event['type']} for order {event.get('order_id', 'N/A')}")

        # Get queue attributes
        response = sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=["ApproximateNumberOfMessages"],
        )
        print(f"\nMessages in queue: {response['Attributes']['ApproximateNumberOfMessages']}")

        # Process messages
        print("\nProcessing messages:")
        processed = 0
        while True:
            response = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=10,
                MessageAttributeNames=["All"],
                WaitTimeSeconds=0,
            )

            if "Messages" not in response:
                break

            for message in response["Messages"]:
                event = json.loads(message["Body"])
                event_type = message["MessageAttributes"]["event_type"]["StringValue"]
                print(f"  Processing: {event_type} - {event}")

                # Delete after processing
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message["ReceiptHandle"],
                )
                processed += 1

        print(f"\nProcessed {processed} messages")

    print()
    print("Run the tests with:")
    print("  pytest tests/test_sqs.py -v")
    print()
    print("Example completed!")


if __name__ == "__main__":
    main()
