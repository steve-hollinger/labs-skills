"""Solution for Exercise 1: Audit Log

Complete implementation of the audit logging system.
"""

from datetime import datetime
from typing import Any
import json
import time

import boto3
from moto import mock_aws

from dynamodb_streams_cdc.processor import StreamRecord


class AuditLogger:
    """Logs all DynamoDB changes to an audit table."""

    def __init__(self, audit_table: Any):
        self.audit_table = audit_table
        self.retention_days = 90

    def log_change(self, record: StreamRecord) -> dict[str, Any]:
        """Log a stream record as an audit entry."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        entity_pk = record.keys.get("PK", "UNKNOWN")
        entity_sk = record.keys.get("SK", "UNKNOWN")

        # Compute changes for MODIFY events
        changes = self._compute_changes(record)

        # Create audit entry
        audit_entry = {
            "PK": f"AUDIT#{entity_pk}",
            "SK": f"CHANGE#{timestamp}#{record.event_id}",
            "event_id": record.event_id,
            "event_type": record.event_name,
            "entity_pk": entity_pk,
            "entity_sk": entity_sk,
            "timestamp": timestamp,
            "changes": changes,
            # Store full images for complete audit trail
            "old_values": self._serialize(record.old_image) if record.old_image else None,
            "new_values": self._serialize(record.new_image) if record.new_image else None,
            # TTL for retention (90 days)
            "ttl": int(time.time()) + (self.retention_days * 24 * 60 * 60),
        }

        # Store in audit table
        self.audit_table.put_item(Item=audit_entry)

        return audit_entry

    def _compute_changes(self, record: StreamRecord) -> list[dict[str, Any]]:
        """Compute field-level changes for an audit entry."""
        changes = []

        if record.event_name == "INSERT":
            # All fields are "new"
            for field, value in (record.new_image or {}).items():
                changes.append({
                    "field": field,
                    "action": "added",
                    "new_value": self._serialize_value(value),
                })
        elif record.event_name == "REMOVE":
            # All fields are "removed"
            for field, value in (record.old_image or {}).items():
                changes.append({
                    "field": field,
                    "action": "removed",
                    "old_value": self._serialize_value(value),
                })
        elif record.event_name == "MODIFY":
            # Compute diff
            for field, (old_val, new_val) in record.get_changes().items():
                changes.append({
                    "field": field,
                    "action": "modified",
                    "old_value": self._serialize_value(old_val),
                    "new_value": self._serialize_value(new_val),
                })

        return changes

    def _serialize(self, obj: Any) -> str | None:
        """Serialize object to JSON string."""
        if obj is None:
            return None
        return json.dumps(obj, default=str)

    def _serialize_value(self, value: Any) -> str:
        """Serialize a single value."""
        if value is None:
            return "null"
        return json.dumps(value, default=str)

    def get_audit_history(
        self,
        entity_pk: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get audit history for an entity."""
        response = self.audit_table.query(
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={":pk": f"AUDIT#{entity_pk}"},
            ScanIndexForward=False,  # Newest first
            Limit=limit,
        )
        return response.get("Items", [])

    def get_changes_by_field(
        self,
        entity_pk: str,
        field_name: str,
    ) -> list[dict[str, Any]]:
        """Get all changes to a specific field."""
        # Get all audit entries
        all_entries = self.get_audit_history(entity_pk, limit=1000)

        # Filter for entries that changed this field
        filtered = []
        for entry in all_entries:
            changes = entry.get("changes", [])
            field_changes = [c for c in changes if c.get("field") == field_name]
            if field_changes:
                filtered.append({
                    **entry,
                    "changes": field_changes,  # Only include relevant changes
                })

        return filtered


def create_audit_table_schema() -> dict[str, Any]:
    """Create the audit table schema."""
    return {
        "TableName": "AuditLog",
        "KeySchema": [
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
    }


def create_sample_events() -> list[dict[str, Any]]:
    """Create sample events for testing."""
    return [
        {
            "eventID": "evt-001",
            "eventName": "INSERT",
            "dynamodb": {
                "Keys": {"PK": {"S": "USER#user-001"}, "SK": {"S": "PROFILE#user-001"}},
                "NewImage": {
                    "PK": {"S": "USER#user-001"},
                    "name": {"S": "Alice Smith"},
                    "email": {"S": "alice@example.com"},
                    "role": {"S": "member"},
                },
                "SequenceNumber": "1",
            },
        },
        {
            "eventID": "evt-002",
            "eventName": "MODIFY",
            "dynamodb": {
                "Keys": {"PK": {"S": "USER#user-001"}, "SK": {"S": "PROFILE#user-001"}},
                "OldImage": {
                    "PK": {"S": "USER#user-001"},
                    "name": {"S": "Alice Smith"},
                    "email": {"S": "alice@example.com"},
                    "role": {"S": "member"},
                },
                "NewImage": {
                    "PK": {"S": "USER#user-001"},
                    "name": {"S": "Alice Smith"},
                    "email": {"S": "alice@example.com"},
                    "role": {"S": "admin"},
                },
                "SequenceNumber": "2",
            },
        },
        {
            "eventID": "evt-003",
            "eventName": "MODIFY",
            "dynamodb": {
                "Keys": {"PK": {"S": "USER#user-001"}, "SK": {"S": "PROFILE#user-001"}},
                "OldImage": {
                    "PK": {"S": "USER#user-001"},
                    "name": {"S": "Alice Smith"},
                    "email": {"S": "alice@example.com"},
                    "role": {"S": "admin"},
                },
                "NewImage": {
                    "PK": {"S": "USER#user-001"},
                    "name": {"S": "Alice Smith"},
                    "email": {"S": "alice.smith@company.com"},
                    "role": {"S": "admin"},
                },
                "SequenceNumber": "3",
            },
        },
    ]


@mock_aws
def solution() -> None:
    """Demonstrate the audit log solution."""
    print("Solution 1: Audit Log")
    print("=" * 50)

    # Set up DynamoDB
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    client = boto3.client("dynamodb", region_name="us-east-1")

    # Create audit table
    client.create_table(**create_audit_table_schema())
    audit_table = dynamodb.Table("AuditLog")

    # Create logger
    logger = AuditLogger(audit_table)

    # Process events
    print("\n--- Processing Events ---\n")
    events = create_sample_events()

    for raw_record in events:
        record = StreamRecord.from_raw(raw_record)
        entry = logger.log_change(record)
        print(f"Logged: {record.event_name} - {record.keys.get('PK')}")
        print(f"  Changes: {len(entry['changes'])} field(s)")

    # Query audit history
    print("\n--- Audit History for USER#user-001 ---\n")
    history = logger.get_audit_history("USER#user-001")

    for entry in history:
        print(f"Event: {entry['event_type']} at {entry['timestamp']}")
        for change in entry['changes']:
            field = change['field']
            if change['action'] == 'modified':
                print(f"  - {field}: {change['old_value']} -> {change['new_value']}")
            elif change['action'] == 'added':
                print(f"  - {field}: (added) {change['new_value']}")

    # Query specific field changes
    print("\n--- Changes to 'role' field ---\n")
    role_changes = logger.get_changes_by_field("USER#user-001", "role")

    for entry in role_changes:
        print(f"At {entry['timestamp']}:")
        for change in entry['changes']:
            print(f"  {change['old_value']} -> {change['new_value']}")

    print("\n" + "=" * 50)
    print("Solution completed successfully!")


if __name__ == "__main__":
    solution()
