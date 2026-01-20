"""Exercise 3: Implement a Rate Limiting Middleware

Create a middleware that rate limits tool invocations per tool name.
This is useful for protecting expensive operations or external API calls.

Instructions:
1. Create a RateLimitMiddleware class
2. Track invocations per tool with timestamps
3. Implement a sliding window rate limit (X calls per Y seconds)
4. Raise an exception when rate limit is exceeded
5. Support different limits for different tools

Expected Output:
- First N calls within the window should succeed
- Additional calls should raise RateLimitExceeded
- After the window passes, calls should succeed again

Hints:
- Store timestamps of recent calls per tool
- Clean up old timestamps outside the window
- Use time.time() for timestamps
- Consider using a deque with maxlen for the window
"""

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
    """Middleware that rate limits tool invocations.

    TODO: Implement this middleware:
    1. Track call timestamps per tool in a dictionary
    2. In __call__, check if rate limit is exceeded
    3. Clean up old timestamps outside the window
    4. Raise RateLimitExceeded if limit exceeded
    5. Otherwise, record the call and proceed
    """

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
        # TODO: Initialize storage for tracking calls
        # self._calls: dict[str, deque] = {}

    def _get_limit(self, tool_name: str) -> tuple[int, float]:
        """Get the rate limit for a tool."""
        if tool_name in self.tool_limits:
            return self.tool_limits[tool_name]
        return (self.default_limit, self.default_window)

    async def __call__(
        self,
        tool: Tool,
        params: dict[str, Any],
        next: Any,
    ) -> Any:
        """Execute the middleware.

        TODO: Implement rate limiting logic:
        1. Get current time
        2. Get limit and window for this tool
        3. Clean up old timestamps
        4. Check if limit exceeded
        5. If ok, record call and proceed
        """
        # TODO: Implement this method
        return await next(tool, params)


# Test tools


@tool(name="fast_api", description="A fast API call")
async def fast_api() -> str:
    return "fast response"


@tool(name="slow_api", description="A slow API call")
async def slow_api() -> str:
    await asyncio.sleep(0.1)
    return "slow response"


async def main() -> None:
    """Test rate limiting middleware."""
    print("Testing Rate Limiting Middleware...")

    registry = ToolRegistry(validate_inputs=False)

    # Create rate limiter with:
    # - Default: 5 calls per 2 seconds
    # - slow_api: 2 calls per 5 seconds
    rate_limiter = RateLimitMiddleware(
        default_limit=5,
        default_window=2.0,
        tool_limits={
            "slow_api": (2, 5.0),
        },
    )

    registry.use(rate_limiter)
    registry.register(fast_api)
    registry.register(slow_api)

    # Test fast_api rate limit (5 per 2 seconds)
    print("\n--- Testing fast_api (limit: 5 per 2s) ---")
    for i in range(7):
        try:
            result = await registry.invoke("fast_api", {})
            print(f"Call {i+1}: {result}")
        except RateLimitExceeded as e:
            print(f"Call {i+1}: {e}")

    # Wait for window to pass
    print("\nWaiting 2 seconds for window to reset...")
    await asyncio.sleep(2)

    # Should work again
    print("\n--- After window reset ---")
    try:
        result = await registry.invoke("fast_api", {})
        print(f"Call after reset: {result}")
    except RateLimitExceeded as e:
        print(f"Call after reset: {e}")

    # Test slow_api rate limit (2 per 5 seconds)
    print("\n--- Testing slow_api (limit: 2 per 5s) ---")
    for i in range(4):
        try:
            result = await registry.invoke("slow_api", {})
            print(f"Call {i+1}: {result}")
        except RateLimitExceeded as e:
            print(f"Call {i+1}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
