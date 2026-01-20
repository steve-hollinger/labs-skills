# Component System

Learn to build modular, extensible component architectures in Python. This skill teaches the patterns used in modern frameworks, plugin systems, and microservice architectures.

## Learning Objectives

After completing this skill, you will be able to:
- Design and implement component-based architectures
- Manage component lifecycle (initialization, startup, shutdown)
- Handle component dependencies and dependency injection
- Build plugin systems with dynamic registration and discovery
- Create extensible applications using composition

## Prerequisites

- Python 3.11+
- UV package manager
- Basic understanding of Python classes and decorators
- Familiarity with type hints

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Concepts

### Component Lifecycle

Components follow a predictable lifecycle: creation, initialization, startup, running, shutdown, and cleanup. Understanding this lifecycle is crucial for managing resources properly.

```python
from component_system import Component, Lifecycle

class DatabaseComponent(Component):
    async def initialize(self) -> None:
        """Prepare configuration, validate settings."""
        self.pool = None

    async def start(self) -> None:
        """Acquire resources, establish connections."""
        self.pool = await create_pool(self.config.db_url)

    async def stop(self) -> None:
        """Release resources, close connections."""
        if self.pool:
            await self.pool.close()
```

### Dependency Injection

Components can declare dependencies on other components. The system resolves these dependencies automatically, ensuring proper initialization order.

```python
from component_system import Component, Requires

class UserService(Component):
    database: DatabaseComponent = Requires()
    cache: CacheComponent = Requires()

    async def get_user(self, user_id: str) -> User:
        # Dependencies are automatically injected and available
        cached = await self.cache.get(f"user:{user_id}")
        if cached:
            return cached
        return await self.database.query_user(user_id)
```

### Component Registry

The registry tracks all components, manages their lifecycle, and provides discovery capabilities.

```python
from component_system import Registry

registry = Registry()

# Register components
registry.register(DatabaseComponent)
registry.register(CacheComponent)
registry.register(UserService)

# Start all components in dependency order
await registry.start_all()

# Access components by type
db = registry.get(DatabaseComponent)
```

## Examples

### Example 1: Basic Component

This example demonstrates creating a simple component with lifecycle hooks.

```bash
make example-1
```

### Example 2: Component Dependencies

Building components that depend on other components with automatic injection.

```bash
make example-2
```

### Example 3: Plugin System

Creating an extensible plugin system where plugins are discovered and loaded dynamically.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Create a simple logging component with proper lifecycle management
2. **Exercise 2**: Build a component with multiple dependencies and proper error handling
3. **Exercise 3**: Implement a plugin discovery system that loads plugins from a directory

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Forgetting to Call Parent Lifecycle Methods
When overriding lifecycle methods, always call the parent implementation:
```python
async def start(self) -> None:
    await super().start()  # Don't forget this!
    # Your startup logic
```

### Circular Dependencies
Components cannot depend on each other circularly. Design your component hierarchy to avoid cycles.

### Not Handling Shutdown Errors
Shutdown should continue even if one component fails:
```python
async def stop(self) -> None:
    try:
        await self.resource.close()
    except Exception as e:
        self.logger.error(f"Shutdown error: {e}")
        # Continue shutdown, don't re-raise
```

## Further Reading

- [Official Documentation](https://docs.python.org/3/library/abc.html) - Abstract Base Classes
- Related skills in this repository:
  - [Tool Registry](../tool-registry/) - Dynamic tool management patterns
  - [Dependency Injection](../dependency-injection/) - DI patterns in depth
