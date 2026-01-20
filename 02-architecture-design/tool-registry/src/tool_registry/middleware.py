"""Middleware system for tool execution.

Middleware allows adding cross-cutting concerns like logging, timing,
authentication, and error handling to tool invocations.
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Awaitable

from tool_registry.tool import Tool


# Type for the next middleware or final handler
NextHandler = Callable[[Tool, dict[str, Any]], Awaitable[Any]]


class Middleware(ABC):
    """Base class for tool middleware.

    Middleware intercepts tool invocations and can:
    - Modify inputs before execution
    - Modify outputs after execution
    - Handle errors
    - Add logging, timing, or other cross-cutting concerns

    Example:
        class LoggingMiddleware(Middleware):
            async def __call__(self, tool, params, next):
                print(f"Calling {tool.name}")
                result = await next(tool, params)
                print(f"Result: {result}")
                return result
    """

    @abstractmethod
    async def __call__(
        self,
        tool: Tool,
        params: dict[str, Any],
        next: NextHandler,
    ) -> Any:
        """Execute the middleware.

        Args:
            tool: The tool being invoked
            params: The input parameters
            next: The next middleware or final handler

        Returns:
            The result of the tool execution
        """
        ...


class MiddlewareChain:
    """Chain of middleware that wraps tool execution.

    Middleware is executed in the order it was added, creating a
    pipeline that processes each tool invocation.
    """

    def __init__(self) -> None:
        self._middleware: list[Middleware] = []

    def use(self, middleware: Middleware) -> "MiddlewareChain":
        """Add middleware to the chain.

        Args:
            middleware: The middleware to add

        Returns:
            Self for chaining
        """
        self._middleware.append(middleware)
        return self

    async def execute(
        self,
        tool: Tool,
        params: dict[str, Any],
        final_handler: NextHandler,
    ) -> Any:
        """Execute the middleware chain.

        Args:
            tool: The tool to invoke
            params: The input parameters
            final_handler: The handler to call after all middleware

        Returns:
            The result of the tool execution
        """
        # Build the chain from the end
        handler = final_handler

        for middleware in reversed(self._middleware):
            # Capture current handler and middleware in closure
            current_handler = handler
            current_middleware = middleware

            async def make_next(h: NextHandler, m: Middleware) -> NextHandler:
                async def next_fn(t: Tool, p: dict[str, Any]) -> Any:
                    return await m(t, p, h)
                return next_fn

            handler = await make_next(current_handler, current_middleware)

        return await handler(tool, params)

    def clear(self) -> None:
        """Remove all middleware from the chain."""
        self._middleware.clear()


# Common middleware implementations


class LoggingMiddleware(Middleware):
    """Middleware that logs tool invocations."""

    def __init__(self, logger: Any = None) -> None:
        self._logger = logger

    def _log(self, message: str) -> None:
        if self._logger:
            self._logger.info(message)
        else:
            print(message)

    async def __call__(
        self,
        tool: Tool,
        params: dict[str, Any],
        next: NextHandler,
    ) -> Any:
        self._log(f"[Tool] Invoking {tool.name} with params: {params}")
        try:
            result = await next(tool, params)
            self._log(f"[Tool] {tool.name} returned: {result}")
            return result
        except Exception as e:
            self._log(f"[Tool] {tool.name} failed: {e}")
            raise


class TimingMiddleware(Middleware):
    """Middleware that tracks execution time."""

    def __init__(self) -> None:
        self.timings: dict[str, list[float]] = {}

    async def __call__(
        self,
        tool: Tool,
        params: dict[str, Any],
        next: NextHandler,
    ) -> Any:
        start = time.perf_counter()
        try:
            return await next(tool, params)
        finally:
            elapsed = time.perf_counter() - start
            if tool.name not in self.timings:
                self.timings[tool.name] = []
            self.timings[tool.name].append(elapsed)

    def get_stats(self, tool_name: str) -> dict[str, float]:
        """Get timing statistics for a tool."""
        times = self.timings.get(tool_name, [])
        if not times:
            return {"count": 0, "avg": 0, "min": 0, "max": 0}
        return {
            "count": len(times),
            "avg": sum(times) / len(times),
            "min": min(times),
            "max": max(times),
        }


class ErrorHandlingMiddleware(Middleware):
    """Middleware that handles and transforms errors."""

    def __init__(
        self,
        error_handler: Callable[[Tool, Exception], Any] | None = None,
    ) -> None:
        self._error_handler = error_handler

    async def __call__(
        self,
        tool: Tool,
        params: dict[str, Any],
        next: NextHandler,
    ) -> Any:
        try:
            return await next(tool, params)
        except Exception as e:
            if self._error_handler:
                return self._error_handler(tool, e)
            raise


class RetryMiddleware(Middleware):
    """Middleware that retries failed tool invocations."""

    def __init__(
        self,
        max_retries: int = 3,
        delay: float = 0.1,
        backoff: float = 2.0,
    ) -> None:
        self._max_retries = max_retries
        self._delay = delay
        self._backoff = backoff

    async def __call__(
        self,
        tool: Tool,
        params: dict[str, Any],
        next: NextHandler,
    ) -> Any:
        import asyncio

        last_error: Exception | None = None
        delay = self._delay

        for attempt in range(self._max_retries + 1):
            try:
                return await next(tool, params)
            except Exception as e:
                last_error = e
                if attempt < self._max_retries:
                    await asyncio.sleep(delay)
                    delay *= self._backoff

        raise last_error  # type: ignore[misc]


class ValidationMiddleware(Middleware):
    """Middleware that validates inputs and outputs."""

    def __init__(self, validate_output: bool = False) -> None:
        self._validate_output = validate_output

    async def __call__(
        self,
        tool: Tool,
        params: dict[str, Any],
        next: NextHandler,
    ) -> Any:
        # Validate input
        tool.validate_input(params)

        # Execute tool
        result = await next(tool, params)

        # Optionally validate output
        if self._validate_output:
            tool.validate_output(result)

        return result
