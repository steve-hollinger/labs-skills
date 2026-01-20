"""Example 1: Basic Producer and Consumer.

This example demonstrates the fundamentals of producing and consuming
messages with Kafka using the confluent-kafka library.

Learning objectives:
- Create a Kafka producer and send messages
- Create a Kafka consumer and receive messages
- Understand delivery callbacks and error handling
- Work with message keys for partitioning

Prerequisites:
- Kafka running on localhost:9092
- Start with: make infra-up (from repository root)
"""

from __future__ import annotations

import json
import time
from datetime import datetime

from confluent_kafka import Consumer, KafkaError, Producer


def delivery_report(err: Exception | None, msg: object) -> None:
    """Callback for message delivery reports.

    This is called once for each message produced to indicate the result
    of the production attempt.
    """
    if err is not None:
        print(f"  [ERROR] Message delivery failed: {err}")
    else:
        # msg is a confluent_kafka.Message object
        print(f"  [OK] Message delivered to {msg.topic()}[{msg.partition()}] @ offset {msg.offset()}")  # type: ignore


def run_producer() -> None:
    """Demonstrate basic message production."""
    print("\n" + "=" * 60)
    print("PART 1: Basic Producer")
    print("=" * 60)

    # Producer configuration
    config = {
        "bootstrap.servers": "localhost:9092",
        "acks": "all",  # Wait for all in-sync replicas to acknowledge
    }

    producer = Producer(config)
    topic = "basic-events"

    print(f"\nProducing messages to topic: {topic}")

    # Produce simple messages
    messages = [
        {"event": "user_login", "user_id": "user-001", "timestamp": datetime.utcnow().isoformat()},
        {"event": "page_view", "user_id": "user-001", "page": "/home", "timestamp": datetime.utcnow().isoformat()},
        {"event": "button_click", "user_id": "user-002", "button": "signup", "timestamp": datetime.utcnow().isoformat()},
    ]

    for i, message in enumerate(messages):
        # Serialize message to JSON bytes
        value = json.dumps(message).encode("utf-8")

        # Key determines partition - same key = same partition = ordered
        key = message["user_id"].encode("utf-8")

        print(f"\n  Producing message {i + 1}: {message['event']}")

        # Produce with callback
        producer.produce(
            topic=topic,
            key=key,
            value=value,
            callback=delivery_report,
        )

        # Poll for delivery reports (non-blocking)
        producer.poll(0)

    # Wait for all messages to be delivered
    print("\n  Flushing producer (waiting for delivery)...")
    remaining = producer.flush(timeout=10)

    if remaining > 0:
        print(f"  [WARNING] {remaining} messages were not delivered")
    else:
        print("  All messages delivered successfully!")


def run_consumer() -> None:
    """Demonstrate basic message consumption."""
    print("\n" + "=" * 60)
    print("PART 2: Basic Consumer")
    print("=" * 60)

    # Consumer configuration
    config = {
        "bootstrap.servers": "localhost:9092",
        "group.id": "basic-consumer-group",
        "auto.offset.reset": "earliest",  # Start from beginning if no offset
        "enable.auto.commit": True,
        "auto.commit.interval.ms": 5000,
    }

    consumer = Consumer(config)
    topic = "basic-events"

    print(f"\nConsuming messages from topic: {topic}")
    print("  (Press Ctrl+C to stop)\n")

    consumer.subscribe([topic])

    message_count = 0
    max_messages = 10  # Stop after 10 messages for demo
    empty_polls = 0
    max_empty_polls = 5  # Stop after 5 empty polls

    try:
        while message_count < max_messages and empty_polls < max_empty_polls:
            # Poll for messages (1 second timeout)
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                empty_polls += 1
                print(f"  No message received (poll {empty_polls}/{max_empty_polls})")
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition - not an error
                    print(f"  Reached end of partition {msg.partition()}")
                    empty_polls += 1
                    continue
                else:
                    print(f"  [ERROR] Consumer error: {msg.error()}")
                    break

            # Reset empty poll counter on successful message
            empty_polls = 0
            message_count += 1

            # Decode message
            key = msg.key().decode("utf-8") if msg.key() else None
            value = json.loads(msg.value().decode("utf-8"))

            print(f"  Message {message_count}:")
            print(f"    Topic: {msg.topic()}")
            print(f"    Partition: {msg.partition()}")
            print(f"    Offset: {msg.offset()}")
            print(f"    Key: {key}")
            print(f"    Value: {value}")
            print()

    except KeyboardInterrupt:
        print("\n  Consumer interrupted by user")
    finally:
        # Close consumer connection
        consumer.close()
        print(f"\n  Consumed {message_count} messages total")


def run_key_based_partitioning() -> None:
    """Demonstrate how keys affect partitioning."""
    print("\n" + "=" * 60)
    print("PART 3: Key-Based Partitioning")
    print("=" * 60)

    producer = Producer({"bootstrap.servers": "localhost:9092"})
    topic = "partitioned-events"

    print(f"\nProducing messages with different keys to: {topic}")
    print("  Messages with the same key go to the same partition\n")

    # Track which partition each key goes to
    key_partitions: dict[str, set[int]] = {}

    def track_partition(err: Exception | None, msg: object) -> None:
        if err is None:
            key = msg.key().decode("utf-8") if msg.key() else "null"  # type: ignore
            partition = msg.partition()  # type: ignore
            if key not in key_partitions:
                key_partitions[key] = set()
            key_partitions[key].add(partition)

    # Produce multiple messages per key
    keys = ["customer-A", "customer-B", "customer-C"]

    for i in range(9):
        key = keys[i % 3]
        message = {"order": i + 1, "customer": key}

        producer.produce(
            topic=topic,
            key=key.encode("utf-8"),
            value=json.dumps(message).encode("utf-8"),
            callback=track_partition,
        )

    producer.flush(timeout=10)

    print("  Partition assignments:")
    for key, partitions in sorted(key_partitions.items()):
        print(f"    Key '{key}' -> Partition(s): {sorted(partitions)}")

    print("\n  Note: Each key consistently goes to the same partition,")
    print("  ensuring ordering for events with that key.")


def main() -> None:
    """Run all examples."""
    print("\n" + "#" * 60)
    print("# Example 1: Basic Producer and Consumer")
    print("#" * 60)

    try:
        run_producer()
        time.sleep(1)  # Give Kafka a moment to persist messages
        run_consumer()
        run_key_based_partitioning()

        print("\n" + "=" * 60)
        print("Example completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Example failed: {e}")
        print("\nMake sure Kafka is running:")
        print("  cd ../../.. && make infra-up")
        raise


if __name__ == "__main__":
    main()
