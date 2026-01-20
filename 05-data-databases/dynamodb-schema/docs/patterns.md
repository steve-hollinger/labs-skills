# Common Patterns

## Overview

This document covers common DynamoDB schema design patterns and best practices for building scalable, performant applications.

## Pattern 1: Adjacency List

### When to Use

Use adjacency lists when modeling graph-like relationships such as:
- Social networks (users and followers)
- Organizational hierarchies
- Bill of materials
- Many-to-many relationships

### Implementation

```python
from typing import Any

def create_adjacency_list_item(
    entity_type: str,
    entity_id: str,
    target_type: str,
    target_id: str,
    attributes: dict[str, Any]
) -> dict[str, Any]:
    """Create an adjacency list item for graph relationships."""
    return {
        "PK": f"{entity_type}#{entity_id}",
        "SK": f"{target_type}#{target_id}",
        "entity_type": entity_type,
        "entity_id": entity_id,
        "target_type": target_type,
        "target_id": target_id,
        **attributes
    }
```

### Example

```python
# Social network: Users and followers
items = [
    # User profile
    {"PK": "USER#alice", "SK": "USER#alice", "name": "Alice", "type": "profile"},
    # Alice follows Bob
    {"PK": "USER#alice", "SK": "FOLLOWS#bob", "type": "follows", "since": "2024-01-01"},
    # Alice follows Carol
    {"PK": "USER#alice", "SK": "FOLLOWS#carol", "type": "follows", "since": "2024-01-05"},
    # Inverted: Who follows Alice (using GSI)
    {"PK": "USER#bob", "SK": "FOLLOWS#alice", "type": "follows",
     "GSI1PK": "USER#alice", "GSI1SK": "FOLLOWER#bob"},
]

# Query: Get all users Alice follows
# PK = "USER#alice", SK begins_with "FOLLOWS#"

# Query: Get all followers of Alice (using GSI1)
# GSI1PK = "USER#alice", GSI1SK begins_with "FOLLOWER#"
```

### Pitfalls to Avoid

- Forgetting the inverted index for bidirectional queries
- Not considering GSI write costs for large follower counts
- Storing redundant data without consistency strategy

## Pattern 2: Composite Sort Key

### When to Use

Use composite sort keys when you need:
- Hierarchical queries at multiple levels
- Multiple sort dimensions
- Type-prefixed entities in same partition

### Implementation

```python
def create_composite_sort_key(*components: str, separator: str = "#") -> str:
    """Create a composite sort key from multiple components."""
    return separator.join(components)

# Example: DATE#STATUS#ORDER_ID
sort_key = create_composite_sort_key("2024-01-15", "pending", "order-123")
# Result: "2024-01-15#pending#order-123"
```

### Example

```python
# E-commerce: Orders with multiple query patterns
items = [
    {
        "PK": "CUSTOMER#123",
        "SK": "ORDER#2024-01-15#shipped#order-456",
        "status": "shipped",
        "total": 99.99
    },
    {
        "PK": "CUSTOMER#123",
        "SK": "ORDER#2024-01-15#pending#order-789",
        "status": "pending",
        "total": 149.99
    },
    {
        "PK": "CUSTOMER#123",
        "SK": "ORDER#2024-01-10#delivered#order-111",
        "status": "delivered",
        "total": 49.99
    }
]

# Query patterns supported:
# 1. All orders: SK begins_with "ORDER#"
# 2. Orders on date: SK begins_with "ORDER#2024-01-15"
# 3. Orders on date with status: SK begins_with "ORDER#2024-01-15#shipped"
```

### Pitfalls to Avoid

- Choosing wrong component order (filter most common first)
- Making sort key too long (max 1024 bytes)
- Forgetting that begins_with only works left-to-right

## Pattern 3: GSI Overloading

### When to Use

Overload GSIs when you have multiple access patterns that:
- Can share the same index
- Have non-overlapping key prefixes
- Don't all need to exist on every item

### Implementation

```python
def add_gsi_attributes(
    item: dict[str, Any],
    access_pattern: str,
    gsi_pk_value: str,
    gsi_sk_value: str,
    gsi_number: int = 1
) -> dict[str, Any]:
    """Add GSI attributes to an item for a specific access pattern."""
    item[f"GSI{gsi_number}PK"] = gsi_pk_value
    item[f"GSI{gsi_number}SK"] = gsi_sk_value
    return item

# Different entity types use same GSI differently
user_item = add_gsi_attributes(
    {"PK": "USER#123", "SK": "USER#123"},
    access_pattern="users_by_email",
    gsi_pk_value="EMAIL#john@example.com",
    gsi_sk_value="USER#123"
)

order_item = add_gsi_attributes(
    {"PK": "ORDER#456", "SK": "ORDER#456"},
    access_pattern="orders_by_date",
    gsi_pk_value="DATE#2024-01-15",
    gsi_sk_value="ORDER#456"
)
```

### Example

```python
# Single GSI serving multiple access patterns
items = [
    # Users: GSI1 for email lookup
    {
        "PK": "USER#123",
        "SK": "USER#123",
        "type": "user",
        "email": "john@example.com",
        "GSI1PK": "EMAIL#john@example.com",
        "GSI1SK": "USER#123"
    },
    # Orders: GSI1 for status lookup
    {
        "PK": "ORDER#456",
        "SK": "ORDER#456",
        "type": "order",
        "status": "pending",
        "GSI1PK": "STATUS#pending",
        "GSI1SK": "ORDER#2024-01-15#456"
    },
    # Products: GSI1 for category lookup
    {
        "PK": "PRODUCT#789",
        "SK": "PRODUCT#789",
        "type": "product",
        "category": "electronics",
        "GSI1PK": "CATEGORY#electronics",
        "GSI1SK": "PRODUCT#789"
    }
]

# All use GSI1 but with different prefix patterns
```

### Pitfalls to Avoid

- Overloading so much that the GSI becomes a hot partition
- Not documenting which entities use which GSI patterns
- Forgetting sparse indexes (items without GSI attrs aren't indexed)

## Pattern 4: Write Sharding

### When to Use

Use write sharding when:
- Single partition receives too many writes
- Time-series data with predictable hot times
- High-velocity event streams

### Implementation

```python
import hashlib
from datetime import datetime

def get_sharded_partition_key(
    base_key: str,
    shard_value: str,
    num_shards: int = 10
) -> str:
    """Create a sharded partition key for write distribution."""
    hash_val = int(hashlib.md5(shard_value.encode()).hexdigest(), 16)
    shard_id = hash_val % num_shards
    return f"{base_key}#SHARD#{shard_id}"

def get_time_sharded_key(
    base_key: str,
    timestamp: datetime,
    shard_id: int
) -> str:
    """Create a time-based sharded partition key."""
    date_str = timestamp.strftime("%Y-%m-%d")
    return f"{base_key}#{date_str}#SHARD#{shard_id}"
```

### Example

```python
from datetime import datetime
import random

# High-velocity metrics collection
def write_metric(table, metric_name: str, value: float) -> None:
    timestamp = datetime.utcnow()
    shard_id = random.randint(0, 9)  # Random sharding for writes

    item = {
        "PK": f"METRIC#{metric_name}#{timestamp.strftime('%Y-%m-%d')}#SHARD#{shard_id}",
        "SK": f"TS#{timestamp.isoformat()}",
        "value": value,
        "metric_name": metric_name
    }
    table.put_item(Item=item)

# Reading requires scatter-gather across shards
def read_metrics(table, metric_name: str, date: str, num_shards: int = 10) -> list:
    all_items = []
    for shard_id in range(num_shards):
        response = table.query(
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={
                ":pk": f"METRIC#{metric_name}#{date}#SHARD#{shard_id}"
            }
        )
        all_items.extend(response.get("Items", []))
    return sorted(all_items, key=lambda x: x["SK"])
```

### Pitfalls to Avoid

- Using too many shards (increases read complexity)
- Using too few shards (doesn't solve hot partition)
- Forgetting to implement scatter-gather for reads

## Pattern 5: Sparse Indexes

### When to Use

Use sparse indexes when:
- Only some items need secondary access
- You want to filter items by existence of attribute
- Reducing GSI storage and write costs

### Implementation

```python
def create_item_with_optional_gsi(
    base_item: dict[str, Any],
    include_in_gsi: bool,
    gsi_pk: str,
    gsi_sk: str
) -> dict[str, Any]:
    """Create an item that's optionally included in a GSI."""
    if include_in_gsi:
        base_item["GSI1PK"] = gsi_pk
        base_item["GSI1SK"] = gsi_sk
    # If not included, item won't appear in GSI
    return base_item
```

### Example

```python
# Only index featured products
items = [
    # Featured product - appears in GSI
    {
        "PK": "PRODUCT#123",
        "SK": "PRODUCT#123",
        "name": "Premium Widget",
        "featured": True,
        "GSI1PK": "FEATURED",
        "GSI1SK": "PRODUCT#123"
    },
    # Regular product - NOT in GSI (no GSI1PK/GSI1SK)
    {
        "PK": "PRODUCT#456",
        "SK": "PRODUCT#456",
        "name": "Basic Widget",
        "featured": False
        # No GSI attributes = not indexed
    }
]

# Query GSI1: Get all featured products
# Only returns product 123
```

### Pitfalls to Avoid

- Assuming all items appear in all GSIs
- Not handling None values in queries
- Forgetting to add GSI attributes when status changes

## Anti-Patterns

### Anti-Pattern 1: One Table Per Entity Type

Using separate tables for each entity type like a relational database.

```python
# BAD: Separate tables
users_table = dynamodb.Table("Users")
orders_table = dynamodb.Table("Orders")
products_table = dynamodb.Table("Products")

# Requires multiple queries and no transactions across tables
user = users_table.get_item(Key={"user_id": "123"})
orders = orders_table.query(KeyConditionExpression="user_id = :uid")
```

### Better Approach

```python
# GOOD: Single table with entity prefixes
table = dynamodb.Table("EcommerceData")

# Get user and orders in one query
response = table.query(
    KeyConditionExpression="PK = :pk",
    ExpressionAttributeValues={":pk": "USER#123"}
)
# Returns user profile AND all orders

# Transaction across entities
table.transact_write_items(
    TransactItems=[
        {"Put": {"Item": user_item}},
        {"Put": {"Item": order_item}},
        {"Update": {"Key": inventory_key, ...}}
    ]
)
```

### Anti-Pattern 2: Scan-Based Queries

Using Scan operations for regular queries.

```python
# BAD: Scanning entire table
response = table.scan(
    FilterExpression="status = :status",
    ExpressionAttributeValues={":status": "pending"}
)
# Reads ENTIRE table, then filters - expensive and slow
```

### Better Approach

```python
# GOOD: Query with proper key design
response = table.query(
    IndexName="GSI1",
    KeyConditionExpression="GSI1PK = :pk",
    ExpressionAttributeValues={":pk": "STATUS#pending"}
)
# Only reads matching items
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Graph relationships (social, org charts) | Adjacency List |
| Multi-level hierarchies | Composite Sort Key |
| Multiple access patterns | GSI Overloading |
| High write throughput | Write Sharding |
| Subset needs secondary access | Sparse Indexes |
| Related entities queried together | Single-Table Design |
| Time-series data | Composite Key + Sharding |
| Status-based filtering | GSI with Status Prefix |
