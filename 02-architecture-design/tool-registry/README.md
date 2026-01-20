# Tool Registry Pattern

Learn to build dynamic tool management systems in Python. This skill teaches patterns for registering, discovering, and invoking tools with schema validation - essential for building extensible applications, CLI frameworks, and AI agent systems.

## Learning Objectives

After completing this skill, you will be able to:
- Design and implement dynamic tool registries
- Define tools with typed schemas and validation
- Build tool discovery and invocation systems
- Create middleware for tool execution
- Implement permission and access control for tools

## Prerequisites

- Python 3.11+
- UV package manager
- Understanding of Python decorators
- Familiarity with Pydantic for validation
- Basic knowledge of JSON Schema

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

### Tool Definition

Tools are defined with metadata, input/output schemas, and an execution function. This allows for validation, documentation generation, and introspection.

```python
from tool_registry import Tool, ToolSchema, tool

@tool(
    name="search",
    description="Search for documents by query",
    schema=ToolSchema(
        input={
            "query": {"type": "string", "description": "Search query"},
            "limit": {"type": "integer", "default": 10},
        },
        output={"type": "array", "items": {"type": "object"}},
    ),
)
async def search(query: str, limit: int = 10) -> list[dict]:
    """Execute search and return results."""
    return await search_engine.search(query, limit)
```

### Tool Registry

The registry manages tool registration, discovery, and provides a unified interface for tool invocation.

```python
from tool_registry import ToolRegistry

registry = ToolRegistry()

# Register tools
registry.register(search)
registry.register(get_user)
registry.register(send_email)

# Discover tools
tools = registry.list_tools()
schema = registry.get_schema("search")

# Invoke tools
result = await registry.invoke("search", {"query": "python", "limit": 5})
```

### Schema Validation

Tool inputs and outputs are validated against their schemas, ensuring type safety and clear error messages.

```python
from tool_registry import validate_input, ValidationError

try:
    validate_input("search", {"query": 123})  # Wrong type
except ValidationError as e:
    print(f"Validation failed: {e.errors}")
    # Output: [{"field": "query", "message": "Expected string, got integer"}]
```

## Examples

### Example 1: Basic Tool Registration

This example demonstrates creating and registering simple tools.

```bash
make example-1
```

### Example 2: Tool Middleware

Building a middleware system for logging, timing, and error handling around tool execution.

```bash
make example-2
```

### Example 3: AI Agent Tools

Creating a complete tool system for AI agents with discovery and invocation.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Create a calculator tool with input validation
2. **Exercise 2**: Build a file operations tool set with permissions
3. **Exercise 3**: Implement a tool middleware for rate limiting

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Forgetting to Validate Inputs
Always validate inputs before execution:
```python
# Good: Validation happens automatically
result = await registry.invoke("tool", params)

# Bad: Direct call bypasses validation
result = await tool_func(**params)
```

### Not Handling Tool Errors
Wrap tool invocation to handle errors gracefully:
```python
try:
    result = await registry.invoke("tool", params)
except ToolNotFoundError:
    # Tool doesn't exist
except ValidationError:
    # Input validation failed
except ToolExecutionError:
    # Tool threw an exception
```

### Exposing Internal Tools
Use permissions to control tool access:
```python
@tool(name="admin_reset", permissions=["admin"])
async def admin_reset():
    ...

# Check permissions before invocation
if not registry.can_invoke("admin_reset", user_permissions):
    raise PermissionDenied()
```

## Further Reading

- [JSON Schema Documentation](https://json-schema.org/)
- Related skills in this repository:
  - [Component System](../component-system/) - Component architecture patterns
  - [Pydantic V2](../../01-language-frameworks/python/pydantic-v2/) - Data validation
