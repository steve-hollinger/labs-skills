"""Solution for Exercise 3: Multi-Tool MCP Server"""

from datetime import datetime
from typing import Any

from mcp_tool_schemas import ToolDefinition, ToolParameter, ToolResult
from mcp_tool_schemas.server import ToolServer, create_server


def create_task_tools() -> list[ToolDefinition]:
    """Create tool definitions for task management."""
    tools = []

    # 1. create_task
    tools.append(
        ToolDefinition(
            name="create_task",
            description="""Create a new task in the task management system.

            Creates a task with the specified details and returns the created task
            with a generated unique ID.

            Use this tool when a user wants to:
            - Add a new task or todo item
            - Create a reminder
            - Schedule work to be done
            """,
            parameters=[
                ToolParameter(
                    name="title",
                    type="string",
                    description="Task title (required)",
                    required=True,
                    min_length=1,
                    max_length=200,
                ),
                ToolParameter(
                    name="description",
                    type="string",
                    description="Detailed task description",
                    max_length=2000,
                    default="",
                ),
                ToolParameter(
                    name="priority",
                    type="string",
                    description="Task priority level",
                    enum=["low", "medium", "high"],
                    default="medium",
                ),
                ToolParameter(
                    name="due_date",
                    type="string",
                    description="Due date (YYYY-MM-DD format)",
                    format="date",
                ),
                ToolParameter(
                    name="tags",
                    type="array",
                    description="Tags for organizing tasks",
                    items={"type": "string", "maxLength": 50},
                    max_items=10,
                    default=[],
                ),
            ],
        )
    )

    # 2. get_task
    tools.append(
        ToolDefinition(
            name="get_task",
            description="""Get details of a specific task by ID.

            Returns the full task details including title, description,
            status, priority, dates, and tags.

            Returns an error if the task doesn't exist.
            """,
            parameters=[
                ToolParameter(
                    name="task_id",
                    type="string",
                    description="Unique task identifier",
                    required=True,
                ),
            ],
        )
    )

    # 3. update_task
    tools.append(
        ToolDefinition(
            name="update_task",
            description="""Update an existing task.

            Updates only the specified fields, leaving others unchanged.
            Returns the updated task.

            Use this tool to:
            - Change task status (pending -> in_progress -> completed)
            - Update priority
            - Modify title, description, or due date
            - Add or remove tags
            """,
            parameters=[
                ToolParameter(
                    name="task_id",
                    type="string",
                    description="Unique task identifier",
                    required=True,
                ),
                ToolParameter(
                    name="title",
                    type="string",
                    description="New task title",
                    min_length=1,
                    max_length=200,
                ),
                ToolParameter(
                    name="description",
                    type="string",
                    description="New task description",
                    max_length=2000,
                ),
                ToolParameter(
                    name="priority",
                    type="string",
                    description="New priority level",
                    enum=["low", "medium", "high"],
                ),
                ToolParameter(
                    name="status",
                    type="string",
                    description="New task status",
                    enum=["pending", "in_progress", "completed", "cancelled"],
                ),
                ToolParameter(
                    name="due_date",
                    type="string",
                    description="New due date (YYYY-MM-DD)",
                    format="date",
                ),
                ToolParameter(
                    name="tags",
                    type="array",
                    description="New tags (replaces existing)",
                    items={"type": "string", "maxLength": 50},
                    max_items=10,
                ),
            ],
        )
    )

    # 4. delete_task
    tools.append(
        ToolDefinition(
            name="delete_task",
            description="""Delete a task permanently.

            Removes the task from the system. This action cannot be undone.
            Returns confirmation of deletion.
            """,
            parameters=[
                ToolParameter(
                    name="task_id",
                    type="string",
                    description="Unique task identifier",
                    required=True,
                ),
            ],
        )
    )

    # 5. list_tasks
    tools.append(
        ToolDefinition(
            name="list_tasks",
            description="""List tasks with optional filtering and pagination.

            Returns a list of tasks matching the specified filters.
            Use pagination (limit/offset) for large result sets.

            Results are sorted by creation date (newest first).
            """,
            parameters=[
                ToolParameter(
                    name="status",
                    type="string",
                    description="Filter by status",
                    enum=["pending", "in_progress", "completed", "cancelled"],
                ),
                ToolParameter(
                    name="priority",
                    type="string",
                    description="Filter by priority",
                    enum=["low", "medium", "high"],
                ),
                ToolParameter(
                    name="limit",
                    type="integer",
                    description="Maximum tasks to return",
                    minimum=1,
                    maximum=100,
                    default=50,
                ),
                ToolParameter(
                    name="offset",
                    type="integer",
                    description="Number of tasks to skip",
                    minimum=0,
                    default=0,
                ),
            ],
        )
    )

    return tools


def create_task_server() -> tuple[ToolServer, dict[str, dict[str, Any]]]:
    """Create and configure the task management server."""
    server = create_server("task-manager", "1.0.0")
    tasks_db: dict[str, dict[str, Any]] = {}
    task_counter = 0

    tools = create_task_tools()

    @server.tool(tools[0])  # create_task
    def handle_create_task(
        title: str,
        description: str = "",
        priority: str = "medium",
        due_date: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        nonlocal task_counter
        task_counter += 1
        task_id = f"task_{task_counter}"

        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
            "status": "pending",
            "due_date": due_date,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        tasks_db[task_id] = task
        return {"task": task}

    @server.tool(tools[1])  # get_task
    def handle_get_task(task_id: str) -> dict[str, Any]:
        if task_id not in tasks_db:
            raise ValueError(f"Task not found: {task_id}")
        return {"task": tasks_db[task_id]}

    @server.tool(tools[2])  # update_task
    def handle_update_task(
        task_id: str,
        title: str | None = None,
        description: str | None = None,
        priority: str | None = None,
        status: str | None = None,
        due_date: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        if task_id not in tasks_db:
            raise ValueError(f"Task not found: {task_id}")

        task = tasks_db[task_id]

        if title is not None:
            task["title"] = title
        if description is not None:
            task["description"] = description
        if priority is not None:
            task["priority"] = priority
        if status is not None:
            task["status"] = status
        if due_date is not None:
            task["due_date"] = due_date
        if tags is not None:
            task["tags"] = tags

        task["updated_at"] = datetime.now().isoformat()

        return {"task": task}

    @server.tool(tools[3])  # delete_task
    def handle_delete_task(task_id: str) -> dict[str, Any]:
        if task_id not in tasks_db:
            raise ValueError(f"Task not found: {task_id}")

        deleted_task = tasks_db.pop(task_id)
        return {"deleted": True, "task_id": task_id, "title": deleted_task["title"]}

    @server.tool(tools[4])  # list_tasks
    def handle_list_tasks(
        status: str | None = None,
        priority: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        # Filter tasks
        filtered = list(tasks_db.values())

        if status:
            filtered = [t for t in filtered if t["status"] == status]
        if priority:
            filtered = [t for t in filtered if t["priority"] == priority]

        # Sort by created_at (newest first)
        filtered.sort(key=lambda t: t["created_at"], reverse=True)

        # Apply pagination
        total = len(filtered)
        paginated = filtered[offset : offset + limit]

        return {
            "tasks": paginated,
            "count": len(paginated),
            "total": total,
            "offset": offset,
            "limit": limit,
        }

    return server, tasks_db


def solution() -> None:
    """Demonstrate the solution."""
    print("Solution 3: Multi-Tool MCP Server")
    print("=" * 50)

    server, tasks_db = create_task_server()

    print("\nRegistered Tools:")
    for tool in server.list_tools():
        print(f"  - {tool['name']}")

    # Create some tasks
    print("\nCreating tasks...")
    result = server.call_tool(
        "create_task",
        {
            "title": "Review code",
            "description": "Review the pull request",
            "priority": "high",
            "tags": ["code", "review"],
        },
    )
    print(f"  Created: {result.data['task']['id']}")

    result = server.call_tool(
        "create_task",
        {"title": "Write documentation", "priority": "medium"},
    )
    print(f"  Created: {result.data['task']['id']}")

    # List tasks
    print("\nListing tasks:")
    result = server.call_tool("list_tasks", {})
    for task in result.data["tasks"]:
        print(f"  - [{task['priority']}] {task['title']}")

    # Update a task
    print("\nUpdating task_1 status...")
    result = server.call_tool(
        "update_task", {"task_id": "task_1", "status": "in_progress"}
    )
    print(f"  New status: {result.data['task']['status']}")

    # Delete a task
    print("\nDeleting task_2...")
    result = server.call_tool("delete_task", {"task_id": "task_2"})
    print(f"  Deleted: {result.data['title']}")

    print("\nFinal task list:")
    result = server.call_tool("list_tasks", {})
    print(f"  Total tasks: {result.data['total']}")


if __name__ == "__main__":
    solution()
