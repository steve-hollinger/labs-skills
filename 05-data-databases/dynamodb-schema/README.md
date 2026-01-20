# DynamoDB Schema Design

Master DynamoDB schema design patterns including single-table design, Global Secondary Indexes (GSIs), Local Secondary Indexes (LSIs), and access pattern modeling.

## Learning Objectives

After completing this skill, you will be able to:
- Design effective DynamoDB schemas using single-table design patterns
- Model complex access patterns with partition and sort keys
- Implement GSIs and LSIs for secondary access patterns
- Apply best practices for key design and data distribution
- Write efficient queries using boto3

## Prerequisites

- Python 3.11+
- UV package manager
- Basic understanding of NoSQL concepts
- AWS account (optional, for production testing)

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Concepts

### Single-Table Design

DynamoDB's single-table design pattern allows you to store multiple entity types in a single table, reducing the number of round trips and enabling transactional operations across entities.

```python
from dynamodb_schema.examples.example_1 import UserOrderSchema

# Store users and orders in one table
schema = UserOrderSchema()
schema.create_user(user_id="USER#123", name="John Doe", email="john@example.com")
schema.create_order(user_id="USER#123", order_id="ORDER#456", total=99.99)

# Query user and all their orders in one request
result = schema.get_user_with_orders(user_id="USER#123")
```

### Access Pattern Modeling

Design your schema around your access patterns, not your data model:

```python
# Access patterns drive key design
# 1. Get user by ID -> PK=USER#id
# 2. Get order by ID -> PK=ORDER#id
# 3. Get all orders for user -> PK=USER#id, SK begins_with "ORDER#"
# 4. Get orders by date -> GSI1PK=USER#id, GSI1SK=date

access_patterns = [
    "Get user profile",
    "Get single order",
    "List all orders for a user",
    "List orders by date range",
]
```

### Global Secondary Indexes (GSIs)

GSIs enable querying on attributes other than the primary key:

```python
# GSI for querying orders by status
gsi_config = {
    "IndexName": "GSI1",
    "KeySchema": [
        {"AttributeName": "GSI1PK", "KeyType": "HASH"},
        {"AttributeName": "GSI1SK", "KeyType": "RANGE"}
    ],
    "Projection": {"ProjectionType": "ALL"}
}
```

## Examples

### Example 1: Basic Single-Table Design

Demonstrates the fundamental single-table pattern with users and orders.

```bash
make example-1
```

### Example 2: Complex Access Patterns with GSIs

Building on basics with multiple access patterns and GSIs.

```bash
make example-2
```

### Example 3: E-commerce Schema Design

Real-world e-commerce schema with products, orders, customers, and inventory.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Design a schema for a blog platform (users, posts, comments)
2. **Exercise 2**: Add GSIs for tag-based queries and recent posts
3. **Exercise 3**: Design a multi-tenant SaaS schema with isolation

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Hot Partition Keys

Using low-cardinality partition keys leads to hot partitions:

```python
# BAD: All items go to same partition
pk = "ORDERS"

# GOOD: Distribute across partitions
pk = f"ORDER#{order_id}"
```

### Over-Normalization

Don't bring relational thinking to DynamoDB:

```python
# BAD: Separate tables like relational DB
users_table = "Users"
orders_table = "Orders"

# GOOD: Single table with entity prefixes
table = "EcommerceData"
user_pk = "USER#123"
order_pk = "ORDER#456"
```

### Not Planning Access Patterns

Always define access patterns before designing your schema.

## Further Reading

- [Official DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [AWS DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- Related skills in this repository:
  - [DynamoDB Streams/CDC](../dynamodb-streams-cdc/)
  - [S3 Content-Addressed Storage](../s3-content-addressed/)
