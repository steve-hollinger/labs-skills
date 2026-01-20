"""Solution for Exercise 1: Write a CLAUDE.md for a Flask API

This is the reference solution demonstrating a well-structured CLAUDE.md
for a Flask todo list API.
"""


def solution() -> str:
    """Reference solution for Exercise 1.

    Returns:
        Complete CLAUDE.md content for the Flask Todo API.
    """
    return '''# CLAUDE.md - Todo List API

A Flask-based REST API for managing personal todo lists with user authentication.

## Overview

This service provides:
- User registration and JWT-based authentication
- CRUD operations for todo items
- Todo filtering by status (pending, completed)
- PostgreSQL storage with SQLAlchemy ORM

All endpoints return JSON. Authentication required for `/todos/*` routes.

## Key Commands

```bash
# Development Setup
make setup              # Create venv and install dependencies
make db-start           # Start PostgreSQL in Docker
make db-migrate         # Run database migrations
make dev                # Start Flask dev server on port 5000

# Testing
make test               # Run all tests with coverage
make test-unit          # Run unit tests only
make test-auth          # Run authentication tests
pytest -k "test_create" # Run specific tests

# Code Quality
make lint               # Run flake8 + mypy
make format             # Format with black + isort

# Database
make db-reset           # Drop and recreate database
make db-seed            # Populate with test data
flask db migrate -m "description"  # Create new migration
```

## Project Structure

```
app/
├── __init__.py          # Flask app factory
├── config.py            # Configuration classes
├── models/
│   ├── user.py          # User model with password hashing
│   └── todo.py          # Todo model with status enum
├── routes/
│   ├── auth.py          # /auth/* endpoints
│   └── todos.py         # /todos/* endpoints (protected)
└── services/
    └── todo_service.py  # Business logic layer

tests/
├── conftest.py          # Fixtures: app, client, auth_headers
├── test_auth.py         # Auth endpoint tests
└── test_todos.py        # Todo CRUD tests
```

## Architecture Decisions

### Why Flask over FastAPI?
- Team has existing Flask expertise
- Simpler for synchronous workloads
- Extensive ecosystem of extensions

### Repository Pattern (Not Used)
We use services directly accessing models. For this simple app,
a repository layer would be over-engineering.

### JWT in Headers (Not Cookies)
- Stateless authentication
- Easier for API clients
- Token in `Authorization: Bearer <token>`

## Code Patterns

### Route Definition
```python
from flask import Blueprint, request, jsonify
from app.services.todo_service import TodoService

todos_bp = Blueprint("todos", __name__)

@todos_bp.route("/todos", methods=["GET"])
@jwt_required()
def list_todos():
    user_id = get_jwt_identity()
    todos = TodoService.get_user_todos(user_id)
    return jsonify([t.to_dict() for t in todos])
```

### Model Definition
```python
from app import db

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def to_dict(self):
        return {"id": self.id, "title": self.title, "completed": self.completed}
```

### Service Layer
```python
class TodoService:
    @staticmethod
    def create_todo(user_id: int, title: str) -> Todo:
        todo = Todo(title=title, user_id=user_id)
        db.session.add(todo)
        db.session.commit()
        return todo
```

### Error Handling
```python
from flask import jsonify

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "not_found", "message": str(error)}), 404

# In routes - use abort with description
from flask import abort
abort(404, description=f"Todo {todo_id} not found")
```

### Test Fixtures (conftest.py)
```python
import pytest
from app import create_app, db

@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def auth_headers(client):
    # Register and login to get token
    client.post("/auth/register", json={"email": "test@example.com", "password": "password123"})
    response = client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})
    token = response.json["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

## Common Mistakes

1. **Not using `@jwt_required()` on protected routes**
   - All `/todos/*` routes need this decorator
   - Forgetting allows unauthenticated access

2. **Committing inside loops**
   ```python
   # Bad - N commits
   for item in items:
       db.session.add(Todo(title=item))
       db.session.commit()

   # Good - 1 commit
   for item in items:
       db.session.add(Todo(title=item))
   db.session.commit()
   ```

3. **Not handling IntegrityError on duplicate emails**
   ```python
   from sqlalchemy.exc import IntegrityError

   try:
       db.session.commit()
   except IntegrityError:
       db.session.rollback()
       abort(409, description="Email already registered")
   ```

4. **Returning model objects directly**
   - Always call `.to_dict()` before `jsonify()`
   - Models are not JSON-serializable

## When Users Ask About...

### "How do I add a new field to Todo?"
1. Add column to `app/models/todo.py`
2. Create migration: `flask db migrate -m "Add field to todo"`
3. Apply migration: `flask db upgrade`
4. Update `to_dict()` method
5. Add tests for new field

### "How do I test authenticated endpoints?"
Use the `auth_headers` fixture:
```python
def test_create_todo(client, auth_headers):
    response = client.post(
        "/todos",
        json={"title": "Test todo"},
        headers=auth_headers
    )
    assert response.status_code == 201
```

### "Why is my token invalid?"
- Token expired (default 24h) - login again
- Wrong header format - must be `Bearer <token>`
- Token from different environment - check JWT_SECRET_KEY

### "How do I debug a failing request?"
```python
# Add to route temporarily
import logging
logging.debug(f"Request data: {request.json}")
logging.debug(f"User ID: {get_jwt_identity()}")
```
Or run with `FLASK_DEBUG=1 make dev`

## Testing Notes

- Tests use SQLite in-memory for speed
- Each test gets fresh database (fixtures handle setup/teardown)
- `auth_headers` fixture creates test user automatically
- Use `client.get(..., headers=auth_headers)` for protected routes

## Dependencies

Key packages in requirements.txt:
- Flask: Web framework
- Flask-SQLAlchemy: ORM integration
- Flask-JWT-Extended: JWT authentication
- Flask-Migrate: Database migrations (Alembic wrapper)
- psycopg2-binary: PostgreSQL driver
- pytest-flask: Testing utilities
'''


if __name__ == "__main__":
    from claude_md_standards.validator import validate_claude_md
    from rich.console import Console

    console = Console()
    content = solution()

    result = validate_claude_md(content)

    console.print(f"[bold]Solution Validation:[/bold]")
    console.print(f"Score: [green]{result.score}/100[/green]")
    console.print(f"Valid: [green]{result.is_valid}[/green]")

    if result.issues:
        console.print("\n[yellow]Minor issues (acceptable in solution):[/yellow]")
        for issue in result.issues:
            console.print(f"  - {issue}")
