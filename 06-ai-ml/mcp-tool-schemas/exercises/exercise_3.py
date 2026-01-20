"""Exercise 3: Build a Multi-Tool MCP Server

In this exercise, you'll build a complete MCP tool server with multiple
related tools for a task management system.

Instructions:
1. Create tool definitions for: create_task, get_task, update_task, delete_task, list_tasks
2. Register all tools with a ToolServer
3. Implement handlers for each tool
4. Add proper error handling

Expected Output:
When you run this file, the tests at the bottom should pass.

Hints:
- Use consistent parameter naming across tools
- Implement an in-memory task storage
- Return structured responses (success/error)
- Handle edge cases (not found, validation errors)
"""

from datetime import datetime
from typing import Any

from mcp_tool_schemas import ToolDefinition, ToolParameter, ToolResult
from mcp_tool_schemas.server import ToolServer, create_server


def create_task_tools() -> list[ToolDefinition]:
    """Create tool definitions for task management.

    Required tools:

    1. create_task:
       - title: Required string (1-200 chars)
       - description: Optional string (max 2000 chars)
       - priority: Optional enum (low, medium, high), default medium
       - due_date: Optional date string
       - tags: Optional array of strings
       Returns: Created task with generated ID

    2. get_task:
       - task_id: Required string
       Returns: Task details or error if not found

    3. update_task:
       - task_id: Required string
       - title: Optional string
       - description: Optional string
       - priority: Optional enum
       - status: Optional enum (pending, in_progress, completed, cancelled)
       - due_date: Optional date string
       - tags: Optional array
       Returns: Updated task

    4. delete_task:
       - task_id: Required string
       Returns: Confirmation

    5. list_tasks:
       - status: Optional enum to filter
       - priority: Optional enum to filter
       - limit: Optional integer (1-100, default 50)
       - offset: Optional integer (default 0)
       Returns: List of tasks with count
    """
    # TODO: Implement the tool definitions
    tools = []

    # TODO: Create create_task tool
    # TODO: Create get_task tool
    # TODO: Create update_task tool
    # TODO: Create delete_task tool
    # TODO: Create list_tasks tool

    return tools


def create_task_server() -> tuple[ToolServer, dict[str, dict[str, Any]]]:
    """Create and configure the task management server.

    Returns:
        Tuple of (server, tasks_db) where tasks_db is the in-memory storage
    """
    server = create_server("task-manager", "1.0.0")
    tasks_db: dict[str, dict[str, Any]] = {}
    task_counter = 0

    tools = create_task_tools()

    # TODO: Register handlers for each tool
    # Hint: Use @server.tool(definition) decorator or server.register_tool()

    # Example handler structure:
    # @server.tool(tools[0])  # create_task
    # def handle_create_task(title: str, description: str = "", ...) -> dict:
    #     nonlocal task_counter
    #     task_counter += 1
    #     task_id = f"task_{task_counter}"
    #     ...
    #     return {"task": task_data}

    return server, tasks_db


def exercise() -> None:
    """Run exercise tests."""
    print("Exercise 3: Multi-Tool MCP Server")
    print("=" * 50)

    server, tasks_db = create_task_server()

    # Test 1: Check all tools registered
    print("\nTest 1: Tools registered")
    expected_tools = ["create_task", "get_task", "update_task", "delete_task", "list_tasks"]
    for tool_name in expected_tools:
        assert server.get_tool(tool_name) is not None, f"Tool '{tool_name}' not registered"
        print(f"  - {tool_name}: registered")
    print("  PASSED!")

    # Test 2: Create a task
    print("\nTest 2: Create task")
    result = server.call_tool("create_task", {
        "title": "Complete exercise",
        "description": "Finish the MCP tool schemas exercise",
        "priority": "high",
        "tags": ["learning", "python"],
    })
    assert result.success, f"Create task failed: {result.error}"
    assert "task" in result.data
    task_id = result.data["task"]["id"]
    print(f"  Created task: {task_id}")
    print("  PASSED!")

    # Test 3: Get the task
    print("\nTest 3: Get task")
    result = server.call_tool("get_task", {"task_id": task_id})
    assert result.success, f"Get task failed: {result.error}"
    assert result.data["task"]["title"] == "Complete exercise"
    print(f"  Retrieved task: {result.data['task']['title']}")
    print("  PASSED!")

    # Test 4: Update the task
    print("\nTest 4: Update task")
    result = server.call_tool("update_task", {
        "task_id": task_id,
        "status": "in_progress",
        "priority": "medium",
    })
    assert result.success, f"Update task failed: {result.error}"
    assert result.data["task"]["status"] == "in_progress"
    print(f"  Updated status to: {result.data['task']['status']}")
    print("  PASSED!")

    # Test 5: Create more tasks
    print("\nTest 5: Create multiple tasks")
    for i in range(3):
        result = server.call_tool("create_task", {
            "title": f"Task {i + 2}",
            "priority": ["low", "medium", "high"][i],
        })
        assert result.success
    print("  Created 3 more tasks")
    print("  PASSED!")

    # Test 6: List tasks
    print("\nTest 6: List tasks")
    result = server.call_tool("list_tasks", {})
    assert result.success, f"List tasks failed: {result.error}"
    assert result.data["count"] >= 4
    print(f"  Total tasks: {result.data['count']}")
    print("  PASSED!")

    # Test 7: List with filter
    print("\nTest 7: List tasks with filter")
    result = server.call_tool("list_tasks", {"priority": "high"})
    assert result.success
    # Should have at least 1 high priority task
    high_priority = [t for t in result.data["tasks"] if t.get("priority") == "high"]
    assert len(high_priority) >= 1
    print(f"  High priority tasks: {len(high_priority)}")
    print("  PASSED!")

    # Test 8: Delete task
    print("\nTest 8: Delete task")
    result = server.call_tool("delete_task", {"task_id": task_id})
    assert result.success, f"Delete task failed: {result.error}"
    print(f"  Deleted task: {task_id}")

    # Verify deletion
    result = server.call_tool("get_task", {"task_id": task_id})
    assert not result.success, "Task should not exist after deletion"
    print("  Verified task is deleted")
    print("  PASSED!")

    # Test 9: Error handling - not found
    print("\nTest 9: Error handling - not found")
    result = server.call_tool("get_task", {"task_id": "nonexistent"})
    assert not result.success
    assert "not found" in result.error.lower() or "TASK_NOT_FOUND" in str(result.error_code)
    print("  Not found error handled correctly")
    print("  PASSED!")

    # Test 10: Validation error
    print("\nTest 10: Validation error")
    result = server.call_tool("create_task", {})  # Missing required title
    assert not result.success
    assert "validation" in result.error.lower() or result.error_code == "VALIDATION_ERROR"
    print("  Validation error handled correctly")
    print("  PASSED!")

    # Test 11: Server manifest
    print("\nTest 11: Server manifest")
    manifest = server.to_manifest()
    assert manifest["name"] == "task-manager"
    assert len(manifest["tools"]) == 5
    print(f"  Server: {manifest['name']} v{manifest['version']}")
    print(f"  Tools: {len(manifest['tools'])}")
    print("  PASSED!")

    print("\n" + "=" * 50)
    print("All tests passed! You've built a complete MCP server!")


if __name__ == "__main__":
    exercise()
