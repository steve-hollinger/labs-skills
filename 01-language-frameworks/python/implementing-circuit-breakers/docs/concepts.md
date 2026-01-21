# Core Concepts: Circuit Breaker and Retry Patterns

## What

Circuit breakers are a resilience pattern that prevents cascading failures when calling external services. The pattern monitors failures and "opens" the circuit to fail fast when a service is down, rather than continuing to make doomed requests that waste resources and time.

The circuit breaker acts like an electrical circuit breaker - when too many failures occur, it trips open and stops sending requests to the failing service. After a timeout period, it enters a half-open state to test if the service has recovered.

## Why

**Problem:** When external services fail (network issues, service downtime, rate limiting), applications that keep retrying can:
- Waste compute resources on requests that will fail
- Increase latency as threads wait for timeouts
- Cause cascading failures as upstream services also become overloaded
- Create "retry storms" where many clients hammer a recovering service

**Solution:** Circuit breakers solve this by:
- Detecting failures quickly and failing fast without making actual requests
- Giving the downstream service time to recover
- Testing recovery carefully with limited requests before fully reopening
- Preventing resource exhaustion from waiting on doomed requests

**Fetch Context:** At Fetch, circuit breakers protect against:
- ML API calls to Sagemaker endpoints that may throttle or fail
- External partner APIs (advertising, location services) with variable reliability
- Internal microservices that depend on external data sources
- Rate-limited third-party APIs that need backoff strategies

## How

### Circuit Breaker States

The circuit breaker operates in three states:

1. **CLOSED (Normal Operation)**
   - All requests pass through to the external service
   - Failures are counted but don't block requests
   - Transitions to OPEN when failure threshold is exceeded

2. **OPEN (Failing Fast)**
   - All requests fail immediately without calling the service
   - Saves resources by not waiting for timeouts
   - After a timeout period, transitions to HALF_OPEN to test recovery

3. **HALF_OPEN (Testing Recovery)**
   - Limited requests are allowed through to test if service recovered
   - One success transitions back to CLOSED (service is healthy)
   - One failure transitions back to OPEN (service still down)

### Exponential Backoff

When retrying failed requests, use exponential backoff to avoid overwhelming the recovering service:

```
delay = base_delay * (exponential_base ** attempt_number)
```

For example with base_delay=1s and exponential_base=2:
- Attempt 1: Wait 1s
- Attempt 2: Wait 2s
- Attempt 3: Wait 4s
- Attempt 4: Wait 8s

### Jitter

Add random jitter to backoff delays to prevent thundering herd:

```
delay *= random.uniform(0.5, 1.5)
```

This spreads out retries from multiple clients instead of having them all retry at the same time.

### Retry Logic

Retry logic should be separate from circuit breakers:
- Retries handle transient failures (network blips, temporary errors)
- Circuit breakers handle sustained failures (service down, rate limiting)
- Place circuit breaker OUTSIDE retry logic to prevent retry storms

## When to Use

**Use when:**
- Making HTTP calls to external APIs (partner services, ML endpoints)
- Calling third-party services with unknown reliability
- Accessing Sagemaker models that may be cold-starting or throttling
- Integrating with rate-limited APIs that require backoff
- Services that can experience extended downtime (not just transient failures)

**Avoid when:**
- Calling internal services within the same cluster (use retries only)
- Database operations (Snowflake, DynamoDB) - use retry with backoff instead
- Message queue operations (Kafka, SQS) - these have their own retry mechanisms
- Operations that must complete exactly once (use idempotency instead)
- Services with SLAs that guarantee uptime (circuit breakers add overhead)

## Key Terminology

- **Circuit Breaker** - Pattern that monitors failures and stops requests when threshold exceeded
- **Failure Threshold** - Number of consecutive failures before opening the circuit
- **Timeout** - Duration to wait in OPEN state before testing recovery (half-open)
- **Half-Open Attempts** - Number of test requests allowed in HALF_OPEN state
- **Exponential Backoff** - Retry strategy that increases delay exponentially between attempts
- **Jitter** - Random variation added to backoff delays to prevent synchronized retries
- **Thundering Herd** - Problem where many clients retry simultaneously, overwhelming service
- **Cascading Failure** - Failure that propagates from one service to dependent services
- **Fail Fast** - Design principle of failing immediately rather than waiting for timeout
