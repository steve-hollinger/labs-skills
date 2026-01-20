"""Example 3: Consumer Groups and Offset Management.

This example demonstrates consumer groups for parallel processing
and various offset management strategies.

Learning objectives:
- Understand consumer groups and partition assignment
- Implement manual offset commits
- Handle rebalances gracefully
- Choose appropriate commit strategies

Prerequisites:
- Kafka running on localhost:9092
- Start with: make infra-up (from repository root)
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from confluent_kafka import Consumer, KafkaError, Producer, TopicPartition


# ============================================================
# PART 1: Producer for Test Messages
# ============================================================


def produce_test_messages(topic: str, count: int = 20) -> None:
    """Produce test messages with different keys."""
    print(f"\n  Producing {count} test messages to {topic}...")

    producer = Producer({"bootstrap.servers": "localhost:9092"})

    for i in range(count):
        message = {
            "id": i + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "data": f"Message {i + 1}",
        }
        # Use modulo to distribute across 3 keys
        key = f"key-{i % 3}"

        producer.produce(
            topic=topic,
            key=key.encode("utf-8"),
            value=json.dumps(message).encode("utf-8"),
        )

    producer.flush(timeout=10)
    print(f"  Produced {count} messages")


# ============================================================
# PART 2: Basic Consumer Group
# ============================================================


@dataclass
class ConsumerStats:
    """Track consumer statistics."""

    consumer_id: str
    messages_processed: int = 0
    partitions_assigned: list[int] = field(default_factory=list)


def run_consumer_in_group(
    consumer_id: str,
    group_id: str,
    topic: str,
    stats: ConsumerStats,
    duration: float = 5.0,
) -> None:
    """Run a consumer as part of a consumer group."""

    def on_assign(consumer: Any, partitions: list[TopicPartition]) -> None:
        """Called when partitions are assigned."""
        stats.partitions_assigned = [p.partition for p in partitions]
        print(f"    [{consumer_id}] Assigned partitions: {stats.partitions_assigned}")

    def on_revoke(consumer: Any, partitions: list[TopicPartition]) -> None:
        """Called when partitions are revoked."""
        partition_ids = [p.partition for p in partitions]
        print(f"    [{consumer_id}] Revoked partitions: {partition_ids}")

    consumer = Consumer({
        "bootstrap.servers": "localhost:9092",
        "group.id": group_id,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
    })

    consumer.subscribe([topic], on_assign=on_assign, on_revoke=on_revoke)

    start_time = time.time()

    try:
        while time.time() - start_time < duration:
            msg = consumer.poll(timeout=0.5)

            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                print(f"    [{consumer_id}] Error: {msg.error()}")
                continue

            stats.messages_processed += 1

    finally:
        consumer.close()


def demonstrate_consumer_groups() -> None:
    """Demonstrate consumer group behavior."""
    print("\n" + "=" * 60)
    print("PART 1: Consumer Groups")
    print("=" * 60)

    topic = "consumer-group-demo"
    group_id = "demo-group"

    # Produce messages first
    produce_test_messages(topic, count=30)

    print(f"\n  Starting 2 consumers in group '{group_id}'")
    print("  Each consumer will receive a subset of partitions\n")

    # Create stats trackers
    stats1 = ConsumerStats(consumer_id="consumer-1")
    stats2 = ConsumerStats(consumer_id="consumer-2")

    # Run consumers in parallel
    threads = [
        threading.Thread(
            target=run_consumer_in_group,
            args=("consumer-1", group_id, topic, stats1),
        ),
        threading.Thread(
            target=run_consumer_in_group,
            args=("consumer-2", group_id, topic, stats2),
        ),
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print("\n  Results:")
    print(f"    Consumer 1: {stats1.messages_processed} messages from partitions {stats1.partitions_assigned}")
    print(f"    Consumer 2: {stats2.messages_processed} messages from partitions {stats2.partitions_assigned}")
    print(f"    Total: {stats1.messages_processed + stats2.messages_processed} messages")


# ============================================================
# PART 3: Manual Offset Commits
# ============================================================


def demonstrate_manual_commits() -> None:
    """Demonstrate manual offset commit strategies."""
    print("\n" + "=" * 60)
    print("PART 2: Manual Offset Commits")
    print("=" * 60)

    topic = "manual-commit-demo"
    produce_test_messages(topic, count=10)

    # Strategy 1: Commit after each message (safest, slowest)
    print("\n  Strategy 1: Commit after each message")
    print("  - Guarantees at-most-once processing")
    print("  - Highest overhead")

    consumer = Consumer({
        "bootstrap.servers": "localhost:9092",
        "group.id": "manual-commit-each",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,  # Disable auto-commit
    })
    consumer.subscribe([topic])

    processed = 0
    empty_polls = 0

    try:
        while processed < 5 and empty_polls < 3:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                empty_polls += 1
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    empty_polls += 1
                    continue
                raise Exception(msg.error())

            empty_polls = 0
            processed += 1

            # Process message
            value = json.loads(msg.value().decode("utf-8"))
            print(f"    Processed message {value['id']}")

            # Commit immediately after processing
            consumer.commit(asynchronous=False)
            print(f"      Committed offset {msg.offset() + 1}")

    finally:
        consumer.close()

    # Strategy 2: Batch commits
    print("\n  Strategy 2: Commit after batch")
    print("  - Better throughput")
    print("  - Risk of reprocessing on failure")

    consumer = Consumer({
        "bootstrap.servers": "localhost:9092",
        "group.id": "manual-commit-batch",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    })
    consumer.subscribe([topic])

    batch_size = 3
    batch: list[dict[str, Any]] = []
    empty_polls = 0

    try:
        while len(batch) < 6 and empty_polls < 3:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                empty_polls += 1
                # Commit remaining batch on timeout
                if batch:
                    consumer.commit(asynchronous=False)
                    print(f"    Committed batch of {len(batch)} on timeout")
                    batch = []
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    empty_polls += 1
                    continue
                raise Exception(msg.error())

            empty_polls = 0
            value = json.loads(msg.value().decode("utf-8"))
            batch.append(value)
            print(f"    Added message {value['id']} to batch")

            # Commit when batch is full
            if len(batch) >= batch_size:
                consumer.commit(asynchronous=False)
                print(f"    Committed batch of {len(batch)} messages")
                batch = []

    finally:
        consumer.close()


# ============================================================
# PART 4: Handling Rebalances
# ============================================================


def demonstrate_rebalance_handling() -> None:
    """Demonstrate graceful rebalance handling."""
    print("\n" + "=" * 60)
    print("PART 3: Handling Rebalances")
    print("=" * 60)

    topic = "rebalance-demo"
    produce_test_messages(topic, count=10)

    print("\n  Demonstrating rebalance callbacks")
    print("  - on_assign: Called when partitions are assigned")
    print("  - on_revoke: Called before partitions are revoked\n")

    # Track in-progress processing
    in_progress_offsets: dict[tuple[str, int], int] = {}

    def on_assign(consumer: Any, partitions: list[TopicPartition]) -> None:
        """Handle partition assignment."""
        print(f"    [ASSIGN] Received partitions: {[p.partition for p in partitions]}")

        # Could seek to specific offset here if needed
        # For example, to replay from a specific point:
        # for p in partitions:
        #     p.offset = specific_offset
        # consumer.assign(partitions)

    def on_revoke(consumer: Any, partitions: list[TopicPartition]) -> None:
        """Handle partition revocation."""
        print(f"    [REVOKE] Losing partitions: {[p.partition for p in partitions]}")

        # Commit any in-progress work before losing partitions
        if in_progress_offsets:
            print("    [REVOKE] Committing in-progress offsets")
            consumer.commit(asynchronous=False)
            in_progress_offsets.clear()

    consumer = Consumer({
        "bootstrap.servers": "localhost:9092",
        "group.id": "rebalance-demo-group",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    })

    consumer.subscribe([topic], on_assign=on_assign, on_revoke=on_revoke)

    processed = 0
    empty_polls = 0

    try:
        while processed < 5 and empty_polls < 3:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                empty_polls += 1
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    empty_polls += 1
                    continue
                raise Exception(msg.error())

            empty_polls = 0

            # Track in-progress offset
            partition_key = (msg.topic(), msg.partition())
            in_progress_offsets[partition_key] = msg.offset()

            # Process message
            value = json.loads(msg.value().decode("utf-8"))
            print(f"    Processing message {value['id']} from partition {msg.partition()}")

            # Simulate processing time
            time.sleep(0.1)

            # Commit after successful processing
            consumer.commit(asynchronous=False)
            del in_progress_offsets[partition_key]
            processed += 1

    finally:
        # Final commit before closing
        if in_progress_offsets:
            consumer.commit(asynchronous=False)
        consumer.close()

    print(f"\n    Processed {processed} messages with rebalance handling")


# ============================================================
# PART 5: Offset Reset and Replay
# ============================================================


def demonstrate_offset_control() -> None:
    """Demonstrate offset seeking and replay."""
    print("\n" + "=" * 60)
    print("PART 4: Offset Control and Replay")
    print("=" * 60)

    topic = "offset-control-demo"
    produce_test_messages(topic, count=10)

    print("\n  Demonstrating offset control")

    consumer = Consumer({
        "bootstrap.servers": "localhost:9092",
        "group.id": "offset-control-group",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    })

    # Get partition assignment
    consumer.subscribe([topic])

    # Poll once to trigger assignment
    consumer.poll(timeout=2.0)

    # Get assigned partitions
    assignment = consumer.assignment()
    if not assignment:
        print("    No partitions assigned")
        consumer.close()
        return

    print(f"    Assigned partitions: {[p.partition for p in assignment]}")

    # Seek to beginning
    print("\n    Seeking to beginning of all partitions...")
    for tp in assignment:
        consumer.seek(TopicPartition(tp.topic, tp.partition, 0))

    # Read first 3 messages
    print("    Reading first 3 messages:")
    for _ in range(3):
        msg = consumer.poll(timeout=1.0)
        if msg and not msg.error():
            value = json.loads(msg.value().decode("utf-8"))
            print(f"      Message {value['id']} @ offset {msg.offset()}")

    # Seek to offset 5
    print("\n    Seeking to offset 5...")
    for tp in assignment:
        consumer.seek(TopicPartition(tp.topic, tp.partition, 5))

    # Read next 3 messages
    print("    Reading 3 messages from offset 5:")
    for _ in range(3):
        msg = consumer.poll(timeout=1.0)
        if msg and not msg.error():
            value = json.loads(msg.value().decode("utf-8"))
            print(f"      Message {value['id']} @ offset {msg.offset()}")

    consumer.close()


def main() -> None:
    """Run all examples."""
    print("\n" + "#" * 60)
    print("# Example 3: Consumer Groups and Offset Management")
    print("#" * 60)

    try:
        demonstrate_consumer_groups()
        demonstrate_manual_commits()
        demonstrate_rebalance_handling()
        demonstrate_offset_control()

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
