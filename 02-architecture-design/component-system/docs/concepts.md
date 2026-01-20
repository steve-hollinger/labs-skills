# Core Concepts

## Overview

Component systems provide a structured approach to building modular, extensible applications. This skill covers the fundamental concepts of component-based architecture: lifecycle management, dependency injection, and plugin patterns.

## Concept 1: Component Lifecycle

### What It Is

The component lifecycle defines the stages a component goes through from creation to destruction. A well-defined lifecycle ensures resources are properly acquired and released, and that components interact predictably.

### Why It Matters

- **Resource Management**: Proper lifecycle management prevents resource leaks
- **Predictable Behavior**: Components behave consistently across the application
- **Error Handling**: Clear stages make error recovery more straightforward
- **Testing**: Lifecycle hooks make components easier to test in isolation

### How It Works

Components progress through four states:

```
CREATED --> INITIALIZED --> STARTED --> STOPPED
                ^                          |
                |__________________________|
                        (restart)
```

```python
from enum import Enum, auto

class Lifecycle(Enum):
    CREATED = auto()      # Instance exists, not configured
    INITIALIZED = auto()  # Configured, dependencies resolved
    STARTED = auto()      # Running, serving requests
    STOPPED = auto()      # Shutdown, resources released

class Component:
    def __init__(self, config: dict | None = None):
        self._state = Lifecycle.CREATED
        self._config = config or {}

    async def initialize(self) -> None:
        """Prepare the component (validate config, resolve deps)."""
        self._state = Lifecycle.INITIALIZED

    async def start(self) -> None:
        """Acquire resources and begin operation."""
        self._state = Lifecycle.STARTED

    async def stop(self) -> None:
        """Release resources and shutdown."""
        self._state = Lifecycle.STOPPED
```

### Best Practices

1. **Always call super()**: When overriding lifecycle methods, call the parent implementation
2. **Validate early**: Validate configuration in `initialize()`, not `start()`
3. **Handle stop errors**: The `stop()` method should be resilient and not raise exceptions
4. **Use state checks**: Only perform operations when in the appropriate state

## Concept 2: Dependency Injection

### What It Is

Dependency Injection (DI) is a pattern where components receive their dependencies from an external source rather than creating them internally. This promotes loose coupling and makes components more testable.

### Why It Matters

- **Testability**: Dependencies can be mocked or stubbed for testing
- **Flexibility**: Dependencies can be swapped without changing component code
- **Reusability**: Components aren't tied to specific implementations
- **Clarity**: Dependencies are explicitly declared, making relationships visible

### How It Works

Dependencies are declared using descriptors and resolved by a registry:

```python
class Requires:
    """Descriptor for declaring dependencies."""

    def __init__(self, optional: bool = False):
        self.optional = optional
        self._name = None

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, obj, objtype):
        if obj is None:
            return self
        return obj._injected_deps.get(self._name)

    def __set__(self, obj, value):
        obj._injected_deps[self._name] = value


class UserService(Component):
    # Declare dependencies
    database: DatabaseComponent = Requires()
    cache: CacheComponent = Requires()

    async def get_user(self, user_id: str) -> User:
        # Dependencies are automatically available
        cached = await self.cache.get(f"user:{user_id}")
        if cached:
            return cached
        return await self.database.query(user_id)
```

The registry handles dependency resolution:

```python
class Registry:
    def _inject_dependencies(self, component: Component):
        deps = get_dependencies(type(component))
        for name, dep_type in deps.items():
            dep_instance = self._components[dep_type]
            setattr(component, name, dep_instance)
```

### Dependency Resolution Order

The registry builds a dependency graph and starts components in topological order:

```
DatabaseComponent (no deps) --> starts first
    |
CacheComponent (no deps) --> can start in parallel
    |
UserService (depends on both) --> starts last
```

## Concept 3: Registry Pattern

### What It Is

A registry is a central manager that tracks components, resolves dependencies, and orchestrates lifecycle operations. It acts as a service locator that components can use to find each other.

### Why It Matters

- **Centralized Management**: Single point for component lifecycle control
- **Dependency Resolution**: Automatically resolves component dependencies
- **Discovery**: Components can be found by type or name
- **Ordering**: Ensures correct startup and shutdown order

### How It Works

```python
class Registry:
    def __init__(self):
        self._components: dict[type, Component] = {}
        self._start_order: list[type] = []

    def register(self, cls: type[Component], config: dict = None):
        """Register a component class."""
        instance = cls(config)
        self._components[cls] = instance

    def get(self, cls: type[T]) -> T:
        """Get a component by its class."""
        return self._components[cls]

    async def start_all(self):
        """Start all components in dependency order."""
        self._start_order = self._resolve_dependencies()
        for cls in self._start_order:
            component = self._components[cls]
            self._inject_dependencies(component)
            await component.initialize()
            await component.start()

    async def stop_all(self):
        """Stop all components in reverse order."""
        for cls in reversed(self._start_order):
            await self._components[cls].stop()
```

## Concept 4: Plugin Architecture

### What It Is

A plugin architecture allows extending an application's functionality through dynamically loaded modules. Plugins implement a common interface and can be discovered and loaded at runtime.

### Why It Matters

- **Extensibility**: Add features without modifying core code
- **Customization**: Users can add their own functionality
- **Modularity**: Features can be enabled/disabled independently
- **Updates**: Plugins can be updated separately from the core

### How It Works

Plugins implement a common interface:

```python
class PluginInterface(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def version(self) -> str: ...

    @abstractmethod
    async def process(self, data: dict) -> dict: ...
```

A plugin registry manages discovery and registration:

```python
class PluginRegistry:
    _plugins: dict[str, type[Plugin]] = {}

    @classmethod
    def register(cls, plugin_class):
        """Decorator for registering plugins."""
        cls._plugins[plugin_class.plugin_id] = plugin_class
        return plugin_class

    @classmethod
    def create(cls, plugin_id: str, config: dict = None):
        """Create a plugin instance by ID."""
        return cls._plugins[plugin_id](config)
```

Plugins can be loaded from files:

```python
def load_plugin_from_file(filepath: Path) -> Plugin:
    spec = importlib.util.spec_from_file_location("plugin", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    for attr in dir(module):
        obj = getattr(module, attr)
        if isinstance(obj, type) and issubclass(obj, PluginInterface):
            return obj()
```

## Summary

Key takeaways from these concepts:

1. **Lifecycle Management**: Components have predictable stages (created, initialized, started, stopped) that ensure proper resource handling

2. **Dependency Injection**: Dependencies are declared explicitly and injected automatically, promoting loose coupling and testability

3. **Registry Pattern**: A central registry manages component registration, dependency resolution, and lifecycle orchestration

4. **Plugin Architecture**: Extensibility through common interfaces and dynamic loading allows applications to grow without core changes

These patterns work together to create maintainable, extensible applications where components are loosely coupled, easily testable, and follow predictable behavior patterns.
