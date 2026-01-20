# CLAUDE.md - Component System

This skill teaches modular component architecture patterns in Python, including lifecycle management, dependency injection, and plugin systems.

## Key Concepts

- **Component**: A self-contained unit with defined lifecycle (init, start, stop)
- **Lifecycle**: The stages a component goes through: created -> initialized -> started -> stopped
- **Registry**: Central manager that tracks, discovers, and orchestrates components
- **Dependency Injection**: Automatic resolution and injection of component dependencies
- **Plugin Pattern**: Dynamic discovery and loading of components at runtime

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run specific example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
component-system/
├── src/component_system/
│   ├── __init__.py
│   ├── component.py      # Base component class
│   ├── lifecycle.py      # Lifecycle enum and manager
│   ├── registry.py       # Component registry
│   ├── requires.py       # Dependency descriptor
│   └── examples/
│       ├── example_1.py  # Basic component
│       ├── example_2.py  # Dependencies
│       └── example_3.py  # Plugin system
├── exercises/
│   ├── exercise_1.py
│   ├── exercise_2.py
│   ├── exercise_3.py
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic Component
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

### Pattern 2: Component with Dependencies
```python
from component_system import Component, Requires

class ServiceComponent(Component):
    database: "DatabaseComponent" = Requires()

    async def start(self) -> None:
        await super().start()
        # database is automatically injected before start
        await self.database.execute("SELECT 1")
```

### Pattern 3: Registry Usage
```python
from component_system import Registry

async def main():
    registry = Registry()
    registry.register(DatabaseComponent)
    registry.register(ServiceComponent)

    await registry.start_all()  # Starts in dependency order

    service = registry.get(ServiceComponent)
    # Use service...

    await registry.stop_all()  # Stops in reverse order
```

## Common Mistakes

1. **Forgetting async/await**
   - All lifecycle methods are async
   - Always await them: `await registry.start_all()`

2. **Circular dependencies**
   - A depends on B, B depends on A = Error
   - Design hierarchy carefully

3. **Missing super() calls**
   - Override lifecycle must call super()
   - `await super().start()` before your logic

4. **Not handling stop() errors**
   - Stop should be resilient
   - Log errors but continue stopping other components

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make example-1` to see a basic component in action.

### "How do dependencies work?"
Explain the `Requires()` descriptor and how the registry resolves dependencies before starting a component.

### "How do I build a plugin system?"
Direct them to example-3 which shows dynamic plugin discovery and registration.

### "Why isn't my component starting?"
Check:
1. Is it registered with the registry?
2. Are all dependencies registered?
3. Is there a circular dependency?
4. Are lifecycle methods properly async?

## Testing Notes

- Tests use pytest with pytest-asyncio for async testing
- Run specific tests: `pytest -k "test_lifecycle"`
- Integration tests marked with `@pytest.mark.integration`

## Dependencies

Key dependencies in pyproject.toml:
- typing-extensions: For advanced type hints
- pytest-asyncio: For testing async components
