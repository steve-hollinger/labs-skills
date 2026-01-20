"""Solution for Exercise 1: Build a Todo API

This is the reference solution for the Todo API exercise.
"""

from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field


# Models
class TodoCreate(BaseModel):
    """Model for creating a todo."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    priority: int = Field(default=3, ge=1, le=5)


class TodoUpdate(BaseModel):
    """Model for updating a todo (all fields optional)."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    priority: int | None = Field(None, ge=1, le=5)
    completed: bool | None = None


class TodoResponse(BaseModel):
    """Model for todo responses."""

    id: int
    title: str
    description: str | None
    priority: int
    completed: bool
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class TodoListResponse(BaseModel):
    """Paginated list of todos."""

    items: list[TodoResponse]
    total: int
    skip: int
    limit: int


# Simulated database
todos_db: dict[int, dict] = {}
next_id = 1


# Create the app
app = FastAPI(
    title="Todo API",
    description="A complete CRUD API for managing todos",
    version="1.0.0",
)


@app.get("/todos/", response_model=TodoListResponse)
def list_todos(
    skip: int = Query(0, ge=0, description="Items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max items to return"),
    completed: bool | None = Query(None, description="Filter by completed status"),
    sort: Literal["priority", "created_at", "-priority", "-created_at"] = Query(
        "created_at", description="Sort field (prefix with - for descending)"
    ),
):
    """List all todos with filtering, sorting, and pagination."""
    items = list(todos_db.values())

    # Filter by completed status
    if completed is not None:
        items = [t for t in items if t["completed"] == completed]

    # Sort
    reverse = sort.startswith("-")
    sort_field = sort.lstrip("-")
    items.sort(key=lambda x: x[sort_field], reverse=reverse)

    total = len(items)

    # Paginate
    items = items[skip : skip + limit]

    return TodoListResponse(items=items, total=total, skip=skip, limit=limit)


@app.post("/todos/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate):
    """Create a new todo."""
    global next_id

    new_todo = {
        "id": next_id,
        **todo.model_dump(),
        "completed": False,
        "created_at": datetime.now(),
        "updated_at": None,
    }
    todos_db[next_id] = new_todo
    next_id += 1

    return new_todo


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    """Get a specific todo by ID."""
    if todo_id not in todos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} not found",
        )
    return todos_db[todo_id]


@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoCreate):
    """Fully update a todo (all fields required)."""
    if todo_id not in todos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} not found",
        )

    existing = todos_db[todo_id]
    updated = {
        **existing,
        **todo.model_dump(),
        "updated_at": datetime.now(),
    }
    todos_db[todo_id] = updated
    return updated


@app.patch("/todos/{todo_id}", response_model=TodoResponse)
def partial_update_todo(todo_id: int, todo: TodoUpdate):
    """Partially update a todo (only provided fields)."""
    if todo_id not in todos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} not found",
        )

    existing = todos_db[todo_id]
    update_data = todo.model_dump(exclude_unset=True)

    updated = {
        **existing,
        **update_data,
        "updated_at": datetime.now(),
    }
    todos_db[todo_id] = updated
    return updated


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int):
    """Delete a todo."""
    if todo_id not in todos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} not found",
        )
    del todos_db[todo_id]


def test_todo_api():
    """Test the Todo API implementation."""
    global todos_db, next_id
    todos_db = {}
    next_id = 1

    client = TestClient(app)
    print("Testing Todo API...")

    # Test 1: Create a todo
    response = client.post(
        "/todos/",
        json={"title": "Learn FastAPI", "description": "Complete the tutorial", "priority": 5},
    )
    assert response.status_code == 201
    todo1 = response.json()
    assert todo1["id"] == 1
    assert todo1["title"] == "Learn FastAPI"
    assert todo1["completed"] is False
    print("  Test 1 passed: Create todo")

    # Test 2: Create another todo
    response = client.post("/todos/", json={"title": "Write tests", "priority": 3})
    assert response.status_code == 201
    todo2 = response.json()
    assert todo2["id"] == 2
    print("  Test 2 passed: Create second todo")

    # Test 3: List todos
    response = client.get("/todos/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    print("  Test 3 passed: List todos")

    # Test 4: Filter by completed
    response = client.get("/todos/?completed=false")
    assert response.status_code == 200
    assert response.json()["total"] == 2
    print("  Test 4 passed: Filter by completed")

    # Test 5: Get single todo
    response = client.get("/todos/1")
    assert response.status_code == 200
    assert response.json()["title"] == "Learn FastAPI"
    print("  Test 5 passed: Get single todo")

    # Test 6: Get non-existent todo
    response = client.get("/todos/999")
    assert response.status_code == 404
    print("  Test 6 passed: 404 for non-existent todo")

    # Test 7: Partial update (mark as completed)
    response = client.patch("/todos/1", json={"completed": True})
    assert response.status_code == 200
    assert response.json()["completed"] is True
    assert response.json()["title"] == "Learn FastAPI"  # Unchanged
    print("  Test 7 passed: Partial update")

    # Test 8: Full update
    response = client.put(
        "/todos/2",
        json={"title": "Write more tests", "description": "Updated", "priority": 4},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Write more tests"
    print("  Test 8 passed: Full update")

    # Test 9: Sort by priority
    response = client.get("/todos/?sort=-priority")
    assert response.status_code == 200
    items = response.json()["items"]
    assert items[0]["priority"] >= items[1]["priority"]
    print("  Test 9 passed: Sort by priority")

    # Test 10: Pagination
    response = client.get("/todos/?skip=1&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["total"] == 2
    print("  Test 10 passed: Pagination")

    # Test 11: Delete todo
    response = client.delete("/todos/1")
    assert response.status_code == 204
    response = client.get("/todos/1")
    assert response.status_code == 404
    print("  Test 11 passed: Delete todo")

    # Test 12: Validation - priority out of range
    response = client.post("/todos/", json={"title": "Invalid", "priority": 10})
    assert response.status_code == 422
    print("  Test 12 passed: Validation error for invalid priority")

    print("\nAll tests passed!")


if __name__ == "__main__":
    test_todo_api()
