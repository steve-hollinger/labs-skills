"""Solution for Exercise 1: Create a Calculator Tool with Input Validation"""

import asyncio
from typing import Any

from tool_registry import ToolRegistry, ToolSchema, tool


# Define the schema with validation for operations
calculator_schema = ToolSchema(
    input={
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["add", "subtract", "multiply", "divide"],
                "description": "The arithmetic operation to perform",
            },
            "a": {
                "type": "number",
                "description": "First operand",
            },
            "b": {
                "type": "number",
                "description": "Second operand",
            },
        },
        "required": ["operation", "a", "b"],
    },
    output={
        "type": "object",
        "properties": {
            "result": {"type": "number"},
            "operation": {"type": "string"},
        },
    },
)


class DivisionByZeroError(Exception):
    """Exception for division by zero."""

    pass


@tool(
    name="calculate",
    description="Perform arithmetic calculations",
    schema=calculator_schema,
)
async def calculate(operation: str, a: float, b: float) -> dict[str, Any]:
    """Perform a calculation.

    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
        a: First number
        b: Second number

    Returns:
        Dictionary with result and operation string
    """
    # Map operations to their symbols and functions
    operations = {
        "add": ("+", lambda x, y: x + y),
        "subtract": ("-", lambda x, y: x - y),
        "multiply": ("*", lambda x, y: x * y),
        "divide": ("/", lambda x, y: x / y if y != 0 else None),
    }

    if operation not in operations:
        raise ValueError(f"Invalid operation: {operation}")

    symbol, func = operations[operation]

    # Handle divide by zero
    if operation == "divide" and b == 0:
        raise DivisionByZeroError("Cannot divide by zero")

    result = func(a, b)

    return {
        "result": result,
        "operation": f"{a} {symbol} {b}",
    }


async def main() -> None:
    """Test the calculator tool."""
    print("Solution 1: Calculator Tool with Input Validation")
    print("=" * 50)

    registry = ToolRegistry()
    registry.register(calculate)

    # Test cases
    test_cases = [
        ({"operation": "add", "a": 5, "b": 3}, "Should return 8"),
        ({"operation": "subtract", "a": 10, "b": 4}, "Should return 6"),
        ({"operation": "multiply", "a": 6, "b": 7}, "Should return 42"),
        ({"operation": "divide", "a": 20, "b": 4}, "Should return 5"),
        ({"operation": "divide", "a": 10, "b": 0}, "Should handle divide by zero"),
        ({"operation": "modulo", "a": 1, "b": 2}, "Should fail validation (invalid operation)"),
        ({"operation": "add", "a": "five", "b": 3}, "Should fail validation (wrong type)"),
        ({"a": 5, "b": 3}, "Should fail validation (missing operation)"),
    ]

    for params, description in test_cases:
        print(f"\n{description}:")
        print(f"  Input: {params}")
        try:
            result = await registry.invoke("calculate", params)
            print(f"  Output: {result}")
        except DivisionByZeroError as e:
            print(f"  Error (DivisionByZero): {e}")
        except Exception as e:
            print(f"  Error: {type(e).__name__}: {e}")

    print("\n" + "=" * 50)
    print("Solution demonstration complete!")


if __name__ == "__main__":
    asyncio.run(main())
