---
name: streaming-kafka-events
description: Event-driven architecture using Apache Kafka with Python's confluent-kafka library. Use when writing or improving tests.
---

# Kafka Event Streaming

## Quick Start
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
    # ... see docs/patterns.md for more
```


## Key Points
- Event-Driven Architecture
- Producers/Consumers
- Topics/Partitions

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples