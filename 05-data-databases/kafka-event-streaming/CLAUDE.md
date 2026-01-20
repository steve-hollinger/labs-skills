# CLAUDE.md - Kafka Event Streaming

This skill teaches event-driven architecture using Apache Kafka with Python's confluent-kafka library.

## Key Concepts

- **Event-Driven Architecture**: Decoupled services communicating through events rather than direct calls
- **Producers/Consumers**: Components that publish and subscribe to event streams
- **Topics/Partitions**: Logical organization of events with parallelism support
- **Consumer Groups**: Coordinated consumers for parallel processing with exactly-once semantics
- **Offset Management**: Tracking message consumption progress for reliability
- **Event Schemas**: Structured event definitions for type safety and evolution

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run specific example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
kafka-event-streaming/
├── src/kafka_event_streaming/
│   ├── __init__.py
│   ├── producer.py          # Producer wrapper utilities
│   ├── consumer.py          # Consumer wrapper utilities
│   ├── schemas.py           # Event schema definitions
│   └── examples/
│       ├── example_1.py     # Basic producer/consumer
│       ├── example_2.py     # Event schemas
│       ├── example_3.py     # Consumer groups
│       └── example_4.py     # Order processing system
├── exercises/
│   ├── exercise_1.py
│   ├── exercise_2.py
│   ├── exercise_3.py
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Producer with Delivery Callback
```python
from confluent_kafka import Producer
import json

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()}[{msg.partition()}]')

producer = Producer({'bootstrap.servers': 'localhost:9092'})
producer.produce(
    'events',
    key='key'.encode('utf-8'),
    value=json.dumps({'data': 'value'}).encode('utf-8'),
    callback=delivery_report
)
producer.flush()
```

### Pattern 2: Consumer with Error Handling
```python
from confluent_kafka import Consumer, KafkaError

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
})
consumer.subscribe(['events'])

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            raise Exception(msg.error())

        # Process message
        process(msg.value().decode('utf-8'))
        consumer.commit()
finally:
    consumer.close()
```

### Pattern 3: Event Schema with Pydantic
```python
from pydantic import BaseModel
from datetime import datetime
import json

class OrderEvent(BaseModel):
    event_type: str
    order_id: str
    customer_id: str
    timestamp: datetime
    data: dict

def serialize_event(event: OrderEvent) -> bytes:
    return event.model_dump_json().encode('utf-8')

def deserialize_event(data: bytes) -> OrderEvent:
    return OrderEvent.model_validate_json(data)
```

## Common Mistakes

1. **Not calling flush() on producer**
   - Messages are batched and may not be sent immediately
   - Always flush before exiting or when delivery is critical

2. **Ignoring partition assignment in consumer groups**
   - Consumers in same group share partitions
   - More consumers than partitions means idle consumers

3. **Using auto.offset.reset incorrectly**
   - 'earliest' starts from beginning (first time only)
   - 'latest' starts from end (may miss messages)
   - Committed offsets take precedence

4. **Not handling rebalances**
   - Partitions can be reassigned at any time
   - Commit offsets before rebalance completes

5. **Synchronous production in hot path**
   - Use asynchronous production with callbacks
   - Flush periodically or when necessary

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make examples` and the README.md. Ensure Kafka is running via `make infra-up` from repo root.

### "Why aren't my messages being consumed?"
Check:
1. Consumer group.id matches expectation
2. auto.offset.reset setting (earliest vs latest)
3. Topic exists and has messages
4. Consumer is subscribed to correct topic

### "How do I ensure message ordering?"
- Messages with same key go to same partition
- Ordering is guaranteed within a partition
- Use a consistent key for related messages

### "How do I handle failures?"
- Use delivery callbacks for producer
- Implement retry logic in consumer
- Use dead letter queues for failed messages
- Consider idempotent processing

### "What's the best practice for schemas?"
Refer to docs/patterns.md. Use Pydantic for schema validation, consider Avro with Schema Registry for production.

## Testing Notes

- Tests use pytest with markers
- Integration tests require running Kafka
- Use `pytest -k "test_name"` for specific tests
- Check coverage: `make coverage`
- Mark integration tests with `@pytest.mark.integration`

## Dependencies

Key dependencies in pyproject.toml:
- confluent-kafka: Official Kafka client for Python
- pydantic: Schema validation and serialization
- pytest-asyncio: Async test support

## Infrastructure Requirements

Kafka must be running. Start from repo root:
```bash
make infra-up
```

This starts:
- Kafka broker on localhost:9092
- Kafka UI on localhost:8080
- Zookeeper on localhost:2181
