"""Solution for Exercise 3: Implement a Rate Limiting Middleware"""

import asyncio
import time
from collections import deque
from typing import Any

from tool_registry import Middleware, ToolRegistry, tool
from tool_registry.tool import Tool


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, tool_name: str, limit: int, window: float) -> None:
        self.tool_name = tool_name
        self.limit = limit
        self.window = window
        super().__init__(
            f"Rate limit exceeded for {tool_name}: "
            f"max {limit} calls per {window} seconds"
        )


class RateLimitMiddleware(Middleware):
    """Middleware that rate limits tool invocations using a sliding window."""

    def __init__(
        self,
        default_limit: int = 10,
        default_window: float = 60.0,
        tool_limits: dict[str, tuple[int, float]] | None = None,
    ) -> None:
        """Initialize the rate limiter.

        Args:
            default_limit: Default max calls per window
            default_window: Default window size in seconds
            tool_limits: Optional per-tool limits as {tool_name: (limit, window)}
        """
        self.default_limit = default_limit
        self.default_window = default_window
        self.tool_limits = tool_limits or {}
        # Storage for tracking calls: {tool_name: deque of timestamps}
        self._calls: dict[str, deque[float]] = {}

    def _get_limit(self, tool_name: str) -> tuple[int, float]:
        """Get the rate limit for a tool."""
        if tool_name in self.tool_limits:
            return self.tool_limits[tool_name]
        return (self.default_limit, self.default_window)

    def _cleanup_old_calls(self, tool_name: str, window: float) -> None:
        """Remove calls outside the current window."""
        if tool_name not in self._calls:
            return

        current_time = time.time()
        window_start = current_time - window

        # Remove all timestamps before the window start
        calls = self._calls[tool_name]
        while calls and calls[0] < window_start:
            calls.popleft()

    def get_remaining_calls(self, tool_name: str) -> int:
        """Get the number of remaining calls allowed for a tool."""
        limit, window = self._get_limit(tool_name)
        self._cleanup_old_calls(tool_name, window)

        current_calls = len(self._calls.get(tool_name, []))
        return max(0, limit - current_calls)

    def get_reset_time(self, tool_name: str) -> float:
        """Get seconds until the oldest call falls out of the window."""
        limit, window = self._get_limit(tool_name)

        if tool_name not in self._calls or not self._calls[tool_name]:
            return 0.0

        oldest_call = self._calls[tool_name][0]
        reset_at = oldest_call + window
        return max(0.0, reset_at - time.time())

    async def __call__(
        self,
        tool: Tool,
        params: dict[str, Any],
        next: Any,
    ) -> Any:
        """Execute the middleware with rate limiting."""
        tool_name = tool.name
        limit, window = self._get_limit(tool_name)
        current_time = time.time()

        # Initialize call tracking for this tool if needed
        if tool_name not in self._calls:
            self._calls[tool_name] = deque()

        # Clean up old calls outside the window
        self._cleanup_old_calls(tool_name, window)

        # Check if rate limit exceeded
        if len(self._calls[tool_name]) >= limit:
            raise RateLimitExceeded(tool_name, limit, window)

        # Record this call
        self._calls[tool_name].append(current_time)

        # Proceed with the tool execution
        return await next(tool, params)


# Test tools


@tool(name="fast_api", description="A fast API call")
async def fast_api() -> str:
    return "fast response"


@tool(name="slow_api", description="A slow API call")
async def slow_api() -> str:
    await asyncio.sleep(0.1)
    return "slow response"


@tool(name="expensive_api", description="An expensive API call")
async def expensive_api() -> str:
    return "expensive response"


async def main() -> None:
    """Test rate limiting middleware."""
    print("Solution 3: Rate Limiting Middleware")
    print("=" * 50)

    registry = ToolRegistry(validate_inputs=False)

    # Create rate limiter with:
    # - Default: 5 calls per 2 seconds
    # - slow_api: 2 calls per 5 seconds
    # - expensive_api: 1 call per 10 seconds
    rate_limiter = RateLimitMiddleware(
        default_limit=5,
        default_window=2.0,
        tool_limits={
            "slow_api": (2, 5.0),
            "expensive_api": (1, 10.0),
        },
    )

    registry.use(rate_limiter)
    registry.register(fast_api)
    registry.register(slow_api)
    registry.register(expensive_api)

    # Test fast_api rate limit (5 per 2 seconds)
    print("\n--- Testing fast_api (limit: 5 per 2s) ---")
    for i in range(7):
        remaining = rate_limiter.get_remaining_calls("fast_api")
        try:
            result = await registry.invoke("fast_api", {})
            print(f"Call {i+1}: {result} (remaining: {remaining - 1})")
        except RateLimitExceeded as e:
            reset_in = rate_limiter.get_reset_time("fast_api")
            print(f"Call {i+1}: RATE LIMITED (resets in {reset_in:.1f}s)")

    # Wait for window to pass
    print("\nWaiting 2.1 seconds for window to reset...")
    await asyncio.sleep(2.1)

    # Should work again
    print("\n--- After window reset ---")
    for i in range(3):
        try:
            result = await registry.invoke("fast_api", {})
            remaining = rate_limiter.get_remaining_calls("fast_api")
            print(f"Call {i+1}: {result} (remaining: {remaining})")
        except RateLimitExceeded as e:
            print(f"Call {i+1}: RATE LIMITED")

    # Test slow_api rate limit (2 per 5 seconds)
    print("\n--- Testing slow_api (limit: 2 per 5s) ---")
    for i in range(4):
        try:
            result = await registry.invoke("slow_api", {})
            remaining = rate_limiter.get_remaining_calls("slow_api")
            print(f"Call {i+1}: {result} (remaining: {remaining})")
        except RateLimitExceeded as e:
            reset_in = rate_limiter.get_reset_time("slow_api")
            print(f"Call {i+1}: RATE LIMITED (resets in {reset_in:.1f}s)")

    # Test expensive_api rate limit (1 per 10 seconds)
    print("\n--- Testing expensive_api (limit: 1 per 10s) ---")
    for i in range(3):
        try:
            result = await registry.invoke("expensive_api", {})
            remaining = rate_limiter.get_remaining_calls("expensive_api")
            print(f"Call {i+1}: {result} (remaining: {remaining})")
        except RateLimitExceeded as e:
            reset_in = rate_limiter.get_reset_time("expensive_api")
            print(f"Call {i+1}: RATE LIMITED (resets in {reset_in:.1f}s)")

    print("\n" + "=" * 50)
    print("Solution demonstration complete!")


if __name__ == "__main__":
    asyncio.run(main())
