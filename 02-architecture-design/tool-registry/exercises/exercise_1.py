"""Exercise 1: Create a Calculator Tool with Input Validation

Build a calculator tool that supports basic arithmetic operations with
proper input validation using JSON Schema.

Instructions:
1. Create a calculator tool that accepts an operation and two numbers
2. Support operations: add, subtract, multiply, divide
3. Add validation for:
   - Operation must be one of the allowed values
   - Numbers must be numeric (int or float)
   - Division by zero should be handled
4. Return the result with operation details

Expected Output:
- calculate({"operation": "add", "a": 5, "b": 3}) -> {"result": 8, "operation": "5 + 3"}
- calculate({"operation": "divide", "a": 10, "b": 0}) -> Error
- calculate({"operation": "invalid", "a": 1, "b": 2}) -> Validation Error

Hints:
- Use JSON Schema enum for operation validation
- Handle divide by zero in the function, not the schema
- The @tool decorator can auto-generate schemas from type hints
"""

import asyncio
from typing import Any

from tool_registry import ToolRegistry, ToolSchema, tool


# TODO: Define the schema with validation for operations
calculator_schema = ToolSchema(
    input={
        "type": "object",
        "properties": {
            # TODO: Add "operation" with enum validation
            # TODO: Add "a" as number
            # TODO: Add "b" as number
        },
        # TODO: Add required fields
    },
    output={
        "type": "object",
        "properties": {
            "result": {"type": "number"},
            "operation": {"type": "string"},
        },
    },
)


# TODO: Implement the calculator tool
@tool(
    name="calculate",
    description="Perform arithmetic calculations",
    schema=calculator_schema,
)
async def calculate(operation: str, a: float, b: float) -> dict[str, Any]:
    """Perform a calculation.

    TODO: Implement this function:
    1. Check if operation is valid
    2. Handle divide by zero
    3. Perform the operation
    4. Return result with operation string
    """
    pass


async def main() -> None:
    """Test the calculator tool."""
    print("Testing Calculator Tool...")

    registry = ToolRegistry()
    registry.register(calculate)

    # Test cases
    test_cases = [
        ({"operation": "add", "a": 5, "b": 3}, "Should return 8"),
        ({"operation": "subtract", "a": 10, "b": 4}, "Should return 6"),
        ({"operation": "multiply", "a": 6, "b": 7}, "Should return 42"),
        ({"operation": "divide", "a": 20, "b": 4}, "Should return 5"),
        ({"operation": "divide", "a": 10, "b": 0}, "Should handle divide by zero"),
        ({"operation": "modulo", "a": 1, "b": 2}, "Should fail validation"),
    ]

    for params, description in test_cases:
        print(f"\n{description}:")
        print(f"  Input: {params}")
        try:
            result = await registry.invoke("calculate", params)
            print(f"  Output: {result}")
        except Exception as e:
            print(f"  Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
