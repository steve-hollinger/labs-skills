# CLAUDE.md - FastAPI Basics

This skill teaches building modern web APIs with FastAPI, the high-performance Python framework with automatic validation, documentation, and async support.

## Key Concepts

- **Route Handlers**: Decorated functions that handle HTTP requests
- **Path Parameters**: Dynamic URL segments with type validation
- **Query Parameters**: URL query string parameters with defaults
- **Request Bodies**: Pydantic models for JSON request validation
- **Response Models**: Type-safe API responses with automatic serialization
- **Dependency Injection**: Clean, testable code with `Depends`
- **Async Support**: Non-blocking I/O with async/await
- **Middleware**: Cross-cutting concerns like logging and CORS

## Common Commands

```bash
make setup      # Install dependencies with UV
make serve      # Run development server with auto-reload
make examples   # Run all examples
make example-1  # Run basic routes example
make example-2  # Run request/response models example
make example-3  # Run dependency injection example
make example-4  # Run async and middleware example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
fastapi-basics/
├── src/fastapi_basics/
│   ├── __init__.py
│   └── examples/
│       ├── example_1_basic_routes.py
│       ├── example_2_models.py
│       ├── example_3_dependencies.py
│       └── example_4_async_middleware.py
├── exercises/
│   ├── exercise_1_todo_api.py
│   ├── exercise_2_auth.py
│   ├── exercise_3_files.py
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic Route Handler
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id}
```

### Pattern 2: Request/Response with Pydantic
```python
from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str
    price: float

class ItemResponse(BaseModel):
    id: int
    name: str
    price: float

@app.post("/items/", response_model=ItemResponse)
def create_item(item: ItemCreate):
    return {"id": 1, **item.model_dump()}
```

### Pattern 3: Dependency Injection
```python
from fastapi import Depends

def get_current_user(token: str = Header(...)):
    return verify_token(token)

@app.get("/me")
def get_me(user = Depends(get_current_user)):
    return user
```

### Pattern 4: Async Endpoint
```python
@app.get("/async-data")
async def get_async_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
    return response.json()
```

## Common Mistakes

1. **Blocking in async endpoints**
   - Don't use `requests` library in async endpoints
   - Use `httpx` or `aiohttp` for async HTTP calls
   - Use `asyncio.to_thread()` for CPU-bound work

2. **Not using response_model**
   - Always specify `response_model` for type safety
   - It also documents the API in OpenAPI schema

3. **Incorrect exception handling**
   - Use `HTTPException` for HTTP errors
   - Don't catch exceptions and return regular dicts

4. **Dependency scope confusion**
   - Regular `Depends` creates per-request instances
   - Use `lru_cache` for singleton dependencies

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make serve` and the README.md. Start with example_1 for basics.

### "How do I test my endpoints?"
FastAPI provides TestClient:
```python
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.get("/items/1")
```

### "How do I add authentication?"
Use OAuth2PasswordBearer for token-based auth:
```python
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```

### "How do I handle file uploads?"
Use `UploadFile`:
```python
from fastapi import UploadFile, File

@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
    return {"filename": file.filename}
```

### "How do I add CORS?"
Use CORSMiddleware:
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

### "How do I customize OpenAPI docs?"
Configure in FastAPI constructor:
```python
app = FastAPI(
    title="My API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
```

## Testing Notes

- Tests use pytest with pytest-asyncio for async tests
- Use `TestClient` for synchronous-style testing
- Use `httpx.AsyncClient` for async testing
- Run specific tests: `pytest -k "test_name"`
- Check coverage: `make coverage`

## Dependencies

Key dependencies in pyproject.toml:
- fastapi>=0.109.0: Web framework
- uvicorn[standard]: ASGI server
- pydantic>=2.5.0: Data validation
- httpx: Async HTTP client for testing
- pytest: Testing framework
