# Code Patterns: Circuit Breaker and Retry Patterns

## Pattern 1: Circuit Breaker Decorator Implementation

**When to Use:** Protect external service calls from cascading failures. Use for ML APIs, partner services, or any external HTTP endpoint that may experience downtime.

```python
# src/resilience.py
import time
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    timeout: float = 60.0
    half_open_attempts: int = 1


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """Circuit breaker for external service calls."""

    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.next_attempt_time: Optional[float] = None

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == CircuitBreakerState.OPEN:
            if time.time() < self.next_attempt_time:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{self.name}' is OPEN"
                )
            self.state = CircuitBreakerState.HALF_OPEN
            logger.info(f"Circuit breaker '{self.name}' entering HALF_OPEN")

        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure()
            raise

    def _record_success(self):
        """Record successful operation."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            logger.info(f"Circuit breaker '{self.name}' closed")
        self.failure_count = 0
        self.last_failure_time = None

    def _record_failure(self):
        """Record failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.next_attempt_time = time.time() + self.config.timeout
            logger.warning(
                f"Circuit breaker '{self.name}' OPEN after "
                f"{self.failure_count} failures"
            )


# Usage example
sagemaker_breaker = CircuitBreaker(
    name="sagemaker_fraud_model",
    config=CircuitBreakerConfig(
        failure_threshold=5,
        timeout=60.0,
        half_open_attempts=1
    )
)


def predict_fraud(transaction_data: dict) -> dict:
    """Call Sagemaker fraud detection model with circuit breaker."""
    return sagemaker_breaker.call(
        lambda: call_sagemaker_endpoint(transaction_data)
    )


def call_sagemaker_endpoint(data: dict) -> dict:
    # Actual Sagemaker API call
    import boto3
    runtime = boto3.client('sagemaker-runtime')
    response = runtime.invoke_endpoint(
        EndpointName='fraud-detection-v2',
        ContentType='application/json',
        Body=json.dumps(data)
    )
    return json.loads(response['Body'].read())
```

**Pitfalls:**
- Don't share circuit breakers across different services - each external service needs its own breaker
- Avoid setting failure_threshold too low (1-2) or circuit will trip on transient errors
- Don't forget to monitor circuit breaker state transitions in production

## Pattern 2: Integration with httpx

**When to Use:** Wrapping HTTP client calls to external APIs with circuit breaker protection. Common for partner APIs, external ML services, or third-party integrations.

```python
# src/http_client.py
import httpx
from typing import Optional
from resilience import CircuitBreaker, CircuitBreakerConfig


class ResilientHttpClient:
    """HTTP client with circuit breaker protection."""

    def __init__(
        self,
        base_url: str,
        breaker_config: Optional[CircuitBreakerConfig] = None
    ):
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(10.0),
            limits=httpx.Limits(max_connections=100)
        )
        self.breaker = CircuitBreaker(
            name=f"http_{base_url}",
            config=breaker_config or CircuitBreakerConfig()
        )

    async def post(self, endpoint: str, data: dict) -> dict:
        """POST request with circuit breaker protection."""
        return self.breaker.call(
            lambda: self._do_post(endpoint, data)
        )

    async def _do_post(self, endpoint: str, data: dict) -> dict:
        response = await self.client.post(endpoint, json=data)
        response.raise_for_status()
        return response.json()

    async def get(self, endpoint: str, params: dict = None) -> dict:
        """GET request with circuit breaker protection."""
        return self.breaker.call(
            lambda: self._do_get(endpoint, params)
        )

    async def _do_get(self, endpoint: str, params: dict = None) -> dict:
        response = await self.client.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()


# Usage example for partner API
partner_client = ResilientHttpClient(
    base_url="https://api.partner.com",
    breaker_config=CircuitBreakerConfig(
        failure_threshold=3,  # Partner API is flaky
        timeout=120.0,        # Wait 2 minutes
        half_open_attempts=1
    )
)


async def get_location_data(user_id: str) -> dict:
    """Get user location from partner API."""
    try:
        return await partner_client.get(
            f"/users/{user_id}/location",
            params={"include_history": True}
        )
    except CircuitBreakerOpenError:
        logger.warning(f"Partner API circuit breaker open for user {user_id}")
        return {"location": None, "source": "fallback"}
```

**Pitfalls:**
- Don't forget to handle CircuitBreakerOpenError gracefully with fallbacks
- Avoid using synchronous httpx.Client with async code - keep async consistent
- Don't set httpx timeout longer than circuit breaker timeout

## Pattern 3: Exponential Backoff with Jitter

**When to Use:** Retry transient failures with increasing delays. Use for network errors, rate limiting, or temporary service unavailability. Combine with circuit breakers for robust resilience.

```python
# src/retry.py
import asyncio
import random
import logging
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


def retry_with_backoff(
    config: RetryConfig,
    retryable_exceptions: tuple = (Exception,)
):
    """Decorator for retry with exponential backoff and jitter."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    if attempt == config.max_attempts - 1:
                        logger.error(
                            f"Max retries ({config.max_attempts}) exceeded",
                            extra={
                                "function": func.__name__,
                                "error": str(e),
                                "attempts": config.max_attempts
                            }
                        )
                        raise

                    # Calculate exponential backoff
                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )

                    # Add jitter to prevent thundering herd
                    if config.jitter:
                        delay *= random.uniform(0.5, 1.5)

                    logger.warning(
                        f"Retry attempt {attempt + 1}/{config.max_attempts} "
                        f"after {delay:.2f}s",
                        extra={
                            "function": func.__name__,
                            "error": str(e),
                            "delay": delay
                        }
                    )

                    await asyncio.sleep(delay)

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    if attempt == config.max_attempts - 1:
                        raise

                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )

                    if config.jitter:
                        delay *= random.uniform(0.5, 1.5)

                    logger.warning(
                        f"Retry {attempt + 1}/{config.max_attempts} "
                        f"after {delay:.2f}s"
                    )
                    time.sleep(delay)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# Usage example - combining retry with circuit breaker
@retry_with_backoff(
    RetryConfig(
        max_attempts=3,
        base_delay=1.0,
        exponential_base=2.0,
        jitter=True
    ),
    retryable_exceptions=(httpx.RequestError, httpx.TimeoutException)
)
async def call_ml_api_with_retry(data: dict) -> dict:
    """Call ML API with retry, wrapped by circuit breaker."""
    return ml_breaker.call(
        lambda: httpx.post("https://ml-api.fetch.com/predict", json=data)
    )


# Fetch use case: Sagemaker endpoint with retry
@retry_with_backoff(
    RetryConfig(max_attempts=3, base_delay=2.0),
    retryable_exceptions=(ClientError,)
)
def invoke_sagemaker_with_retry(endpoint: str, payload: dict) -> dict:
    """Invoke Sagemaker endpoint with exponential backoff."""
    runtime = boto3.client('sagemaker-runtime')
    response = runtime.invoke_endpoint(
        EndpointName=endpoint,
        ContentType='application/json',
        Body=json.dumps(payload)
    )
    return json.loads(response['Body'].read())
```

**Pitfalls:**
- Don't retry non-idempotent operations (POST that creates records) - use idempotency keys instead
- Avoid retrying 4xx client errors (bad request, unauthorized) - only retry 5xx server errors and network issues
- Don't forget jitter - without it, all clients will retry simultaneously creating thundering herd

---

## Additional Patterns

### Combining Circuit Breaker and Retry

Place circuit breaker OUTSIDE retry logic to prevent retry storms:

```python
# CORRECT: Circuit breaker wraps retry logic
circuit_breaker.call(
    lambda: retry_with_backoff()(api_call)()
)

# WRONG: Retry wraps circuit breaker (causes retry storm when breaker opens)
@retry_with_backoff()
def bad_pattern():
    return circuit_breaker.call(api_call)
```

### Monitoring Circuit Breaker State

```python
# Add metrics to track circuit breaker health
def _record_failure(self):
    self.failure_count += 1
    metrics.increment('circuit_breaker.failures', tags=[f'breaker:{self.name}'])

    if self.failure_count >= self.config.failure_threshold:
        self.state = CircuitBreakerState.OPEN
        metrics.increment('circuit_breaker.opened', tags=[f'breaker:{self.name}'])
        alert.send(f"Circuit breaker {self.name} OPEN")
```

