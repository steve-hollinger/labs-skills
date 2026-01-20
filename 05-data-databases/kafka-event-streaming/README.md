# Kafka Event Streaming

Master event-driven architecture with Apache Kafka - the industry-standard distributed streaming platform for building real-time data pipelines and streaming applications.

## Learning Objectives

After completing this skill, you will be able to:
- Understand event-driven architecture principles and when to use Kafka
- Create producers and consumers using confluent-kafka-python
- Design topics, partitions, and understand message ordering
- Implement event schemas with serialization (JSON, Avro)
- Manage consumer groups and handle offset commits
- Build resilient event-driven systems with error handling and retries

## Prerequisites

- Python 3.11+
- UV package manager
- Docker (for local Kafka via shared infrastructure)
- Basic understanding of distributed systems concepts

## Quick Start

```bash
# Start shared infrastructure (includes Kafka)
cd ../../../
make infra-up
cd 05-data-databases/kafka-event-streaming

# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Concepts

### Event-Driven Architecture

Event-driven architecture (EDA) decouples services by having them communicate through events rather than direct calls. Kafka acts as the central nervous system, durably storing events and allowing multiple consumers to process them independently.

```python
from confluent_kafka import Producer

# Producer sends events without knowing who consumes them
producer = Producer({'bootstrap.servers': 'localhost:9092'})
producer.produce('user-events', key='user-123', value='{"action": "login"}')
producer.flush()
```

### Topics and Partitions

Topics are categories for organizing events. Partitions enable parallelism and ordering guarantees within a key.

```python
# Events with the same key go to the same partition
# Ensuring ordering for that key
producer.produce('orders', key='customer-456', value='{"order_id": 1}')
producer.produce('orders', key='customer-456', value='{"order_id": 2}')
# These will be processed in order for customer-456
```

### Consumer Groups

Consumer groups enable parallel processing while ensuring each message is processed once per group.

```python
from confluent_kafka import Consumer

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'order-processors',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe(['orders'])
```

## Examples

### Example 1: Basic Producer and Consumer

Learn the fundamentals of producing and consuming messages with Kafka.

```bash
make example-1
```

### Example 2: Event Schemas and Serialization

Implement structured event schemas with JSON serialization and validation.

```bash
make example-2
```

### Example 3: Consumer Groups and Offset Management

Build multi-consumer applications with manual offset commits and error handling.

```bash
make example-3
```

### Example 4: Event-Driven Order Processing

Complete event-driven system with multiple services communicating via Kafka.

```bash
make example-4
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Build an Event Logger - Create a producer that logs application events
2. **Exercise 2**: Implement a Message Processor - Build a consumer with retry logic
3. **Exercise 3**: Design an Event-Driven System - Create a multi-service order processing pipeline

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Not Flushing the Producer

Messages are batched by default. Always call `flush()` or use callbacks to ensure delivery:

```python
# Wrong - messages may not be sent
producer.produce('topic', value='message')

# Correct - ensure delivery
producer.produce('topic', value='message')
producer.flush()

# Or use delivery callbacks
def delivery_report(err, msg):
    if err:
        print(f'Delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()}[{msg.partition()}]')

producer.produce('topic', value='message', callback=delivery_report)
```

### Ignoring Consumer Poll Errors

Always check for errors when polling:

```python
msg = consumer.poll(timeout=1.0)
if msg is None:
    continue
if msg.error():
    if msg.error().code() == KafkaError._PARTITION_EOF:
        continue  # End of partition, not an error
    else:
        raise KafkaException(msg.error())
# Process message
```

### Not Handling Rebalances

Consumer group rebalances can cause duplicate processing. Implement rebalance callbacks:

```python
def on_revoke(consumer, partitions):
    # Commit offsets before partitions are revoked
    consumer.commit(asynchronous=False)

consumer.subscribe(['topic'], on_revoke=on_revoke)
```

## Infrastructure

This skill uses the shared Kafka infrastructure:

- **Bootstrap Server**: localhost:9092
- **Kafka UI**: localhost:8080
- **Schema Registry**: localhost:8081 (if enabled)

Start infrastructure from repository root:
```bash
make infra-up
```

## Further Reading

- [Kafka Official Documentation](https://kafka.apache.org/documentation/)
- [confluent-kafka-python Documentation](https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html)
- [Designing Event-Driven Systems (O'Reilly)](https://www.confluent.io/designing-event-driven-systems/)
- Related skills in this repository:
  - [DynamoDB Streams CDC](../dynamodb-streams-cdc/) - Change data capture patterns
  - [Kafka with franz-go](../../01-language-frameworks/go/kafka-franz-go/) - High-performance Go client
