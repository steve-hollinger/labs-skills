"""Exercise 3: Implement Event Sourcing with Streams

Build an event sourcing system where DynamoDB Streams events are stored
as immutable events and used to reconstruct entity state.

Requirements:
1. Store all events in an event store
2. Reconstruct entity state from events
3. Support point-in-time queries
4. Implement snapshots for performance

Instructions:
1. Create an EventStore that persists all events
2. Implement state reconstruction from events
3. Add snapshot support for large event histories
4. Handle concurrent modifications

Hints:
- Events are immutable - never modify them
- State is derived by replaying events
- Snapshots avoid replaying entire history
- Use sequence numbers for ordering
"""

from datetime import datetime
from decimal import Decimal
from typing import Any
import json

import boto3
from moto import mock_aws

from dynamodb_streams_cdc.processor import StreamRecord


class Event:
    """Immutable event in the event store."""

    def __init__(
        self,
        event_id: str,
        entity_id: str,
        event_type: str,
        data: dict[str, Any],
        timestamp: str,
        sequence_number: int,
    ):
        self.event_id = event_id
        self.entity_id = entity_id
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp
        self.sequence_number = sequence_number

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "event_id": self.event_id,
            "entity_id": self.entity_id,
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp,
            "sequence_number": self.sequence_number,
        }


class EventStore:
    """Stores and retrieves events for event sourcing."""

    def __init__(self, events_table: Any, snapshots_table: Any):
        """Initialize event store.

        Args:
            events_table: DynamoDB table for events
            snapshots_table: DynamoDB table for snapshots
        """
        self.events_table = events_table
        self.snapshots_table = snapshots_table
        self.snapshot_frequency = 10  # Create snapshot every N events

    def append_event(self, event: Event) -> None:
        """Append an event to the store.

        TODO: Implement event storage.

        Events should be:
        - Immutable (never updated)
        - Ordered by sequence number
        - Queryable by entity

        Args:
            event: Event to store
        """
        # TODO: Store event in events_table
        # PK: ENTITY#{entity_id}
        # SK: EVENT#{sequence_number:010d}
        pass

    def get_events(
        self,
        entity_id: str,
        after_sequence: int = 0,
    ) -> list[Event]:
        """Get events for an entity after a sequence number.

        TODO: Implement event retrieval.

        Args:
            entity_id: Entity to get events for
            after_sequence: Return events after this sequence number

        Returns:
            List of events in order
        """
        # TODO: Query events after sequence number
        pass

    def get_all_events(self, entity_id: str) -> list[Event]:
        """Get all events for an entity."""
        return self.get_events(entity_id, after_sequence=0)


class SnapshotStore:
    """Manages entity snapshots for faster reconstruction."""

    def __init__(self, snapshots_table: Any):
        """Initialize snapshot store.

        Args:
            snapshots_table: DynamoDB table for snapshots
        """
        self.snapshots_table = snapshots_table

    def save_snapshot(
        self,
        entity_id: str,
        state: dict[str, Any],
        sequence_number: int,
    ) -> None:
        """Save a snapshot of entity state.

        TODO: Implement snapshot storage.

        Args:
            entity_id: Entity ID
            state: Current entity state
            sequence_number: Sequence number at this state
        """
        # TODO: Store snapshot
        pass

    def get_latest_snapshot(
        self,
        entity_id: str,
    ) -> tuple[dict[str, Any], int] | None:
        """Get the latest snapshot for an entity.

        TODO: Implement snapshot retrieval.

        Args:
            entity_id: Entity ID

        Returns:
            Tuple of (state, sequence_number) or None
        """
        # TODO: Get most recent snapshot
        pass


class EntityReconstructor:
    """Reconstructs entity state from events."""

    def __init__(self, event_store: EventStore, snapshot_store: SnapshotStore):
        """Initialize reconstructor.

        Args:
            event_store: Event store
            snapshot_store: Snapshot store
        """
        self.event_store = event_store
        self.snapshot_store = snapshot_store

    def reconstruct(self, entity_id: str) -> dict[str, Any]:
        """Reconstruct entity state from events.

        TODO: Implement state reconstruction.

        Steps:
        1. Try to get latest snapshot
        2. Get events after snapshot (or all events)
        3. Apply events to state
        4. Return final state

        Args:
            entity_id: Entity to reconstruct

        Returns:
            Current entity state
        """
        # TODO: Implement reconstruction logic
        pass

    def reconstruct_at_time(
        self,
        entity_id: str,
        timestamp: str,
    ) -> dict[str, Any]:
        """Reconstruct entity state at a specific point in time.

        TODO: Implement point-in-time reconstruction.

        Args:
            entity_id: Entity ID
            timestamp: ISO timestamp to reconstruct at

        Returns:
            Entity state at that time
        """
        # TODO: Apply events only up to timestamp
        pass

    def _apply_event(
        self,
        state: dict[str, Any],
        event: Event,
    ) -> dict[str, Any]:
        """Apply an event to update state.

        TODO: Implement event application.

        Args:
            state: Current state
            event: Event to apply

        Returns:
            Updated state
        """
        # TODO: Handle different event types
        # - entity.created: Set initial state
        # - entity.updated: Merge changes
        # - entity.deleted: Mark as deleted
        pass


class StreamToEventAdapter:
    """Converts DynamoDB stream records to domain events."""

    def __init__(self, event_store: EventStore):
        """Initialize adapter.

        Args:
            event_store: Event store to write to
        """
        self.event_store = event_store
        self.sequence_counters: dict[str, int] = {}

    def process_record(self, record: StreamRecord) -> Event:
        """Convert stream record to event and store it.

        TODO: Implement stream to event conversion.

        Args:
            record: Stream record

        Returns:
            Created event
        """
        # TODO: Convert record to Event and store
        pass

    def _get_next_sequence(self, entity_id: str) -> int:
        """Get next sequence number for entity.

        TODO: Implement sequence number generation.

        Args:
            entity_id: Entity ID

        Returns:
            Next sequence number
        """
        # TODO: Track and increment sequence
        pass


def create_sample_events() -> list[dict[str, Any]]:
    """Create sample events showing order lifecycle."""
    return [
        # Order created
        {
            "eventID": "evt-001",
            "eventName": "INSERT",
            "dynamodb": {
                "Keys": {"PK": {"S": "ORDER#order-001"}, "SK": {"S": "ORDER#order-001"}},
                "NewImage": {
                    "PK": {"S": "ORDER#order-001"},
                    "order_id": {"S": "order-001"},
                    "user_id": {"S": "user-001"},
                    "status": {"S": "pending"},
                    "total": {"N": "99.99"},
                    "items": {"L": [{"M": {"product": {"S": "Widget"}, "qty": {"N": "2"}}}]},
                },
                "SequenceNumber": "1",
            },
        },
        # Order confirmed
        {
            "eventID": "evt-002",
            "eventName": "MODIFY",
            "dynamodb": {
                "Keys": {"PK": {"S": "ORDER#order-001"}, "SK": {"S": "ORDER#order-001"}},
                "OldImage": {
                    "PK": {"S": "ORDER#order-001"},
                    "status": {"S": "pending"},
                    "total": {"N": "99.99"},
                },
                "NewImage": {
                    "PK": {"S": "ORDER#order-001"},
                    "status": {"S": "confirmed"},
                    "total": {"N": "99.99"},
                    "confirmed_at": {"S": "2024-01-15T10:30:00Z"},
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
                    "status": {"S": "confirmed"},
                },
                "NewImage": {
                    "PK": {"S": "ORDER#order-001"},
                    "status": {"S": "shipped"},
                    "shipped_at": {"S": "2024-01-16T14:00:00Z"},
                    "tracking_number": {"S": "TRACK123456"},
                },
                "SequenceNumber": "3",
            },
        },
        # Order delivered
        {
            "eventID": "evt-004",
            "eventName": "MODIFY",
            "dynamodb": {
                "Keys": {"PK": {"S": "ORDER#order-001"}, "SK": {"S": "ORDER#order-001"}},
                "OldImage": {
                    "PK": {"S": "ORDER#order-001"},
                    "status": {"S": "shipped"},
                },
                "NewImage": {
                    "PK": {"S": "ORDER#order-001"},
                    "status": {"S": "delivered"},
                    "delivered_at": {"S": "2024-01-18T09:00:00Z"},
                },
                "SequenceNumber": "4",
            },
        },
    ]


@mock_aws
def exercise() -> None:
    """Test your event sourcing implementation."""
    print("Exercise 3: Event Sourcing")
    print("=" * 50)

    # TODO: Set up DynamoDB tables
    # TODO: Create EventStore, SnapshotStore, EntityReconstructor
    # TODO: Process sample events
    # TODO: Reconstruct entity state
    # TODO: Test point-in-time queries

    print("\nImplement the TODO sections and verify:")
    print("1. All events are stored immutably")
    print("2. Entity state can be reconstructed from events")
    print("3. Point-in-time queries return correct state")
    print("4. Snapshots speed up reconstruction")


if __name__ == "__main__":
    exercise()
