# Core Concepts

## Overview

DynamoDB schema design differs fundamentally from relational database design. Instead of normalizing data and using JOINs, DynamoDB schemas are designed around access patterns using denormalization and single-table design.

## Concept 1: Single-Table Design

### What It Is

Single-table design is a pattern where multiple entity types are stored in a single DynamoDB table. Entities are distinguished using composite keys with prefixes.

### Why It Matters

- **Reduced latency**: Fetch related entities in a single query
- **Transactional operations**: ACID transactions across entity types
- **Cost efficiency**: Fewer tables to manage and provision
- **Simplified operations**: Single backup, restore, and monitoring point

### How It Works

```python
# Multiple entity types in one table
items = [
    # User entity
    {
        "PK": "USER#123",
        "SK": "PROFILE#123",
        "type": "user",
        "name": "John Doe",
        "email": "john@example.com"
    },
    # Order entity (under same partition for queries)
    {
        "PK": "USER#123",
        "SK": "ORDER#2024-01-15#456",
        "type": "order",
        "order_id": "456",
        "total": 99.99,
        "status": "shipped"
    },
    # Another order
    {
        "PK": "USER#123",
        "SK": "ORDER#2024-01-10#789",
        "type": "order",
        "order_id": "789",
        "total": 149.99,
        "status": "delivered"
    }
]

# Query: Get user and all orders
# PK = "USER#123"
# Result includes profile and all orders sorted by date
```

## Concept 2: Access Pattern Modeling

### What It Is

Designing your schema by first identifying all the ways your application will query the data, then modeling keys and indexes to support those patterns.

### Why It Matters

- DynamoDB is optimized for specific query patterns
- Schema changes are expensive after data exists
- Wrong key design leads to expensive scans
- Proper modeling enables sub-millisecond queries

### How It Works

```python
# Step 1: List all access patterns
access_patterns = [
    "Get user by ID",
    "Get order by ID",
    "Get all orders for a user",
    "Get orders by status",
    "Get recent orders (last 30 days)",
    "Get orders by product",
]

# Step 2: Design keys for each pattern
key_design = {
    "Get user by ID": {
        "pattern": "Query",
        "PK": "USER#{user_id}",
        "SK": "PROFILE#{user_id}"
    },
    "Get order by ID": {
        "pattern": "Query",
        "PK": "ORDER#{order_id}",
        "SK": "ORDER#{order_id}"
    },
    "Get all orders for user": {
        "pattern": "Query",
        "PK": "USER#{user_id}",
        "SK": "begins_with ORDER#"
    },
    "Get orders by status": {
        "pattern": "Query on GSI1",
        "GSI1PK": "STATUS#{status}",
        "GSI1SK": "ORDER#{date}"
    }
}
```

## Concept 3: Partition Key Design

### What It Is

The partition key determines how data is distributed across DynamoDB's storage nodes. It's the most critical design decision for performance.

### Why It Matters

- Even distribution prevents hot partitions
- Hot partitions cause throttling and latency
- Each partition supports ~3000 RCUs and 1000 WCUs
- Cardinality directly impacts scalability

### How It Works

```python
# BAD: Low cardinality causes hot partitions
# All orders go to same partition
bad_key = {"PK": "ORDERS"}  # Only one partition!

# GOOD: High cardinality distributes load
good_key = {"PK": f"ORDER#{order_id}"}  # Millions of partitions

# For time-series data, add date sharding
sharded_key = {"PK": f"ORDERS#{date}#{shard_id}"}

# Calculate shard
import hashlib
def get_shard(order_id: str, num_shards: int = 10) -> str:
    hash_val = int(hashlib.md5(order_id.encode()).hexdigest(), 16)
    return str(hash_val % num_shards)
```

## Concept 4: Sort Key Patterns

### What It Is

The sort key enables range queries and hierarchical data organization within a partition. Combined with the partition key, it forms the primary key.

### Why It Matters

- Enables efficient range queries
- Supports hierarchical data (parent/child)
- Allows sorting without additional indexes
- Reduces need for filtering

### How It Works

```python
# Hierarchical data with sort key
# Organization -> Department -> Employee
items = [
    {"PK": "ORG#acme", "SK": "ORG#acme", "name": "Acme Corp"},
    {"PK": "ORG#acme", "SK": "DEPT#engineering", "name": "Engineering"},
    {"PK": "ORG#acme", "SK": "DEPT#engineering#EMP#001", "name": "Alice"},
    {"PK": "ORG#acme", "SK": "DEPT#engineering#EMP#002", "name": "Bob"},
    {"PK": "ORG#acme", "SK": "DEPT#sales", "name": "Sales"},
    {"PK": "ORG#acme", "SK": "DEPT#sales#EMP#003", "name": "Carol"},
]

# Query patterns:
# 1. Get org: PK = "ORG#acme", SK = "ORG#acme"
# 2. Get all depts: PK = "ORG#acme", SK begins_with "DEPT#"
# 3. Get specific dept: PK = "ORG#acme", SK = "DEPT#engineering"
# 4. Get dept employees: PK = "ORG#acme", SK begins_with "DEPT#engineering#EMP#"
```

## Concept 5: Global Secondary Indexes (GSIs)

### What It Is

GSIs allow querying data using different partition and sort keys than the base table. They maintain a separate copy of the data with the new key structure.

### Why It Matters

- Enable alternative access patterns
- Support queries on non-key attributes
- Can project subset of attributes (cost savings)
- Eventually consistent reads (usually sufficient)

### How It Works

```python
# Base table item
item = {
    "PK": "ORDER#123",
    "SK": "ORDER#123",
    "user_id": "USER#456",
    "status": "pending",
    "created_at": "2024-01-15T10:00:00Z",
    # GSI attributes
    "GSI1PK": "USER#456",              # Query orders by user
    "GSI1SK": "2024-01-15T10:00:00Z",  # Sorted by date
    "GSI2PK": "STATUS#pending",        # Query by status
    "GSI2SK": "2024-01-15T10:00:00Z",  # Sorted by date
}

# GSI Definition
gsi1_definition = {
    "IndexName": "GSI1",
    "KeySchema": [
        {"AttributeName": "GSI1PK", "KeyType": "HASH"},
        {"AttributeName": "GSI1SK", "KeyType": "RANGE"}
    ],
    "Projection": {
        "ProjectionType": "INCLUDE",
        "NonKeyAttributes": ["status", "total"]
    }
}

# Query GSI: Get all orders for user, sorted by date
response = table.query(
    IndexName="GSI1",
    KeyConditionExpression="GSI1PK = :pk",
    ExpressionAttributeValues={":pk": "USER#456"},
    ScanIndexForward=False  # Descending order (newest first)
)
```

## Concept 6: Local Secondary Indexes (LSIs)

### What It Is

LSIs allow alternate sort keys while keeping the same partition key. They share throughput with the base table and support strongly consistent reads.

### Why It Matters

- Same partition key = strongly consistent reads
- No additional throughput provisioning
- Must be defined at table creation
- Limited to 10GB per partition key value

### How It Works

```python
# LSI: Same partition key, different sort key
# Base table: PK=USER#id, SK=ORDER#date
# LSI: PK=USER#id, SK=ORDER#total (sort by amount)

lsi_definition = {
    "IndexName": "LSI1",
    "KeySchema": [
        {"AttributeName": "PK", "KeyType": "HASH"},
        {"AttributeName": "order_total", "KeyType": "RANGE"}
    ],
    "Projection": {"ProjectionType": "ALL"}
}

# Query: Get user's highest value orders
response = table.query(
    IndexName="LSI1",
    KeyConditionExpression="PK = :pk",
    ExpressionAttributeValues={":pk": "USER#456"},
    ScanIndexForward=False,  # Descending (highest first)
    Limit=10
)
```

## Summary

Key takeaways from DynamoDB schema design:

1. **Design for access patterns, not data structure**
2. **Use single-table design to reduce latency and enable transactions**
3. **Choose high-cardinality partition keys to avoid hot partitions**
4. **Use sort keys for hierarchical data and range queries**
5. **Add GSIs sparingly - they have write cost implications**
6. **Consider LSIs for strongly consistent alternative sort orders**
7. **Plan indexes at table creation time when possible**
