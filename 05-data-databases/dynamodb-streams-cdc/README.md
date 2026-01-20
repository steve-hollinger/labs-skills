# DynamoDB Streams and Change Data Capture

Master change data capture (CDC) patterns using DynamoDB Streams, including stream processing with Lambda, event-driven architectures, and real-time data synchronization.

## Learning Objectives

After completing this skill, you will be able to:
- Enable and configure DynamoDB Streams on tables
- Process stream events with AWS Lambda triggers
- Implement common CDC patterns (aggregations, sync, audit)
- Build event-driven architectures with DynamoDB as the event source
- Handle stream processing failures and ensure exactly-once semantics

## Prerequisites

- Python 3.11+
- UV package manager
- Completed [DynamoDB Schema Design](../dynamodb-schema/) skill
- Basic understanding of AWS Lambda
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

### DynamoDB Streams Overview

DynamoDB Streams captures a time-ordered sequence of item-level modifications in a table and stores this information for up to 24 hours.

```python
# Stream record structure
stream_record = {
    "eventID": "unique-event-id",
    "eventName": "INSERT" | "MODIFY" | "REMOVE",
    "eventVersion": "1.1",
    "eventSource": "aws:dynamodb",
    "dynamodb": {
        "Keys": {...},
        "NewImage": {...},      # Present for INSERT/MODIFY
        "OldImage": {...},      # Present for MODIFY/REMOVE (if enabled)
        "SequenceNumber": "...",
        "SizeBytes": 123,
        "StreamViewType": "NEW_AND_OLD_IMAGES"
    }
}
```

### Stream View Types

Choose the right view type based on your use case:

| View Type | Contains | Use Case |
|-----------|----------|----------|
| KEYS_ONLY | Just the key attributes | Triggering external lookups |
| NEW_IMAGE | Item after modification | Sync to search/analytics |
| OLD_IMAGE | Item before modification | Audit trail, undo |
| NEW_AND_OLD_IMAGES | Both states | Diff computation, validation |

### Lambda Trigger Pattern

```python
def lambda_handler(event, context):
    for record in event["Records"]:
        event_name = record["eventName"]
        dynamodb = record["dynamodb"]

        if event_name == "INSERT":
            new_item = dynamodb.get("NewImage", {})
            # Process new item
        elif event_name == "MODIFY":
            old_item = dynamodb.get("OldImage", {})
            new_item = dynamodb.get("NewImage", {})
            # Process change
        elif event_name == "REMOVE":
            old_item = dynamodb.get("OldImage", {})
            # Process deletion
```

## Examples

### Example 1: Basic Stream Processing

Demonstrates capturing and processing stream events with Lambda.

```bash
make example-1
```

### Example 2: Aggregation Pattern

Building real-time aggregations (counters, sums) from stream events.

```bash
make example-2
```

### Example 3: Event-Driven Architecture

Complete event-driven system with multiple consumers and error handling.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Build an audit log from stream events
2. **Exercise 2**: Sync DynamoDB to Elasticsearch/OpenSearch
3. **Exercise 3**: Implement event sourcing with streams

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Processing Failures

Always handle failures gracefully - unhandled exceptions cause Lambda to retry:

```python
# BAD: Unhandled error retries forever
def handler(event, context):
    for record in event["Records"]:
        process(record)  # If this fails, entire batch retries

# GOOD: Handle errors per record
def handler(event, context):
    failures = []
    for record in event["Records"]:
        try:
            process(record)
        except Exception as e:
            failures.append(record["eventID"])
            # Log error, maybe send to DLQ
    return {"batchItemFailures": [{"itemIdentifier": f} for f in failures]}
```

### Idempotency

Streams guarantee at-least-once delivery, so make handlers idempotent:

```python
# Use eventID for deduplication
processed_events = set()  # Or check persistent storage

def process_with_dedup(record):
    event_id = record["eventID"]
    if event_id in processed_events:
        return  # Already processed
    # Process record
    processed_events.add(event_id)
```

## Further Reading

- [DynamoDB Streams Documentation](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html)
- [Lambda Event Source Mappings](https://docs.aws.amazon.com/lambda/latest/dg/with-ddb.html)
- Related skills in this repository:
  - [DynamoDB Schema Design](../dynamodb-schema/)
  - [Event-Driven Architecture](../../02-architecture-design/event-driven/)
