# Core Concepts

## Overview

This document covers the fundamental concepts of Apache Kafka and event-driven architecture that form the foundation of modern distributed systems.

## Concept 1: Event-Driven Architecture

### What It Is

Event-driven architecture (EDA) is a software design pattern where the flow of the program is determined by events - significant changes in state that are worth capturing and potentially reacting to. In EDA, components communicate by producing and consuming events rather than making direct calls.

### Why It Matters

- **Decoupling**: Services don't need to know about each other
- **Scalability**: Add consumers without changing producers
- **Resilience**: Services can fail independently without cascading failures
- **Auditability**: Events create a natural audit log
- **Flexibility**: New features can consume existing event streams

### How It Works

```python
from confluent_kafka import Producer, Consumer
import json

# Producer: Doesn't know or care who consumes the event
def publish_user_created(producer: Producer, user_id: str, email: str) -> None:
    event = {
        "event_type": "user.created",
        "user_id": user_id,
        "email": email,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    producer.produce(
        topic="user-events",
        key=user_id.encode("utf-8"),
        value=json.dumps(event).encode("utf-8")
    )
    producer.flush()

# Consumer A: Sends welcome email
# Consumer B: Updates analytics
# Consumer C: Provisions user resources
# All consume the same event independently
```

## Concept 2: Topics and Partitions

### What It Is

**Topics** are named feeds or categories to which records are published. They are the fundamental unit of organization in Kafka.

**Partitions** are ordered, immutable sequences of records within a topic. Each partition is an ordered log that can be consumed independently.

### Why It Matters

- **Parallelism**: Multiple partitions allow parallel processing
- **Ordering**: Messages within a partition are strictly ordered
- **Scalability**: Partitions can be spread across brokers
- **Retention**: Each partition retains messages based on policy

### How It Works

```
Topic: orders (3 partitions)

Partition 0: [order-1] [order-4] [order-7] ...
Partition 1: [order-2] [order-5] [order-8] ...
Partition 2: [order-3] [order-6] [order-9] ...
```

Key-based partitioning ensures related messages go to the same partition:

```python
from confluent_kafka import Producer

producer = Producer({"bootstrap.servers": "localhost:9092"})

# All orders for customer-123 go to the same partition
# Guaranteeing order for this customer
for order_num in range(1, 4):
    producer.produce(
        topic="orders",
        key="customer-123".encode("utf-8"),  # Determines partition
        value=f'{{"order": {order_num}}}'.encode("utf-8")
    )

producer.flush()
```

## Concept 3: Producers

### What It Is

A producer is a client that publishes records to Kafka topics. Producers are responsible for choosing which partition to send records to, typically based on the record key.

### Why It Matters

- **Throughput**: Batching and compression for high throughput
- **Reliability**: Acknowledgment settings control durability
- **Flexibility**: Callbacks for async processing

### How It Works

```python
from confluent_kafka import Producer
from typing import Optional

def delivery_callback(err: Optional[Exception], msg) -> None:
    """Called once for each message produced."""
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()}[{msg.partition()}] @ offset {msg.offset()}")

# Producer configuration
config = {
    "bootstrap.servers": "localhost:9092",
    "acks": "all",  # Wait for all replicas to acknowledge
    "retries": 3,   # Retry on transient failures
    "linger.ms": 5, # Batch messages for 5ms
}

producer = Producer(config)

# Produce with callback
producer.produce(
    topic="events",
    key="event-key".encode("utf-8"),
    value='{"data": "value"}'.encode("utf-8"),
    callback=delivery_callback
)

# Poll for delivery reports
producer.poll(0)

# Ensure all messages are delivered
producer.flush()
```

## Concept 4: Consumers and Consumer Groups

### What It Is

A consumer reads records from topics. Consumer groups are sets of consumers that cooperate to consume records from topics, with each partition assigned to exactly one consumer in the group.

### Why It Matters

- **Scalability**: Add consumers to increase throughput
- **Fault Tolerance**: Failed consumers have their partitions reassigned
- **Load Balancing**: Partitions are distributed among consumers
- **Independence**: Different groups can consume the same topic independently

### How It Works

```
Topic: orders (3 partitions)

Consumer Group A (Order Processors):
  Consumer A1 <- Partition 0
  Consumer A2 <- Partition 1, Partition 2

Consumer Group B (Analytics):
  Consumer B1 <- Partition 0, Partition 1, Partition 2
```

```python
from confluent_kafka import Consumer, KafkaError

config = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "order-processors",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,  # Manual commit for reliability
}

consumer = Consumer(config)
consumer.subscribe(["orders"])

try:
    while True:
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition - not an error
                continue
            else:
                raise Exception(msg.error())

        # Process the message
        print(f"Received: {msg.value().decode('utf-8')}")

        # Commit offset after successful processing
        consumer.commit()

finally:
    consumer.close()
```

## Concept 5: Offsets and Commit Strategies

### What It Is

An offset is a unique identifier for each record within a partition. It represents the position of a consumer in the log. Committing offsets saves the consumer's progress.

### Why It Matters

- **Exactly-once semantics**: Proper offset management prevents duplicate processing
- **Recovery**: Consumers resume from committed offset after restart
- **Reprocessing**: Can reset offsets to replay messages

### How It Works

```
Partition 0: [0] [1] [2] [3] [4] [5] [6] [7] ...
                              ^
                              Current offset (committed: 4)
```

Commit strategies:

```python
from confluent_kafka import Consumer

# Strategy 1: Auto-commit (simplest, but least reliable)
config_auto = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "my-group",
    "enable.auto.commit": True,
    "auto.commit.interval.ms": 5000,
}

# Strategy 2: Manual commit after each message (most reliable)
config_manual = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "my-group",
    "enable.auto.commit": False,
}

consumer = Consumer(config_manual)
consumer.subscribe(["events"])

msg = consumer.poll(1.0)
if msg and not msg.error():
    # Process message
    process(msg)
    # Commit synchronously - blocks until committed
    consumer.commit(asynchronous=False)

# Strategy 3: Batch commit (balance of throughput and reliability)
batch_size = 100
processed = 0

while True:
    msg = consumer.poll(1.0)
    if msg and not msg.error():
        process(msg)
        processed += 1
        if processed >= batch_size:
            consumer.commit(asynchronous=False)
            processed = 0
```

## Concept 6: Event Schemas

### What It Is

Event schemas define the structure and types of data in events. They provide contracts between producers and consumers, enabling schema evolution and validation.

### Why It Matters

- **Type Safety**: Catch errors at serialization time
- **Documentation**: Schema serves as documentation
- **Evolution**: Add fields without breaking consumers
- **Validation**: Ensure data quality

### How It Works

```python
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import json

class OrderStatus(str, Enum):
    CREATED = "created"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

class OrderEvent(BaseModel):
    """Schema for order events."""
    event_type: str = Field(..., pattern="^order\\.")
    order_id: str
    customer_id: str
    status: OrderStatus
    total_amount: float = Field(..., gt=0)
    timestamp: datetime
    version: int = 1

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Serialize for production
event = OrderEvent(
    event_type="order.created",
    order_id="ord-123",
    customer_id="cust-456",
    status=OrderStatus.CREATED,
    total_amount=99.99,
    timestamp=datetime.utcnow()
)

# Produce serialized event
producer.produce(
    topic="orders",
    key=event.order_id.encode("utf-8"),
    value=event.model_dump_json().encode("utf-8")
)

# Deserialize on consumption
def process_order_event(data: bytes) -> OrderEvent:
    return OrderEvent.model_validate_json(data)
```

## Summary

Key takeaways from these concepts:

1. **Event-driven architecture** decouples services through asynchronous event communication
2. **Topics and partitions** organize events and enable parallel processing
3. **Producers** publish events with delivery guarantees
4. **Consumer groups** enable scalable, fault-tolerant consumption
5. **Offset management** controls delivery semantics
6. **Event schemas** provide contracts and type safety

These concepts work together to build resilient, scalable event-driven systems.
