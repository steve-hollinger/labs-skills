---
name: designing-dynamodb-schemas
description: This skill teaches DynamoDB schema design patterns including single-table design, GSIs, LSIs, and access pattern modeling using Python boto3. Use when writing or improving tests.
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

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Basic single-table design
make example-2  # GSI access patterns
make example-3  # E-commerce schema
make test       # Run pytest with mocked DynamoDB
```

## Key Points
- Single-Table Design
- Access Patterns
- Partition Keys

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples