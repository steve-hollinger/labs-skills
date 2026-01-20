# Common Patterns

## Overview

This document covers common patterns for DynamoDB Streams and change data capture, including aggregations, data synchronization, and event-driven architectures.

## Pattern 1: Real-Time Aggregations

### When to Use

Use real-time aggregations when you need:
- Live counters (page views, likes, inventory)
- Running totals (order amounts, revenue)
- Statistical summaries updated in real-time

### Implementation

```python
from decimal import Decimal
from typing import Any


def process_order_for_aggregation(record: dict[str, Any], aggregates_table: Any) -> None:
    """Update order aggregates based on stream events."""
    event_name = record["eventName"]
    dynamodb = record["dynamodb"]

    if event_name == "INSERT":
        new_order = deserialize(dynamodb["NewImage"])
        user_id = new_order["user_id"]
        amount = Decimal(new_order["total"])

        # Increment order count and total
        aggregates_table.update_item(
            Key={"PK": f"USER#{user_id}", "SK": "AGGREGATES"},
            UpdateExpression="""
                SET order_count = if_not_exists(order_count, :zero) + :one,
                    total_spent = if_not_exists(total_spent, :zero) + :amount
            """,
            ExpressionAttributeValues={
                ":zero": 0,
                ":one": 1,
                ":amount": amount
            }
        )

    elif event_name == "REMOVE":
        old_order = deserialize(dynamodb["OldImage"])
        user_id = old_order["user_id"]
        amount = Decimal(old_order["total"])

        # Decrement counters
        aggregates_table.update_item(
            Key={"PK": f"USER#{user_id}", "SK": "AGGREGATES"},
            UpdateExpression="""
                SET order_count = order_count - :one,
                    total_spent = total_spent - :amount
            """,
            ExpressionAttributeValues={
                ":one": 1,
                ":amount": amount
            }
        )
```

### Example

```python
# Daily sales aggregation
def aggregate_daily_sales(record: dict[str, Any], sales_table: Any) -> None:
    event_name = record["eventName"]

    if event_name in ("INSERT", "MODIFY"):
        new_order = deserialize(record["dynamodb"]["NewImage"])
        date = new_order["created_at"][:10]  # "2024-01-15"
        amount = Decimal(new_order["total"])
        category = new_order.get("category", "other")

        # Update daily aggregate
        sales_table.update_item(
            Key={"PK": f"SALES#{date}", "SK": f"CATEGORY#{category}"},
            UpdateExpression="""
                ADD order_count :one, revenue :amount
            """,
            ExpressionAttributeValues={
                ":one": 1,
                ":amount": amount
            }
        )
```

### Pitfalls to Avoid

- Not handling REMOVE events (counters become inaccurate)
- Not considering MODIFY events (may need to adjust diff)
- Race conditions with concurrent updates (use atomic operations)

## Pattern 2: Data Synchronization

### When to Use

Use data sync when you need to:
- Replicate data to search engines (Elasticsearch, OpenSearch)
- Maintain cache consistency (Redis, Memcached)
- Sync to analytics systems (Redshift, BigQuery)

### Implementation

```python
from elasticsearch import Elasticsearch


class SearchSyncProcessor:
    """Sync DynamoDB changes to Elasticsearch."""

    def __init__(self, es_client: Elasticsearch, index_name: str):
        self.es = es_client
        self.index_name = index_name

    def process_record(self, record: dict[str, Any]) -> None:
        event_name = record["eventName"]
        keys = deserialize(record["dynamodb"]["Keys"])
        doc_id = f"{keys['PK']}#{keys['SK']}"

        if event_name in ("INSERT", "MODIFY"):
            new_item = deserialize(record["dynamodb"]["NewImage"])
            # Index/update document
            self.es.index(
                index=self.index_name,
                id=doc_id,
                document=self._transform_for_search(new_item)
            )

        elif event_name == "REMOVE":
            # Delete document
            self.es.delete(
                index=self.index_name,
                id=doc_id,
                ignore=[404]  # OK if already deleted
            )

    def _transform_for_search(self, item: dict[str, Any]) -> dict[str, Any]:
        """Transform DynamoDB item to search document."""
        return {
            "title": item.get("title", ""),
            "content": item.get("content", ""),
            "tags": item.get("tags", []),
            "created_at": item.get("created_at"),
            # Add searchable fields...
        }
```

### Example

```python
# Cache invalidation sync
class CacheInvalidator:
    def __init__(self, redis_client):
        self.redis = redis_client

    def process_record(self, record: dict[str, Any]) -> None:
        event_name = record["eventName"]
        keys = deserialize(record["dynamodb"]["Keys"])
        cache_key = f"item:{keys['PK']}:{keys['SK']}"

        if event_name == "INSERT":
            # Pre-populate cache
            new_item = deserialize(record["dynamodb"]["NewImage"])
            self.redis.setex(cache_key, 3600, json.dumps(new_item))

        elif event_name == "MODIFY":
            # Update cache
            new_item = deserialize(record["dynamodb"]["NewImage"])
            self.redis.setex(cache_key, 3600, json.dumps(new_item))

        elif event_name == "REMOVE":
            # Invalidate cache
            self.redis.delete(cache_key)
```

### Pitfalls to Avoid

- Not handling eventual consistency (search may lag behind)
- Not implementing idempotency (duplicates in search)
- Not batching operations (performance issues)

## Pattern 3: Audit Trail

### When to Use

Use audit trails when you need:
- Compliance logging (who changed what, when)
- Change history for debugging
- Undo/rollback capabilities

### Implementation

```python
from datetime import datetime
from typing import Any
import json


class AuditLogger:
    """Log all changes to an audit table."""

    def __init__(self, audit_table: Any):
        self.audit_table = audit_table

    def log_change(self, record: dict[str, Any]) -> None:
        event_name = record["eventName"]
        event_id = record["eventID"]
        timestamp = datetime.utcnow().isoformat() + "Z"
        dynamodb = record["dynamodb"]

        keys = deserialize(dynamodb["Keys"])
        old_image = deserialize(dynamodb.get("OldImage", {}))
        new_image = deserialize(dynamodb.get("NewImage", {}))

        # Compute what changed
        changes = self._compute_diff(old_image, new_image)

        audit_entry = {
            "PK": f"AUDIT#{keys['PK']}",
            "SK": f"CHANGE#{timestamp}#{event_id}",
            "event_type": event_name,
            "event_id": event_id,
            "timestamp": timestamp,
            "entity_pk": keys["PK"],
            "entity_sk": keys["SK"],
            "changes": json.dumps(changes),
            "old_values": json.dumps(old_image) if old_image else None,
            "new_values": json.dumps(new_image) if new_image else None,
            # TTL for retention policy (90 days)
            "ttl": int(datetime.utcnow().timestamp()) + (90 * 24 * 60 * 60)
        }

        self.audit_table.put_item(Item=audit_entry)

    def _compute_diff(
        self,
        old: dict[str, Any],
        new: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Compute field-level changes."""
        changes = []
        all_keys = set(old.keys()) | set(new.keys())

        for key in all_keys:
            old_val = old.get(key)
            new_val = new.get(key)

            if old_val != new_val:
                changes.append({
                    "field": key,
                    "old_value": old_val,
                    "new_value": new_val
                })

        return changes
```

### Example

```python
# Query audit history for an entity
def get_audit_history(audit_table: Any, entity_pk: str, limit: int = 50) -> list[dict]:
    response = audit_table.query(
        KeyConditionExpression="PK = :pk",
        ExpressionAttributeValues={":pk": f"AUDIT#{entity_pk}"},
        ScanIndexForward=False,  # Newest first
        Limit=limit
    )
    return response.get("Items", [])
```

### Pitfalls to Avoid

- Not using NEW_AND_OLD_IMAGES view type (missing change context)
- Not implementing TTL for retention management
- Storing sensitive data in audit logs without encryption

## Pattern 4: Event-Driven Architecture

### When to Use

Use event-driven patterns when:
- Multiple systems need to react to changes
- Decoupling producers from consumers
- Building microservices that communicate via events

### Implementation

```python
import json
import boto3


class EventPublisher:
    """Publish DynamoDB changes as domain events."""

    def __init__(self, eventbridge_client, event_bus_name: str):
        self.eventbridge = eventbridge_client
        self.event_bus = event_bus_name

    def publish_event(self, record: dict[str, Any]) -> None:
        event_name = record["eventName"]
        dynamodb = record["dynamodb"]

        keys = deserialize(dynamodb["Keys"])
        entity_type = self._extract_entity_type(keys["PK"])

        # Map DynamoDB events to domain events
        domain_event = self._create_domain_event(
            entity_type=entity_type,
            event_name=event_name,
            keys=keys,
            old_image=deserialize(dynamodb.get("OldImage", {})),
            new_image=deserialize(dynamodb.get("NewImage", {}))
        )

        # Publish to EventBridge
        self.eventbridge.put_events(
            Entries=[{
                "Source": "myapp.dynamodb",
                "DetailType": domain_event["type"],
                "Detail": json.dumps(domain_event),
                "EventBusName": self.event_bus
            }]
        )

    def _extract_entity_type(self, pk: str) -> str:
        """Extract entity type from PK (e.g., 'USER#123' -> 'user')."""
        return pk.split("#")[0].lower()

    def _create_domain_event(
        self,
        entity_type: str,
        event_name: str,
        keys: dict,
        old_image: dict,
        new_image: dict
    ) -> dict[str, Any]:
        """Create domain event from DynamoDB change."""
        event_type_map = {
            "INSERT": f"{entity_type}.created",
            "MODIFY": f"{entity_type}.updated",
            "REMOVE": f"{entity_type}.deleted"
        }

        return {
            "type": event_type_map.get(event_name, f"{entity_type}.changed"),
            "entity_type": entity_type,
            "entity_id": keys.get("PK"),
            "data": new_image or old_image,
            "previous_data": old_image if event_name == "MODIFY" else None
        }
```

### Example

```python
# Lambda handler for event-driven processing
def lambda_handler(event, context):
    eventbridge = boto3.client("events")
    publisher = EventPublisher(eventbridge, "MyEventBus")

    for record in event["Records"]:
        try:
            publisher.publish_event(record)
        except Exception as e:
            print(f"Failed to publish event: {e}")
            raise  # Let Lambda retry

    return {"statusCode": 200}
```

### Pitfalls to Avoid

- Not handling EventBridge limits (10 events per put_events)
- Not including enough context in events
- Creating overly chatty event streams

## Anti-Patterns

### Anti-Pattern 1: Synchronous Heavy Processing

Processing heavy workloads synchronously in the Lambda handler.

```python
# BAD: Heavy processing blocks stream
def handler(event, context):
    for record in event["Records"]:
        # This takes too long!
        process_image(record)  # 30 seconds
        send_notifications(record)  # 10 seconds
        update_analytics(record)  # 5 seconds
```

### Better Approach

```python
# GOOD: Fan out to async processing
def handler(event, context):
    sqs = boto3.client("sqs")

    for record in event["Records"]:
        # Quick: just queue for async processing
        sqs.send_message(
            QueueUrl="...",
            MessageBody=json.dumps(record)
        )

    return {"statusCode": 200}
```

### Anti-Pattern 2: Ignoring Idempotency

Assuming exactly-once delivery.

```python
# BAD: Duplicate processing corrupts data
def handler(event, context):
    for record in event["Records"]:
        if record["eventName"] == "INSERT":
            # This runs multiple times!
            increment_counter()
            send_welcome_email()
```

### Better Approach

```python
# GOOD: Idempotent processing
def handler(event, context):
    for record in event["Records"]:
        event_id = record["eventID"]

        if is_already_processed(event_id):
            continue

        if record["eventName"] == "INSERT":
            increment_counter()
            send_welcome_email()

        mark_as_processed(event_id)
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Track metrics/KPIs | Real-Time Aggregations |
| Keep search index current | Data Synchronization |
| Compliance requirements | Audit Trail |
| Microservices communication | Event-Driven Architecture |
| Cache consistency | Data Synchronization |
| User activity tracking | Audit Trail + Aggregations |
| Real-time dashboards | Aggregations + Sync |
