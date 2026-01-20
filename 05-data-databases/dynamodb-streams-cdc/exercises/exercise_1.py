"""Exercise 1: Build an Audit Log from Stream Events

Create an audit logging system that captures all changes to DynamoDB items
and stores them in an audit table for compliance and debugging.

Requirements:
1. Capture INSERT, MODIFY, and REMOVE events
2. Store who changed what and when
3. For MODIFY events, store the diff (what changed)
4. Support querying audit history for an entity
5. Implement TTL for audit retention

Instructions:
1. Implement the AuditLogger class
2. Create audit entries with field-level changes
3. Store audit entries in a DynamoDB table
4. Implement query functions for audit history

Hints:
- Use NEW_AND_OLD_IMAGES stream view type
- Compute diffs using StreamRecord.get_changes()
- Store entries with entity as PK and timestamp as SK
- Use TTL for automatic cleanup
"""

from datetime import datetime
from typing import Any
import json

import boto3
from moto import mock_aws

from dynamodb_streams_cdc.processor import StreamRecord


class AuditLogger:
    """Logs all DynamoDB changes to an audit table."""

    def __init__(self, audit_table: Any):
        """Initialize audit logger.

        Args:
            audit_table: DynamoDB table for storing audit entries
        """
        self.audit_table = audit_table
        self.retention_days = 90

    def log_change(self, record: StreamRecord) -> dict[str, Any]:
        """Log a stream record as an audit entry.

        TODO: Implement audit logging.

        Steps:
        1. Extract entity information from record
        2. Compute what changed (for MODIFY events)
        3. Create audit entry with all relevant info
        4. Store in audit table
        5. Return the created audit entry

        Args:
            record: Parsed stream record

        Returns:
            The audit entry that was created
        """
        # TODO: Implement this method
        # Think about:
        # - What information should be in the audit entry?
        # - How to structure the primary key for querying?
        # - What format should the changes be in?
        # - How to set TTL for retention?
        pass

    def _compute_changes(self, record: StreamRecord) -> list[dict[str, Any]]:
        """Compute field-level changes for an audit entry.

        TODO: Implement change computation.

        Args:
            record: Stream record

        Returns:
            List of change records: [{"field": "name", "old": "A", "new": "B"}]
        """
        # TODO: Use record.get_changes() and format appropriately
        pass

    def get_audit_history(
        self,
        entity_pk: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get audit history for an entity.

        TODO: Implement query for audit history.

        Args:
            entity_pk: Entity's partition key
            limit: Maximum entries to return

        Returns:
            List of audit entries, newest first
        """
        # TODO: Query audit table by entity, sorted by time descending
        pass

    def get_changes_by_field(
        self,
        entity_pk: str,
        field_name: str,
    ) -> list[dict[str, Any]]:
        """Get all changes to a specific field.

        TODO: Implement field-specific audit query.

        Args:
            entity_pk: Entity's partition key
            field_name: Field to filter by

        Returns:
            List of audit entries where this field changed
        """
        # TODO: Query and filter for specific field changes
        pass


def create_audit_table_schema() -> dict[str, Any]:
    """Create the audit table schema.

    TODO: Define table schema with appropriate keys and GSIs.

    Returns:
        Table creation parameters
    """
    # TODO: Implement
    # Consider:
    # - PK: AUDIT#{entity_pk}
    # - SK: CHANGE#{timestamp}#{event_id}
    # - TTL attribute for retention
    return {
        "TableName": "AuditLog",
        # TODO: Add KeySchema, AttributeDefinitions, etc.
    }


def create_sample_events() -> list[dict[str, Any]]:
    """Create sample events for testing."""
    return [
        # User created
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
        # User role changed
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
        # User email changed
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
def exercise() -> None:
    """Test your audit logger implementation."""
    print("Exercise 1: Audit Log")
    print("=" * 50)

    # TODO: Set up DynamoDB and create audit table
    # TODO: Create AuditLogger instance
    # TODO: Process sample events
    # TODO: Query and display audit history

    print("\nImplement the TODO sections and verify:")
    print("1. All changes are logged to audit table")
    print("2. MODIFY events show field-level diffs")
    print("3. Audit history can be queried by entity")
    print("4. TTL is set for retention policy")


if __name__ == "__main__":
    exercise()
