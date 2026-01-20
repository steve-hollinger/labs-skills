---
name: building-fastapi-services
description: This skill teaches building modern web APIs with FastAPI, the high-performance Python framework with automatic validation, documentation, and async support. Use when implementing authentication or verifying tokens.
---

# Fastapi Basics

## Quick Start
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id}
```

## Commands
```bash
make setup      # Install dependencies with UV
make serve      # Run development server with auto-reload
make examples   # Run all examples
make example-1  # Run basic routes example
make example-2  # Run request/response models example
make example-3  # Run dependency injection example
```

## Key Points
- Route Handlers
- Path Parameters
- Query Parameters

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples