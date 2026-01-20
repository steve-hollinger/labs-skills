"""Exercise 2: Sync DynamoDB to Search Index

Build a stream processor that keeps a search index (simulated) in sync
with DynamoDB changes.

Requirements:
1. Index new items when inserted
2. Update index when items are modified
3. Remove from index when items are deleted
4. Handle partial failures gracefully
5. Implement idempotency

Instructions:
1. Implement the SearchIndexSync class
2. Transform DynamoDB items to searchable documents
3. Handle each event type appropriately
4. Add error handling and retry logic

Hints:
- In production, this would use Elasticsearch/OpenSearch
- Focus on the sync logic, not the actual search
- Consider what fields should be searchable
- Think about how to handle sync failures
"""

from typing import Any
import json

import boto3
from moto import mock_aws

from dynamodb_streams_cdc.processor import StreamRecord, BatchProcessor


class MockSearchIndex:
    """Simulated search index (would be Elasticsearch in production)."""

    def __init__(self):
        self.documents: dict[str, dict[str, Any]] = {}
        self.operations: list[dict[str, Any]] = []

    def index(self, doc_id: str, document: dict[str, Any]) -> None:
        """Index a document."""
        self.documents[doc_id] = document
        self.operations.append({
            "operation": "index",
            "doc_id": doc_id,
            "document": document,
        })

    def delete(self, doc_id: str) -> None:
        """Delete a document."""
        if doc_id in self.documents:
            del self.documents[doc_id]
        self.operations.append({
            "operation": "delete",
            "doc_id": doc_id,
        })

    def search(self, query: str) -> list[dict[str, Any]]:
        """Simple text search (simulated)."""
        results = []
        query_lower = query.lower()
        for doc_id, doc in self.documents.items():
            # Simple substring matching
            doc_text = json.dumps(doc).lower()
            if query_lower in doc_text:
                results.append({"id": doc_id, **doc})
        return results


class SearchIndexSync:
    """Syncs DynamoDB changes to search index."""

    def __init__(self, search_index: MockSearchIndex):
        """Initialize sync processor.

        Args:
            search_index: Search index to sync to
        """
        self.index = search_index
        self.supported_entity_types = {"USER", "PRODUCT", "ORDER"}

    def process_record(self, record: StreamRecord) -> None:
        """Process a stream record and sync to search.

        TODO: Implement sync logic.

        Steps:
        1. Check if entity type should be indexed
        2. Generate document ID from keys
        3. Handle INSERT/MODIFY by indexing
        4. Handle REMOVE by deleting
        5. Transform item to searchable document

        Args:
            record: Parsed stream record
        """
        # TODO: Implement this method
        pass

    def _should_index(self, record: StreamRecord) -> bool:
        """Determine if this record should be indexed.

        TODO: Implement filtering logic.

        Args:
            record: Stream record

        Returns:
            True if should be indexed
        """
        # TODO: Check entity type, maybe other criteria
        pass

    def _generate_doc_id(self, record: StreamRecord) -> str:
        """Generate search document ID from DynamoDB keys.

        TODO: Implement ID generation.

        Args:
            record: Stream record

        Returns:
            Unique document ID
        """
        # TODO: Combine PK and SK into unique ID
        pass

    def _transform_to_document(
        self,
        item: dict[str, Any],
        entity_type: str,
    ) -> dict[str, Any]:
        """Transform DynamoDB item to searchable document.

        TODO: Implement transformation.

        Think about:
        - What fields should be searchable?
        - How to handle nested data?
        - What metadata to include?

        Args:
            item: DynamoDB item
            entity_type: Type of entity

        Returns:
            Search document
        """
        # TODO: Create searchable document
        # Include relevant fields based on entity type
        pass


class SyncErrorHandler:
    """Handles sync errors with retry logic."""

    def __init__(self):
        self.failed_records: list[dict[str, Any]] = []
        self.retry_count: dict[str, int] = {}
        self.max_retries = 3

    def handle_error(self, record: StreamRecord, error: Exception) -> bool:
        """Handle a sync error.

        TODO: Implement error handling.

        Args:
            record: Failed record
            error: The exception

        Returns:
            True if should retry, False to skip
        """
        # TODO: Track retries, decide if should retry
        pass

    def get_failed_records(self) -> list[dict[str, Any]]:
        """Get records that failed after max retries."""
        return self.failed_records


def create_sample_events() -> list[dict[str, Any]]:
    """Create sample events for testing."""
    return [
        # Product created
        {
            "eventID": "evt-001",
            "eventName": "INSERT",
            "dynamodb": {
                "Keys": {"PK": {"S": "PRODUCT#prod-001"}, "SK": {"S": "PRODUCT#prod-001"}},
                "NewImage": {
                    "PK": {"S": "PRODUCT#prod-001"},
                    "name": {"S": "Wireless Mouse"},
                    "description": {"S": "Ergonomic wireless mouse with long battery life"},
                    "category": {"S": "Electronics"},
                    "price": {"N": "29.99"},
                    "tags": {"L": [{"S": "wireless"}, {"S": "mouse"}, {"S": "ergonomic"}]},
                },
                "SequenceNumber": "1",
            },
        },
        # Product updated
        {
            "eventID": "evt-002",
            "eventName": "MODIFY",
            "dynamodb": {
                "Keys": {"PK": {"S": "PRODUCT#prod-001"}, "SK": {"S": "PRODUCT#prod-001"}},
                "OldImage": {
                    "PK": {"S": "PRODUCT#prod-001"},
                    "name": {"S": "Wireless Mouse"},
                    "price": {"N": "29.99"},
                },
                "NewImage": {
                    "PK": {"S": "PRODUCT#prod-001"},
                    "name": {"S": "Wireless Mouse Pro"},
                    "price": {"N": "34.99"},
                },
                "SequenceNumber": "2",
            },
        },
        # User created (should be indexed)
        {
            "eventID": "evt-003",
            "eventName": "INSERT",
            "dynamodb": {
                "Keys": {"PK": {"S": "USER#user-001"}, "SK": {"S": "PROFILE#user-001"}},
                "NewImage": {
                    "PK": {"S": "USER#user-001"},
                    "name": {"S": "Alice Smith"},
                    "email": {"S": "alice@example.com"},
                    "bio": {"S": "Software engineer who loves Python"},
                },
                "SequenceNumber": "3",
            },
        },
        # Audit log (should NOT be indexed)
        {
            "eventID": "evt-004",
            "eventName": "INSERT",
            "dynamodb": {
                "Keys": {"PK": {"S": "AUDIT#123"}, "SK": {"S": "CHANGE#2024"}},
                "NewImage": {
                    "PK": {"S": "AUDIT#123"},
                    "change": {"S": "something"},
                },
                "SequenceNumber": "4",
            },
        },
        # Product deleted
        {
            "eventID": "evt-005",
            "eventName": "REMOVE",
            "dynamodb": {
                "Keys": {"PK": {"S": "PRODUCT#prod-002"}, "SK": {"S": "PRODUCT#prod-002"}},
                "OldImage": {
                    "PK": {"S": "PRODUCT#prod-002"},
                    "name": {"S": "Old Product"},
                },
                "SequenceNumber": "5",
            },
        },
    ]


@mock_aws
def exercise() -> None:
    """Test your search sync implementation."""
    print("Exercise 2: Search Index Sync")
    print("=" * 50)

    # TODO: Create search index
    # TODO: Create SearchIndexSync
    # TODO: Process sample events
    # TODO: Verify index state
    # TODO: Test search functionality

    print("\nImplement the TODO sections and verify:")
    print("1. Products and users are indexed")
    print("2. Audit logs are NOT indexed")
    print("3. Updates modify existing documents")
    print("4. Deletes remove documents")
    print("5. Search returns matching results")


if __name__ == "__main__":
    exercise()
