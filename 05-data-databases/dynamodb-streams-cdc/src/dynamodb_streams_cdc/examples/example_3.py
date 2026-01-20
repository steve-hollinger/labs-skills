"""Example 3: Event-Driven Architecture

This example demonstrates a complete event-driven system with DynamoDB Streams,
including multiple consumers, error handling, and dead letter queues.

Key concepts:
- Publishing domain events from stream records
- Multiple consumers processing events
- Idempotent processing
- Dead letter queue for failed events
- Event fan-out pattern
"""

import json
from datetime import datetime
from decimal import Decimal
from typing import Any, Callable

import boto3
from moto import mock_aws

from dynamodb_streams_cdc.processor import (
    BatchProcessor,
    IdempotentProcessor,
    StreamRecord,
    create_dynamodb_idempotency_store,
)


class DomainEvent:
    """Domain event created from DynamoDB stream record."""

    def __init__(
        self,
        event_type: str,
        entity_type: str,
        entity_id: str,
        data: dict[str, Any],
        previous_data: dict[str, Any] | None = None,
        timestamp: str | None = None,
    ):
        self.event_type = event_type
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.data = data
        self.previous_data = previous_data
        self.timestamp = timestamp or datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "event_type": self.event_type,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "data": self._serialize_decimals(self.data),
            "previous_data": self._serialize_decimals(self.previous_data) if self.previous_data else None,
            "timestamp": self.timestamp,
        }

    def _serialize_decimals(self, obj: Any) -> Any:
        """Convert Decimals to strings for JSON serialization."""
        if isinstance(obj, Decimal):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: self._serialize_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_decimals(item) for item in obj]
        return obj

    @classmethod
    def from_stream_record(cls, record: StreamRecord) -> "DomainEvent":
        """Create domain event from stream record."""
        entity_type = record.get_entity_type().lower()

        event_type_map = {
            "INSERT": f"{entity_type}.created",
            "MODIFY": f"{entity_type}.updated",
            "REMOVE": f"{entity_type}.deleted",
        }

        entity_id = record.keys.get("PK", "")

        return cls(
            event_type=event_type_map.get(record.event_name, f"{entity_type}.changed"),
            entity_type=entity_type,
            entity_id=entity_id,
            data=record.new_image or record.old_image or {},
            previous_data=record.old_image if record.event_name == "MODIFY" else None,
        )


class EventPublisher:
    """Publishes domain events to multiple subscribers."""

    def __init__(self):
        self.subscribers: list[Callable[[DomainEvent], None]] = []

    def subscribe(self, handler: Callable[[DomainEvent], None]) -> None:
        """Add a subscriber to receive events."""
        self.subscribers.append(handler)

    def publish(self, event: DomainEvent) -> None:
        """Publish event to all subscribers."""
        for subscriber in self.subscribers:
            try:
                subscriber(event)
            except Exception as e:
                print(f"  Error in subscriber: {e}")


class NotificationService:
    """Sends notifications based on events."""

    def __init__(self):
        self.notifications_sent: list[dict[str, Any]] = []

    def handle_event(self, event: DomainEvent) -> None:
        """Handle events and send appropriate notifications."""
        if event.event_type == "user.created":
            self._send_welcome_notification(event)
        elif event.event_type == "order.created":
            self._send_order_confirmation(event)
        elif event.event_type == "order.updated":
            self._check_status_change(event)

    def _send_welcome_notification(self, event: DomainEvent) -> None:
        """Send welcome notification to new user."""
        email = event.data.get("email", "unknown")
        notification = {
            "type": "welcome",
            "to": email,
            "subject": "Welcome!",
            "timestamp": event.timestamp,
        }
        self.notifications_sent.append(notification)
        print(f"    [Notification] Welcome email to: {email}")

    def _send_order_confirmation(self, event: DomainEvent) -> None:
        """Send order confirmation."""
        order_id = event.data.get("order_id", "unknown")
        total = event.data.get("total", 0)
        notification = {
            "type": "order_confirmation",
            "order_id": order_id,
            "total": total,
            "timestamp": event.timestamp,
        }
        self.notifications_sent.append(notification)
        print(f"    [Notification] Order confirmation for: {order_id} (${total})")

    def _check_status_change(self, event: DomainEvent) -> None:
        """Check for status changes and notify."""
        if event.previous_data:
            old_status = event.previous_data.get("status")
            new_status = event.data.get("status")

            if old_status != new_status:
                notification = {
                    "type": "status_update",
                    "order_id": event.data.get("order_id"),
                    "old_status": old_status,
                    "new_status": new_status,
                    "timestamp": event.timestamp,
                }
                self.notifications_sent.append(notification)
                print(f"    [Notification] Order status: {old_status} -> {new_status}")


class AnalyticsService:
    """Records events for analytics."""

    def __init__(self):
        self.events_recorded: list[dict[str, Any]] = []

    def handle_event(self, event: DomainEvent) -> None:
        """Record event for analytics."""
        analytics_record = {
            "event_type": event.event_type,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "timestamp": event.timestamp,
        }
        self.events_recorded.append(analytics_record)
        print(f"    [Analytics] Recorded: {event.event_type}")


class SearchIndexer:
    """Updates search index based on events."""

    def __init__(self):
        self.index: dict[str, dict[str, Any]] = {}

    def handle_event(self, event: DomainEvent) -> None:
        """Update search index."""
        if event.event_type.endswith(".deleted"):
            if event.entity_id in self.index:
                del self.index[event.entity_id]
                print(f"    [Search] Removed from index: {event.entity_id}")
        else:
            self.index[event.entity_id] = event.data
            print(f"    [Search] Indexed: {event.entity_id}")


class DeadLetterQueue:
    """Stores failed events for later processing."""

    def __init__(self):
        self.failed_events: list[dict[str, Any]] = []

    def add(self, record: StreamRecord, error: Exception) -> None:
        """Add failed event to DLQ."""
        self.failed_events.append({
            "event_id": record.event_id,
            "event_name": record.event_name,
            "keys": record.keys,
            "error": str(error),
            "timestamp": datetime.utcnow().isoformat(),
        })
        print(f"    [DLQ] Added failed event: {record.event_id}")


def create_sample_events() -> list[dict[str, Any]]:
    """Create sample stream events for the demo."""
    return [
        # New user
        {
            "eventID": "evt-001",
            "eventName": "INSERT",
            "dynamodb": {
                "Keys": {"PK": {"S": "USER#user-001"}, "SK": {"S": "PROFILE#user-001"}},
                "NewImage": {
                    "PK": {"S": "USER#user-001"},
                    "SK": {"S": "PROFILE#user-001"},
                    "name": {"S": "Alice Smith"},
                    "email": {"S": "alice@example.com"},
                },
                "SequenceNumber": "1",
            },
        },
        # New order
        {
            "eventID": "evt-002",
            "eventName": "INSERT",
            "dynamodb": {
                "Keys": {"PK": {"S": "ORDER#order-001"}, "SK": {"S": "ORDER#order-001"}},
                "NewImage": {
                    "PK": {"S": "ORDER#order-001"},
                    "SK": {"S": "ORDER#order-001"},
                    "order_id": {"S": "order-001"},
                    "user_id": {"S": "user-001"},
                    "total": {"N": "99.99"},
                    "status": {"S": "pending"},
                },
                "SequenceNumber": "2",
            },
        },
        # Order shipped
        {
            "eventID": "evt-003",
            "eventName": "MODIFY",
            "dynamodb": {
                "Keys": {"PK": {"S": "ORDER#order-001"}, "SK": {"S": "ORDER#order-001"}},
                "OldImage": {
                    "PK": {"S": "ORDER#order-001"},
                    "order_id": {"S": "order-001"},
                    "status": {"S": "pending"},
                    "total": {"N": "99.99"},
                },
                "NewImage": {
                    "PK": {"S": "ORDER#order-001"},
                    "order_id": {"S": "order-001"},
                    "status": {"S": "shipped"},
                    "total": {"N": "99.99"},
                },
                "SequenceNumber": "3",
            },
        },
        # Product created
        {
            "eventID": "evt-004",
            "eventName": "INSERT",
            "dynamodb": {
                "Keys": {"PK": {"S": "PRODUCT#prod-001"}, "SK": {"S": "PRODUCT#prod-001"}},
                "NewImage": {
                    "PK": {"S": "PRODUCT#prod-001"},
                    "name": {"S": "Widget Pro"},
                    "price": {"N": "29.99"},
                    "category": {"S": "Electronics"},
                },
                "SequenceNumber": "4",
            },
        },
        # Duplicate event (testing idempotency)
        {
            "eventID": "evt-001",  # Same ID as first event!
            "eventName": "INSERT",
            "dynamodb": {
                "Keys": {"PK": {"S": "USER#user-001"}, "SK": {"S": "PROFILE#user-001"}},
                "NewImage": {
                    "PK": {"S": "USER#user-001"},
                    "name": {"S": "Alice Smith"},
                    "email": {"S": "alice@example.com"},
                },
                "SequenceNumber": "1",
            },
        },
    ]


@mock_aws
def main() -> None:
    """Run the event-driven architecture example."""
    print("Example 3: Event-Driven Architecture")
    print("=" * 50)

    # Set up DynamoDB for idempotency tracking
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    client = boto3.client("dynamodb", region_name="us-east-1")

    client.create_table(
        TableName="ProcessedEvents",
        KeySchema=[{"AttributeName": "eventID", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "eventID", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    processed_table = dynamodb.Table("ProcessedEvents")

    # Create services
    notification_service = NotificationService()
    analytics_service = AnalyticsService()
    search_indexer = SearchIndexer()
    dlq = DeadLetterQueue()

    # Create event publisher with subscribers
    publisher = EventPublisher()
    publisher.subscribe(notification_service.handle_event)
    publisher.subscribe(analytics_service.handle_event)
    publisher.subscribe(search_indexer.handle_event)

    # Create idempotency store
    is_processed, mark_processed = create_dynamodb_idempotency_store(processed_table)

    # Main processing function
    def process_record(record: StreamRecord) -> None:
        print(f"\nProcessing: {record.event_name} - {record.keys.get('PK')}")

        # Create and publish domain event
        domain_event = DomainEvent.from_stream_record(record)
        print(f"  Domain Event: {domain_event.event_type}")

        publisher.publish(domain_event)

    # Wrap with idempotency
    idempotent_processor = IdempotentProcessor(
        processor=process_record,
        is_processed=is_processed,
        mark_processed=mark_processed,
    )

    # Process events
    print("\n--- Processing Stream Events ---")

    events = create_sample_events()
    processed_count = 0
    skipped_count = 0

    for raw_record in events:
        record = StreamRecord.from_raw(raw_record)

        try:
            was_processed = idempotent_processor.process(record)
            if was_processed:
                processed_count += 1
            else:
                skipped_count += 1
                print(f"\n  [SKIPPED] Duplicate: {record.event_id}")
        except Exception as e:
            dlq.add(record, e)

    # Summary
    print("\n" + "=" * 50)
    print("--- Processing Summary ---\n")

    print(f"Events processed: {processed_count}")
    print(f"Duplicates skipped: {skipped_count}")
    print(f"Failed (in DLQ): {len(dlq.failed_events)}")

    print(f"\nNotifications sent: {len(notification_service.notifications_sent)}")
    for notif in notification_service.notifications_sent:
        print(f"  - {notif['type']}: {notif.get('to') or notif.get('order_id')}")

    print(f"\nAnalytics events: {len(analytics_service.events_recorded)}")
    for event in analytics_service.events_recorded:
        print(f"  - {event['event_type']}")

    print(f"\nSearch index entries: {len(search_indexer.index)}")
    for entity_id in search_indexer.index:
        print(f"  - {entity_id}")

    print("\n" + "=" * 50)
    print("Key Takeaways:")
    print("1. Transform stream records to domain events")
    print("2. Fan-out to multiple consumers/services")
    print("3. Use idempotency tracking for exactly-once semantics")
    print("4. Dead letter queue for failed events")
    print("5. Each consumer handles events independently")
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
