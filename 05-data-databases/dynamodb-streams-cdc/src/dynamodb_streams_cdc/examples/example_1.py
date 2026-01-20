"""Example 1: Basic Stream Processing

This example demonstrates the fundamentals of DynamoDB Streams processing,
including deserializing records and routing by event type.

Key concepts:
- Stream record structure
- Deserializing DynamoDB wire format
- Handling INSERT, MODIFY, REMOVE events
- Simulating stream processing locally
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

import boto3
from moto import mock_aws

from dynamodb_streams_cdc.deserializer import (
    deserialize_dynamodb_item,
    serialize_dynamodb_item,
)
from dynamodb_streams_cdc.processor import StreamRecord


def create_sample_stream_records() -> list[dict[str, Any]]:
    """Create sample stream records for demonstration.

    In production, these records come from Lambda event source mapping.

    Returns:
        List of simulated stream records
    """
    return [
        # INSERT event - new user created
        {
            "eventID": "evt-001",
            "eventName": "INSERT",
            "eventSource": "aws:dynamodb",
            "dynamodb": {
                "Keys": {
                    "PK": {"S": "USER#user-123"},
                    "SK": {"S": "PROFILE#user-123"},
                },
                "NewImage": {
                    "PK": {"S": "USER#user-123"},
                    "SK": {"S": "PROFILE#user-123"},
                    "name": {"S": "Alice Smith"},
                    "email": {"S": "alice@example.com"},
                    "created_at": {"S": "2024-01-15T10:00:00Z"},
                },
                "SequenceNumber": "100000000000000000001",
                "SizeBytes": 256,
                "StreamViewType": "NEW_AND_OLD_IMAGES",
                "ApproximateCreationDateTime": 1705312800,
            },
        },
        # MODIFY event - user updated
        {
            "eventID": "evt-002",
            "eventName": "MODIFY",
            "eventSource": "aws:dynamodb",
            "dynamodb": {
                "Keys": {
                    "PK": {"S": "USER#user-123"},
                    "SK": {"S": "PROFILE#user-123"},
                },
                "OldImage": {
                    "PK": {"S": "USER#user-123"},
                    "SK": {"S": "PROFILE#user-123"},
                    "name": {"S": "Alice Smith"},
                    "email": {"S": "alice@example.com"},
                    "created_at": {"S": "2024-01-15T10:00:00Z"},
                },
                "NewImage": {
                    "PK": {"S": "USER#user-123"},
                    "SK": {"S": "PROFILE#user-123"},
                    "name": {"S": "Alice Johnson"},
                    "email": {"S": "alice.johnson@example.com"},
                    "created_at": {"S": "2024-01-15T10:00:00Z"},
                    "updated_at": {"S": "2024-01-16T14:00:00Z"},
                },
                "SequenceNumber": "100000000000000000002",
                "SizeBytes": 512,
                "StreamViewType": "NEW_AND_OLD_IMAGES",
                "ApproximateCreationDateTime": 1705413600,
            },
        },
        # INSERT event - order created
        {
            "eventID": "evt-003",
            "eventName": "INSERT",
            "eventSource": "aws:dynamodb",
            "dynamodb": {
                "Keys": {
                    "PK": {"S": "USER#user-123"},
                    "SK": {"S": "ORDER#2024-01-16#order-456"},
                },
                "NewImage": {
                    "PK": {"S": "USER#user-123"},
                    "SK": {"S": "ORDER#2024-01-16#order-456"},
                    "order_id": {"S": "order-456"},
                    "total": {"N": "99.99"},
                    "status": {"S": "pending"},
                    "items": {
                        "L": [
                            {
                                "M": {
                                    "product_id": {"S": "prod-001"},
                                    "quantity": {"N": "2"},
                                    "price": {"N": "49.99"},
                                }
                            }
                        ]
                    },
                },
                "SequenceNumber": "100000000000000000003",
                "SizeBytes": 384,
                "StreamViewType": "NEW_AND_OLD_IMAGES",
                "ApproximateCreationDateTime": 1705413700,
            },
        },
        # REMOVE event - user deleted
        {
            "eventID": "evt-004",
            "eventName": "REMOVE",
            "eventSource": "aws:dynamodb",
            "dynamodb": {
                "Keys": {
                    "PK": {"S": "USER#user-999"},
                    "SK": {"S": "PROFILE#user-999"},
                },
                "OldImage": {
                    "PK": {"S": "USER#user-999"},
                    "SK": {"S": "PROFILE#user-999"},
                    "name": {"S": "Test User"},
                    "email": {"S": "test@example.com"},
                },
                "SequenceNumber": "100000000000000000004",
                "SizeBytes": 128,
                "StreamViewType": "NEW_AND_OLD_IMAGES",
                "ApproximateCreationDateTime": 1705413800,
            },
        },
    ]


def basic_stream_handler(record: StreamRecord) -> None:
    """Basic handler that logs stream events.

    This demonstrates the simplest form of stream processing.

    Args:
        record: Parsed stream record
    """
    print(f"\n  Event ID: {record.event_id}")
    print(f"  Event Type: {record.event_name}")
    print(f"  Entity Type: {record.get_entity_type()}")
    print(f"  Keys: {record.keys}")

    if record.event_name == "INSERT":
        print(f"  New Item: {record.new_image}")

    elif record.event_name == "MODIFY":
        changes = record.get_changes()
        print(f"  Changes:")
        for field, (old_val, new_val) in changes.items():
            print(f"    - {field}: '{old_val}' -> '{new_val}'")

    elif record.event_name == "REMOVE":
        print(f"  Deleted Item: {record.old_image}")


def lambda_handler_example(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Example Lambda handler for DynamoDB Streams.

    This shows how a real Lambda function would be structured.

    Args:
        event: Lambda event with stream records
        context: Lambda context (unused in this example)

    Returns:
        Response with any batch failures
    """
    print(f"Processing {len(event.get('Records', []))} records")

    batch_failures = []

    for raw_record in event.get("Records", []):
        record = StreamRecord.from_raw(raw_record)

        try:
            # Route to handlers based on event type
            if record.event_name == "INSERT":
                handle_insert(record)
            elif record.event_name == "MODIFY":
                handle_modify(record)
            elif record.event_name == "REMOVE":
                handle_remove(record)

        except Exception as e:
            print(f"Error processing {record.event_id}: {e}")
            batch_failures.append({"itemIdentifier": record.event_id})

    return {"batchItemFailures": batch_failures}


def handle_insert(record: StreamRecord) -> None:
    """Handle INSERT events."""
    entity_type = record.get_entity_type()
    print(f"New {entity_type} created: {record.keys}")

    # Example: Send welcome email for new users
    if entity_type == "USER":
        email = record.new_image.get("email") if record.new_image else None
        print(f"  -> Would send welcome email to: {email}")


def handle_modify(record: StreamRecord) -> None:
    """Handle MODIFY events."""
    changes = record.get_changes()
    print(f"Item modified: {record.keys}")
    print(f"  -> Changed fields: {list(changes.keys())}")

    # Example: Notify on status changes
    if "status" in changes:
        old_status, new_status = changes["status"]
        print(f"  -> Status changed: {old_status} -> {new_status}")


def handle_remove(record: StreamRecord) -> None:
    """Handle REMOVE events."""
    print(f"Item deleted: {record.keys}")

    # Example: Cleanup related data
    entity_type = record.get_entity_type()
    if entity_type == "USER":
        print("  -> Would cleanup user's related data")


def main() -> None:
    """Run the basic stream processing example."""
    print("Example 1: Basic Stream Processing")
    print("=" * 50)

    # Create sample stream records
    stream_records = create_sample_stream_records()

    print(f"\n--- Processing {len(stream_records)} Stream Records ---")

    for raw_record in stream_records:
        record = StreamRecord.from_raw(raw_record)
        basic_stream_handler(record)

    # Demonstrate Lambda handler format
    print("\n" + "=" * 50)
    print("--- Lambda Handler Simulation ---\n")

    lambda_event = {"Records": stream_records}
    result = lambda_handler_example(lambda_event, None)

    print(f"\nLambda Response: {result}")

    print("\n" + "=" * 50)
    print("Key Takeaways:")
    print("1. Stream records contain eventName (INSERT/MODIFY/REMOVE)")
    print("2. DynamoDB wire format uses type descriptors (S, N, L, M, etc.)")
    print("3. Route processing based on event type")
    print("4. Return batchItemFailures for partial batch failures")
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
