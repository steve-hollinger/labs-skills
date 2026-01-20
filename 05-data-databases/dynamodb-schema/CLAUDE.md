# CLAUDE.md - DynamoDB Schema Design

This skill teaches DynamoDB schema design patterns including single-table design, GSIs, LSIs, and access pattern modeling using Python boto3.

## Key Concepts

- **Single-Table Design**: Store multiple entity types in one table with composite keys
- **Access Patterns**: Design schema around query patterns, not data relationships
- **Partition Keys**: Choose high-cardinality attributes for even distribution
- **Sort Keys**: Enable range queries and hierarchical data organization
- **GSIs/LSIs**: Secondary indexes for alternative access patterns
- **Composite Keys**: Combine entity type prefixes with identifiers (USER#123)

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Basic single-table design
make example-2  # GSI access patterns
make example-3  # E-commerce schema
make test       # Run pytest with mocked DynamoDB
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
dynamodb-schema/
├── src/dynamodb_schema/
│   ├── __init__.py
│   ├── models.py          # Pydantic models for entities
│   ├── schema.py          # Schema design utilities
│   └── examples/
│       ├── example_1.py   # Basic single-table
│       ├── example_2.py   # GSI patterns
│       └── example_3.py   # E-commerce schema
├── exercises/
│   ├── exercise_1.py      # Blog schema design
│   ├── exercise_2.py      # GSI implementation
│   ├── exercise_3.py      # Multi-tenant design
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Entity Prefixing
```python
# Always prefix keys with entity type
pk = f"USER#{user_id}"
sk = f"PROFILE#{user_id}"

# For related entities under same partition
pk = f"USER#{user_id}"
sk = f"ORDER#{order_id}"  # All orders queryable with begins_with
```

### Pattern 2: GSI Overloading
```python
# Overload GSI for multiple access patterns
item = {
    "PK": f"ORDER#{order_id}",
    "SK": f"ORDER#{order_id}",
    "GSI1PK": f"USER#{user_id}",      # Query orders by user
    "GSI1SK": f"ORDER#{created_at}",   # Sort by date
    "GSI2PK": f"STATUS#{status}",      # Query by status
    "GSI2SK": f"ORDER#{created_at}"    # Sort by date
}
```

### Pattern 3: Adjacency List
```python
# Model graph-like relationships
# User -> Orders relationship
{"PK": "USER#123", "SK": "USER#123", "type": "user"}
{"PK": "USER#123", "SK": "ORDER#456", "type": "order"}
{"PK": "USER#123", "SK": "ORDER#789", "type": "order"}

# Query: PK = USER#123, SK begins_with ORDER#
```

## Common Mistakes

1. **Using low-cardinality partition keys**
   - Why it happens: Coming from relational thinking
   - How to fix it: Use unique identifiers or compound keys

2. **Creating too many tables**
   - Why it happens: Modeling like relational DB
   - How to fix it: Use single-table design with entity prefixes

3. **Not defining access patterns first**
   - Why it happens: Starting with data model instead of queries
   - How to fix it: List all access patterns before designing

4. **Forgetting GSI costs**
   - Why it happens: Not considering write amplification
   - How to fix it: Project only needed attributes, minimize GSIs

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make example-1` for the basic single-table pattern.

### "When should I use GSIs vs LSIs?"
- GSIs: Different partition key than base table, eventually consistent
- LSIs: Same partition key, strongly consistent, defined at table creation

### "How do I handle many-to-many relationships?"
Use adjacency list pattern with inverted indexes. See docs/patterns.md.

### "What about transactions?"
DynamoDB supports ACID transactions for up to 100 items. Use `transact_write_items`.

## Testing Notes

- Tests use moto library to mock DynamoDB locally
- Run specific tests: `pytest -k "test_single_table"`
- Integration tests can use DynamoDB Local (port 8000)
- Mark slow tests with `@pytest.mark.slow`

## Dependencies

Key dependencies in pyproject.toml:
- boto3: AWS SDK for DynamoDB operations
- moto: Mock AWS services for testing
- pydantic: Data validation and serialization
