---
name: designing-dynamodb-schemas
description: DynamoDB schema design patterns including single-table design, GSIs, LSIs, and access pattern modeling using Python boto3. Use when writing or improving tests.
---

# Dynamodb Schema

## Quick Start
```python
# Always prefix keys with entity type
pk = f"USER#{user_id}"
sk = f"PROFILE#{user_id}"

# For related entities under same partition
pk = f"USER#{user_id}"
sk = f"ORDER#{order_id}"  # All orders queryable with begins_with
```


## Key Points
- Single-Table Design
- Access Patterns
- Partition Keys

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples