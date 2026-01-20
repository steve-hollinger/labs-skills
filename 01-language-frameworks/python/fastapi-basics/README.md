# FastAPI Basics

Master FastAPI - the modern, high-performance Python web framework for building APIs with automatic OpenAPI documentation, type validation, and async support.

## Learning Objectives

After completing this skill, you will be able to:
- Create RESTful API endpoints with FastAPI
- Use Pydantic models for request/response validation
- Implement dependency injection for shared resources
- Build async endpoints for better performance
- Add middleware for cross-cutting concerns
- Generate and customize OpenAPI documentation

## Prerequisites

- Python 3.11+
- UV package manager
- Basic understanding of HTTP and REST APIs
- Familiarity with Pydantic (see [pydantic-v2](../pydantic-v2/) skill)

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run the development server
make serve

# Run tests
make test
```

## Concepts

### Route Handlers

FastAPI uses Python decorators to define routes with automatic request parsing.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "query": q}
```

### Request/Response Models

Pydantic models define request bodies and response schemas with automatic validation.

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    description: str | None = None

@app.post("/items/", response_model=Item)
def create_item(item: Item):
    return item
```

### Dependency Injection

FastAPI's `Depends` system enables clean, testable code.

```python
from fastapi import Depends

def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}")
def get_user(user_id: int, db = Depends(get_db)):
    return db.get_user(user_id)
```

## Examples

### Example 1: Basic Routes

This example demonstrates creating simple GET and POST routes.

```bash
make example-1
```

### Example 2: Request/Response Models

Working with Pydantic models for type-safe APIs.

```bash
make example-2
```

### Example 3: Dependency Injection

Implementing dependencies for database connections and shared resources.

```bash
make example-3
```

### Example 4: Async and Middleware

Async endpoints and middleware for logging, CORS, and more.

```bash
make example-4
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Build a Todo API - Create CRUD endpoints for a todo list
2. **Exercise 2**: User Authentication - Implement JWT-based authentication
3. **Exercise 3**: File Upload API - Handle file uploads with validation

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Mixing Sync and Async

Don't call blocking functions in async endpoints:

```python
# Bad - blocks the event loop
@app.get("/data")
async def get_data():
    result = requests.get(url)  # Blocking!
    return result.json()

# Good - use async libraries
@app.get("/data")
async def get_data():
    async with httpx.AsyncClient() as client:
        result = await client.get(url)
    return result.json()
```

### Forgetting Response Models

Always define response_model for consistent API responses:

```python
# Good - documents and validates response
@app.get("/items/{id}", response_model=ItemResponse)
def get_item(id: int):
    return get_item_from_db(id)
```

### Not Using HTTPException

Use FastAPI's HTTPException for proper error responses:

```python
from fastapi import HTTPException

@app.get("/items/{id}")
def get_item(id: int):
    item = db.get(id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

## Further Reading

- [Official FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI GitHub](https://github.com/tiangolo/fastapi)
- Related skills in this repository:
  - [Pydantic v2](../pydantic-v2/) - Foundation for FastAPI models
  - [Dynaconf Config](../dynaconf-config/) - Configuration management
