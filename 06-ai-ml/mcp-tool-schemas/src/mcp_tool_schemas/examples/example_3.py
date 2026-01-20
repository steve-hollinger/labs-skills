"""Example 3: Tool Server Implementation

This example demonstrates how to build a complete MCP tool server
with multiple tools, validation, and execution.
"""

import json
from datetime import datetime
from typing import Any

from mcp_tool_schemas import ToolDefinition, ToolParameter
from mcp_tool_schemas.server import ToolServer, create_server


def main() -> None:
    """Run the tool server example."""
    print("Example 3: Tool Server Implementation")
    print("=" * 60)

    # Create a tool server
    server = create_server(
        name="demo-tools",
        version="1.0.0",
    )

    # Define tools
    print("\n1. Defining Tools")
    print("-" * 40)

    # Calculator tool
    calculator_tool = ToolDefinition(
        name="calculate",
        description="""Perform mathematical calculations.

        Evaluates a mathematical expression safely.
        Supports: +, -, *, /, **, %, sqrt, abs, round
        Returns the numeric result.
        """,
        parameters=[
            ToolParameter(
                name="expression",
                type="string",
                description="Mathematical expression to evaluate (e.g., '2 + 2', 'sqrt(16)')",
                required=True,
                max_length=200,
            ),
            ToolParameter(
                name="precision",
                type="integer",
                description="Decimal places for rounding result",
                minimum=0,
                maximum=10,
                default=2,
            ),
        ],
    )

    # Note-taking tool
    notes_tool = ToolDefinition(
        name="manage_notes",
        description="""Create, read, update, or delete notes.

        Manages a simple in-memory note storage.
        Notes have a title, content, and tags.
        Returns the affected note(s) or confirmation.
        """,
        parameters=[
            ToolParameter(
                name="action",
                type="string",
                description="Action to perform",
                required=True,
                enum=["create", "read", "update", "delete", "list", "search"],
            ),
            ToolParameter(
                name="note_id",
                type="string",
                description="Note ID (required for read, update, delete)",
            ),
            ToolParameter(
                name="title",
                type="string",
                description="Note title (for create/update)",
                max_length=100,
            ),
            ToolParameter(
                name="content",
                type="string",
                description="Note content (for create/update)",
                max_length=5000,
            ),
            ToolParameter(
                name="tags",
                type="array",
                description="Tags for organization",
                items={"type": "string", "maxLength": 30},
                max_items=10,
            ),
            ToolParameter(
                name="search_query",
                type="string",
                description="Search query (for search action)",
            ),
        ],
    )

    # Time tool
    time_tool = ToolDefinition(
        name="get_time",
        description="""Get current time in various formats and timezones.

        Returns the current date/time formatted as requested.
        Supports multiple output formats and timezone conversion.
        """,
        parameters=[
            ToolParameter(
                name="format",
                type="string",
                description="Output format",
                enum=["iso", "unix", "human", "date_only", "time_only"],
                default="human",
            ),
            ToolParameter(
                name="timezone",
                type="string",
                description="Timezone (e.g., 'UTC', 'US/Pacific')",
                default="UTC",
            ),
        ],
    )

    # Register tool handlers
    # In-memory storage for notes
    notes_db: dict[str, dict[str, Any]] = {}
    note_counter = 0

    @server.tool(calculator_tool)
    def handle_calculate(expression: str, precision: int = 2) -> dict[str, Any]:
        """Handle calculator tool."""
        import math

        # Safe evaluation with limited operations
        allowed_names = {
            "sqrt": math.sqrt,
            "abs": abs,
            "round": round,
            "pow": pow,
            "pi": math.pi,
            "e": math.e,
        }

        try:
            # Simple safe eval (in production, use a proper expression parser)
            # This is a simplified example
            result = eval(expression, {"__builtins__": {}}, allowed_names)  # noqa: S307
            return {
                "expression": expression,
                "result": round(float(result), precision),
            }
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")

    @server.tool(notes_tool)
    def handle_notes(
        action: str,
        note_id: str | None = None,
        title: str | None = None,
        content: str | None = None,
        tags: list[str] | None = None,
        search_query: str | None = None,
    ) -> dict[str, Any]:
        """Handle notes tool."""
        nonlocal note_counter

        if action == "create":
            if not title:
                raise ValueError("Title required for create")
            note_counter += 1
            new_id = f"note_{note_counter}"
            notes_db[new_id] = {
                "id": new_id,
                "title": title,
                "content": content or "",
                "tags": tags or [],
                "created": datetime.now().isoformat(),
            }
            return {"created": notes_db[new_id]}

        elif action == "read":
            if not note_id or note_id not in notes_db:
                raise ValueError(f"Note not found: {note_id}")
            return {"note": notes_db[note_id]}

        elif action == "update":
            if not note_id or note_id not in notes_db:
                raise ValueError(f"Note not found: {note_id}")
            if title:
                notes_db[note_id]["title"] = title
            if content is not None:
                notes_db[note_id]["content"] = content
            if tags is not None:
                notes_db[note_id]["tags"] = tags
            notes_db[note_id]["updated"] = datetime.now().isoformat()
            return {"updated": notes_db[note_id]}

        elif action == "delete":
            if not note_id or note_id not in notes_db:
                raise ValueError(f"Note not found: {note_id}")
            deleted = notes_db.pop(note_id)
            return {"deleted": deleted}

        elif action == "list":
            return {"notes": list(notes_db.values())}

        elif action == "search":
            if not search_query:
                raise ValueError("Search query required")
            query_lower = search_query.lower()
            matches = [
                note
                for note in notes_db.values()
                if query_lower in note["title"].lower()
                or query_lower in note["content"].lower()
                or any(query_lower in tag.lower() for tag in note["tags"])
            ]
            return {"matches": matches, "count": len(matches)}

        else:
            raise ValueError(f"Unknown action: {action}")

    @server.tool(time_tool)
    def handle_time(format: str = "human", timezone: str = "UTC") -> dict[str, Any]:
        """Handle time tool."""
        now = datetime.utcnow()

        if format == "iso":
            return {"time": now.isoformat() + "Z", "timezone": timezone}
        elif format == "unix":
            return {"time": int(now.timestamp()), "timezone": timezone}
        elif format == "human":
            return {
                "time": now.strftime("%A, %B %d, %Y at %I:%M %p"),
                "timezone": timezone,
            }
        elif format == "date_only":
            return {"date": now.strftime("%Y-%m-%d"), "timezone": timezone}
        elif format == "time_only":
            return {"time": now.strftime("%H:%M:%S"), "timezone": timezone}
        else:
            return {"time": now.isoformat(), "timezone": timezone}

    # Show registered tools
    print(f"Registered {len(server.tools)} tools:")
    for tool_name in server.tools:
        print(f"  - {tool_name}")

    # Generate server manifest
    print("\n2. Server Manifest")
    print("-" * 40)
    manifest = server.to_manifest()
    print(json.dumps(manifest, indent=2))

    # Test tool execution
    print("\n3. Tool Execution")
    print("-" * 40)

    # Test calculator
    print("\nCalculator:")
    result = server.call_tool("calculate", {"expression": "sqrt(16) + 2**3"})
    print(f"  Input: sqrt(16) + 2**3")
    print(f"  Result: {result.to_dict()}")

    # Test notes - create
    print("\nNotes - Create:")
    result = server.call_tool(
        "manage_notes",
        {
            "action": "create",
            "title": "Meeting Notes",
            "content": "Discussed project timeline",
            "tags": ["work", "important"],
        },
    )
    print(f"  Result: {json.dumps(result.to_dict(), indent=4)}")

    # Test notes - list
    print("\nNotes - List:")
    result = server.call_tool("manage_notes", {"action": "list"})
    print(f"  Result: {json.dumps(result.to_dict(), indent=4)}")

    # Test time
    print("\nTime:")
    result = server.call_tool("get_time", {"format": "human"})
    print(f"  Result: {result.to_dict()}")

    # Test validation error
    print("\n4. Error Handling")
    print("-" * 40)

    print("\nInvalid input (missing required):")
    result = server.call_tool("calculate", {})
    print(f"  Result: {result.to_dict()}")

    print("\nUnknown tool:")
    result = server.call_tool("nonexistent_tool", {})
    print(f"  Result: {result.to_dict()}")

    print("\nExecution error:")
    result = server.call_tool("calculate", {"expression": "invalid + + syntax"})
    print(f"  Result: {result.to_dict()}")

    # Create more notes and search
    print("\n5. Advanced Operations")
    print("-" * 40)

    server.call_tool(
        "manage_notes",
        {
            "action": "create",
            "title": "Shopping List",
            "content": "Milk, bread, eggs",
            "tags": ["personal"],
        },
    )
    server.call_tool(
        "manage_notes",
        {
            "action": "create",
            "title": "Project Ideas",
            "content": "Build a chatbot, create API documentation",
            "tags": ["work", "ideas"],
        },
    )

    print("\nSearch for 'work':")
    result = server.call_tool("manage_notes", {"action": "search", "search_query": "work"})
    print(f"  Found {result.data['count']} notes")
    for note in result.data["matches"]:
        print(f"    - {note['title']}")

    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
