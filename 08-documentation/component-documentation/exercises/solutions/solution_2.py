"""Solution for Exercise 2: Task Management API Documentation."""

from component_documentation.api_docs import document_endpoint


def solution() -> list:
    """Reference solution for Exercise 2.

    Returns:
        List of documented API endpoints.
    """
    endpoints = []

    # List Tasks
    list_tasks = document_endpoint(
        method="GET",
        path="/tasks",
        summary="List all tasks",
        description="Retrieve a paginated list of tasks. Results can be filtered by status, priority, and assignee.",
        parameters=[
            {"name": "limit", "type": "integer", "required": False,
             "description": "Maximum number of results (default: 20, max: 100)"},
            {"name": "offset", "type": "integer", "required": False,
             "description": "Pagination offset (default: 0)"},
            {"name": "status", "type": "string", "required": False,
             "description": "Filter by status (pending, in_progress, completed, cancelled)"},
            {"name": "priority", "type": "string", "required": False,
             "description": "Filter by priority (low, medium, high, urgent)"},
            {"name": "assignee_id", "type": "string", "required": False,
             "description": "Filter by assigned user ID"},
            {"name": "sort", "type": "string", "required": False,
             "description": "Sort order (created_at, updated_at, due_date, priority)"},
        ],
        responses=[
            {
                "status_code": 200,
                "description": "Successful response",
                "example": {
                    "data": [
                        {
                            "id": "task_123",
                            "title": "Complete documentation",
                            "description": "Write API docs for the task service",
                            "status": "in_progress",
                            "priority": "high",
                            "assignee_id": "user_456",
                            "due_date": "2024-01-20",
                            "created_at": "2024-01-15T10:30:00Z",
                            "updated_at": "2024-01-16T14:20:00Z",
                        }
                    ],
                    "meta": {
                        "total": 42,
                        "limit": 20,
                        "offset": 0,
                    },
                },
            },
            {
                "status_code": 401,
                "description": "Unauthorized - Invalid or missing token",
                "example": {
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "Invalid or expired authentication token",
                    }
                },
            },
        ],
        tags=["Tasks"],
    )
    endpoints.append(list_tasks)

    # Create Task
    create_task = document_endpoint(
        method="POST",
        path="/tasks",
        summary="Create a new task",
        description="Create a new task. The authenticated user becomes the creator.",
        request_body={
            "title": "Complete documentation",
            "description": "Write API docs for the task service",
            "priority": "high",
            "assignee_id": "user_456",
            "due_date": "2024-01-20",
            "tags": ["documentation", "api"],
        },
        responses=[
            {
                "status_code": 201,
                "description": "Task created successfully",
                "example": {
                    "id": "task_789",
                    "title": "Complete documentation",
                    "description": "Write API docs for the task service",
                    "status": "pending",
                    "priority": "high",
                    "assignee_id": "user_456",
                    "creator_id": "user_123",
                    "due_date": "2024-01-20",
                    "tags": ["documentation", "api"],
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z",
                },
            },
            {
                "status_code": 400,
                "description": "Validation error",
                "example": {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Request validation failed",
                        "details": {
                            "title": "Title is required",
                            "due_date": "Invalid date format",
                        },
                    }
                },
            },
            {
                "status_code": 401,
                "description": "Unauthorized",
            },
        ],
        tags=["Tasks"],
    )
    endpoints.append(create_task)

    # Get Task
    get_task = document_endpoint(
        method="GET",
        path="/tasks/{id}",
        summary="Get task by ID",
        description="Retrieve a single task by its unique identifier. Includes full task details and activity history.",
        parameters=[
            {"name": "id", "type": "string", "required": True,
             "description": "The unique task identifier (e.g., task_123)"},
            {"name": "include", "type": "string", "required": False,
             "description": "Additional data to include (comments, attachments, history)"},
        ],
        responses=[
            {
                "status_code": 200,
                "description": "Successful response",
                "example": {
                    "id": "task_123",
                    "title": "Complete documentation",
                    "description": "Write API docs for the task service",
                    "status": "in_progress",
                    "priority": "high",
                    "assignee_id": "user_456",
                    "creator_id": "user_123",
                    "due_date": "2024-01-20",
                    "tags": ["documentation", "api"],
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-16T14:20:00Z",
                    "comments_count": 3,
                    "attachments_count": 1,
                },
            },
            {
                "status_code": 401,
                "description": "Unauthorized",
            },
            {
                "status_code": 404,
                "description": "Task not found",
                "example": {
                    "error": {
                        "code": "TASK_NOT_FOUND",
                        "message": "No task found with the specified ID",
                        "details": {"task_id": "task_999"},
                    }
                },
            },
        ],
        tags=["Tasks"],
    )
    endpoints.append(get_task)

    # Update Task
    update_task = document_endpoint(
        method="PUT",
        path="/tasks/{id}",
        summary="Update a task",
        description="Update an existing task. Only provided fields are updated.",
        parameters=[
            {"name": "id", "type": "string", "required": True,
             "description": "The unique task identifier"},
        ],
        request_body={
            "title": "Updated task title",
            "status": "completed",
            "priority": "low",
        },
        responses=[
            {
                "status_code": 200,
                "description": "Task updated successfully",
                "example": {
                    "id": "task_123",
                    "title": "Updated task title",
                    "status": "completed",
                    "priority": "low",
                    "updated_at": "2024-01-17T09:00:00Z",
                },
            },
            {
                "status_code": 400,
                "description": "Validation error",
                "example": {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Invalid status transition",
                        "details": {"status": "Cannot transition from completed to pending"},
                    }
                },
            },
            {
                "status_code": 401,
                "description": "Unauthorized",
            },
            {
                "status_code": 404,
                "description": "Task not found",
            },
        ],
        tags=["Tasks"],
    )
    endpoints.append(update_task)

    # Delete Task
    delete_task = document_endpoint(
        method="DELETE",
        path="/tasks/{id}",
        summary="Delete a task",
        description="Permanently delete a task. This action cannot be undone. Only the task creator or an admin can delete tasks.",
        parameters=[
            {"name": "id", "type": "string", "required": True,
             "description": "The unique task identifier"},
        ],
        responses=[
            {
                "status_code": 204,
                "description": "Task deleted successfully (no content)",
            },
            {
                "status_code": 401,
                "description": "Unauthorized",
            },
            {
                "status_code": 403,
                "description": "Forbidden - Not authorized to delete this task",
                "example": {
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You don't have permission to delete this task",
                    }
                },
            },
            {
                "status_code": 404,
                "description": "Task not found",
            },
        ],
        tags=["Tasks"],
    )
    endpoints.append(delete_task)

    return endpoints


if __name__ == "__main__":
    from component_documentation.api_docs import generate_api_docs, validate_api_docs
    from component_documentation.models import ApiDocumentation
    from rich.console import Console

    console = Console()
    endpoints = solution()

    docs = ApiDocumentation(
        title="Task Management API",
        description="API for managing tasks",
        base_url="https://api.taskmanager.io/v1",
        version="1.0.0",
        endpoints=endpoints,
        authentication="Bearer token",
    )

    score = validate_api_docs(docs)

    console.print("[bold]Solution 2: Task Management API[/bold]\n")
    console.print(f"Endpoints documented: {len(endpoints)}")
    console.print(f"Score: [green]{score.score}/100[/green]")
