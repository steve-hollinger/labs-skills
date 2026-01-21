# Code Patterns: Kafka Consumer with aiokafka

## Pattern 1: Basic Consumer with MSK IAM Authentication

**When to Use:** Building any Kafka consumer at Fetch that connects to MSK clusters. This is the foundational pattern for all Kafka consumption with IAM authentication.

```python
# src/services/kafka_consumer.py
import asyncio
import logging
import os
from typing import Callable, Optional

from aiokafka import AIOKafkaConsumer
from aiokafka.abc import AbstractTokenProvider
from aiokafka.helpers import create_ssl_context

logger = logging.getLogger(__name__)


class MSKTokenProvider(AbstractTokenProvider):
    """Token provider for AWS MSK IAM authentication."""

    def __init__(self, region: str):
        self.region = region
        logger.info(f"Initialized MSK token provider for region: {region}")

    async def token(self):
        """Generate authentication token for MSK IAM authentication."""
        from aws_msk_iam_sasl_signer import MSKAuthTokenProvider

        # Run synchronously in executor to avoid blocking asyncio loop
        loop = asyncio.get_running_loop()
        token, _ = await loop.run_in_executor(
            None, MSKAuthTokenProvider.generate_auth_token, self.region
        )
        return token


class KafkaConsumerConfig:
    """Configuration for Kafka consumer."""

    def __init__(
        self,
        brokers: list[str],
        topic: str,
        consumer_group: str,
        use_msk_iam: bool = True,
        auto_offset_reset: str = "earliest",
    ):
        self.brokers = brokers
        self.topic = topic
        self.consumer_group = consumer_group
        self.use_msk_iam = use_msk_iam
        self.auto_offset_reset = auto_offset_reset


async def start_kafka_consumer(
    config: KafkaConsumerConfig,
    message_handler: Callable[[bytes], None],
) -> None:
    """Start Kafka consumer and process messages."""
    logger.info(
        f"Starting Kafka consumer: brokers={config.brokers}, "
        f"topic={config.topic}, group={config.consumer_group}"
    )

    # Build consumer configuration
    consumer_config = {
        "bootstrap_servers": config.brokers,
        "group_id": config.consumer_group,
        "auto_offset_reset": config.auto_offset_reset,
        "enable_auto_commit": True,
        "session_timeout_ms": 180000,  # 3 minutes for heavy processing
        "heartbeat_interval_ms": 3000,  # 3 seconds
        "value_deserializer": lambda x: x,  # Return raw bytes
    }

    # Add MSK IAM authentication
    if config.use_msk_iam:
        ssl_context = create_ssl_context()

        # Determine region from broker hostnames
        region = "us-east-1"
        if config.brokers and "us-west-2" in config.brokers[0]:
            region = "us-west-2"

        tp = MSKTokenProvider(region=region)

        consumer_config.update({
            "security_protocol": "SASL_SSL",
            "sasl_mechanism": "OAUTHBEARER",
            "sasl_oauth_token_provider": tp,
            "ssl_context": ssl_context,
        })
        logger.info(f"Using MSK IAM authentication for region: {region}")

    consumer = AIOKafkaConsumer(config.topic, **consumer_config)

    try:
        await consumer.start()
        logger.info("Kafka consumer started successfully")

        async for message in consumer:
            try:
                await message_handler(message.value)
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
                # Continue processing other messages

    except asyncio.CancelledError:
        logger.info("Kafka consumer cancelled")
        raise
    except Exception as e:
        logger.error(f"Fatal error in Kafka consumer: {e}", exc_info=True)
        raise
    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped")


def create_kafka_config_from_env() -> KafkaConsumerConfig:
    """Create Kafka configuration from environment variables."""
    brokers = os.getenv("KAFKA_BROKERS", "localhost:9092").split(",")
    topic = os.getenv("KAFKA_TOPIC", "")
    consumer_group = os.getenv("KAFKA_CONSUMER_GROUP", "python-service-consumer")
    use_msk_iam = os.getenv("USE_MSK_IAM", "true").lower() == "true"

    if not topic:
        raise ValueError("KAFKA_TOPIC environment variable is required")

    return KafkaConsumerConfig(
        brokers=brokers,
        topic=topic,
        consumer_group=consumer_group,
        use_msk_iam=use_msk_iam,
    )


# Usage example
async def process_message(message_bytes: bytes):
    """Process a single message."""
    import json
    data = json.loads(message_bytes)
    logger.info(f"Processing message: {data.get('id')}")
    # Add your business logic here


async def main():
    config = create_kafka_config_from_env()
    await start_kafka_consumer(config, process_message)


if __name__ == "__main__":
    asyncio.run(main())
```

**Pitfalls:**
- **Missing aws-msk-iam-sasl-signer dependency**: Install with `pip install aws-msk-iam-sasl-signer-python`
- **Wrong SASL mechanism**: Use OAUTHBEARER, not AWS_MSK_IAM (that's for Java/Go clients)
- **Blocking token generation**: Always run MSKAuthTokenProvider.generate_auth_token in executor with loop.run_in_executor
- **Session timeout too short**: Set session_timeout_ms to 45-180 seconds to handle slow message processing

---

## Pattern 2: Batch Processing Pattern

**When to Use:** Processing high-volume topics where per-message overhead is significant. Ideal for ETL jobs, data ingestion, or when downstream operations benefit from bulk processing (database inserts, API calls).

```python
# src/services/batch_consumer.py
import asyncio
import logging
from typing import Callable, List

from aiokafka import AIOKafkaConsumer

logger = logging.getLogger(__name__)


async def consume_with_batching(
    consumer: AIOKafkaConsumer,
    batch_handler: Callable[[List[bytes]], None],
    batch_size: int = 100,
    batch_timeout_seconds: float = 3.0,
):
    """
    Consume messages with batching.

    Processes messages in batches when either:
    - Batch size reaches threshold (e.g., 100 messages)
    - Timeout elapsed since last batch (e.g., 3 seconds)
    """
    batch = []
    last_batch_time = asyncio.get_event_loop().time()

    async for message in consumer:
        batch.append(message.value)

        current_time = asyncio.get_event_loop().time()
        time_since_last_batch = current_time - last_batch_time

        # Process batch if size or timeout reached
        should_process = (
            len(batch) >= batch_size or
            time_since_last_batch >= batch_timeout_seconds
        )

        if should_process:
            try:
                await batch_handler(batch)
                logger.info(f"Processed batch of {len(batch)} messages")
            except Exception as e:
                logger.error(
                    f"Error processing batch of {len(batch)} messages: {e}",
                    exc_info=True,
                )
                # Could send to DLQ here

            batch = []
            last_batch_time = current_time


# Example: Batch insert to database
async def batch_insert_products(messages: List[bytes]):
    """Process batch of product messages and insert to database."""
    import json

    products = []
    for msg_bytes in messages:
        try:
            data = json.loads(msg_bytes)
            products.append({
                "id": data["id"],
                "name": data["name"],
                "category": data["category"],
            })
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse message: {e}")
            continue

    if products:
        # Bulk insert to database
        await db.execute_many(
            "INSERT INTO products (id, name, category) VALUES ($1, $2, $3)",
            [(p["id"], p["name"], p["category"]) for p in products]
        )
        logger.info(f"Inserted {len(products)} products")


# Usage
async def main():
    config = create_kafka_config_from_env()
    consumer_config = {
        "bootstrap_servers": config.brokers,
        "group_id": config.consumer_group,
        "auto_offset_reset": "earliest",
        "enable_auto_commit": True,
        "session_timeout_ms": 180000,
        "heartbeat_interval_ms": 3000,
    }

    consumer = AIOKafkaConsumer(config.topic, **consumer_config)
    await consumer.start()

    try:
        await consume_with_batching(
            consumer,
            batch_insert_products,
            batch_size=100,
            batch_timeout_seconds=3.0,
        )
    finally:
        await consumer.stop()
```

**Pitfalls:**
- **Batch timeout too long**: Keep timeout under 30 seconds to avoid delaying low-volume processing
- **No partial batch handling**: Always process remaining batch on shutdown or errors
- **Memory exhaustion**: Set reasonable batch size limits based on message size (100-500 typical)
- **Transaction boundaries**: Consider manual offset commits after successful batch processing

---

## Pattern 3: Error Handling with Dead Letter Queue

**When to Use:** Production services that need resilient error handling. Messages that fail processing should be retried and eventually moved to a DLQ for investigation rather than blocking the consumer.

```python
# src/services/resilient_consumer.py
import asyncio
import logging
from dataclasses import dataclass
from typing import Callable, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError

logger = logging.getLogger(__name__)


@dataclass
class MessageProcessingResult:
    """Result of message processing attempt."""
    success: bool
    error: Optional[str] = None
    retry_count: int = 0


class ResilientConsumer:
    """Kafka consumer with retry logic and dead letter queue."""

    def __init__(
        self,
        consumer: AIOKafkaConsumer,
        dlq_producer: Optional[AIOKafkaProducer] = None,
        dlq_topic: Optional[str] = None,
        max_retries: int = 3,
        retry_delay_seconds: float = 5.0,
    ):
        self.consumer = consumer
        self.dlq_producer = dlq_producer
        self.dlq_topic = dlq_topic
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds

    async def process_with_retry(
        self,
        message_handler: Callable[[bytes], None],
        message_bytes: bytes,
    ) -> MessageProcessingResult:
        """Process message with exponential backoff retry."""
        for attempt in range(self.max_retries):
            try:
                await message_handler(message_bytes)
                return MessageProcessingResult(success=True)
            except Exception as e:
                logger.warning(
                    f"Message processing failed (attempt {attempt + 1}/{self.max_retries}): {e}"
                )

                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.retry_delay_seconds * (2 ** attempt)
                    await asyncio.sleep(delay)
                else:
                    # Final attempt failed
                    return MessageProcessingResult(
                        success=False,
                        error=str(e),
                        retry_count=self.max_retries,
                    )

    async def send_to_dlq(self, message_bytes: bytes, error: str):
        """Send failed message to dead letter queue."""
        if not self.dlq_producer or not self.dlq_topic:
            logger.error(f"No DLQ configured, dropping message: {error}")
            return

        try:
            import json
            import time

            dlq_message = {
                "original_message": message_bytes.decode("utf-8"),
                "error": error,
                "timestamp": int(time.time()),
            }

            await self.dlq_producer.send_and_wait(
                self.dlq_topic,
                json.dumps(dlq_message).encode("utf-8"),
            )
            logger.info(f"Sent failed message to DLQ: {self.dlq_topic}")
        except Exception as e:
            logger.error(f"Failed to send message to DLQ: {e}", exc_info=True)

    async def consume(self, message_handler: Callable[[bytes], None]):
        """Consume messages with retry and DLQ handling."""
        async for message in self.consumer:
            result = await self.process_with_retry(
                message_handler,
                message.value,
            )

            if not result.success:
                logger.error(
                    f"Message processing failed after {result.retry_count} retries: "
                    f"{result.error}"
                )
                await self.send_to_dlq(message.value, result.error)


# Usage example
async def main():
    config = create_kafka_config_from_env()

    # Create consumer
    consumer = AIOKafkaConsumer(
        config.topic,
        bootstrap_servers=config.brokers,
        group_id=config.consumer_group,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )
    await consumer.start()

    # Create DLQ producer
    dlq_producer = AIOKafkaProducer(
        bootstrap_servers=config.brokers,
    )
    await dlq_producer.start()

    resilient_consumer = ResilientConsumer(
        consumer=consumer,
        dlq_producer=dlq_producer,
        dlq_topic=f"{config.topic}.dlq",
        max_retries=3,
        retry_delay_seconds=5.0,
    )

    try:
        await resilient_consumer.consume(process_message)
    finally:
        await consumer.stop()
        await dlq_producer.stop()
```

**Pitfalls:**
- **Retry without backoff**: Always use exponential backoff to avoid overwhelming downstream services
- **Infinite retries**: Set reasonable max_retries (3-5) to avoid blocking consumer
- **DLQ without monitoring**: Set up alerts for DLQ message count to catch recurring failures
- **Retrying non-retryable errors**: Use different strategies for transient (retry) vs permanent (DLQ) failures

---

## Pattern 4: Graceful Shutdown with Offset Reset

**When to Use:** Development and testing environments where you need to replay messages from the beginning. Also critical for production services to ensure clean shutdown without message loss.

```python
# src/services/consumer_lifecycle.py
import asyncio
import logging
import signal
from typing import Callable, Optional

from aiokafka import AIOKafkaConsumer

logger = logging.getLogger(__name__)


class GracefulConsumer:
    """Kafka consumer with graceful shutdown and offset management."""

    def __init__(
        self,
        consumer: AIOKafkaConsumer,
        reset_offset_on_start: bool = False,
    ):
        self.consumer = consumer
        self.reset_offset_on_start = reset_offset_on_start
        self.running = False
        self._shutdown_event = asyncio.Event()

    async def reset_offsets(self):
        """Reset consumer offsets to beginning."""
        logger.info("Resetting offsets to beginning...")

        # Create temporary consumer for offset reset
        temp_consumer = AIOKafkaConsumer(
            *self.consumer._subscription.subscription,
            bootstrap_servers=self.consumer._client.config["bootstrap_servers"],
            group_id=self.consumer._group_id,
            enable_auto_commit=False,
        )

        try:
            await asyncio.wait_for(temp_consumer.start(), timeout=30.0)

            # Wait for partition assignment
            max_retries = 6
            for attempt in range(max_retries):
                partitions = temp_consumer.assignment()
                if partitions:
                    logger.info(f"Got {len(partitions)} partitions assigned")
                    break
                await asyncio.sleep(5)

            if partitions:
                await temp_consumer.seek_to_beginning(*partitions)
                await temp_consumer.commit()
                logger.info(f"Successfully reset offsets for {len(partitions)} partitions")
            else:
                logger.error("Failed to get partition assignment")
        finally:
            await temp_consumer.stop()

    async def start(self, message_handler: Callable[[bytes], None]):
        """Start consumer with optional offset reset."""
        await self.consumer.start()

        if self.reset_offset_on_start:
            await self.reset_offsets()

        self.running = True
        logger.info("Kafka consumer started")

        try:
            while self.running:
                try:
                    # Use timeout to check shutdown event periodically
                    message = await asyncio.wait_for(
                        self.consumer.getone(),
                        timeout=1.0,
                    )
                    await message_handler(message.value)
                except asyncio.TimeoutError:
                    # Check if shutdown requested
                    if self._shutdown_event.is_set():
                        break
                    continue
        except asyncio.CancelledError:
            logger.info("Consumer task cancelled")
        finally:
            await self.stop()

    async def stop(self):
        """Stop consumer gracefully."""
        logger.info("Stopping Kafka consumer...")
        self.running = False
        self._shutdown_event.set()

        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")

    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.stop())

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


# Usage example
async def main():
    import os

    config = create_kafka_config_from_env()
    reset_offset = os.getenv("RESET_OFFSET_ON_START", "false").lower() == "true"

    consumer = AIOKafkaConsumer(
        config.topic,
        bootstrap_servers=config.brokers,
        group_id=config.consumer_group,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        session_timeout_ms=180000,
        heartbeat_interval_ms=3000,
    )

    graceful_consumer = GracefulConsumer(
        consumer=consumer,
        reset_offset_on_start=reset_offset,
    )

    # Setup signal handlers
    graceful_consumer.setup_signal_handlers()

    # Start consuming
    await graceful_consumer.start(process_message)


if __name__ == "__main__":
    asyncio.run(main())
```

**Pitfalls:**
- **Not waiting for partition assignment**: Always check partitions before calling seek_to_beginning
- **Offset reset without separate consumer**: Use a separate consumer instance to avoid conflicts with active consumer
- **Missing signal handlers**: Always handle SIGTERM for graceful shutdown in containers
- **Timeout too short on shutdown**: Give consumer enough time to commit final offsets (10-30 seconds)

---

## Additional Patterns

### Environment-Specific Consumer Groups

Use prefixes/suffixes to isolate consumer groups per environment:

```python
def get_consumer_group(base_group: str) -> str:
    """Get environment-specific consumer group name."""
    env = os.getenv("ENVIRONMENT", "dev")
    prefix = os.getenv("KAFKA_CONSUMER_GROUP_PREFIX", "")
    suffix = os.getenv("KAFKA_CONSUMER_GROUP_SUFFIX", "")

    group = base_group
    if prefix:
        group = f"{prefix}{group}"
    if suffix:
        group = f"{group}{suffix}"

    # Add environment if not in group name
    if env not in group:
        group = f"{env}-{group}"

    return group
```

### Protobuf Message Deserialization

For services consuming from compacted topics (brands, categories):

```python
from google.protobuf.json_format import MessageToDict

async def deserialize_protobuf_message(message_bytes: bytes):
    """Deserialize protobuf message from Kafka."""
    from your_proto_package import CategoryMessage

    msg = CategoryMessage()
    msg.ParseFromString(message_bytes)

    # Convert to dict for easier processing
    return MessageToDict(msg)
```
