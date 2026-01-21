# Core Concepts: Kafka Consumer with aiokafka

## What

**aiokafka** is an async Python Kafka client built on top of the kafka-python library, designed for asyncio-based applications. At Fetch, it's used to consume messages from AWS Managed Streaming for Kafka (MSK) clusters with IAM authentication.

**Key Technologies:**
- **aiokafka**: Async Kafka client library for Python (asyncio-based)
- **AWS MSK (Managed Streaming for Kafka)**: Fully managed Apache Kafka service
- **MSK IAM Authentication**: OAuth-based authentication using AWS IAM credentials
- **aws-msk-iam-sasl-signer**: Python library for generating MSK IAM authentication tokens

**At Fetch, we have:**
- 15+ Python Kafka consumers across Pack-DigDog (backend services)
- Multiple MSK clusters (dev, stage, prod environments)
- IAM-based authentication for all Kafka access (no plaintext SASL)
- Compacted topics for state management (brands, categories)
- Event-driven topics for domain events (ereceipts, purchases, offers)

## Why

**Problem: Blocking Kafka clients don't work with FastAPI**

Traditional kafka-python library uses synchronous, blocking I/O which causes problems in async FastAPI applications:
- Message consumption blocks the event loop
- Prevents concurrent request handling
- Causes consumer group rebalancing from missed heartbeats
- Makes it difficult to integrate with async HTTP APIs

**Solution: aiokafka with async/await pattern**

aiokafka provides native async support that integrates seamlessly with FastAPI and asyncio:
- Non-blocking message consumption using `async for`
- Concurrent processing of messages and HTTP requests
- Proper heartbeat management without blocking
- Clean integration with async downstream services

**Fetch Context:**

Fetch's Python services use aiokafka extensively for real-time data processing:

1. **Category/Brand Services** (rover-mcp/python_services):
   - Consume from `cvs-category-crud-events` and `brands` topics
   - Maintain searchable indices for category and brand filtering
   - Process 100+ messages on bootstrap, then incremental updates
   - Support purchase history filtering with hybrid search

2. **ereceipt-ml-submitter** (Pack-DigDog):
   - Batch processing of receipt parsing jobs
   - Integration with ML models for receipt OCR
   - Error handling with dead letter queue pattern

3. **Common Requirements**:
   - MSK IAM authentication (SASL_SSL with OAUTHBEARER)
   - Environment-specific consumer groups (dev/stage/prod isolation)
   - Offset reset capability for development/testing
   - Graceful shutdown and rebalancing handling

## How

### Architecture

**Consumer Flow:**
```
MSK Broker (SSL/TLS)
    ↓ (IAM Token Auth)
AIOKafkaConsumer
    ↓ (async for message)
Message Handler
    ↓ (batch or single)
Business Logic
    ↓ (commit offsets)
Back to Consumer Loop
```

**Key Components:**

1. **MSKTokenProvider**: Implements `AbstractTokenProvider` interface for MSK IAM authentication
   - Generates temporary OAuth tokens using AWS credentials
   - Runs synchronously in executor to avoid blocking asyncio loop
   - Tokens are refreshed automatically by aiokafka

2. **Consumer Configuration**:
   - `bootstrap_servers`: MSK broker list
   - `group_id`: Consumer group name (environment-specific)
   - `security_protocol`: SASL_SSL for MSK
   - `sasl_mechanism`: OAUTHBEARER for IAM auth
   - `sasl_oauth_token_provider`: MSKTokenProvider instance
   - `ssl_context`: SSL/TLS context for encrypted connection

3. **Consumer Groups**:
   - Each consumer joins a named consumer group
   - Kafka manages partition assignment within group
   - Multiple consumers in same group share partition load
   - Different groups consume independently (separate offsets)

4. **Batch Processing Pattern**:
   - Accumulate messages in a list
   - Process batch when size threshold reached (e.g., 100 messages)
   - OR process when timeout elapsed (e.g., 3 seconds)
   - Reduces per-message overhead and enables bulk operations

5. **Error Handling Strategies**:
   - **Retry with backoff**: Temporary failures (network, downstream API)
   - **Dead letter queue**: Persistent failures (malformed messages, business logic errors)
   - **Continue processing**: Don't block consumer on single message failure
   - **Logging with context**: Record error details for debugging

### Offset Management

**Auto-commit (recommended for most cases)**:
- Set `enable_auto_commit=True`
- Kafka commits offsets automatically every 5 seconds
- Simpler code, but potential for message replay on crash

**Manual commit (for exactly-once semantics)**:
- Set `enable_auto_commit=False`
- Call `consumer.commit()` after successful processing
- More control, but requires careful error handling

**Offset reset for development**:
- Use `seek_to_beginning()` to replay all messages
- Requires separate consumer instance to avoid conflicts
- Essential for testing and data rebuilding

### Session Timeouts and Heartbeats

**Critical for avoiding rebalancing**:
- `session_timeout_ms`: Maximum time without heartbeat before eviction (45-180 seconds)
- `heartbeat_interval_ms`: Frequency of heartbeat messages (3 seconds)
- Set session_timeout_ms high enough for slow message processing
- Fetch uses 180 seconds (3 minutes) for heavy operations like embedding generation

## When to Use

**Use when:**
- Building FastAPI services that consume from Kafka
- Processing event streams in real-time (categories, brands, offers)
- Maintaining in-memory state from compacted topics
- Integrating Kafka with async HTTP APIs or databases
- Need non-blocking message consumption with concurrent request handling

**Avoid when:**
- Building synchronous command-line tools (use kafka-python instead)
- Need Java-level performance (use Go or Java consumer)
- Working with non-async frameworks (Flask, Django without async support)
- Extremely high throughput requirements (consider Go or Java)
- Don't need async capabilities (kafka-python is simpler)

## Key Terminology

- **MSK (Managed Streaming for Kafka)** - AWS fully-managed Kafka service with built-in IAM authentication
- **IAM Authentication** - AWS Identity and Access Management authentication for Kafka using temporary OAuth tokens
- **Consumer Group** - Named group of consumers that share partition load and maintain independent offsets
- **Offset** - Position marker in a Kafka topic partition (like a bookmark)
- **Topic** - Named stream of messages (events) in Kafka
- **Partition** - Ordered, immutable sequence of messages within a topic (enables parallelism)
- **Compacted Topic** - Topic that retains only the latest value for each key (used for state, e.g., brands, categories)
- **Rebalancing** - Process of redistributing partitions among consumer group members when membership changes
- **Session Timeout** - Maximum time consumer can be silent before being evicted from consumer group
- **Heartbeat** - Periodic message sent by consumer to broker to indicate it's alive
- **Auto-commit** - Automatic periodic offset commit by Kafka consumer (every 5 seconds by default)
- **Dead Letter Queue (DLQ)** - Separate topic for messages that fail processing after retries
- **Batch Processing** - Accumulating multiple messages before processing them together (improves throughput)
- **SASL_SSL** - Security protocol combining SASL authentication with SSL/TLS encryption
- **OAUTHBEARER** - SASL mechanism using OAuth tokens (used for MSK IAM authentication)
