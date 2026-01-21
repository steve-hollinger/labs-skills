# Core Concepts

## Overview

A tool registry is a pattern for managing dynamic, discoverable, and invocable operations. This is essential for building extensible applications, CLI frameworks, plugin systems, and AI agent integrations where tools need to be registered, discovered, validated, and executed programmatically.

## Concept 1: Tool Definition

### What It Is

A tool is a callable operation with associated metadata, input/output schemas, and execution logic. Tools are self-describing units that can be introspected, validated, and invoked dynamically.

### Why It Matters

- **Discoverability**: Tools can be listed and inspected at runtime
- **Validation**: Inputs and outputs are validated against schemas
- **Documentation**: Metadata enables automatic documentation generation
- **Type Safety**: Schemas ensure correct data types are passed

### How It Works

```python
from dataclasses import dataclass
from typing import Any, Callable

@dataclass
class Tool:
    name: str                    # Unique identifier
    description: str             # Human-readable description
    func: Callable[..., Any]    # The actual function
    schema: ToolSchema          # Input/output schemas
    permissions: list[str]       # Required permissions
    tags: list[str]             # Categorization tags

    async def execute(self, params: dict) -> Any:
        """Execute the tool with validated parameters."""
        if asyncio.iscoroutinefunction(self.func):
            return await self.func(**params)
        return self.func(**params)
```

Tools can be created using decorators for convenience:

```python
@tool(
    name="search",
    description="Search for documents",
    tags=["search", "query"],
)
async def search(query: str, limit: int = 10) -> list[dict]:
    return await search_engine.search(query, limit)
```

## Concept 2: Schema Validation

### What It Is

Schema validation ensures that tool inputs match expected types and constraints before execution, and optionally validates outputs match the expected format.

### Why It Matters

- **Error Prevention**: Catch invalid inputs before execution
- **Clear Errors**: Provide meaningful error messages
- **API Contracts**: Define clear contracts for tool usage
- **AI Integration**: Schemas help AI models understand tool parameters

### How It Works

Schemas are typically defined using JSON Schema format:

```python
from jsonschema import Draft7Validator

class ToolSchema:
    def __init__(self, input: dict, output: dict = None):
        self.input = input
        self.output = output

    def validate_input(self, tool_name: str, params: dict) -> None:
        validator = Draft7Validator(self.input)
        errors = list(validator.iter_errors(params))
        if errors:
            raise ValidationError(tool_name, [
                {"field": str(e.path), "message": e.message}
                for e in errors
            ])
```

Example schema definition:

```python
schema = ToolSchema(
    input={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query",
                "minLength": 1,
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "default": 10,
            },
        },
        "required": ["query"],
    },
    output={
        "type": "array",
        "items": {"type": "object"},
    },
)
```

## Concept 3: Registry Pattern

### What It Is

The registry is a central manager that tracks tool registration, provides discovery capabilities, and handles invocation with proper validation and middleware execution.

### Why It Matters

- **Centralized Management**: Single source of truth for available tools
- **Dynamic Registration**: Tools can be added/removed at runtime
- **Unified Invocation**: Consistent interface for calling any tool
- **Middleware Support**: Cross-cutting concerns applied uniformly

### How It Works

```python
class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._middleware = MiddlewareChain()

    def register(self, tool: Tool) -> None:
        """Register a tool with the registry."""
        if tool.name in self._tools:
            raise ValueError(f"Tool {tool.name} already registered")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        """Get a tool by name."""
        if name not in self._tools:
            raise ToolNotFoundError(name)
        return self._tools[name]

    async def invoke(self, name: str, params: dict) -> Any:
        """Invoke a tool with validation and middleware."""
        tool = self.get(name)
        return await self._middleware.execute(
            tool, params, tool.execute
        )
```

## Concept 4: Middleware

### What It Is

Middleware are interceptors that wrap tool execution to add cross-cutting concerns like logging, timing, authentication, rate limiting, and error handling.

### Why It Matters

- **Separation of Concerns**: Keep tool logic focused on business logic
- **Reusability**: Apply same behavior to all tools
- **Flexibility**: Add/remove concerns without changing tools
- **Observability**: Unified logging and monitoring

### How It Works

Middleware follows a chain pattern where each middleware can modify inputs, outputs, or handle errors:

```python
class Middleware(ABC):
    @abstractmethod
    async def __call__(self, tool, params, next) -> Any:
        """Execute the middleware.

        Args:
            tool: The tool being invoked
            params: Input parameters
            next: The next handler in the chain

        Returns:
            The result (possibly modified)
        """
        ...

class LoggingMiddleware(Middleware):
    async def __call__(self, tool, params, next) -> Any:
        print(f"Calling {tool.name}")
        result = await next(tool, params)
        print(f"Result: {result}")
        return result
```

Middleware is applied in order:

```python
registry.use(AuthMiddleware())      # First: check auth
registry.use(ValidationMiddleware()) # Second: validate
registry.use(LoggingMiddleware())    # Third: log
registry.use(TimingMiddleware())     # Fourth: time
```

## Concept 5: Access Control

### What It Is

Access control restricts which users can invoke which tools based on permissions. This is essential for multi-tenant systems and AI agents with limited capabilities.

### Why It Matters

- **Security**: Prevent unauthorized operations
- **Isolation**: Different users/agents have different capabilities
- **Compliance**: Enforce access policies
- **Safety**: Limit AI agent capabilities

### How It Works

```python
@tool(
    name="delete_user",
    permissions=["admin", "user:delete"],
)
async def delete_user(user_id: str) -> bool:
    ...

# In registry
def can_invoke(self, name: str, user_permissions: list[str]) -> bool:
    tool = self.get(name)
    if not tool.permissions:
        return True  # No permissions required
    return any(p in user_permissions for p in tool.permissions)

async def invoke(self, name: str, params: dict,
                 user_permissions: list[str] = None) -> Any:
    if user_permissions and not self.can_invoke(name, user_permissions):
        raise PermissionDeniedError(name, tool.permissions)
    ...
```

## Summary

Key takeaways from these concepts:

1. **Tools are Self-Describing**: Each tool carries its own metadata, schema, and execution logic, making them discoverable and introspectable.

2. **Schemas Enable Safety**: JSON Schema validation catches errors early and provides clear error messages.

3. **Registries Centralize Management**: A registry provides a single point for registration, discovery, and invocation.

4. **Middleware Separates Concerns**: Cross-cutting concerns like logging, auth, and rate limiting are handled uniformly.

5. **Permissions Enable Control**: Fine-grained access control ensures tools are used appropriately.

These patterns work together to create flexible, secure, and maintainable systems for dynamic tool management.
