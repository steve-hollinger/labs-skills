"""Example 2: Tool Middleware

This example demonstrates using middleware for cross-cutting concerns
like logging, timing, error handling, and retry logic.

Key concepts:
- Creating custom middleware
- Middleware chain execution order
- Timing and logging middleware
- Retry middleware for transient failures
- Error handling middleware
"""

import asyncio
import random
from typing import Any

from tool_registry import Middleware, ToolRegistry, tool
from tool_registry.middleware import (
    ErrorHandlingMiddleware,
    LoggingMiddleware,
    RetryMiddleware,
    TimingMiddleware,
)
from tool_registry.tool import Tool


# Tools for testing middleware


@tool(name="fast_operation", description="A fast operation")
async def fast_operation(x: int) -> int:
    """Returns the input multiplied by 2."""
    return x * 2


@tool(name="slow_operation", description="A slow operation")
async def slow_operation(delay: float = 0.1) -> str:
    """Simulates a slow operation."""
    await asyncio.sleep(delay)
    return f"Completed after {delay}s"


@tool(name="flaky_operation", description="An operation that sometimes fails")
async def flaky_operation(fail_rate: float = 0.5) -> str:
    """Randomly fails based on fail_rate."""
    if random.random() < fail_rate:
        raise RuntimeError("Random failure!")
    return "Success!"


@tool(name="divide", description="Divide two numbers")
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    return a / b


# Custom middleware example


class AuditMiddleware(Middleware):
    """Middleware that creates an audit log of tool invocations."""

    def __init__(self) -> None:
        self.audit_log: list[dict[str, Any]] = []

    async def __call__(
        self,
        tool: Tool,
        params: dict[str, Any],
        next: Any,
    ) -> Any:
        import time

        entry = {
            "timestamp": time.time(),
            "tool": tool.name,
            "params": params,
            "status": "started",
        }

        try:
            result = await next(tool, params)
            entry["status"] = "success"
            entry["result"] = str(result)[:100]  # Truncate long results
            return result
        except Exception as e:
            entry["status"] = "error"
            entry["error"] = str(e)
            raise
        finally:
            self.audit_log.append(entry)

    def get_log(self) -> list[dict[str, Any]]:
        """Get the audit log."""
        return self.audit_log

    def clear_log(self) -> None:
        """Clear the audit log."""
        self.audit_log.clear()


class TransformMiddleware(Middleware):
    """Middleware that transforms inputs and outputs."""

    def __init__(
        self,
        input_transform: dict[str, Any] | None = None,
        output_transform: Any = None,
    ) -> None:
        self._input_transform = input_transform or {}
        self._output_transform = output_transform

    async def __call__(
        self,
        tool: Tool,
        params: dict[str, Any],
        next: Any,
    ) -> Any:
        # Apply input transformations
        transformed_params = {**params}
        for key, value in self._input_transform.items():
            if key not in transformed_params:
                transformed_params[key] = value

        # Execute
        result = await next(tool, transformed_params)

        # Apply output transformation
        if self._output_transform:
            result = self._output_transform(result)

        return result


async def main() -> None:
    """Run the middleware example."""
    print("Example 2: Tool Middleware")
    print("=" * 50)

    # Example 1: Basic logging and timing
    print("\n1. Logging and Timing Middleware:")
    print("-" * 40)

    registry1 = ToolRegistry(validate_inputs=False)  # Disable default validation for demo
    timing = TimingMiddleware()

    registry1.use(LoggingMiddleware())
    registry1.use(timing)

    registry1.register(fast_operation)
    registry1.register(slow_operation)

    await registry1.invoke("fast_operation", {"x": 21})
    await registry1.invoke("slow_operation", {"delay": 0.2})
    await registry1.invoke("fast_operation", {"x": 42})

    print("\n   Timing Statistics:")
    print(f"   fast_operation: {timing.get_stats('fast_operation')}")
    print(f"   slow_operation: {timing.get_stats('slow_operation')}")

    # Example 2: Retry middleware
    print("\n2. Retry Middleware:")
    print("-" * 40)

    registry2 = ToolRegistry(validate_inputs=False)
    registry2.use(RetryMiddleware(max_retries=3, delay=0.1))
    registry2.register(flaky_operation)

    # Try multiple times to see retry behavior
    successes = 0
    failures = 0
    for i in range(5):
        try:
            result = await registry2.invoke("flaky_operation", {"fail_rate": 0.7})
            print(f"   Attempt {i+1}: {result}")
            successes += 1
        except Exception as e:
            print(f"   Attempt {i+1}: Failed after retries - {e}")
            failures += 1

    print(f"\n   Results: {successes} successes, {failures} failures")

    # Example 3: Error handling middleware
    print("\n3. Error Handling Middleware:")
    print("-" * 40)

    def error_handler(tool: Tool, error: Exception) -> dict[str, Any]:
        """Convert errors to error response objects."""
        return {
            "success": False,
            "error": str(error),
            "tool": tool.name,
        }

    registry3 = ToolRegistry(validate_inputs=False)
    registry3.use(ErrorHandlingMiddleware(error_handler))
    registry3.register(divide)

    # Normal operation
    result = await registry3.invoke("divide", {"a": 10, "b": 2})
    print(f"   divide(10, 2) = {result}")

    # Division by zero (handled by middleware)
    result = await registry3.invoke("divide", {"a": 10, "b": 0})
    print(f"   divide(10, 0) = {result}")

    # Example 4: Custom audit middleware
    print("\n4. Custom Audit Middleware:")
    print("-" * 40)

    registry4 = ToolRegistry(validate_inputs=False)
    audit = AuditMiddleware()

    registry4.use(audit)
    registry4.register(fast_operation)
    registry4.register(divide)

    await registry4.invoke("fast_operation", {"x": 10})
    await registry4.invoke("fast_operation", {"x": 20})

    try:
        await registry4.invoke("divide", {"a": 1, "b": 0})
    except Exception:
        pass

    print("   Audit Log:")
    for entry in audit.get_log():
        status_icon = "+" if entry["status"] == "success" else "X"
        print(f"   [{status_icon}] {entry['tool']}: {entry.get('result', entry.get('error'))}")

    # Example 5: Middleware chain order
    print("\n5. Middleware Chain Order:")
    print("-" * 40)

    class OrderTracker(Middleware):
        def __init__(self, name: str, order_list: list[str]) -> None:
            self.name = name
            self.order_list = order_list

        async def __call__(self, tool: Tool, params: dict[str, Any], next: Any) -> Any:
            self.order_list.append(f"{self.name}:before")
            result = await next(tool, params)
            self.order_list.append(f"{self.name}:after")
            return result

    order: list[str] = []
    registry5 = ToolRegistry(validate_inputs=False)
    registry5.use(OrderTracker("A", order))
    registry5.use(OrderTracker("B", order))
    registry5.use(OrderTracker("C", order))
    registry5.register(fast_operation)

    await registry5.invoke("fast_operation", {"x": 1})

    print(f"   Execution order: {' -> '.join(order)}")
    print("   (Middleware wraps in order: A wraps B wraps C wraps execution)")

    print("\n" + "=" * 50)
    print("Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
