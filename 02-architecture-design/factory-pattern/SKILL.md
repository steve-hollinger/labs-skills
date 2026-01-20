---
name: implementing-factory-patterns
description: The factory pattern for dynamic object creation, including simple factories, abstract factories, registry patterns, and dependency injection integration. Use when building or deploying containerized applications.
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


## Key Points
- Factory Method
- Abstract Factory
- Registry Pattern

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples