"""
Example 4: Production Patterns

This example demonstrates production-ready patterns for OpenAI API integration
including error handling, retries, rate limiting, and cost tracking.

Key concepts:
- Error handling with specific exception types
- Exponential backoff retry logic
- Rate limiting
- Token and cost tracking
- Streaming responses
- Caching strategies
"""

import os
import time
import hashlib
import json
from datetime import datetime
from collections import deque
from threading import Lock
from typing import Generator
from dotenv import load_dotenv
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

# Load environment variables
load_dotenv()


# ============================================================================
# Error Handling
# ============================================================================

class APIErrorHandler:
    """Demonstrates proper error handling for OpenAI API."""

    def __init__(self):
        self.client = self._get_client()

    def _get_client(self):
        if not os.getenv("OPENAI_API_KEY"):
            return None
        from openai import OpenAI
        return OpenAI()

    def safe_completion(self, messages: list, **kwargs) -> dict:
        """Make API call with comprehensive error handling."""
        if self.client is None:
            return {"success": True, "content": "[Mock] Response without API key"}

        from openai import (
            APIError,
            RateLimitError,
            APIConnectionError,
            AuthenticationError,
            BadRequestError,
        )

        try:
            response = self.client.chat.completions.create(
                model=kwargs.get("model", "gpt-4o-mini"),
                messages=messages,
                **kwargs
            )
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }

        except AuthenticationError as e:
            return {
                "success": False,
                "error_type": "authentication",
                "message": "Invalid API key. Please check your OPENAI_API_KEY.",
                "recoverable": False
            }

        except RateLimitError as e:
            return {
                "success": False,
                "error_type": "rate_limit",
                "message": "Rate limit exceeded. Please wait and retry.",
                "recoverable": True,
                "retry_after": getattr(e, "retry_after", 60)
            }

        except BadRequestError as e:
            return {
                "success": False,
                "error_type": "bad_request",
                "message": f"Invalid request: {e.message}",
                "recoverable": False
            }

        except APIConnectionError as e:
            return {
                "success": False,
                "error_type": "connection",
                "message": "Network error. Check your internet connection.",
                "recoverable": True
            }

        except APIError as e:
            return {
                "success": False,
                "error_type": "api_error",
                "message": f"API error (status {e.status_code}): {e.message}",
                "recoverable": e.status_code >= 500
            }


# ============================================================================
# Retry Logic
# ============================================================================

class RetryingClient:
    """Client with automatic retry for transient failures."""

    def __init__(self):
        self._client = None
        if os.getenv("OPENAI_API_KEY"):
            from openai import OpenAI
            self._client = OpenAI()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=60),
        reraise=True
    )
    def completion_with_retry(self, messages: list, **kwargs) -> str:
        """Make API call with automatic retries."""
        if self._client is None:
            return "[Mock] Retrying client response"

        response = self._client.chat.completions.create(
            model=kwargs.get("model", "gpt-4o-mini"),
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content


# ============================================================================
# Rate Limiting
# ============================================================================

class RateLimitedClient:
    """Client that enforces rate limits."""

    def __init__(self, requests_per_minute: int = 60, tokens_per_minute: int = 150000):
        self._client = None
        if os.getenv("OPENAI_API_KEY"):
            from openai import OpenAI
            self._client = OpenAI()

        self.rpm = requests_per_minute
        self.tpm = tokens_per_minute
        self.request_times = deque()
        self.token_usage = deque()  # (timestamp, tokens)
        self.lock = Lock()

    def _wait_for_rate_limit(self):
        """Wait if we're at the rate limit."""
        with self.lock:
            now = time.time()
            minute_ago = now - 60

            # Clean old entries
            while self.request_times and self.request_times[0] < minute_ago:
                self.request_times.popleft()
            while self.token_usage and self.token_usage[0][0] < minute_ago:
                self.token_usage.popleft()

            # Check request rate
            if len(self.request_times) >= self.rpm:
                sleep_time = 60 - (now - self.request_times[0])
                if sleep_time > 0:
                    print(f"  [Rate limit: waiting {sleep_time:.1f}s]")
                    time.sleep(sleep_time)

            # Check token rate
            total_tokens = sum(t[1] for t in self.token_usage)
            if total_tokens >= self.tpm:
                oldest = self.token_usage[0][0]
                sleep_time = 60 - (now - oldest)
                if sleep_time > 0:
                    print(f"  [Token limit: waiting {sleep_time:.1f}s]")
                    time.sleep(sleep_time)

            self.request_times.append(time.time())

    def _record_tokens(self, tokens: int):
        """Record token usage."""
        with self.lock:
            self.token_usage.append((time.time(), tokens))

    def completion(self, messages: list, **kwargs) -> str:
        """Make rate-limited API call."""
        self._wait_for_rate_limit()

        if self._client is None:
            return "[Mock] Rate-limited response"

        response = self._client.chat.completions.create(
            model=kwargs.get("model", "gpt-4o-mini"),
            messages=messages,
            **kwargs
        )

        self._record_tokens(response.usage.total_tokens)
        return response.choices[0].message.content


# ============================================================================
# Cost Tracking
# ============================================================================

class CostTrackingClient:
    """Client that tracks API costs."""

    # Pricing per 1M tokens (as of late 2024)
    PRICING = {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    }

    def __init__(self):
        self._client = None
        if os.getenv("OPENAI_API_KEY"):
            from openai import OpenAI
            self._client = OpenAI()

        self.total_cost = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.requests = []

    def completion(self, messages: list, model: str = "gpt-4o-mini", **kwargs) -> str:
        """Make API call and track costs."""
        if self._client is None:
            self._record_mock_usage(model)
            return "[Mock] Cost-tracked response"

        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )

        self._record_usage(response, model)
        return response.choices[0].message.content

    def _record_mock_usage(self, model: str):
        """Record mock usage for demonstration."""
        self.requests.append({
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "cost": 0.0001
        })

    def _record_usage(self, response, model: str):
        """Record actual usage and calculate cost."""
        usage = response.usage
        pricing = self.PRICING.get(model, self.PRICING["gpt-4o-mini"])

        input_cost = (usage.prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (usage.completion_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost

        self.total_cost += total_cost
        self.total_input_tokens += usage.prompt_tokens
        self.total_output_tokens += usage.completion_tokens

        self.requests.append({
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "cost": total_cost
        })

    def get_summary(self) -> dict:
        """Get cost tracking summary."""
        return {
            "total_requests": len(self.requests),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost": f"${self.total_cost:.6f}",
            "average_cost_per_request": f"${self.total_cost / max(1, len(self.requests)):.6f}"
        }


# ============================================================================
# Streaming
# ============================================================================

class StreamingClient:
    """Client with streaming support."""

    def __init__(self):
        self._client = None
        if os.getenv("OPENAI_API_KEY"):
            from openai import OpenAI
            self._client = OpenAI()

    def stream_completion(self, messages: list, **kwargs) -> Generator[str, None, None]:
        """Stream completion tokens."""
        if self._client is None:
            # Mock streaming
            mock_response = "[Mock] This is a streamed response token by token."
            for word in mock_response.split():
                yield word + " "
                time.sleep(0.1)
            return

        stream = self._client.chat.completions.create(
            model=kwargs.get("model", "gpt-4o-mini"),
            messages=messages,
            stream=True,
            **kwargs
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


# ============================================================================
# Caching
# ============================================================================

class CachingClient:
    """Client with response caching."""

    def __init__(self, cache_size: int = 100):
        self._client = None
        if os.getenv("OPENAI_API_KEY"):
            from openai import OpenAI
            self._client = OpenAI()

        self._cache = {}
        self.cache_size = cache_size
        self.cache_hits = 0
        self.cache_misses = 0

    def _cache_key(self, messages: list, model: str, **kwargs) -> str:
        """Generate cache key from request."""
        content = json.dumps({
            "messages": messages,
            "model": model,
            "temperature": kwargs.get("temperature", 1.0),
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def completion(self, messages: list, model: str = "gpt-4o-mini",
                   use_cache: bool = True, **kwargs) -> str:
        """Make cached API call."""
        key = self._cache_key(messages, model, **kwargs)

        if use_cache and key in self._cache:
            self.cache_hits += 1
            return self._cache[key]

        self.cache_misses += 1

        if self._client is None:
            response = "[Mock] Cached response"
        else:
            result = self._client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            response = result.choices[0].message.content

        if use_cache:
            if len(self._cache) >= self.cache_size:
                # Remove oldest entry
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
            self._cache[key] = response

        return response

    def get_stats(self) -> dict:
        """Get cache statistics."""
        total = self.cache_hits + self.cache_misses
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": f"{(self.cache_hits / max(1, total)) * 100:.1f}%",
            "cache_size": len(self._cache)
        }


# ============================================================================
# Examples
# ============================================================================

def example_error_handling():
    """Demonstrate error handling."""
    print("\n--- Error Handling ---")

    handler = APIErrorHandler()

    # Normal request
    result = handler.safe_completion([
        {"role": "user", "content": "Say hello"}
    ])
    print(f"\nNormal request: {result}")


def example_retry_logic():
    """Demonstrate retry logic."""
    print("\n--- Retry Logic ---")

    client = RetryingClient()
    result = client.completion_with_retry([
        {"role": "user", "content": "What is 2+2?"}
    ])
    print(f"\nResult with retry: {result}")


def example_rate_limiting():
    """Demonstrate rate limiting."""
    print("\n--- Rate Limiting ---")

    client = RateLimitedClient(requests_per_minute=10)

    print("Making 3 rapid requests...")
    for i in range(3):
        result = client.completion([
            {"role": "user", "content": f"Request {i+1}: Say hi"}
        ], max_tokens=10)
        print(f"  Request {i+1}: {result[:50]}...")


def example_cost_tracking():
    """Demonstrate cost tracking."""
    print("\n--- Cost Tracking ---")

    client = CostTrackingClient()

    # Make some requests
    for prompt in ["Hello!", "What is Python?", "Explain AI briefly."]:
        client.completion([{"role": "user", "content": prompt}], max_tokens=50)

    summary = client.get_summary()
    print(f"\nCost Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")


def example_streaming():
    """Demonstrate streaming."""
    print("\n--- Streaming ---")

    client = StreamingClient()

    print("\nStreaming response:")
    for token in client.stream_completion([
        {"role": "user", "content": "Count from 1 to 5."}
    ], max_tokens=50):
        print(token, end="", flush=True)
    print()


def example_caching():
    """Demonstrate caching."""
    print("\n--- Caching ---")

    client = CachingClient()

    # First request - cache miss
    print("\nFirst request (cache miss):")
    result1 = client.completion([
        {"role": "user", "content": "What is the capital of France?"}
    ], temperature=0)
    print(f"  Result: {result1[:50]}...")

    # Same request - cache hit
    print("\nSame request (cache hit):")
    result2 = client.completion([
        {"role": "user", "content": "What is the capital of France?"}
    ], temperature=0)
    print(f"  Result: {result2[:50]}...")

    # Different request - cache miss
    print("\nDifferent request (cache miss):")
    result3 = client.completion([
        {"role": "user", "content": "What is the capital of Germany?"}
    ], temperature=0)
    print(f"  Result: {result3[:50]}...")

    stats = client.get_stats()
    print(f"\nCache Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


def main():
    """Run all production pattern examples."""
    print("=" * 60)
    print("Example 4: Production Patterns")
    print("=" * 60)

    example_error_handling()
    example_retry_logic()
    example_rate_limiting()
    example_cost_tracking()
    example_streaming()
    example_caching()

    print("\n" + "=" * 60)
    print("Key Takeaways:")
    print("1. Always handle specific error types appropriately")
    print("2. Use exponential backoff for retries")
    print("3. Implement rate limiting to avoid API blocks")
    print("4. Track costs to manage API spending")
    print("5. Stream responses for better UX")
    print("6. Cache identical requests to save costs")
    print("=" * 60)


if __name__ == "__main__":
    main()
