# Common Patterns

## Overview

This document covers common patterns and best practices for building event-driven systems with Kafka.

## Pattern 1: Transactional Outbox

### When to Use

When you need to atomically update a database and publish an event. Without this pattern, you risk either:
- Database updated but event not sent (if publish fails)
- Event sent but database not updated (if database fails)

### Implementation

```python
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from confluent_kafka import Producer

@dataclass
class OutboxEvent:
    """Event stored in outbox table."""
    id: str
    aggregate_type: str
    aggregate_id: str
    event_type: str
    payload: dict
    created_at: datetime
    published_at: datetime | None = None

class Database(Protocol):
    def execute(self, query: str, params: tuple) -> None: ...
    def commit(self) -> None: ...

def create_order_with_outbox(
    db: Database,
    order_id: str,
    customer_id: str,
    items: list[dict]
) -> None:
    """Create order and outbox event in same transaction."""
    # Insert order
    db.execute(
        "INSERT INTO orders (id, customer_id, items) VALUES (?, ?, ?)",
        (order_id, customer_id, json.dumps(items))
    )

    # Insert outbox event (same transaction)
    event_payload = {
        "order_id": order_id,
        "customer_id": customer_id,
        "items": items,
        "created_at": datetime.utcnow().isoformat()
    }
    db.execute(
        "INSERT INTO outbox (aggregate_type, aggregate_id, event_type, payload) "
        "VALUES (?, ?, ?, ?)",
        ("order", order_id, "order.created", json.dumps(event_payload))
    )

    db.commit()  # Atomic commit

# Separate process polls outbox and publishes
def publish_outbox_events(db: Database, producer: Producer) -> None:
    """Background job to publish outbox events."""
    events = db.execute("SELECT * FROM outbox WHERE published_at IS NULL LIMIT 100")

    for event in events:
        producer.produce(
            topic=f"{event.aggregate_type}-events",
            key=event.aggregate_id.encode("utf-8"),
            value=event.payload.encode("utf-8")
        )
        producer.flush()

        db.execute(
            "UPDATE outbox SET published_at = ? WHERE id = ?",
            (datetime.utcnow(), event.id)
        )
        db.commit()
```

### Pitfalls to Avoid

- Don't delete outbox records immediately; keep for audit/debugging
- Ensure idempotent consumers in case of duplicate publishes
- Monitor outbox table size and implement cleanup

## Pattern 2: Event Sourcing

### When to Use

When you need a complete audit trail of all state changes, or when you want to reconstruct state at any point in time.

### Implementation

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import json

@dataclass
class Event:
    """Base event class."""
    event_id: str
    aggregate_id: str
    event_type: str
    timestamp: datetime
    data: dict
    version: int

class Aggregate(ABC):
    """Base aggregate with event sourcing."""

    def __init__(self, aggregate_id: str):
        self.aggregate_id = aggregate_id
        self.version = 0
        self._pending_events: List[Event] = []

    @abstractmethod
    def apply(self, event: Event) -> None:
        """Apply event to update state."""
        pass

    def load_from_history(self, events: List[Event]) -> None:
        """Reconstruct state from event history."""
        for event in events:
            self.apply(event)
            self.version = event.version

    def _raise_event(self, event_type: str, data: dict) -> None:
        """Raise a new event."""
        event = Event(
            event_id=f"{self.aggregate_id}-{self.version + 1}",
            aggregate_id=self.aggregate_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            data=data,
            version=self.version + 1
        )
        self.apply(event)
        self._pending_events.append(event)
        self.version = event.version

@dataclass
class OrderAggregate(Aggregate):
    """Order aggregate with event sourcing."""
    customer_id: str = ""
    items: List[dict] = field(default_factory=list)
    status: str = "pending"
    total: float = 0.0

    def create(self, customer_id: str, items: List[dict]) -> None:
        total = sum(item["price"] * item["quantity"] for item in items)
        self._raise_event("OrderCreated", {
            "customer_id": customer_id,
            "items": items,
            "total": total
        })

    def confirm(self) -> None:
        if self.status != "pending":
            raise ValueError("Order must be pending to confirm")
        self._raise_event("OrderConfirmed", {})

    def ship(self, tracking_number: str) -> None:
        if self.status != "confirmed":
            raise ValueError("Order must be confirmed to ship")
        self._raise_event("OrderShipped", {"tracking_number": tracking_number})

    def apply(self, event: Event) -> None:
        if event.event_type == "OrderCreated":
            self.customer_id = event.data["customer_id"]
            self.items = event.data["items"]
            self.total = event.data["total"]
            self.status = "pending"
        elif event.event_type == "OrderConfirmed":
            self.status = "confirmed"
        elif event.event_type == "OrderShipped":
            self.status = "shipped"
```

### Pitfalls to Avoid

- Events are immutable; never modify past events
- Plan for schema evolution (add fields, don't remove)
- Implement snapshots for aggregates with many events

## Pattern 3: Saga Pattern (Choreography)

### When to Use

When you need to coordinate multiple services in a distributed transaction. The choreography approach uses events without a central coordinator.

### Implementation

```python
from confluent_kafka import Producer, Consumer
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import json

class OrderCreatedEvent(BaseModel):
    order_id: str
    customer_id: str
    total_amount: float
    timestamp: datetime

class PaymentCompletedEvent(BaseModel):
    order_id: str
    payment_id: str
    amount: float
    timestamp: datetime

class PaymentFailedEvent(BaseModel):
    order_id: str
    reason: str
    timestamp: datetime

class InventoryReservedEvent(BaseModel):
    order_id: str
    items: list[dict]
    timestamp: datetime

class InventoryReservationFailedEvent(BaseModel):
    order_id: str
    reason: str
    timestamp: datetime

# Order Service - Initiates saga
class OrderService:
    def __init__(self, producer: Producer):
        self.producer = producer

    def create_order(self, order_id: str, customer_id: str, total: float) -> None:
        # Save order with status "pending"
        # ...

        # Publish event to start saga
        event = OrderCreatedEvent(
            order_id=order_id,
            customer_id=customer_id,
            total_amount=total,
            timestamp=datetime.utcnow()
        )
        self.producer.produce(
            "order-events",
            key=order_id.encode("utf-8"),
            value=event.model_dump_json().encode("utf-8")
        )
        self.producer.flush()

# Payment Service - Reacts to order created
class PaymentService:
    def __init__(self, producer: Producer, consumer: Consumer):
        self.producer = producer
        self.consumer = consumer
        self.consumer.subscribe(["order-events"])

    def process_events(self) -> None:
        while True:
            msg = self.consumer.poll(1.0)
            if msg is None or msg.error():
                continue

            event = json.loads(msg.value().decode("utf-8"))
            if "total_amount" in event:  # OrderCreatedEvent
                self.handle_order_created(OrderCreatedEvent(**event))

    def handle_order_created(self, event: OrderCreatedEvent) -> None:
        try:
            # Process payment
            payment_id = self.process_payment(event.customer_id, event.total_amount)

            # Publish success event
            success_event = PaymentCompletedEvent(
                order_id=event.order_id,
                payment_id=payment_id,
                amount=event.total_amount,
                timestamp=datetime.utcnow()
            )
            self.producer.produce(
                "payment-events",
                key=event.order_id.encode("utf-8"),
                value=success_event.model_dump_json().encode("utf-8")
            )
        except Exception as e:
            # Publish failure event for compensation
            failure_event = PaymentFailedEvent(
                order_id=event.order_id,
                reason=str(e),
                timestamp=datetime.utcnow()
            )
            self.producer.produce(
                "payment-events",
                key=event.order_id.encode("utf-8"),
                value=failure_event.model_dump_json().encode("utf-8")
            )
        self.producer.flush()

    def process_payment(self, customer_id: str, amount: float) -> str:
        # Actual payment logic
        return f"pay-{customer_id}-{amount}"
```

### Pitfalls to Avoid

- Ensure all services handle both success and failure events
- Implement compensating transactions for rollback
- Add correlation IDs for tracing across services

## Pattern 4: Dead Letter Queue

### When to Use

When you need to handle messages that fail processing repeatedly. DLQ allows you to capture, inspect, and retry failed messages.

### Implementation

```python
from confluent_kafka import Producer, Consumer, KafkaError
from dataclasses import dataclass
from datetime import datetime
import json
import traceback

@dataclass
class DeadLetterMessage:
    original_topic: str
    original_partition: int
    original_offset: int
    original_key: str | None
    original_value: str
    error_message: str
    error_traceback: str
    retry_count: int
    timestamp: datetime

class ConsumerWithDLQ:
    def __init__(
        self,
        consumer: Consumer,
        producer: Producer,
        dlq_topic: str,
        max_retries: int = 3
    ):
        self.consumer = consumer
        self.producer = producer
        self.dlq_topic = dlq_topic
        self.max_retries = max_retries
        self.retry_counts: dict[str, int] = {}

    def process_with_dlq(self, process_func) -> None:
        while True:
            msg = self.consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                raise Exception(msg.error())

            message_id = f"{msg.topic()}-{msg.partition()}-{msg.offset()}"

            try:
                process_func(msg)
                self.consumer.commit()
                # Clear retry count on success
                self.retry_counts.pop(message_id, None)

            except Exception as e:
                retry_count = self.retry_counts.get(message_id, 0) + 1
                self.retry_counts[message_id] = retry_count

                if retry_count >= self.max_retries:
                    self._send_to_dlq(msg, e, retry_count)
                    self.consumer.commit()
                    self.retry_counts.pop(message_id, None)
                else:
                    # Don't commit - message will be redelivered
                    print(f"Retry {retry_count}/{self.max_retries} for {message_id}")

    def _send_to_dlq(self, msg, error: Exception, retry_count: int) -> None:
        dlq_message = DeadLetterMessage(
            original_topic=msg.topic(),
            original_partition=msg.partition(),
            original_offset=msg.offset(),
            original_key=msg.key().decode("utf-8") if msg.key() else None,
            original_value=msg.value().decode("utf-8"),
            error_message=str(error),
            error_traceback=traceback.format_exc(),
            retry_count=retry_count,
            timestamp=datetime.utcnow()
        )

        self.producer.produce(
            self.dlq_topic,
            key=msg.key(),
            value=json.dumps(dlq_message.__dict__, default=str).encode("utf-8")
        )
        self.producer.flush()
        print(f"Message sent to DLQ: {msg.topic()}[{msg.partition()}]@{msg.offset()}")
```

### Pitfalls to Avoid

- Monitor DLQ size - growing DLQ indicates systemic issues
- Implement tooling to replay DLQ messages
- Don't lose the original message metadata

## Pattern 5: Idempotent Consumer

### When to Use

Always. Kafka guarantees at-least-once delivery, so consumers may see the same message multiple times.

### Implementation

```python
from confluent_kafka import Consumer
import json
from typing import Protocol

class IdempotencyStore(Protocol):
    def has_processed(self, message_id: str) -> bool: ...
    def mark_processed(self, message_id: str) -> None: ...

class RedisIdempotencyStore:
    def __init__(self, redis_client, ttl_seconds: int = 86400):
        self.redis = redis_client
        self.ttl = ttl_seconds
        self.prefix = "kafka:processed:"

    def has_processed(self, message_id: str) -> bool:
        return self.redis.exists(f"{self.prefix}{message_id}")

    def mark_processed(self, message_id: str) -> None:
        self.redis.setex(f"{self.prefix}{message_id}", self.ttl, "1")

class IdempotentConsumer:
    def __init__(self, consumer: Consumer, store: IdempotencyStore):
        self.consumer = consumer
        self.store = store

    def process_idempotently(self, process_func) -> None:
        while True:
            msg = self.consumer.poll(timeout=1.0)
            if msg is None or msg.error():
                continue

            # Create unique message ID
            message_id = f"{msg.topic()}-{msg.partition()}-{msg.offset()}"

            # Skip if already processed
            if self.store.has_processed(message_id):
                print(f"Skipping duplicate: {message_id}")
                self.consumer.commit()
                continue

            # Process message
            process_func(msg)

            # Mark as processed
            self.store.mark_processed(message_id)
            self.consumer.commit()
```

### Pitfalls to Avoid

- Use appropriate TTL for idempotency keys
- Consider using message headers for idempotency key if available
- Ensure idempotency check and processing are atomic if possible

## Anti-Patterns

### Anti-Pattern 1: Large Messages

Kafka is optimized for small messages. Large messages cause:
- Memory pressure on brokers
- Slow replication
- Consumer timeouts

```python
# Bad: Sending large payloads directly
producer.produce("events", value=large_binary_blob)  # >1MB is problematic

# Good: Store in object storage, send reference
reference = upload_to_s3(large_binary_blob)
producer.produce("events", value=json.dumps({"blob_ref": reference}).encode("utf-8"))
```

### Anti-Pattern 2: Synchronous Request-Response

Using Kafka for synchronous communication defeats its purpose.

```python
# Bad: Waiting for response
producer.produce("requests", value=request)
response = wait_for_response(timeout=30)  # Blocks, defeats async benefits

# Good: Use HTTP for request-response, Kafka for events
# Or use correlation IDs with separate response topics
```

### Anti-Pattern 3: Not Using Consumer Groups

Running multiple consumers without a group causes duplicate processing.

```python
# Bad: No group.id means each consumer sees all messages
consumer = Consumer({"bootstrap.servers": "localhost:9092"})

# Good: Use group.id for coordination
consumer = Consumer({
    "bootstrap.servers": "localhost:9092",
    "group.id": "my-service-consumers"
})
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Database + event atomicity | Transactional Outbox |
| Full audit trail needed | Event Sourcing |
| Multi-service coordination | Saga (Choreography or Orchestration) |
| Handling failed messages | Dead Letter Queue |
| Duplicate message handling | Idempotent Consumer |
| High-throughput processing | Batch processing with manual commits |
| Real-time analytics | Consumer groups with partitioning by key |
