---
name: building-component-systems
description: This skill teaches modular component architecture patterns in Python, including lifecycle management, dependency injection, and plugin systems. Use when writing or improving tests.
---

# Component System

## Quick Start
```python
from component_system import Component

class MyComponent(Component):
    name = "my-component"

    async def start(self) -> None:
        await super().start()
        print(f"{self.name} started")

    async def stop(self) -> None:
        print(f"{self.name} stopping")
        await super().stop()
```

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run specific example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Key Points
- Component
- Lifecycle
- Registry

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples