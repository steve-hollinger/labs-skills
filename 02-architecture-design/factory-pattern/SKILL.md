---
name: implementing-factory-patterns
description: This skill teaches the factory pattern for dynamic object creation, including simple factories, abstract factories, registry patterns, and dependency injection integration. Use when building or deploying containerized applications.
---

# Factory Pattern

## Quick Start
```python
from typing import Protocol

class Notification(Protocol):
    def send(self, message: str) -> None: ...

class EmailNotification:
    def send(self, message: str) -> None:
        print(f"Email: {message}")

def create_notification(type: str) -> Notification:
    """Simple factory function."""
    if type == "email":
        return EmailNotification()
    raise ValueError(f"Unknown type: {type}")
```

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run simple factory example
make example-2  # Run abstract factory example
make example-3  # Run registry pattern example
make example-4  # Run DI integration example
```

## Key Points
- Factory Method
- Abstract Factory
- Registry Pattern

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples