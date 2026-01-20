"""Tests for DynamoDB Streams CDC examples."""

from decimal import Decimal
from typing import Any

import boto3
import pytest
from moto import mock_aws

from dynamodb_streams_cdc.deserializer import (
    deserialize_dynamodb_item,
    deserialize_value,
    serialize_dynamodb_item,
    serialize_value,
)
from dynamodb_streams_cdc.processor import (
    BatchProcessor,
    IdempotentProcessor,
    StreamProcessor,
    StreamRecord,
    process_stream_event,
)


class TestDeserializer:
    """Tests for DynamoDB deserializer."""

    def test_deserialize_string(self) -> None:
        """Test deserializing string values."""
        assert deserialize_value({"S": "hello"}) == "hello"

    def test_deserialize_number(self) -> None:
        """Test deserializing number values."""
        result = deserialize_value({"N": "42.5"})
        assert result == Decimal("42.5")

    def test_deserialize_boolean(self) -> None:
        """Test deserializing boolean values."""
        assert deserialize_value({"BOOL": True}) is True
        assert deserialize_value({"BOOL": False}) is False

    def test_deserialize_null(self) -> None:
        """Test deserializing null values."""
        assert deserialize_value({"NULL": True}) is None

    def test_deserialize_list(self) -> None:
        """Test deserializing list values."""
        result = deserialize_value({
            "L": [{"S": "a"}, {"S": "b"}, {"N": "1"}]
        })
        assert result == ["a", "b", Decimal("1")]

    def test_deserialize_map(self) -> None:
        """Test deserializing map values."""
        result = deserialize_value({
            "M": {
                "name": {"S": "Alice"},
                "age": {"N": "30"}
            }
        })
        assert result == {"name": "Alice", "age": Decimal("30")}

    def test_deserialize_string_set(self) -> None:
        """Test deserializing string set values."""
        result = deserialize_value({"SS": ["a", "b", "c"]})
        assert result == {"a", "b", "c"}

    def test_deserialize_item(self) -> None:
        """Test deserializing complete item."""
        item = {
            "PK": {"S": "USER#123"},
            "SK": {"S": "PROFILE#123"},
            "name": {"S": "Alice"},
            "age": {"N": "30"},
            "active": {"BOOL": True},
        }
        result = deserialize_dynamodb_item(item)

        assert result["PK"] == "USER#123"
        assert result["name"] == "Alice"
        assert result["age"] == Decimal("30")
        assert result["active"] is True

    def test_serialize_roundtrip(self) -> None:
        """Test serialization and deserialization roundtrip."""
        original = {
            "name": "Alice",
            "age": 30,
            "active": True,
            "tags": ["python", "aws"],
        }
        serialized = serialize_dynamodb_item(original)
        deserialized = deserialize_dynamodb_item(serialized)

        assert deserialized["name"] == "Alice"
        assert deserialized["age"] == Decimal("30")
        assert deserialized["active"] is True
        assert deserialized["tags"] == ["python", "aws"]


class TestStreamRecord:
    """Tests for StreamRecord parsing."""

    def test_parse_insert_record(self) -> None:
        """Test parsing INSERT stream record."""
        raw = {
            "eventID": "evt-001",
            "eventName": "INSERT",
            "dynamodb": {
                "Keys": {"PK": {"S": "USER#123"}, "SK": {"S": "PROFILE#123"}},
                "NewImage": {
                    "PK": {"S": "USER#123"},
                    "name": {"S": "Alice"},
                },
                "SequenceNumber": "100",
            },
        }

        record = StreamRecord.from_raw(raw)

        assert record.event_id == "evt-001"
        assert record.event_name == "INSERT"
        assert record.keys["PK"] == "USER#123"
        assert record.new_image["name"] == "Alice"
        assert record.old_image is None

    def test_parse_modify_record(self) -> None:
        """Test parsing MODIFY stream record."""
        raw = {
            "eventID": "evt-002",
            "eventName": "MODIFY",
            "dynamodb": {
                "Keys": {"PK": {"S": "USER#123"}, "SK": {"S": "PROFILE#123"}},
                "OldImage": {"name": {"S": "Alice"}},
                "NewImage": {"name": {"S": "Alice Smith"}},
                "SequenceNumber": "101",
            },
        }

        record = StreamRecord.from_raw(raw)

        assert record.event_name == "MODIFY"
        assert record.old_image["name"] == "Alice"
        assert record.new_image["name"] == "Alice Smith"

    def test_parse_remove_record(self) -> None:
        """Test parsing REMOVE stream record."""
        raw = {
            "eventID": "evt-003",
            "eventName": "REMOVE",
            "dynamodb": {
                "Keys": {"PK": {"S": "USER#123"}, "SK": {"S": "PROFILE#123"}},
                "OldImage": {"name": {"S": "Alice"}},
                "SequenceNumber": "102",
            },
        }

        record = StreamRecord.from_raw(raw)

        assert record.event_name == "REMOVE"
        assert record.old_image["name"] == "Alice"
        assert record.new_image is None

    def test_get_entity_type(self) -> None:
        """Test extracting entity type from PK."""
        raw = {
            "eventID": "evt-001",
            "eventName": "INSERT",
            "dynamodb": {
                "Keys": {"PK": {"S": "ORDER#456"}, "SK": {"S": "ORDER#456"}},
                "NewImage": {},
                "SequenceNumber": "1",
            },
        }

        record = StreamRecord.from_raw(raw)
        assert record.get_entity_type() == "ORDER"

    def test_get_changes(self) -> None:
        """Test computing changes between old and new images."""
        raw = {
            "eventID": "evt-002",
            "eventName": "MODIFY",
            "dynamodb": {
                "Keys": {"PK": {"S": "USER#123"}, "SK": {"S": "PROFILE#123"}},
                "OldImage": {"name": {"S": "Alice"}, "age": {"N": "30"}},
                "NewImage": {"name": {"S": "Alice Smith"}, "age": {"N": "30"}},
                "SequenceNumber": "101",
            },
        }

        record = StreamRecord.from_raw(raw)
        changes = record.get_changes()

        assert "name" in changes
        assert changes["name"] == ("Alice", "Alice Smith")
        assert "age" not in changes  # No change


class TestBatchProcessor:
    """Tests for batch processing."""

    def test_successful_batch(self) -> None:
        """Test processing batch with no errors."""
        processed = []

        def handler(record: StreamRecord) -> None:
            processed.append(record.event_id)

        processor = BatchProcessor(handler)

        event = {
            "Records": [
                {
                    "eventID": "evt-001",
                    "eventName": "INSERT",
                    "dynamodb": {"Keys": {"PK": {"S": "A"}}, "SequenceNumber": "1"},
                },
                {
                    "eventID": "evt-002",
                    "eventName": "INSERT",
                    "dynamodb": {"Keys": {"PK": {"S": "B"}}, "SequenceNumber": "2"},
                },
            ]
        }

        result = processor.process_batch(event)

        assert len(processed) == 2
        assert result == {"batchItemFailures": []}

    def test_partial_failure(self) -> None:
        """Test partial batch failure handling."""
        def handler(record: StreamRecord) -> None:
            if record.event_id == "evt-002":
                raise ValueError("Simulated error")

        processor = BatchProcessor(handler)

        event = {
            "Records": [
                {
                    "eventID": "evt-001",
                    "eventName": "INSERT",
                    "dynamodb": {"Keys": {"PK": {"S": "A"}}, "SequenceNumber": "1"},
                },
                {
                    "eventID": "evt-002",
                    "eventName": "INSERT",
                    "dynamodb": {"Keys": {"PK": {"S": "B"}}, "SequenceNumber": "2"},
                },
                {
                    "eventID": "evt-003",
                    "eventName": "INSERT",
                    "dynamodb": {"Keys": {"PK": {"S": "C"}}, "SequenceNumber": "3"},
                },
            ]
        }

        result = processor.process_batch(event)

        assert len(result["batchItemFailures"]) == 1
        assert result["batchItemFailures"][0]["itemIdentifier"] == "evt-002"


class TestIdempotentProcessor:
    """Tests for idempotent processing."""

    def test_skips_duplicate(self) -> None:
        """Test that duplicates are skipped."""
        processed_ids: set[str] = set()
        call_count = 0

        def handler(record: StreamRecord) -> None:
            nonlocal call_count
            call_count += 1

        processor = IdempotentProcessor(
            processor=handler,
            is_processed=lambda eid: eid in processed_ids,
            mark_processed=lambda eid: processed_ids.add(eid),
        )

        record = StreamRecord(
            event_id="evt-001",
            event_name="INSERT",
            keys={"PK": "TEST"},
            new_image={},
            old_image=None,
            sequence_number="1",
            approximate_creation_time=None,
        )

        # Process first time
        result1 = processor.process(record)
        assert result1 is True
        assert call_count == 1

        # Process second time (duplicate)
        result2 = processor.process(record)
        assert result2 is False
        assert call_count == 1  # Still 1, not called again


class TestProcessStreamEvent:
    """Tests for process_stream_event helper."""

    def test_process_stream_event(self) -> None:
        """Test the convenience function."""
        results = []

        def handler(record: StreamRecord) -> None:
            results.append({
                "id": record.event_id,
                "type": record.event_name,
            })

        event = {
            "Records": [
                {
                    "eventID": "evt-001",
                    "eventName": "INSERT",
                    "dynamodb": {"Keys": {"PK": {"S": "A"}}, "SequenceNumber": "1"},
                },
            ]
        }

        response = process_stream_event(event, handler)

        assert len(results) == 1
        assert results[0]["id"] == "evt-001"
        assert response == {"batchItemFailures": []}


class TestStreamProcessor:
    """Tests for abstract StreamProcessor."""

    def test_custom_processor(self) -> None:
        """Test implementing custom processor."""
        events_handled: dict[str, list[StreamRecord]] = {
            "insert": [],
            "modify": [],
            "remove": [],
        }

        class TestProcessor(StreamProcessor):
            def on_insert(self, record: StreamRecord) -> None:
                events_handled["insert"].append(record)

            def on_modify(self, record: StreamRecord) -> None:
                events_handled["modify"].append(record)

            def on_remove(self, record: StreamRecord) -> None:
                events_handled["remove"].append(record)

        processor = TestProcessor()

        # Test INSERT
        insert_record = StreamRecord(
            event_id="1", event_name="INSERT", keys={},
            new_image={}, old_image=None, sequence_number="1",
            approximate_creation_time=None,
        )
        processor.process(insert_record)
        assert len(events_handled["insert"]) == 1

        # Test MODIFY
        modify_record = StreamRecord(
            event_id="2", event_name="MODIFY", keys={},
            new_image={}, old_image={}, sequence_number="2",
            approximate_creation_time=None,
        )
        processor.process(modify_record)
        assert len(events_handled["modify"]) == 1

        # Test REMOVE
        remove_record = StreamRecord(
            event_id="3", event_name="REMOVE", keys={},
            new_image=None, old_image={}, sequence_number="3",
            approximate_creation_time=None,
        )
        processor.process(remove_record)
        assert len(events_handled["remove"]) == 1


@mock_aws
class TestIdempotencyStore:
    """Tests for DynamoDB-backed idempotency store."""

    def test_idempotency_store(self) -> None:
        """Test create_dynamodb_idempotency_store."""
        from dynamodb_streams_cdc.processor import create_dynamodb_idempotency_store

        # Setup
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        client = boto3.client("dynamodb", region_name="us-east-1")

        client.create_table(
            TableName="ProcessedEvents",
            KeySchema=[{"AttributeName": "eventID", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "eventID", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table = dynamodb.Table("ProcessedEvents")

        # Create store
        is_processed, mark_processed = create_dynamodb_idempotency_store(table)

        # Test not processed initially
        assert is_processed("evt-001") is False

        # Mark as processed
        mark_processed("evt-001")

        # Now should be processed
        assert is_processed("evt-001") is True
