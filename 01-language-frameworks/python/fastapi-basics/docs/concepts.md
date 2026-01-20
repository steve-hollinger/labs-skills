# Core Concepts

## Overview

FastAPI is a modern, high-performance Python web framework for building APIs. It leverages Python type hints and Pydantic for automatic request validation, serialization, and OpenAPI documentation generation.

## Concept 1: Route Handlers

### What It Is

Route handlers are Python functions decorated with HTTP method decorators (`@app.get`, `@app.post`, etc.) that process incoming requests and return responses.

### Why It Matters

- Maps URLs to Python functions cleanly
- Automatic request parsing based on function signatures
- Type validation for path and query parameters
- Clear, readable API definitions

### How It Works

```python
from fastapi import FastAPI

app = FastAPI()

# GET request with path parameter
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}

# POST request
@app.post("/users/")
def create_user(name: str, email: str):
    return {"name": name, "email": email}

# Query parameters with defaults
@app.get("/items/")
def list_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# Optional query parameters
@app.get("/search/")
def search(q: str | None = None):
    if q:
        return {"results": f"Searching for: {q}"}
    return {"results": "No query provided"}
```

Path parameters are defined in the route path with curly braces. Query parameters are function parameters not in the path. Type hints enable automatic validation.

## Concept 2: Request and Response Models

### What It Is

Pydantic models define the structure and validation rules for request bodies and responses. FastAPI automatically validates incoming data and serializes outgoing data.

### Why It Matters

- Type-safe request handling
- Automatic validation with clear error messages
- Self-documenting API through OpenAPI schema
- Consistent response structures

### How It Works

```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

# Request model
class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(ge=0, le=150)

# Response model
class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}

# Update model (partial)
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

# Using models in endpoints
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate):
    # user is already validated
    db_user = db.create_user(user.model_dump())
    return db_user  # Automatically serialized to UserResponse

@app.patch("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate):
    updates = user.model_dump(exclude_unset=True)
    return db.update_user(user_id, updates)
```

## Concept 3: Dependency Injection

### What It Is

FastAPI's dependency injection system allows you to declare dependencies that are resolved automatically when handling requests. Dependencies can be database connections, authentication, or any shared resource.

### Why It Matters

- Clean separation of concerns
- Reusable components across endpoints
- Easy testing through dependency overrides
- Automatic resource management with generators

### How It Works

```python
from fastapi import Depends, HTTPException

# Simple dependency
def get_db():
    db = Database()
    try:
        yield db  # Generator for cleanup
    finally:
        db.close()

# Dependency with parameters
def get_pagination(skip: int = 0, limit: int = 100):
    return {"skip": skip, "limit": limit}

# Authentication dependency
def get_current_user(token: str = Header(...)):
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

# Using dependencies
@app.get("/items/")
def list_items(
    db = Depends(get_db),
    pagination = Depends(get_pagination),
    user = Depends(get_current_user),
):
    items = db.query(Item).offset(pagination["skip"]).limit(pagination["limit"])
    return items

# Class-based dependencies
class CommonParams:
    def __init__(self, skip: int = 0, limit: int = 100, search: str = ""):
        self.skip = skip
        self.limit = limit
        self.search = search

@app.get("/search/")
def search(params: CommonParams = Depends()):
    return {"skip": params.skip, "limit": params.limit, "search": params.search}
```

## Concept 4: Async Support

### What It Is

FastAPI fully supports async/await syntax, enabling non-blocking I/O operations for better performance under concurrent load.

### Why It Matters

- Handle more concurrent requests
- Better resource utilization
- Required for async databases and HTTP clients
- Improved scalability

### How It Works

```python
import httpx
import asyncio

# Async endpoint
@app.get("/async-data")
async def get_async_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
    return response.json()

# Parallel async operations
@app.get("/dashboard")
async def get_dashboard():
    async with httpx.AsyncClient() as client:
        # Run requests in parallel
        users_task = client.get("https://api.example.com/users")
        orders_task = client.get("https://api.example.com/orders")

        users_response, orders_response = await asyncio.gather(
            users_task, orders_task
        )

    return {
        "users": users_response.json(),
        "orders": orders_response.json(),
    }

# Async database operations
@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## Concept 5: Middleware

### What It Is

Middleware are functions that run before/after every request, enabling cross-cutting concerns like logging, CORS, authentication, and request timing.

### Why It Matters

- Centralized request/response processing
- Separation of concerns
- Consistent behavior across all endpoints
- Easy to add/remove functionality

### How It Works

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()

# Built-in CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://myapp.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware for timing
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Custom middleware for logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"Response: {response.status_code}")
    return response

# Exception handling middleware
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )
```

## Concept 6: OpenAPI Documentation

### What It Is

FastAPI automatically generates OpenAPI (Swagger) documentation from your code, including routes, parameters, request/response models, and examples.

### Why It Matters

- Self-documenting APIs
- Interactive testing interface
- Client code generation
- API contract for frontend developers

### How It Works

```python
from fastapi import FastAPI, Query, Path

app = FastAPI(
    title="My API",
    description="A sample API with automatic documentation",
    version="1.0.0",
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
)

class Item(BaseModel):
    """An item in the store."""
    name: str = Field(..., description="The name of the item", example="Widget")
    price: float = Field(..., gt=0, description="Price in USD", example=9.99)
    description: str | None = Field(None, description="Optional description")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"name": "Widget", "price": 9.99, "description": "A useful widget"}
            ]
        }
    }

@app.post(
    "/items/",
    response_model=Item,
    summary="Create an item",
    description="Create a new item with name and price.",
    response_description="The created item",
    tags=["items"],
)
def create_item(item: Item):
    """
    Create an item with:
    - **name**: required, the item's name
    - **price**: required, must be greater than zero
    - **description**: optional description
    """
    return item

# Access docs at:
# - /docs (Swagger UI)
# - /redoc (ReDoc)
# - /openapi.json (raw schema)
```

## Summary

Key takeaways from these concepts:

1. **Route Handlers** map URLs to Python functions with automatic validation
2. **Request/Response Models** ensure type safety and generate documentation
3. **Dependency Injection** enables clean, testable, reusable code
4. **Async Support** provides better performance for I/O-bound operations
5. **Middleware** handles cross-cutting concerns consistently
6. **OpenAPI Documentation** is generated automatically from your code

Together, these concepts enable you to build production-ready APIs with minimal boilerplate while maintaining type safety and documentation.
