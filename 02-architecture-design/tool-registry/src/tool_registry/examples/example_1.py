"""Example 1: Basic Tool Registration

This example demonstrates creating and registering simple tools using
both the decorator pattern and explicit registration.

Key concepts:
- Creating tools with the @tool decorator
- Registering tools with a registry
- Invoking tools with validated parameters
- Listing and discovering tools
"""

import asyncio
from typing import Any

from tool_registry import Tool, ToolRegistry, ToolSchema, tool


# Method 1: Using the @tool decorator
@tool(
    name="greet",
    description="Greet a user by name",
)
async def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"


@tool(
    name="add",
    description="Add two numbers together",
    schema=ToolSchema(
        input={
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"},
            },
            "required": ["a", "b"],
        },
        output={"type": "number"},
    ),
)
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@tool(
    name="search",
    description="Search for items by query",
    tags=["search", "query"],
)
async def search(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """Simulate a search operation."""
    # Simulated search results
    results = [
        {"id": i, "title": f"Result {i} for '{query}'", "score": 1.0 - (i * 0.1)}
        for i in range(min(limit, 5))
    ]
    return results


# Method 2: Creating Tool objects directly
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


multiply_tool = Tool(
    name="multiply",
    description="Multiply two numbers together",
    func=multiply,
    schema=ToolSchema(
        input={
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
            "required": ["a", "b"],
        },
        output={"type": "number"},
    ),
)


async def main() -> None:
    """Run the basic tool registration example."""
    print("Example 1: Basic Tool Registration")
    print("=" * 50)

    # Create a registry
    registry = ToolRegistry()

    # Register tools
    print("\n1. Registering tools...")
    registry.register(greet)
    registry.register(add)
    registry.register(search)
    registry.register(multiply_tool)
    print(f"   Registered {len(registry.list_tools())} tools")

    # List all tools
    print("\n2. Available tools:")
    for t in registry.list_tools():
        print(f"   - {t.name}: {t.description}")
        if t.tags:
            print(f"     Tags: {t.tags}")

    # Get tool schemas
    print("\n3. Tool schemas:")
    for name in ["greet", "add"]:
        schema = registry.get_schema(name)
        print(f"   {name}: {schema['input']}")

    # Invoke tools
    print("\n4. Invoking tools:")

    # Invoke greet
    result = await registry.invoke("greet", {"name": "Alice"})
    print(f"   greet({{'name': 'Alice'}}) = {result!r}")

    # Invoke add
    result = await registry.invoke("add", {"a": 5, "b": 3})
    print(f"   add({{'a': 5, 'b': 3}}) = {result}")

    # Invoke multiply
    result = await registry.invoke("multiply", {"a": 4, "b": 7})
    print(f"   multiply({{'a': 4, 'b': 7}}) = {result}")

    # Invoke search
    result = await registry.invoke("search", {"query": "python", "limit": 3})
    print(f"   search({{'query': 'python', 'limit': 3}}) =")
    for item in result:
        print(f"     - {item}")

    # Find tools by tag
    print("\n5. Finding tools by tag:")
    search_tools = registry.find_by_tag("search")
    print(f"   Tools with 'search' tag: {[t.name for t in search_tools]}")

    # Demonstrate validation
    print("\n6. Validation example:")
    from tool_registry import ValidationError

    try:
        # This should fail - missing required parameter
        await registry.invoke("add", {"a": 5})
    except ValidationError as e:
        print(f"   Validation error: {e}")

    try:
        # This should fail - wrong type
        await registry.invoke("add", {"a": "not a number", "b": 3})
    except ValidationError as e:
        print(f"   Validation error: {e}")

    # Using the registry's decorator
    print("\n7. Using registry.tool decorator:")

    @registry.tool(name="divide", description="Divide two numbers")
    def divide(a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

    result = await registry.invoke("divide", {"a": 10, "b": 2})
    print(f"   divide({{'a': 10, 'b': 2}}) = {result}")

    # Get tools as JSON (for AI agents)
    print("\n8. Tools as JSON (for AI agents):")
    tools_json = registry.get_tools_json()
    for tool_info in tools_json[:2]:  # Show first 2
        print(f"   {tool_info}")

    print("\n" + "=" * 50)
    print("Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
