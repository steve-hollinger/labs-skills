# CLAUDE.md - DynamoDB Streams and CDC

This skill teaches change data capture patterns using DynamoDB Streams, Lambda triggers, and event-driven architectures.

## Key Concepts

- **DynamoDB Streams**: Time-ordered sequence of item modifications
- **Stream View Types**: KEYS_ONLY, NEW_IMAGE, OLD_IMAGE, NEW_AND_OLD_IMAGES
- **Lambda Triggers**: Functions invoked by stream events
- **CDC Patterns**: Aggregation, sync, audit, event sourcing
- **Idempotency**: Handling at-least-once delivery
- **Error Handling**: Partial batch failures, DLQs

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Basic stream processing
make example-2  # Aggregation pattern
make example-3  # Event-driven architecture
make test       # Run pytest with mocked streams
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
dynamodb-streams-cdc/
├── src/dynamodb_streams_cdc/
│   ├── __init__.py
│   ├── processor.py       # Stream processing utilities
│   ├── deserializer.py    # DynamoDB to Python conversion
│   └── examples/
│       ├── example_1.py   # Basic processing
│       ├── example_2.py   # Aggregations
│       └── example_3.py   # Event-driven
├── exercises/
│   ├── exercise_1.py      # Audit log
│   ├── exercise_2.py      # Search sync
│   ├── exercise_3.py      # Event sourcing
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Stream Event Handler
```python
def handler(event, context):
    for record in event["Records"]:
        event_name = record["eventName"]
        keys = deserialize(record["dynamodb"]["Keys"])

        if event_name == "INSERT":
            new_item = deserialize(record["dynamodb"]["NewImage"])
            on_insert(keys, new_item)
        elif event_name == "MODIFY":
            old_item = deserialize(record["dynamodb"]["OldImage"])
            new_item = deserialize(record["dynamodb"]["NewImage"])
            on_modify(keys, old_item, new_item)
        elif event_name == "REMOVE":
            old_item = deserialize(record["dynamodb"]["OldImage"])
            on_remove(keys, old_item)
```

### Pattern 2: Partial Batch Failure
```python
def handler(event, context):
    batch_failures = []

    for record in event["Records"]:
        try:
            process_record(record)
        except Exception as e:
            batch_failures.append({
                "itemIdentifier": record["eventID"]
            })

    return {"batchItemFailures": batch_failures}
```

### Pattern 3: Idempotent Processing
```python
def process_with_idempotency(record, processed_table):
    event_id = record["eventID"]

    # Check if already processed
    try:
        processed_table.put_item(
            Item={"eventID": event_id, "processed_at": timestamp},
            ConditionExpression="attribute_not_exists(eventID)"
        )
    except ConditionalCheckFailedException:
        return  # Already processed, skip

    # Process the record
    handle_record(record)
```

## Common Mistakes

1. **Not handling partial failures**
   - Why it happens: Assuming all-or-nothing processing
   - How to fix: Return batchItemFailures for failed records

2. **Ignoring idempotency**
   - Why it happens: Assuming exactly-once delivery
   - How to fix: Use eventID for deduplication

3. **Not using appropriate stream view type**
   - Why it happens: Defaulting to KEYS_ONLY
   - How to fix: Choose based on use case (NEW_AND_OLD_IMAGES for diffs)

4. **Synchronous external calls in handler**
   - Why it happens: Not considering Lambda timeout
   - How to fix: Use async patterns or SQS for long operations

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make example-1` for basic stream processing.

### "How do I debug stream events?"
Recommend logging the full event, using CloudWatch Logs Insights, and testing locally with moto.

### "What about ordering guarantees?"
Explain that streams provide ordering within a shard (partition key), but not across shards.

### "How do I handle large batches?"
Discuss batch size configuration, parallelization, and the tradeoff with Lambda timeout.

## Testing Notes

- Tests use moto library to mock DynamoDB Streams
- Run specific tests: `pytest -k "test_stream"`
- Integration tests require DynamoDB Local with streams enabled
- Use `pytest.mark.integration` for tests needing real AWS

## Dependencies

Key dependencies in pyproject.toml:
- boto3: AWS SDK for DynamoDB and Lambda
- moto: Mock AWS services for testing
- pydantic: Data validation and serialization
