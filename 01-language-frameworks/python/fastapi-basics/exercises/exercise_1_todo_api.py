"""Exercise 1: Build a Todo API

Create a complete CRUD API for managing todo items.

Requirements:
1. Create models:
   - TodoCreate: title (required), description (optional), priority (1-5, default 3)
   - TodoUpdate: all fields optional
   - TodoResponse: id, title, description, priority, completed, created_at, updated_at

2. Implement endpoints:
   - GET /todos/ - List all todos with optional filtering by completed status
   - POST /todos/ - Create a new todo
   - GET /todos/{todo_id} - Get a specific todo
   - PUT /todos/{todo_id} - Full update of a todo
   - PATCH /todos/{todo_id} - Partial update (e.g., mark as completed)
   - DELETE /todos/{todo_id} - Delete a todo

3. Add features:
   - Pagination (skip, limit query params)
   - Filtering by completed status
   - Sorting by priority or created_at
   - Proper HTTP status codes (201 for create, 204 for delete)

Expected behavior:
    # Create a todo
    POST /todos/
    {"title": "Learn FastAPI", "priority": 5}
    -> 201 Created, {"id": 1, "title": "Learn FastAPI", ...}

    # List todos
    GET /todos/?completed=false&sort=priority
    -> 200 OK, [{"id": 1, ...}, ...]

    # Mark as completed
    PATCH /todos/1
    {"completed": true}
    -> 200 OK, {"id": 1, "completed": true, ...}

Hints:
- Use a dictionary to simulate a database
- Use Pydantic models for all request/response types
- Use Query() for pagination and filter parameters
- Remember to set response_model on each endpoint
"""

from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field


# TODO: Define your models here
class TodoCreate(BaseModel):
    """Model for creating a todo."""
    pass


class TodoUpdate(BaseModel):
    """Model for updating a todo (all fields optional)."""
    pass


class TodoResponse(BaseModel):
    """Model for todo responses."""
    pass


# Simulated database
todos_db: dict = {}
next_id = 1


# Create the app
app = FastAPI(title="Todo API")


# TODO: Implement your endpoints here
@app.get("/todos/")
def list_todos():
    """List all todos."""
    pass


@app.post("/todos/", status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate):
    """Create a new todo."""
    pass


# Add more endpoints...


def test_todo_api():
    """Test your Todo API implementation."""
    from fastapi.testclient import TestClient

    client = TestClient(app)

    # Test creating a todo
    response = client.post("/todos/", json={"title": "Test Todo", "priority": 3})
    print(f"Create: {response.status_code}")

    # TODO: Add more tests

    print("\nAll tests passed!")


if __name__ == "__main__":
    test_todo_api()
