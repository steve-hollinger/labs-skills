# Core Concepts

## Overview

DynamoDB Streams provides change data capture (CDC) capabilities, enabling you to capture and respond to item-level modifications in real-time. This is foundational for building event-driven architectures, maintaining materialized views, and implementing audit trails.

## Concept 1: DynamoDB Streams

### What It Is

DynamoDB Streams is an optional feature that captures a time-ordered sequence of item-level modifications in a DynamoDB table. Each stream record contains information about a data modification to a single item.

### Why It Matters

- **Real-time reactions**: Respond to data changes as they happen
- **Decoupled architecture**: Separate read/write from downstream processing
- **Audit compliance**: Maintain history of all changes
- **Data synchronization**: Keep secondary data stores in sync
- **Event sourcing**: Build event-driven systems on DynamoDB

### How It Works

```python
# Enable streams when creating a table
create_table_params = {
    "TableName": "Orders",
    "KeySchema": [...],
    "AttributeDefinitions": [...],
    "StreamSpecification": {
        "StreamEnabled": True,
        "StreamViewType": "NEW_AND_OLD_IMAGES"  # Choose view type
    }
}

# Stream records are partitioned into shards
# Each shard has a sequence of records
stream_record = {
    "eventID": "1234567890",           # Unique identifier
    "eventName": "MODIFY",              # INSERT, MODIFY, or REMOVE
    "eventVersion": "1.1",
    "eventSource": "aws:dynamodb",
    "awsRegion": "us-east-1",
    "dynamodb": {
        "ApproximateCreationDateTime": 1234567890,
        "Keys": {
            "PK": {"S": "ORDER#123"},
            "SK": {"S": "ORDER#123"}
        },
        "NewImage": {
            "PK": {"S": "ORDER#123"},
            "status": {"S": "shipped"}
        },
        "OldImage": {
            "PK": {"S": "ORDER#123"},
            "status": {"S": "pending"}
        },
        "SequenceNumber": "111111111111111111111111",
        "SizeBytes": 256,
        "StreamViewType": "NEW_AND_OLD_IMAGES"
    }
}
```

## Concept 2: Stream View Types

### What It Is

Stream view type determines what information is written to the stream when an item is modified. You choose this when enabling streams.

### Why It Matters

- Affects storage and read costs
- Determines what processing is possible
- Cannot be changed without disabling/re-enabling stream
- Different use cases need different views

### How It Works

```python
# KEYS_ONLY: Just the key attributes
# Best for: Triggering external lookups, minimal data transfer
keys_only_record = {
    "dynamodb": {
        "Keys": {"PK": {"S": "ORDER#123"}, "SK": {"S": "ORDER#123"}}
        # No NewImage or OldImage
    }
}

# NEW_IMAGE: The entire item after modification
# Best for: Syncing to search engines, caching
new_image_record = {
    "dynamodb": {
        "Keys": {...},
        "NewImage": {"PK": {...}, "status": {"S": "shipped"}, ...}
        # No OldImage
    }
}

# OLD_IMAGE: The entire item before modification
# Best for: Audit trails, undo functionality
old_image_record = {
    "dynamodb": {
        "Keys": {...},
        "OldImage": {"PK": {...}, "status": {"S": "pending"}, ...}
        # No NewImage
    }
}

# NEW_AND_OLD_IMAGES: Both before and after
# Best for: Computing diffs, validation, full audit
both_images_record = {
    "dynamodb": {
        "Keys": {...},
        "NewImage": {"status": {"S": "shipped"}, ...},
        "OldImage": {"status": {"S": "pending"}, ...}
    }
}
```

## Concept 3: Lambda Triggers

### What It Is

AWS Lambda can be configured to automatically invoke when records appear in a DynamoDB Stream. Lambda handles polling, batching, and retry logic.

### Why It Matters

- Serverless stream processing
- Automatic scaling with stream throughput
- Built-in error handling and retries
- Easy integration with other AWS services

### How It Works

```python
# Lambda handler receives batches of stream records
def lambda_handler(event, context):
    """Process DynamoDB Stream events."""
    print(f"Processing {len(event['Records'])} records")

    for record in event["Records"]:
        # Extract event details
        event_id = record["eventID"]
        event_name = record["eventName"]
        dynamodb = record["dynamodb"]

        # Process based on event type
        if event_name == "INSERT":
            new_item = deserialize(dynamodb["NewImage"])
            handle_insert(new_item)

        elif event_name == "MODIFY":
            old_item = deserialize(dynamodb.get("OldImage", {}))
            new_item = deserialize(dynamodb["NewImage"])
            handle_modify(old_item, new_item)

        elif event_name == "REMOVE":
            old_item = deserialize(dynamodb.get("OldImage", {}))
            handle_remove(old_item)

    return {"statusCode": 200}


# Lambda Event Source Mapping configuration
event_source_mapping = {
    "EventSourceArn": "arn:aws:dynamodb:...:table/Orders/stream/...",
    "FunctionName": "OrderStreamProcessor",
    "StartingPosition": "LATEST",  # or TRIM_HORIZON for all records
    "BatchSize": 100,
    "MaximumBatchingWindowInSeconds": 5,
    "ParallelizationFactor": 1,  # Up to 10 for parallel processing
    "MaximumRetryAttempts": 3,
    "BisectBatchOnFunctionError": True,  # Split batch on errors
    "DestinationConfig": {
        "OnFailure": {
            "Destination": "arn:aws:sqs:...:dead-letter-queue"
        }
    }
}
```

## Concept 4: At-Least-Once Delivery and Idempotency

### What It Is

DynamoDB Streams guarantees at-least-once delivery, meaning the same record may be delivered multiple times. Your processor must be idempotent.

### Why It Matters

- Prevents duplicate processing side effects
- Ensures data consistency
- Critical for financial or state-changing operations
- Required for exactly-once semantics

### How It Works

```python
# Idempotency using event ID tracking
class IdempotentProcessor:
    def __init__(self, tracking_table):
        self.tracking_table = tracking_table

    def process_record(self, record):
        event_id = record["eventID"]

        # Check if already processed
        response = self.tracking_table.get_item(
            Key={"eventID": event_id}
        )
        if "Item" in response:
            print(f"Already processed: {event_id}")
            return

        # Process the record
        self._do_process(record)

        # Mark as processed
        self.tracking_table.put_item(
            Item={
                "eventID": event_id,
                "processed_at": datetime.utcnow().isoformat(),
                "ttl": int(time.time()) + 86400  # 24 hour TTL
            }
        )

    def _do_process(self, record):
        # Actual processing logic
        pass


# Alternative: Conditional writes for idempotency
def idempotent_update(table, record):
    event_id = record["eventID"]
    sequence_number = record["dynamodb"]["SequenceNumber"]

    try:
        table.update_item(
            Key={"PK": "...", "SK": "..."},
            UpdateExpression="SET last_sequence = :seq",
            ConditionExpression="attribute_not_exists(last_sequence) OR last_sequence < :seq",
            ExpressionAttributeValues={":seq": sequence_number}
        )
        return True  # Proceed with processing
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        return False  # Already processed newer event
```

## Concept 5: Partial Batch Failure Handling

### What It Is

Lambda allows reporting which specific records in a batch failed, enabling retry of only failed records instead of the entire batch.

### Why It Matters

- Prevents infinite retry loops
- Allows successful records to proceed
- Improves throughput under partial failures
- Essential for production reliability

### How It Works

```python
def lambda_handler(event, context):
    """Handler with partial batch failure reporting."""
    batch_item_failures = []

    for record in event["Records"]:
        try:
            process_record(record)
        except RetryableError as e:
            # Record should be retried
            batch_item_failures.append({
                "itemIdentifier": record["eventID"]
            })
            print(f"Retryable failure for {record['eventID']}: {e}")
        except NonRetryableError as e:
            # Log but don't retry
            print(f"Non-retryable failure for {record['eventID']}: {e}")
            send_to_dlq(record, e)

    # Return failures for Lambda to retry
    return {
        "batchItemFailures": batch_item_failures
    }


# Enable in event source mapping
event_source_mapping_config = {
    "FunctionResponseTypes": ["ReportBatchItemFailures"],
    "BisectBatchOnFunctionError": True
}
```

## Concept 6: Stream Shards and Ordering

### What It Is

Stream records are organized into shards. Records within a shard are ordered, but there's no ordering guarantee across shards.

### Why It Matters

- Understanding ordering helps design correct processors
- Partition key determines which shard receives the record
- Parallel processing must consider ordering requirements
- Shard splits/merges affect processing

### How It Works

```python
# Records for same partition key go to same shard (ordered)
# Records for different partition keys may go to different shards (unordered)

# If you need ordering:
# 1. Use single partition key for related items
# 2. Or use sequence numbers for ordering

def process_with_ordering(records):
    """Process records respecting sequence order."""
    # Group by partition key
    by_partition = {}
    for record in records:
        pk = record["dynamodb"]["Keys"]["PK"]["S"]
        if pk not in by_partition:
            by_partition[pk] = []
        by_partition[pk].append(record)

    # Process each partition's records in sequence order
    for pk, partition_records in by_partition.items():
        sorted_records = sorted(
            partition_records,
            key=lambda r: r["dynamodb"]["SequenceNumber"]
        )
        for record in sorted_records:
            process_record(record)
```

## Summary

Key takeaways from DynamoDB Streams:

1. **Enable streams** with the appropriate view type for your use case
2. **Use Lambda triggers** for serverless, scalable processing
3. **Always implement idempotency** - assume at-least-once delivery
4. **Handle partial failures** to avoid infinite retry loops
5. **Understand shard ordering** - ordered within partition, not across
6. **Design for exactly-once semantics** using conditional writes or tracking tables
7. **Monitor and alert** on processing lag and errors
