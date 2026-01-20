"""DynamoDB Stream Processor.

Provides utilities for processing DynamoDB Stream events with
support for idempotency, partial batch failures, and event routing.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from dynamodb_streams_cdc.deserializer import deserialize_dynamodb_item


@dataclass
class StreamRecord:
    """Parsed stream record with deserialized data."""

    event_id: str
    event_name: str  # INSERT, MODIFY, REMOVE
    keys: dict[str, Any]
    new_image: dict[str, Any] | None
    old_image: dict[str, Any] | None
    sequence_number: str
    approximate_creation_time: datetime | None

    @classmethod
    def from_raw(cls, record: dict[str, Any]) -> "StreamRecord":
        """Create StreamRecord from raw Lambda event record.

        Args:
            record: Raw stream record from Lambda event

        Returns:
            Parsed StreamRecord
        """
        dynamodb = record.get("dynamodb", {})

        creation_time = None
        if "ApproximateCreationDateTime" in dynamodb:
            creation_time = datetime.fromtimestamp(
                dynamodb["ApproximateCreationDateTime"]
            )

        return cls(
            event_id=record["eventID"],
            event_name=record["eventName"],
            keys=deserialize_dynamodb_item(dynamodb.get("Keys", {})),
            new_image=deserialize_dynamodb_item(dynamodb.get("NewImage", {}))
            if "NewImage" in dynamodb
            else None,
            old_image=deserialize_dynamodb_item(dynamodb.get("OldImage", {}))
            if "OldImage" in dynamodb
            else None,
            sequence_number=dynamodb.get("SequenceNumber", ""),
            approximate_creation_time=creation_time,
        )

    def get_entity_type(self) -> str:
        """Extract entity type from partition key.

        Assumes format: ENTITY_TYPE#id

        Returns:
            Entity type string (e.g., "USER", "ORDER")
        """
        pk = self.keys.get("PK", "")
        if "#" in pk:
            return pk.split("#")[0]
        return pk

    def get_changes(self) -> dict[str, tuple[Any, Any]]:
        """Compute field-level changes between old and new images.

        Returns:
            Dictionary of {field: (old_value, new_value)} for changed fields
        """
        if self.event_name == "INSERT":
            return {
                key: (None, value) for key, value in (self.new_image or {}).items()
            }
        elif self.event_name == "REMOVE":
            return {
                key: (value, None) for key, value in (self.old_image or {}).items()
            }
        elif self.event_name == "MODIFY":
            old = self.old_image or {}
            new = self.new_image or {}
            all_keys = set(old.keys()) | set(new.keys())
            changes = {}
            for key in all_keys:
                old_val = old.get(key)
                new_val = new.get(key)
                if old_val != new_val:
                    changes[key] = (old_val, new_val)
            return changes
        return {}


class StreamProcessor(ABC):
    """Abstract base class for stream processors."""

    @abstractmethod
    def on_insert(self, record: StreamRecord) -> None:
        """Handle INSERT events.

        Args:
            record: Parsed stream record
        """
        pass

    @abstractmethod
    def on_modify(self, record: StreamRecord) -> None:
        """Handle MODIFY events.

        Args:
            record: Parsed stream record
        """
        pass

    @abstractmethod
    def on_remove(self, record: StreamRecord) -> None:
        """Handle REMOVE events.

        Args:
            record: Parsed stream record
        """
        pass

    def process(self, record: StreamRecord) -> None:
        """Route record to appropriate handler.

        Args:
            record: Parsed stream record
        """
        if record.event_name == "INSERT":
            self.on_insert(record)
        elif record.event_name == "MODIFY":
            self.on_modify(record)
        elif record.event_name == "REMOVE":
            self.on_remove(record)


class BatchProcessor:
    """Process batches of stream records with error handling."""

    def __init__(
        self,
        processor: Callable[[StreamRecord], None],
        on_error: Callable[[StreamRecord, Exception], bool] | None = None,
    ):
        """Initialize batch processor.

        Args:
            processor: Function to process each record
            on_error: Error handler that returns True to retry, False to skip
        """
        self.processor = processor
        self.on_error = on_error

    def process_batch(
        self, event: dict[str, Any]
    ) -> dict[str, list[dict[str, str]]]:
        """Process a batch of stream records from Lambda event.

        Implements partial batch failure reporting.

        Args:
            event: Lambda event containing stream records

        Returns:
            Response with batchItemFailures for Lambda
        """
        batch_item_failures: list[dict[str, str]] = []

        for raw_record in event.get("Records", []):
            record = StreamRecord.from_raw(raw_record)

            try:
                self.processor(record)
            except Exception as e:
                should_retry = True
                if self.on_error:
                    should_retry = self.on_error(record, e)

                if should_retry:
                    batch_item_failures.append(
                        {"itemIdentifier": record.event_id}
                    )

        return {"batchItemFailures": batch_item_failures}


class IdempotentProcessor:
    """Wrapper that adds idempotency to stream processing."""

    def __init__(
        self,
        processor: Callable[[StreamRecord], None],
        is_processed: Callable[[str], bool],
        mark_processed: Callable[[str], None],
    ):
        """Initialize idempotent processor.

        Args:
            processor: Function to process each record
            is_processed: Check if event_id was already processed
            mark_processed: Mark event_id as processed
        """
        self.processor = processor
        self.is_processed = is_processed
        self.mark_processed = mark_processed

    def process(self, record: StreamRecord) -> bool:
        """Process record with idempotency check.

        Args:
            record: Stream record to process

        Returns:
            True if processed, False if skipped (duplicate)
        """
        if self.is_processed(record.event_id):
            return False

        self.processor(record)
        self.mark_processed(record.event_id)
        return True


def process_stream_event(
    event: dict[str, Any],
    handler: Callable[[StreamRecord], None],
) -> dict[str, list[dict[str, str]]]:
    """Process DynamoDB Stream Lambda event with partial batch failure support.

    This is a simple wrapper for common use cases.

    Args:
        event: Lambda event containing stream records
        handler: Function to process each record

    Returns:
        Response with batchItemFailures for Lambda

    Example:
        >>> def my_handler(record: StreamRecord) -> None:
        ...     print(f"Processing {record.event_name}: {record.keys}")
        ...
        >>> def lambda_handler(event, context):
        ...     return process_stream_event(event, my_handler)
    """
    batch_processor = BatchProcessor(handler)
    return batch_processor.process_batch(event)


def create_dynamodb_idempotency_store(
    table: Any, ttl_seconds: int = 86400
) -> tuple[Callable[[str], bool], Callable[[str], None]]:
    """Create idempotency functions backed by DynamoDB.

    Args:
        table: DynamoDB table resource for storing processed event IDs
        ttl_seconds: TTL for processed records (default: 24 hours)

    Returns:
        Tuple of (is_processed, mark_processed) functions
    """
    import time

    def is_processed(event_id: str) -> bool:
        response = table.get_item(Key={"eventID": event_id})
        return "Item" in response

    def mark_processed(event_id: str) -> None:
        table.put_item(
            Item={
                "eventID": event_id,
                "processed_at": datetime.utcnow().isoformat(),
                "ttl": int(time.time()) + ttl_seconds,
            }
        )

    return is_processed, mark_processed
