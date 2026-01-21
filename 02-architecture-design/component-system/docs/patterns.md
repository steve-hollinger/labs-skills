# Common Patterns

## Overview

This document covers common patterns and best practices for building component-based systems in Python.

## Pattern 1: Graceful Shutdown

### When to Use

When components manage resources (connections, files, threads) that must be properly released.

### Implementation

```python
class DatabaseComponent(Component):
    async def stop(self) -> None:
        """Gracefully shutdown with error handling."""
        errors = []

        # Close connections
        try:
            if self._pool:
                await self._pool.close()
        except Exception as e:
            errors.append(f"Pool close failed: {e}")

        # Flush pending writes
        try:
            await self._flush_buffer()
        except Exception as e:
            errors.append(f"Buffer flush failed: {e}")

        # Log errors but don't raise
        for error in errors:
            self.logger.error(error)

        await super().stop()
```

### Example

```python
class FileWriterComponent(Component):
    async def start(self) -> None:
        await super().start()
        self._file = open(self.config["path"], "w")
        self._buffer = []

    async def stop(self) -> None:
        # Flush any buffered data
        if self._buffer:
            self._file.writelines(self._buffer)
            self._buffer.clear()

        # Close file safely
        if self._file:
            self._file.close()
            self._file = None

        await super().stop()
```

### Pitfalls to Avoid

- Don't raise exceptions in stop() - log and continue
- Don't skip cleanup if one step fails
- Always call super().stop() at the end

## Pattern 2: Health Checks

### When to Use

When you need to monitor component health for load balancers, orchestrators, or monitoring systems.

### Implementation

```python
from enum import Enum

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class HealthCheckMixin:
    """Mixin for adding health check capability."""

    async def health_check(self) -> tuple[HealthStatus, dict]:
        """Return health status and details."""
        return HealthStatus.HEALTHY, {}

class DatabaseComponent(Component, HealthCheckMixin):
    async def health_check(self) -> tuple[HealthStatus, dict]:
        try:
            # Test connection
            await self._pool.execute("SELECT 1")
            return HealthStatus.HEALTHY, {"connections": self._pool.size}
        except Exception as e:
            return HealthStatus.UNHEALTHY, {"error": str(e)}
```

### Example

```python
class HealthAggregator(Component):
    """Aggregates health from all components."""

    async def check_all(self, registry: Registry) -> dict:
        results = {}
        overall = HealthStatus.HEALTHY

        for component in registry:
            if hasattr(component, "health_check"):
                status, details = await component.health_check()
                results[component.name] = {
                    "status": status.value,
                    "details": details,
                }
                if status == HealthStatus.UNHEALTHY:
                    overall = HealthStatus.UNHEALTHY
                elif status == HealthStatus.DEGRADED and overall == HealthStatus.HEALTHY:
                    overall = HealthStatus.DEGRADED

        return {"overall": overall.value, "components": results}
```

### Pitfalls to Avoid

- Don't let health checks take too long (use timeouts)
- Don't mark as unhealthy for transient issues
- Include enough detail to diagnose problems

## Pattern 3: Configuration Validation

### When to Use

When components require specific configuration and you want to fail fast with clear error messages.

### Implementation

```python
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")

class ConfigError(Exception):
    """Configuration validation error."""
    pass

@dataclass
class ConfigSchema:
    """Schema for validating configuration."""
    required: list[str]
    optional: dict[str, any]  # name -> default value
    validators: dict[str, callable]  # name -> validator function

class ConfigurableComponent(Component):
    """Component with configuration validation."""

    config_schema: ConfigSchema | None = None

    async def initialize(self) -> None:
        if self.config_schema:
            self._validate_config()
        await super().initialize()

    def _validate_config(self) -> None:
        schema = self.config_schema

        # Check required fields
        missing = [f for f in schema.required if f not in self.config]
        if missing:
            raise ConfigError(f"Missing required config: {missing}")

        # Apply defaults for optional fields
        for name, default in schema.optional.items():
            if name not in self.config:
                self._config[name] = default

        # Run validators
        for name, validator in schema.validators.items():
            if name in self.config:
                if not validator(self.config[name]):
                    raise ConfigError(f"Invalid value for {name}")
```

### Example

```python
class ApiClientComponent(ConfigurableComponent):
    config_schema = ConfigSchema(
        required=["api_url", "api_key"],
        optional={
            "timeout": 30,
            "retries": 3,
            "verify_ssl": True,
        },
        validators={
            "api_url": lambda x: x.startswith("https://"),
            "timeout": lambda x: isinstance(x, int) and x > 0,
            "retries": lambda x: isinstance(x, int) and 0 <= x <= 10,
        },
    )
```

### Pitfalls to Avoid

- Don't validate in __init__ (do it in initialize())
- Provide clear error messages
- Use sensible defaults for optional config

## Pattern 4: Event-Driven Components

### When to Use

When components need to communicate without direct coupling, or when you need pub/sub behavior.

### Implementation

```python
from typing import Callable, Any
from collections import defaultdict

class EventBus(Component):
    """Central event bus for component communication."""

    name = "event-bus"

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to an event type."""
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Unsubscribe from an event type."""
        self._subscribers[event_type].remove(handler)

    async def publish(self, event_type: str, data: Any) -> None:
        """Publish an event to all subscribers."""
        for handler in self._subscribers[event_type]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                print(f"Event handler error: {e}")
```

### Example

```python
class OrderComponent(Component):
    event_bus: EventBus = Requires()

    async def create_order(self, order: dict) -> None:
        # Create order logic...
        await self.event_bus.publish("order.created", order)

class NotificationComponent(Component):
    event_bus: EventBus = Requires()

    async def start(self) -> None:
        await super().start()
        self.event_bus.subscribe("order.created", self._on_order_created)

    async def _on_order_created(self, order: dict) -> None:
        await self.send_notification(f"New order: {order['id']}")
```

### Pitfalls to Avoid

- Don't rely on event ordering
- Handle subscriber errors gracefully
- Unsubscribe when component stops

## Pattern 5: Factory Components

### When to Use

When you need to create multiple instances of a component type dynamically.

### Implementation

```python
class ComponentFactory(Component):
    """Factory for creating component instances."""

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self._instances: dict[str, Component] = {}

    def create(self, name: str, component_class: type[T], config: dict = None) -> T:
        """Create a named component instance."""
        if name in self._instances:
            raise ValueError(f"Component {name} already exists")

        instance = component_class(config)
        self._instances[name] = instance
        return instance

    def get(self, name: str) -> Component | None:
        """Get a component by name."""
        return self._instances.get(name)

    async def start_all(self) -> None:
        """Start all created instances."""
        for instance in self._instances.values():
            await instance.initialize()
            await instance.start()

    async def stop(self) -> None:
        """Stop all created instances."""
        for instance in reversed(list(self._instances.values())):
            await instance.stop()
        self._instances.clear()
        await super().stop()
```

### Example

```python
class ConnectionFactory(ComponentFactory):
    """Factory for database connections."""

    def create_connection(self, name: str, config: dict) -> DatabaseComponent:
        return self.create(name, DatabaseComponent, config)

# Usage
factory = registry.get(ConnectionFactory)
primary = factory.create_connection("primary", {"host": "primary.db"})
replica = factory.create_connection("replica", {"host": "replica.db"})
```

## Anti-Patterns

### Anti-Pattern 1: God Component

A component that does too much and has too many dependencies.

```python
# Bad: God component
class AppComponent(Component):
    database: DatabaseComponent = Requires()
    cache: CacheComponent = Requires()
    email: EmailComponent = Requires()
    payment: PaymentComponent = Requires()
    analytics: AnalyticsComponent = Requires()
    search: SearchComponent = Requires()
    # ... many more

    async def do_everything(self): ...
```

### Better Approach

Split into focused components:

```python
# Good: Focused components
class OrderService(Component):
    database: DatabaseComponent = Requires()
    cache: CacheComponent = Requires()

class NotificationService(Component):
    email: EmailComponent = Requires()

class PaymentService(Component):
    payment: PaymentComponent = Requires()
```

### Anti-Pattern 2: Hidden Dependencies

Dependencies that aren't declared but are accessed through globals or singletons.

```python
# Bad: Hidden dependency
from myapp import global_database

class UserService(Component):
    async def get_user(self, id: str):
        return await global_database.query(id)  # Hidden dependency!
```

### Better Approach

Declare all dependencies explicitly:

```python
# Good: Explicit dependency
class UserService(Component):
    database: DatabaseComponent = Requires()

    async def get_user(self, id: str):
        return await self.database.query(id)
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Resource cleanup | Graceful Shutdown |
| Monitoring integration | Health Checks |
| Complex configuration | Configuration Validation |
| Loose coupling | Event-Driven Components |
| Dynamic instances | Factory Components |
| Cross-cutting concerns | Mixins or Decorators |
