# CLAUDE.md - Factory Pattern

This skill teaches the factory pattern for dynamic object creation, including simple factories, abstract factories, registry patterns, and dependency injection integration.

## Key Concepts

- **Factory Method**: Method that returns instances of a class/interface
- **Abstract Factory**: Creates families of related objects without specifying concrete classes
- **Registry Pattern**: Dynamic registration and lookup of factories by name/key
- **Factory Function**: Standalone function (not method) that creates objects
- **Dependency Injection**: Using factories to inject dependencies at runtime
- **Configuration-Driven Creation**: Creating objects based on external configuration

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run simple factory example
make example-2  # Run abstract factory example
make example-3  # Run registry pattern example
make example-4  # Run DI integration example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
factory-pattern/
├── src/factory_pattern/
│   ├── __init__.py
│   ├── simple.py          # Simple factory patterns
│   ├── abstract.py        # Abstract factory patterns
│   ├── registry.py        # Registry-based factories
│   ├── di.py              # Dependency injection integration
│   └── examples/
│       ├── example_1_simple_factory.py
│       ├── example_2_abstract_factory.py
│       ├── example_3_registry.py
│       └── example_4_di_integration.py
├── cmd/                   # Go examples
│   ├── example1/
│   └── example2/
├── exercises/
│   ├── exercise_1_payment.py
│   ├── exercise_2_plugins.py
│   ├── exercise_3_config.py
│   └── solutions/
├── tests/
│   ├── test_simple.py
│   ├── test_registry.py
│   └── test_abstract.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Simple Factory Function
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

### Pattern 2: Factory Class with Registration
```python
from typing import TypeVar, Callable

T = TypeVar("T")

class Factory[T]:
    def __init__(self):
        self._creators: dict[str, Callable[..., T]] = {}

    def register(self, name: str) -> Callable:
        """Decorator for registration."""
        def wrapper(cls: type[T]) -> type[T]:
            self._creators[name] = cls
            return cls
        return wrapper

    def create(self, name: str, **kwargs) -> T:
        return self._creators[name](**kwargs)

# Usage
factory = Factory[Notification]()

@factory.register("email")
class EmailNotification:
    def send(self, message: str) -> None:
        print(f"Email: {message}")
```

### Pattern 3: Abstract Factory
```python
from abc import ABC, abstractmethod

class UIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button: ...

    @abstractmethod
    def create_checkbox(self) -> Checkbox: ...

class MacUIFactory(UIFactory):
    def create_button(self) -> Button:
        return MacButton()

    def create_checkbox(self) -> Checkbox:
        return MacCheckbox()

class WindowsUIFactory(UIFactory):
    def create_button(self) -> Button:
        return WindowsButton()

    def create_checkbox(self) -> Checkbox:
        return WindowsCheckbox()
```

### Pattern 4: Registry with Metadata
```python
@dataclass
class FactoryEntry[T]:
    factory: Callable[..., T]
    metadata: dict[str, Any]

class Registry[T]:
    def __init__(self):
        self._entries: dict[str, FactoryEntry[T]] = {}

    def register(
        self,
        name: str,
        factory: Callable[..., T],
        **metadata
    ) -> None:
        self._entries[name] = FactoryEntry(factory, metadata)

    def get_by_metadata(self, **criteria) -> list[str]:
        """Find factories matching metadata criteria."""
        return [
            name for name, entry in self._entries.items()
            if all(entry.metadata.get(k) == v for k, v in criteria.items())
        ]
```

## Go Patterns

### Simple Factory in Go
```go
type Notification interface {
    Send(message string) error
}

type NotificationFactory func(config Config) (Notification, error)

var factories = map[string]NotificationFactory{
    "email": NewEmailNotification,
    "sms":   NewSMSNotification,
}

func Create(notifType string, config Config) (Notification, error) {
    factory, ok := factories[notifType]
    if !ok {
        return nil, fmt.Errorf("unknown type: %s", notifType)
    }
    return factory(config)
}
```

### Registry in Go
```go
type Registry struct {
    mu       sync.RWMutex
    creators map[string]Creator
}

func (r *Registry) Register(name string, creator Creator) {
    r.mu.Lock()
    defer r.mu.Unlock()
    r.creators[name] = creator
}

func (r *Registry) Create(name string) (interface{}, error) {
    r.mu.RLock()
    defer r.mu.RUnlock()

    creator, ok := r.creators[name]
    if !ok {
        return nil, fmt.Errorf("not found: %s", name)
    }
    return creator()
}
```

## Common Mistakes

1. **Returning concrete types**
   - Factory should return interface/protocol, not concrete class
   - Allows for substitution and testing

2. **Forgetting thread safety in registries**
   - Go: Use sync.RWMutex
   - Python: Consider threading.Lock for concurrent access

3. **Hardcoding factory logic**
   - Use registry pattern for extensibility
   - Allow external registration

4. **Not validating inputs**
   - Always check if type exists before creating
   - Provide helpful error messages

5. **God factories**
   - Keep factories focused on one type family
   - Split large factories into domain-specific ones

## When Users Ask About...

### "When should I use a factory?"
- Object creation is complex (many parameters, setup steps)
- You need to decouple client from concrete implementations
- Object type is determined at runtime
- You want to centralize creation logic

### "Factory vs constructor?"
- Constructor: Simple creation, type known at compile time
- Factory: Complex creation, type determined at runtime, need abstraction

### "Factory vs dependency injection?"
- Factories create objects, DI containers manage lifecycle and injection
- Factories can be used within DI containers
- Use together: DI container injects factory, factory creates objects

### "How do I test code using factories?"
```python
# Inject factory dependency
class Service:
    def __init__(self, factory: NotificationFactory):
        self.factory = factory

# In tests, inject mock factory
mock_factory = Mock()
mock_factory.create.return_value = MockNotification()
service = Service(mock_factory)
```

## Testing Notes

- Test factory creates correct types
- Test error handling for unknown types
- Test with mock factories for dependent code
- Test registry registration and lookup
- Test thread safety if applicable

## Dependencies

Python:
- No external dependencies for basic patterns
- pytest>=8.0.0 for testing

Go:
- Standard library only
- testify for assertions (optional)
