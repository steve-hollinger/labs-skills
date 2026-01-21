---
name: streaming-dynamodb-changes
description: Change data capture patterns using DynamoDB Streams, Lambda triggers, and event-driven architectures. Use when writing or improving tests.
---

# Dynamodb Streams Cdc

## Quick Start
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


## Key Points
- DynamoDB Streams
- Stream View Types
- Lambda Triggers

## Common Mistakes
1. **Not handling partial failures** - Return batchItemFailures for failed records
2. **Ignoring idempotency** - Use eventID for deduplication
3. **Not using appropriate stream view type** - Choose based on use case (NEW_AND_OLD_IMAGES for diffs)

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples