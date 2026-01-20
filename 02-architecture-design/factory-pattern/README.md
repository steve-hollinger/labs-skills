# Factory Pattern

Master the factory pattern for dynamic object creation, including abstract factories, registry patterns, and dependency injection integration.

## Learning Objectives

After completing this skill, you will be able to:
- Implement simple factory methods for object creation
- Design abstract factory patterns for family of related objects
- Build registry-based factories for plugin architectures
- Integrate factories with dependency injection containers
- Apply factory patterns in Python and Go

## Prerequisites

- Python 3.11+ or Go 1.21+
- Understanding of OOP concepts
- Basic knowledge of interfaces/protocols

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Core Concepts

### What is the Factory Pattern?

The factory pattern is a creational design pattern that provides an interface for creating objects without specifying their concrete classes. It encapsulates object creation logic, making code more flexible and testable.

### Why Use Factories?

| Benefit | Description |
|---------|-------------|
| **Decoupling** | Client code doesn't depend on concrete implementations |
| **Flexibility** | Easy to add new types without changing existing code |
| **Testability** | Can inject mock factories for testing |
| **Configuration** | Object creation can be driven by configuration |
| **Consistency** | Centralized creation ensures consistent setup |

### Types of Factory Patterns

1. **Simple Factory**: Single function/method that creates objects
2. **Factory Method**: Subclasses decide which class to instantiate
3. **Abstract Factory**: Create families of related objects
4. **Registry Pattern**: Dynamic registration and lookup of factories

## Python Example

### Simple Factory

```python
from abc import ABC, abstractmethod

class Notification(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        pass

class EmailNotification(Notification):
    def send(self, message: str) -> None:
        print(f"Email: {message}")

class SMSNotification(Notification):
    def send(self, message: str) -> None:
        print(f"SMS: {message}")

def create_notification(type: str) -> Notification:
    """Simple factory function."""
    factories = {
        "email": EmailNotification,
        "sms": SMSNotification,
    }
    if type not in factories:
        raise ValueError(f"Unknown notification type: {type}")
    return factories[type]()

# Usage
notification = create_notification("email")
notification.send("Hello!")
```

### Registry Pattern

```python
from typing import Type, TypeVar, Callable

T = TypeVar("T")

class Registry[T]:
    """Generic registry for factories."""

    def __init__(self) -> None:
        self._factories: dict[str, Callable[..., T]] = {}

    def register(self, name: str, factory: Callable[..., T]) -> None:
        self._factories[name] = factory

    def create(self, name: str, **kwargs) -> T:
        if name not in self._factories:
            raise KeyError(f"Unknown type: {name}")
        return self._factories[name](**kwargs)

# Usage
registry = Registry[Notification]()
registry.register("email", EmailNotification)
registry.register("sms", SMSNotification)

notification = registry.create("email")
```

## Go Example

```go
package main

// Notification interface
type Notification interface {
    Send(message string) error
}

// Factory function type
type NotificationFactory func() Notification

// Registry
type NotificationRegistry struct {
    factories map[string]NotificationFactory
}

func NewRegistry() *NotificationRegistry {
    return &NotificationRegistry{
        factories: make(map[string]NotificationFactory),
    }
}

func (r *NotificationRegistry) Register(name string, factory NotificationFactory) {
    r.factories[name] = factory
}

func (r *NotificationRegistry) Create(name string) (Notification, error) {
    factory, ok := r.factories[name]
    if !ok {
        return nil, fmt.Errorf("unknown type: %s", name)
    }
    return factory(), nil
}
```

## Examples

### Example 1: Simple Factory

Demonstrates basic factory function for creating objects based on type.

```bash
make example-1
```

### Example 2: Abstract Factory

Shows creating families of related objects with abstract factory.

```bash
make example-2
```

### Example 3: Registry Pattern

Demonstrates dynamic registration and plugin architectures.

```bash
make example-3
```

### Example 4: Dependency Injection Integration

Shows integrating factories with DI containers.

```bash
make example-4
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Build a Payment Gateway Factory - Create factories for different payment providers
2. **Exercise 2**: Plugin System with Registry - Build an extensible plugin architecture
3. **Exercise 3**: Configuration-Driven Factory - Create objects based on configuration files

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Returning Concrete Types

```python
# Bad: Returning concrete type defeats the purpose
def create_notification(type: str) -> EmailNotification:
    ...

# Good: Return abstract type/protocol
def create_notification(type: str) -> Notification:
    ...
```

### Not Validating Factory Input

```python
# Bad: Crashes with KeyError
def create(type: str):
    return self._factories[type]()

# Good: Meaningful error
def create(type: str):
    if type not in self._factories:
        raise ValueError(f"Unknown type '{type}'. Available: {list(self._factories.keys())}")
    return self._factories[type]()
```

### God Factory

```python
# Bad: One factory creates everything
class UniversalFactory:
    def create_notification(self): ...
    def create_user(self): ...
    def create_database(self): ...
    def create_everything_else(self): ...

# Good: Focused factories
class NotificationFactory: ...
class UserFactory: ...
```

## Pattern Variations

### Factory with Configuration

```python
@dataclass
class NotificationConfig:
    type: str
    retry_count: int = 3
    timeout: float = 30.0

class ConfigurableFactory:
    def create(self, config: NotificationConfig) -> Notification:
        notification = self._create_base(config.type)
        notification.retry_count = config.retry_count
        notification.timeout = config.timeout
        return notification
```

### Factory with Caching (Singleton-like)

```python
class CachedFactory:
    def __init__(self):
        self._cache: dict[str, Notification] = {}

    def get_or_create(self, type: str) -> Notification:
        if type not in self._cache:
            self._cache[type] = self._create(type)
        return self._cache[type]
```

### Async Factory

```python
class AsyncNotificationFactory:
    async def create(self, type: str) -> Notification:
        # Async initialization (e.g., connection setup)
        notification = await self._create_and_connect(type)
        return notification
```

## Further Reading

- [Design Patterns: Elements of Reusable Object-Oriented Software](https://en.wikipedia.org/wiki/Design_Patterns)
- [Python Design Patterns](https://python-patterns.guide/)
- Related skills in this repository:
  - [Dependency Injection](../dependency-injection/)
  - [Plugin Architecture](../plugin-architecture/)
