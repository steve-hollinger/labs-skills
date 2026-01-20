---
name: building-fastapi-services
description: Building modern web APIs with FastAPI, the high-performance Python framework with automatic validation, documentation, and async support. Use when implementing authentication or verifying tokens.
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


## Key Points
- Route Handlers
- Path Parameters
- Query Parameters

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples