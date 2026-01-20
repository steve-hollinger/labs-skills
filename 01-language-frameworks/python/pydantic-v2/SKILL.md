---
name: validating-with-pydantic
description: This skill teaches data validation, serialization, and settings management using Pydantic v2, the most widely-used data validation library for Python. Use when writing or improving tests.
---

# Pydantic V2

## Quick Start
```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=0, le=150)
    email: str
```

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run basic models example
make example-2  # Run validators example
make example-3  # Run serialization example
make example-4  # Run composition example
```

## Key Points
- BaseModel
- Field Types
- Validators

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples