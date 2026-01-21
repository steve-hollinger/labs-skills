---
name: implementing-circuit-breakers
description: Implement circuit breakers for resilient external service calls with exponential backoff. Use when adding fault tolerance to HTTP clients or external dependencies.
tags: ['python', 'resilience', 'circuit-breaker', 'retry', 'httpx']
---

# Circuit Breaker and Retry Patterns

## Quick Start
```python
# Circuit breaker decorator for external API calls
from resilience import CircuitBreaker, CircuitBreakerConfig

# Configure circuit breaker for ML API
ml_breaker = CircuitBreaker(
    name="ml_api",
    config=CircuitBreakerConfig(
        failure_threshold=5,  # Open after 5 failures
        timeout=60.0,         # Wait 60s before retry
        half_open_attempts=1  # Test with 1 request
    )
)

# Protect external calls
def call_ml_model(data):
    return ml_breaker.call(
        lambda: httpx.post("https://ml-api.fetch.com/predict", json=data)
    )

# Result: Fails fast when ML API is down, prevents cascade failures
```

## Key Points
- Circuit breakers prevent cascading failures by failing fast when external services are down
- Three states: CLOSED (normal), OPEN (failing fast), HALF_OPEN (testing recovery)
- Exponential backoff with jitter prevents thundering herd when retrying
- Place circuit breaker outside retry logic to avoid retry storms during outages
- Use for external HTTP APIs and ML services, not for internal database calls

## Common Mistakes
1. **Putting retry inside circuit breaker** - This causes retry storms when the breaker opens. Place circuit breaker outside retry logic.
2. **Using circuit breakers for internal services** - Circuit breakers are for external dependencies. Use retries only for internal database calls.
3. **No jitter in backoff delays** - Without jitter, all clients retry simultaneously causing thundering herd. Always add randomization.
4. **Setting timeout too short** - If timeout is shorter than recovery time, breaker thrashes between OPEN and HALF_OPEN. Set timeout to 2-3x expected recovery.
5. **Not monitoring circuit breaker state** - Track state transitions and failure counts to detect issues early. Log all OPEN events.

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
