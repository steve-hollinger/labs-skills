# Factory Pattern Concepts

## Overview

The Factory Pattern is a creational design pattern that provides an interface for creating objects in a superclass, while allowing subclasses to alter the type of objects that will be created. It's one of the most commonly used design patterns in software development.

## The Problem

Without factories, client code must know about concrete classes:

```python
# Direct instantiation - tightly coupled
class OrderService:
    def notify_customer(self, order: Order) -> None:
        if order.customer.prefers_email:
            notification = EmailNotification(
                smtp_server="mail.example.com",
                port=587,
                username="...",
            )
        elif order.customer.prefers_sms:
            notification = SMSNotification(
                api_key="...",
                sender_id="...",
            )
        else:
            notification = PushNotification(...)

        notification.send(f"Order {order.id} confirmed")
```

Problems with this approach:
- Client knows about all concrete implementations
- Complex creation logic scattered throughout code
- Hard to test (can't easily substitute implementations)
- Adding new types requires changing existing code

## The Solution

Factories encapsulate object creation:

```python
class OrderService:
    def __init__(self, notification_factory: NotificationFactory):
        self.factory = notification_factory

    def notify_customer(self, order: Order) -> None:
        notification = self.factory.create(order.customer.notification_preference)
        notification.send(f"Order {order.id} confirmed")
```

## Types of Factory Patterns

### 1. Simple Factory

A single function or class that creates objects based on input.

```python
def create_notification(type: str, config: Config) -> Notification:
    """Simple factory function."""
    if type == "email":
        return EmailNotification(
            smtp_server=config.smtp_server,
            port=config.smtp_port,
        )
    elif type == "sms":
        return SMSNotification(api_key=config.sms_api_key)
    else:
        raise ValueError(f"Unknown type: {type}")
```

**Use when:**
- Object creation logic is simple
- Few types to create
- No need for extensibility

### 2. Factory Method

Subclasses decide which class to instantiate.

```python
from abc import ABC, abstractmethod

class NotificationService(ABC):
    @abstractmethod
    def create_notification(self) -> Notification:
        """Factory method - subclasses implement this."""
        pass

    def notify(self, message: str) -> None:
        notification = self.create_notification()
        notification.send(message)

class EmailNotificationService(NotificationService):
    def create_notification(self) -> Notification:
        return EmailNotification()

class SMSNotificationService(NotificationService):
    def create_notification(self) -> Notification:
        return SMSNotification()
```

**Use when:**
- Need to defer instantiation to subclasses
- Creating objects in a base class but types vary
- Framework/library code that users extend

### 3. Abstract Factory

Creates families of related objects.

```python
from abc import ABC, abstractmethod

class UIFactory(ABC):
    """Abstract factory for UI components."""

    @abstractmethod
    def create_button(self) -> Button:
        pass

    @abstractmethod
    def create_checkbox(self) -> Checkbox:
        pass

    @abstractmethod
    def create_text_field(self) -> TextField:
        pass

class MacUIFactory(UIFactory):
    """Concrete factory for Mac UI."""

    def create_button(self) -> Button:
        return MacButton()

    def create_checkbox(self) -> Checkbox:
        return MacCheckbox()

    def create_text_field(self) -> TextField:
        return MacTextField()

class WindowsUIFactory(UIFactory):
    """Concrete factory for Windows UI."""

    def create_button(self) -> Button:
        return WindowsButton()

    def create_checkbox(self) -> Checkbox:
        return WindowsCheckbox()

    def create_text_field(self) -> TextField:
        return WindowsTextField()
```

**Use when:**
- Creating families of related objects
- Objects must be used together
- Want to enforce consistency

### 4. Registry Pattern

Dynamic registration and lookup of factories.

```python
class FactoryRegistry:
    """Registry for dynamic factory registration."""

    _instance: "FactoryRegistry | None" = None
    _factories: dict[str, type] = {}

    @classmethod
    def register(cls, name: str) -> Callable:
        """Decorator for registering factories."""
        def decorator(factory_class: type) -> type:
            cls._factories[name] = factory_class
            return factory_class
        return decorator

    @classmethod
    def create(cls, name: str, **kwargs) -> Any:
        """Create instance using registered factory."""
        if name not in cls._factories:
            raise KeyError(f"No factory registered for: {name}")
        return cls._factories[name](**kwargs)

# Usage with decorator
@FactoryRegistry.register("email")
class EmailNotification:
    def send(self, message: str) -> None:
        print(f"Email: {message}")

# Dynamic creation
notification = FactoryRegistry.create("email")
```

**Use when:**
- Plugin architectures
- Configuration-driven object creation
- Types added at runtime

## Key Principles

### 1. Program to Interfaces

Factories should return abstract types:

```python
# Good: Returns protocol/interface
def create_notification(type: str) -> Notification:
    ...

# Bad: Returns concrete type
def create_notification(type: str) -> EmailNotification:
    ...
```

### 2. Single Responsibility

Each factory should create one type of object:

```python
# Good: Focused factories
class NotificationFactory:
    def create(self, type: str) -> Notification: ...

class UserFactory:
    def create(self, data: dict) -> User: ...

# Bad: God factory
class UniversalFactory:
    def create_notification(self, type: str) -> Notification: ...
    def create_user(self, data: dict) -> User: ...
    def create_order(self, items: list) -> Order: ...
```

### 3. Open/Closed Principle

Factories should be open for extension but closed for modification:

```python
# Registry pattern enables extension without modification
registry.register("new_type", NewTypeFactory)
```

## Factory vs Other Patterns

### Factory vs Builder

| Factory | Builder |
|---------|---------|
| Creates complete objects in one step | Creates objects step by step |
| Best for simple object creation | Best for complex objects with many options |
| Returns different types | Returns same type with different config |

### Factory vs Prototype

| Factory | Prototype |
|---------|-----------|
| Creates new instances | Clones existing instances |
| Uses constructor/initialization | Uses copy mechanism |
| Type-based creation | Instance-based creation |

### Factory vs Dependency Injection

| Factory | Dependency Injection |
|---------|---------------------|
| Creates objects on demand | Container manages object lifecycle |
| Client calls factory | Container injects dependencies |
| Runtime type determination | Configuration-time wiring |

They work well together: DI container injects factory, factory creates objects as needed.

## Best Practices

### 1. Validate Input

```python
def create(self, type: str) -> Notification:
    if type not in self._factories:
        available = list(self._factories.keys())
        raise ValueError(
            f"Unknown type '{type}'. Available types: {available}"
        )
    return self._factories[type]()
```

### 2. Use Type Hints

```python
from typing import TypeVar, Protocol

T = TypeVar("T", bound="Notification")

class NotificationFactory(Protocol[T]):
    def create(self, type: str) -> T: ...
```

### 3. Consider Thread Safety

```python
import threading

class ThreadSafeRegistry:
    def __init__(self):
        self._lock = threading.RLock()
        self._factories: dict[str, type] = {}

    def register(self, name: str, factory: type) -> None:
        with self._lock:
            self._factories[name] = factory

    def create(self, name: str) -> Any:
        with self._lock:
            return self._factories[name]()
```

### 4. Support Configuration

```python
@dataclass
class FactoryConfig:
    type: str
    options: dict[str, Any]

class ConfigurableFactory:
    def create(self, config: FactoryConfig) -> Notification:
        notification = self._base_create(config.type)
        self._apply_options(notification, config.options)
        return notification
```
