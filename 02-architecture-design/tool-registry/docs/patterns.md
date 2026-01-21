# Common Patterns

## Overview

This document covers common patterns and best practices for building tool registry systems in Python.

## Pattern 1: Decorator-Based Registration

### When to Use

When you want a clean, declarative way to define and register tools directly where they're implemented.

### Implementation

```python
class ToolRegistry:
    def tool(self, name=None, description=None, **kwargs):
        """Decorator for registering tools."""
        def decorator(func):
            t = Tool(
                name=name or func.__name__,
                description=description or func.__doc__,
                func=func,
                **kwargs
            )
            self.register(t)
            return t
        return decorator

# Usage
registry = ToolRegistry()

@registry.tool(name="greet", description="Greet a user")
async def greet(name: str) -> str:
    return f"Hello, {name}!"
```

### Example

```python
# Define tools inline with the registry
@registry.tool(tags=["math"])
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

@registry.tool(tags=["math"], permissions=["calculator"])
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

### Pitfalls to Avoid

- Don't use the decorator without the registry instance
- Remember decorators return Tool objects, not functions
- Handle async vs sync functions appropriately

## Pattern 2: Schema Generation from Type Hints

### When to Use

When you want to reduce boilerplate by automatically generating schemas from Python type annotations.

### Implementation

```python
import inspect
from typing import get_type_hints

def schema_from_hints(func) -> ToolSchema:
    hints = get_type_hints(func)
    sig = inspect.signature(func)

    properties = {}
    required = []

    for name, param in sig.parameters.items():
        prop = {}
        if name in hints:
            prop["type"] = python_type_to_json(hints[name])
        if param.default is inspect.Parameter.empty:
            required.append(name)
        else:
            prop["default"] = param.default
        properties[name] = prop

    return ToolSchema(
        input={
            "type": "object",
            "properties": properties,
            "required": required,
        }
    )
```

### Example

```python
@tool()  # Schema auto-generated from type hints
async def search(
    query: str,
    limit: int = 10,
    include_metadata: bool = False,
) -> list[dict]:
    """Search for documents."""
    ...

# Equivalent to explicit schema:
# {
#     "type": "object",
#     "properties": {
#         "query": {"type": "string"},
#         "limit": {"type": "integer", "default": 10},
#         "include_metadata": {"type": "boolean", "default": false}
#     },
#     "required": ["query"]
# }
```

### Pitfalls to Avoid

- Complex types (Union, Optional, generics) need special handling
- Default values must be JSON-serializable
- Always validate the generated schema

## Pattern 3: Middleware Chain

### When to Use

When you need to apply cross-cutting concerns uniformly across all tool invocations.

### Implementation

```python
class MiddlewareChain:
    def __init__(self):
        self._middleware = []

    def use(self, middleware):
        self._middleware.append(middleware)
        return self

    async def execute(self, tool, params, final_handler):
        # Build chain from end to start
        handler = final_handler

        for mw in reversed(self._middleware):
            prev_handler = handler
            handler = lambda t, p, h=prev_handler, m=mw: m(t, p, h)

        return await handler(tool, params)
```

### Example

```python
# Build middleware chain
registry.use(AuthenticationMiddleware())
registry.use(ValidationMiddleware())
registry.use(RateLimitMiddleware(limit=100, window=60))
registry.use(LoggingMiddleware())
registry.use(MetricsMiddleware())

# Execution order:
# 1. Auth checks user credentials
# 2. Validation checks input schema
# 3. Rate limit checks call frequency
# 4. Logging records the call
# 5. Metrics tracks timing
# 6. Tool executes
# 7. Metrics records duration
# 8. Logging records result
```

### Pitfalls to Avoid

- Order matters - auth should come before rate limiting
- Don't catch errors in early middleware (let them propagate)
- Be careful with closure captures in the chain

## Pattern 4: Tool Discovery for AI Agents

### When to Use

When exposing tools to AI models that need to understand available operations and their parameters.

### Implementation

```python
class ToolRegistry:
    def get_tools_for_ai(self, user_permissions=None) -> list[dict]:
        """Get tool definitions suitable for AI model consumption."""
        tools = []
        for tool in self._tools.values():
            # Filter by permissions if provided
            if user_permissions and tool.permissions:
                if not any(p in user_permissions for p in tool.permissions):
                    continue

            tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.schema.input,
                }
            })
        return tools
```

### Example

```python
# Get tools for OpenAI function calling
tools = registry.get_tools_for_ai(user_permissions=["read", "write"])

# Use with OpenAI
response = await client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

# Process tool calls
for tool_call in response.choices[0].message.tool_calls:
    result = await registry.invoke(
        tool_call.function.name,
        json.loads(tool_call.function.arguments),
        user_permissions=user_permissions,
    )
```

### Pitfalls to Avoid

- Don't expose sensitive tools to AI without permission checks
- Validate AI-generated parameters carefully
- Handle tool errors gracefully in the conversation

## Pattern 5: Namespaced Tools

### When to Use

When you have many tools or multiple modules that might have naming conflicts.

### Implementation

```python
class NamespacedRegistry:
    def __init__(self):
        self._namespaces: dict[str, ToolRegistry] = {}
        self._default = ToolRegistry()

    def namespace(self, name: str) -> ToolRegistry:
        if name not in self._namespaces:
            self._namespaces[name] = ToolRegistry()
        return self._namespaces[name]

    async def invoke(self, name: str, params: dict) -> Any:
        if ":" in name:
            ns, tool_name = name.split(":", 1)
            return await self._namespaces[ns].invoke(tool_name, params)
        return await self._default.invoke(name, params)
```

### Example

```python
registry = NamespacedRegistry()

# Register in different namespaces
@registry.namespace("users").tool()
async def get(id: str) -> dict:
    """Get a user."""
    ...

@registry.namespace("orders").tool()
async def get(id: str) -> dict:
    """Get an order."""
    ...

# Invoke with namespace prefix
await registry.invoke("users:get", {"id": "u123"})
await registry.invoke("orders:get", {"id": "o456"})
```

### Pitfalls to Avoid

- Be consistent with namespace separators
- Document namespace structure clearly
- Consider namespace permissions

## Anti-Patterns

### Anti-Pattern 1: Unvalidated Direct Execution

Bypassing the registry to call tool functions directly.

```python
# Bad: Direct call bypasses validation and middleware
result = await my_tool.func(**params)

# Good: Use registry invocation
result = await registry.invoke("my_tool", params)
```

### Better Approach

Always invoke through the registry to ensure validation and middleware are applied.

### Anti-Pattern 2: Stateful Tools

Tools that maintain state between invocations.

```python
# Bad: Stateful tool
class CounterTool:
    count = 0

    @tool()
    async def increment(self) -> int:
        self.count += 1  # Shared state!
        return self.count
```

### Better Approach

Keep tools stateless and pass state explicitly:

```python
# Good: Stateless tool with explicit state
@tool()
async def increment(current: int) -> int:
    return current + 1
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Simple tool definitions | Decorator-Based Registration |
| Reducing boilerplate | Schema Generation from Type Hints |
| Cross-cutting concerns | Middleware Chain |
| AI agent integration | Tool Discovery for AI |
| Large applications | Namespaced Tools |
| Rate limiting | Middleware with state |
| Authentication | Permissions + Auth Middleware |
