"""Example 3: AI Agent Tools

This example demonstrates creating a complete tool system for AI agents,
including tool discovery, schema generation, and invocation patterns
commonly used in LLM applications.

Key concepts:
- Exposing tools for AI agent consumption
- JSON Schema generation for tool definitions
- Tool invocation from AI-generated parameters
- Permission-based tool access control
"""

import asyncio
import json
from datetime import datetime
from typing import Any

from tool_registry import ToolRegistry, ToolSchema, tool
from tool_registry.exceptions import PermissionDeniedError, ToolNotFoundError, ValidationError


# Simulated data stores
USERS_DB = {
    "u1": {"id": "u1", "name": "Alice", "email": "alice@example.com", "role": "admin"},
    "u2": {"id": "u2", "name": "Bob", "email": "bob@example.com", "role": "user"},
}

ORDERS_DB = {
    "o1": {"id": "o1", "user_id": "u1", "product": "Widget", "status": "shipped"},
    "o2": {"id": "o2", "user_id": "u2", "product": "Gadget", "status": "pending"},
}


# Define tools for the AI agent


@tool(
    name="get_user",
    description="Retrieve user information by user ID",
    schema=ToolSchema(
        input={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The unique identifier of the user",
                }
            },
            "required": ["user_id"],
        },
        output={
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "email": {"type": "string"},
            },
        },
    ),
    tags=["user", "read"],
)
async def get_user(user_id: str) -> dict[str, Any] | None:
    """Get user by ID."""
    return USERS_DB.get(user_id)


@tool(
    name="search_users",
    description="Search for users by name or email",
    schema=ToolSchema(
        input={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for name or email",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    ),
    tags=["user", "search"],
)
async def search_users(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """Search users by name or email."""
    results = []
    query_lower = query.lower()
    for user in USERS_DB.values():
        if query_lower in user["name"].lower() or query_lower in user["email"].lower():
            results.append(user)
            if len(results) >= limit:
                break
    return results


@tool(
    name="get_orders",
    description="Get orders for a specific user",
    tags=["order", "read"],
)
async def get_orders(user_id: str) -> list[dict[str, Any]]:
    """Get all orders for a user."""
    return [o for o in ORDERS_DB.values() if o["user_id"] == user_id]


@tool(
    name="update_order_status",
    description="Update the status of an order (admin only)",
    permissions=["admin"],
    tags=["order", "write"],
)
async def update_order_status(order_id: str, status: str) -> dict[str, Any]:
    """Update order status."""
    if order_id not in ORDERS_DB:
        raise ValueError(f"Order {order_id} not found")
    ORDERS_DB[order_id]["status"] = status
    return ORDERS_DB[order_id]


@tool(
    name="get_current_time",
    description="Get the current date and time",
    tags=["utility"],
)
async def get_current_time() -> str:
    """Get current timestamp."""
    return datetime.now().isoformat()


@tool(
    name="calculate",
    description="Perform basic arithmetic calculations",
    schema=ToolSchema(
        input={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A simple arithmetic expression (e.g., '2 + 2')",
                }
            },
            "required": ["expression"],
        },
    ),
    tags=["utility", "math"],
)
async def calculate(expression: str) -> float:
    """Evaluate a simple arithmetic expression."""
    # Only allow safe operations
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        raise ValueError("Invalid characters in expression")
    try:
        return float(eval(expression))  # noqa: S307 - safe due to character filtering
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}") from e


class AIAgent:
    """Simulated AI agent that uses tools."""

    def __init__(self, registry: ToolRegistry, permissions: list[str]) -> None:
        self.registry = registry
        self.permissions = permissions
        self.conversation_history: list[dict[str, Any]] = []

    def get_available_tools(self) -> list[dict[str, Any]]:
        """Get tools available to this agent (respecting permissions)."""
        tools = []
        for t in self.registry.list_tools():
            # Check if agent has permission
            if not t.permissions or any(p in self.permissions for p in t.permissions):
                tools.append(t.get_signature())
        return tools

    async def process_tool_call(
        self,
        tool_name: str,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        """Process a tool call from the AI model.

        Returns a structured response suitable for the conversation.
        """
        try:
            result = await self.registry.invoke(
                tool_name,
                parameters,
                user_permissions=self.permissions,
            )
            return {
                "success": True,
                "tool": tool_name,
                "result": result,
            }
        except ToolNotFoundError:
            return {
                "success": False,
                "tool": tool_name,
                "error": f"Tool '{tool_name}' not found",
            }
        except ValidationError as e:
            return {
                "success": False,
                "tool": tool_name,
                "error": f"Invalid parameters: {e.errors}",
            }
        except PermissionDeniedError:
            return {
                "success": False,
                "tool": tool_name,
                "error": "Permission denied",
            }
        except Exception as e:
            return {
                "success": False,
                "tool": tool_name,
                "error": str(e),
            }


async def main() -> None:
    """Run the AI agent tools example."""
    print("Example 3: AI Agent Tools")
    print("=" * 50)

    # Create registry and register tools
    registry = ToolRegistry()

    print("\n1. Registering tools...")
    registry.register(get_user)
    registry.register(search_users)
    registry.register(get_orders)
    registry.register(update_order_status)
    registry.register(get_current_time)
    registry.register(calculate)

    print(f"   Registered {len(registry.list_tools())} tools")

    # Get tools as JSON (for AI model)
    print("\n2. Tool definitions (for AI model):")
    tools_json = registry.get_tools_json()
    print(json.dumps(tools_json, indent=2))

    # Create agents with different permissions
    print("\n3. Creating agents with different permissions:")
    admin_agent = AIAgent(registry, permissions=["admin", "user"])
    user_agent = AIAgent(registry, permissions=["user"])

    print(f"   Admin agent tools: {[t['name'] for t in admin_agent.get_available_tools()]}")
    print(f"   User agent tools: {[t['name'] for t in user_agent.get_available_tools()]}")

    # Simulate AI tool calls
    print("\n4. Simulating AI tool calls:")
    print("-" * 40)

    # User agent calls
    print("\n   User Agent calls:")

    # Get user
    result = await user_agent.process_tool_call("get_user", {"user_id": "u1"})
    print(f"   get_user('u1'): {result}")

    # Search users
    result = await user_agent.process_tool_call("search_users", {"query": "alice"})
    print(f"   search_users('alice'): {result}")

    # Get orders
    result = await user_agent.process_tool_call("get_orders", {"user_id": "u1"})
    print(f"   get_orders('u1'): {result}")

    # Try admin operation (should fail)
    result = await user_agent.process_tool_call(
        "update_order_status",
        {"order_id": "o1", "status": "delivered"},
    )
    print(f"   update_order_status (as user): {result}")

    # Admin agent calls
    print("\n   Admin Agent calls:")

    # Admin can update orders
    result = await admin_agent.process_tool_call(
        "update_order_status",
        {"order_id": "o1", "status": "delivered"},
    )
    print(f"   update_order_status (as admin): {result}")

    # Utility tools
    print("\n5. Utility tool calls:")

    result = await user_agent.process_tool_call("get_current_time", {})
    print(f"   get_current_time(): {result}")

    result = await user_agent.process_tool_call("calculate", {"expression": "2 + 2 * 3"})
    print(f"   calculate('2 + 2 * 3'): {result}")

    # Invalid expression
    result = await user_agent.process_tool_call("calculate", {"expression": "import os"})
    print(f"   calculate('import os'): {result}")

    # Error handling examples
    print("\n6. Error handling:")

    # Non-existent tool
    result = await user_agent.process_tool_call("non_existent", {})
    print(f"   non_existent(): {result}")

    # Invalid parameters
    result = await user_agent.process_tool_call("get_user", {})  # Missing user_id
    print(f"   get_user() (missing param): {result}")

    # Finding tools by tag
    print("\n7. Finding tools by tag:")
    user_tools = registry.find_by_tag("user")
    print(f"   Tools tagged 'user': {[t.name for t in user_tools]}")

    utility_tools = registry.find_by_tag("utility")
    print(f"   Tools tagged 'utility': {[t.name for t in utility_tools]}")

    print("\n" + "=" * 50)
    print("Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
