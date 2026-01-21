---
name: consuming-kafka-aiokafka
description: Build async Kafka consumers with aiokafka, MSK IAM auth, and batch processing. Use when consuming from Kafka topics with proper error handling.
tags: ['python', 'kafka', 'aiokafka', 'msk', 'streaming', 'async', 'fetch']
---

# Kafka Consumer with aiokafka

## Quick Start
```python
# src/services/kafka_consumer.py
import asyncio
import logging
from typing import Optional

from aiokafka import AIOKafkaConsumer
from aiokafka.abc import AbstractTokenProvider
from aiokafka.helpers import create_ssl_context

logger = logging.getLogger(__name__)


class MSKTokenProvider(AbstractTokenProvider):
    """Token provider for AWS MSK IAM authentication."""

    def __init__(self, region: str):
        self.region = region

    async def token(self):
        from aws_msk_iam_sasl_signer import MSKAuthTokenProvider
        loop = asyncio.get_running_loop()
        token, _ = await loop.run_in_executor(
            None, MSKAuthTokenProvider.generate_auth_token, self.region
        )
        return token


async def start_consumer(brokers: list[str], topic: str, group_id: str):
    """Start Kafka consumer with MSK IAM auth."""
    ssl_context = create_ssl_context()
    tp = MSKTokenProvider(region="us-east-1")

    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=brokers,
        group_id=group_id,
        security_protocol="SASL_SSL",
        sasl_mechanism="OAUTHBEARER",
        sasl_oauth_token_provider=tp,
        ssl_context=ssl_context,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )

    await consumer.start()
    try:
        async for message in consumer:
            await process_message(message.value)
    finally:
        await consumer.stop()
```

## Key Points
- **MSK IAM authentication is standard at Fetch** - All Kafka consumers use AWS MSK with IAM authentication, not SASL_PLAINTEXT
- **Async processing with aiokafka** - FastAPI services require async Kafka clients for non-blocking message consumption
- **Batch processing for efficiency** - Process messages in batches (100-500 messages or 3-5 second timeout) to reduce overhead
- **Consumer groups per environment** - Use environment-specific consumer group names to isolate dev/stage/prod consumers
- **Compacted topics for state** - Category and brand topics use log compaction for maintaining latest state (e.g., cvs-category-crud-events, brands)

## Common Mistakes
1. **Hardcoding SASL_PLAINTEXT security** - Always use SASL_SSL with OAUTHBEARER mechanism for MSK IAM authentication, not SASL_PLAINTEXT
2. **Blocking synchronous handlers** - Use async message handlers to avoid blocking the consumer loop and causing rebalancing timeouts
3. **Missing session timeout configuration** - Set session_timeout_ms (45-180 seconds) and heartbeat_interval_ms (3 seconds) to prevent rebalancing during heavy processing
4. **Not handling offset reset** - Implement offset reset logic for development/testing to replay messages from beginning when needed
5. **Swallowing processing errors** - Log errors with full context and consider dead letter queue pattern for failed messages instead of silent failures

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
