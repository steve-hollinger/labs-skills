# Factory Pattern Implementations

## Pattern 1: Simple Factory Function

The simplest form - a function that creates and returns objects.

```python
from typing import Protocol

class Logger(Protocol):
    def log(self, message: str) -> None: ...

class ConsoleLogger:
    def log(self, message: str) -> None:
        print(f"[CONSOLE] {message}")

class FileLogger:
    def __init__(self, filename: str):
        self.filename = filename

    def log(self, message: str) -> None:
        with open(self.filename, "a") as f:
            f.write(f"{message}\n")

def create_logger(
    type: str,
    filename: str | None = None
) -> Logger:
    """Simple factory function."""
    if type == "console":
        return ConsoleLogger()
    elif type == "file":
        if not filename:
            raise ValueError("Filename required for file logger")
        return FileLogger(filename)
    else:
        raise ValueError(f"Unknown logger type: {type}")


# Usage
logger = create_logger("console")
logger.log("Hello")
```

**When to use**: Quick and simple, few types, no need for extensibility.

## Pattern 2: Factory Class

Encapsulates factory logic in a class for better organization.

```python
from dataclasses import dataclass

@dataclass
class LoggerConfig:
    level: str = "INFO"
    format: str = "[{level}] {message}"

class LoggerFactory:
    """Factory class for creating loggers."""

    def __init__(self, default_config: LoggerConfig | None = None):
        self.default_config = default_config or LoggerConfig()

    def create(
        self,
        type: str,
        config: LoggerConfig | None = None
    ) -> Logger:
        cfg = config or self.default_config

        if type == "console":
            return ConsoleLogger(level=cfg.level, format=cfg.format)
        elif type == "file":
            return FileLogger(level=cfg.level, format=cfg.format)
        else:
            raise ValueError(f"Unknown type: {type}")

    def create_console(self) -> Logger:
        """Convenience method for console logger."""
        return self.create("console")

    def create_file(self, filename: str) -> Logger:
        """Convenience method for file logger."""
        logger = self.create("file")
        logger.filename = filename
        return logger


# Usage
factory = LoggerFactory(LoggerConfig(level="DEBUG"))
logger = factory.create("console")
```

**When to use**: More complex creation logic, shared configuration, multiple creation methods.

## Pattern 3: Registry Pattern with Decorator

Allows dynamic registration of factories using decorators.

```python
from typing import TypeVar, Callable, Any

T = TypeVar("T")

class Registry[T]:
    """Generic registry with decorator support."""

    def __init__(self):
        self._factories: dict[str, Callable[..., T]] = {}

    def register(self, name: str) -> Callable[[type[T]], type[T]]:
        """Decorator for registering a class."""
        def decorator(cls: type[T]) -> type[T]:
            self._factories[name] = cls
            return cls
        return decorator

    def register_factory(
        self,
        name: str,
        factory: Callable[..., T]
    ) -> None:
        """Register a factory function directly."""
        self._factories[name] = factory

    def create(self, name: str, **kwargs: Any) -> T:
        """Create an instance by name."""
        if name not in self._factories:
            available = ", ".join(self._factories.keys())
            raise KeyError(f"Unknown '{name}'. Available: {available}")
        return self._factories[name](**kwargs)

    def list_registered(self) -> list[str]:
        """List all registered names."""
        return list(self._factories.keys())


# Usage
notification_registry = Registry()

@notification_registry.register("email")
class EmailNotification:
    def __init__(self, to: str = ""):
        self.to = to

    def send(self, message: str) -> None:
        print(f"Email to {self.to}: {message}")

@notification_registry.register("sms")
class SMSNotification:
    def __init__(self, phone: str = ""):
        self.phone = phone

    def send(self, message: str) -> None:
        print(f"SMS to {self.phone}: {message}")

# Dynamic creation
notif = notification_registry.create("email", to="user@example.com")
notif.send("Hello!")
```

**When to use**: Plugin architectures, extensible systems, config-driven creation.

## Pattern 4: Abstract Factory

Creates families of related objects.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

# Abstract products
class Button(ABC):
    @abstractmethod
    def render(self) -> str: ...

    @abstractmethod
    def on_click(self, handler: Callable) -> None: ...

class Checkbox(ABC):
    @abstractmethod
    def render(self) -> str: ...

    @abstractmethod
    def is_checked(self) -> bool: ...

# Abstract factory
class UIFactory(ABC):
    @abstractmethod
    def create_button(self, label: str) -> Button: ...

    @abstractmethod
    def create_checkbox(self, label: str, checked: bool) -> Checkbox: ...


# Concrete products - Material Design
class MaterialButton(Button):
    def __init__(self, label: str):
        self.label = label
        self._handler = None

    def render(self) -> str:
        return f"<md-button>{self.label}</md-button>"

    def on_click(self, handler: Callable) -> None:
        self._handler = handler

class MaterialCheckbox(Checkbox):
    def __init__(self, label: str, checked: bool):
        self.label = label
        self._checked = checked

    def render(self) -> str:
        state = "checked" if self._checked else ""
        return f"<md-checkbox {state}>{self.label}</md-checkbox>"

    def is_checked(self) -> bool:
        return self._checked


# Concrete products - Bootstrap
class BootstrapButton(Button):
    def __init__(self, label: str):
        self.label = label
        self._handler = None

    def render(self) -> str:
        return f'<button class="btn btn-primary">{self.label}</button>'

    def on_click(self, handler: Callable) -> None:
        self._handler = handler

class BootstrapCheckbox(Checkbox):
    def __init__(self, label: str, checked: bool):
        self.label = label
        self._checked = checked

    def render(self) -> str:
        checked = "checked" if self._checked else ""
        return f'<input type="checkbox" class="form-check" {checked}> {self.label}'

    def is_checked(self) -> bool:
        return self._checked


# Concrete factories
class MaterialUIFactory(UIFactory):
    def create_button(self, label: str) -> Button:
        return MaterialButton(label)

    def create_checkbox(self, label: str, checked: bool = False) -> Checkbox:
        return MaterialCheckbox(label, checked)

class BootstrapUIFactory(UIFactory):
    def create_button(self, label: str) -> Button:
        return BootstrapButton(label)

    def create_checkbox(self, label: str, checked: bool = False) -> Checkbox:
        return BootstrapCheckbox(label, checked)


# Client code - works with any factory
def create_form(factory: UIFactory) -> str:
    button = factory.create_button("Submit")
    checkbox = factory.create_checkbox("Accept terms", False)

    return f"""
    <form>
        {checkbox.render()}
        {button.render()}
    </form>
    """

# Usage
material_form = create_form(MaterialUIFactory())
bootstrap_form = create_form(BootstrapUIFactory())
```

**When to use**: Families of related objects, ensuring consistency, cross-platform code.

## Pattern 5: Factory with Dependency Injection

Integrating factories with DI containers.

```python
from dataclasses import dataclass
from typing import Callable

# Simple DI container
class Container:
    def __init__(self):
        self._services: dict[type, Callable] = {}

    def register(self, service_type: type, factory: Callable) -> None:
        self._services[service_type] = factory

    def resolve[T](self, service_type: type[T]) -> T:
        if service_type not in self._services:
            raise KeyError(f"Service not registered: {service_type}")
        return self._services[service_type]()


# Services and factories
@dataclass
class EmailConfig:
    smtp_server: str
    port: int
    username: str

class EmailService:
    def __init__(self, config: EmailConfig):
        self.config = config

    def send(self, to: str, message: str) -> None:
        print(f"Sending via {self.config.smtp_server} to {to}: {message}")

class EmailServiceFactory:
    def __init__(self, config: EmailConfig):
        self.config = config

    def create(self) -> EmailService:
        return EmailService(self.config)


# Setup
container = Container()
config = EmailConfig("smtp.example.com", 587, "user")
factory = EmailServiceFactory(config)

# Register factory's create method
container.register(EmailService, factory.create)

# Usage
email_service = container.resolve(EmailService)
email_service.send("user@example.com", "Hello!")
```

**When to use**: Complex applications, managing dependencies, lifecycle management.

## Pattern 6: Cached Factory (Singleton-like)

Factory that caches created instances.

```python
from typing import TypeVar, Callable, Any

T = TypeVar("T")

class CachedFactory[T]:
    """Factory that caches instances by key."""

    def __init__(self, creator: Callable[..., T]):
        self._creator = creator
        self._cache: dict[str, T] = {}

    def get_or_create(self, key: str, **kwargs: Any) -> T:
        """Get from cache or create new instance."""
        if key not in self._cache:
            self._cache[key] = self._creator(**kwargs)
        return self._cache[key]

    def clear(self, key: str | None = None) -> None:
        """Clear cache."""
        if key:
            self._cache.pop(key, None)
        else:
            self._cache.clear()


# Usage
def create_db_connection(host: str, port: int = 5432):
    print(f"Creating connection to {host}:{port}")
    return {"host": host, "port": port, "connected": True}

db_factory = CachedFactory(create_db_connection)

# First call creates
conn1 = db_factory.get_or_create("main", host="localhost")
# Second call returns cached
conn2 = db_factory.get_or_create("main", host="localhost")

assert conn1 is conn2  # Same instance
```

**When to use**: Expensive object creation, connection pools, shared resources.

## Go Implementation

```go
package factory

import (
    "fmt"
    "sync"
)

// Notification interface
type Notification interface {
    Send(message string) error
}

// Email notification
type EmailNotification struct {
    To string
}

func (e *EmailNotification) Send(message string) error {
    fmt.Printf("Email to %s: %s\n", e.To, message)
    return nil
}

// SMS notification
type SMSNotification struct {
    Phone string
}

func (s *SMSNotification) Send(message string) error {
    fmt.Printf("SMS to %s: %s\n", s.Phone, message)
    return nil
}

// Factory function type
type NotificationCreator func(opts map[string]string) Notification

// Thread-safe registry
type NotificationRegistry struct {
    mu       sync.RWMutex
    creators map[string]NotificationCreator
}

func NewRegistry() *NotificationRegistry {
    return &NotificationRegistry{
        creators: make(map[string]NotificationCreator),
    }
}

func (r *NotificationRegistry) Register(name string, creator NotificationCreator) {
    r.mu.Lock()
    defer r.mu.Unlock()
    r.creators[name] = creator
}

func (r *NotificationRegistry) Create(name string, opts map[string]string) (Notification, error) {
    r.mu.RLock()
    defer r.mu.RUnlock()

    creator, ok := r.creators[name]
    if !ok {
        return nil, fmt.Errorf("unknown notification type: %s", name)
    }
    return creator(opts), nil
}

// Example usage
func main() {
    registry := NewRegistry()

    registry.Register("email", func(opts map[string]string) Notification {
        return &EmailNotification{To: opts["to"]}
    })

    registry.Register("sms", func(opts map[string]string) Notification {
        return &SMSNotification{Phone: opts["phone"]}
    })

    notif, _ := registry.Create("email", map[string]string{"to": "user@example.com"})
    notif.Send("Hello from Go!")
}
```
