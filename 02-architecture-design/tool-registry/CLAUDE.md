# CLAUDE.md - Tool Registry Pattern

This skill teaches dynamic tool management patterns in Python, including registration, discovery, validation, and invocation systems.

## Key Concepts

- **Tool**: A callable with metadata, schema, and execution function
- **Registry**: Central manager for tool registration and discovery
- **Schema**: JSON Schema-based definition of tool inputs and outputs
- **Middleware**: Interceptors for cross-cutting concerns (logging, auth, etc.)
- **Invocation**: Validated execution of tools with proper error handling

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run specific example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
tool-registry/
├── src/tool_registry/
│   ├── __init__.py
│   ├── tool.py           # Tool class and decorator
│   ├── schema.py         # Schema definition and validation
│   ├── registry.py       # Tool registry implementation
│   ├── middleware.py     # Middleware system
│   ├── exceptions.py     # Custom exceptions
│   └── examples/
│       ├── example_1.py  # Basic registration
│       ├── example_2.py  # Middleware
│       └── example_3.py  # AI agent tools
├── exercises/
│   ├── exercise_1.py
│   ├── exercise_2.py
│   ├── exercise_3.py
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Tool Decorator
```python
from tool_registry import tool

@tool(
    name="greet",
    description="Greet a user by name",
)
async def greet(name: str) -> str:
    return f"Hello, {name}!"
```

### Pattern 2: Registry Usage
```python
from tool_registry import ToolRegistry

registry = ToolRegistry()
registry.register(greet)

# List available tools
for tool in registry.list_tools():
    print(f"{tool.name}: {tool.description}")

# Invoke a tool
result = await registry.invoke("greet", {"name": "Alice"})
```

### Pattern 3: Middleware Chain
```python
from tool_registry import Middleware

class LoggingMiddleware(Middleware):
    async def __call__(self, tool, params, next):
        print(f"Calling {tool.name}")
        result = await next(tool, params)
        print(f"Result: {result}")
        return result

registry.use(LoggingMiddleware())
```

## Common Mistakes

1. **Registering duplicate tools**
   - Registry raises error on duplicate names
   - Use unique names or namespaces

2. **Missing required parameters**
   - Validation catches this before execution
   - Check error messages for missing fields

3. **Not awaiting async tools**
   - All tool invocations are async
   - Always use `await registry.invoke(...)`

4. **Ignoring middleware order**
   - Middleware executes in registration order
   - Put auth/validation middleware first

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make example-1` to see basic tool registration.

### "How do I validate inputs?"
Explain that validation happens automatically based on the tool's schema. Show the schema definition in the @tool decorator.

### "How do I add logging?"
Direct them to example-2 which shows the middleware pattern for logging.

### "How do I use this with AI agents?"
Show example-3 which demonstrates tool discovery and invocation for AI agents.

## Testing Notes

- Tests use pytest with pytest-asyncio
- Run specific tests: `pytest -k "test_invoke"`
- Mock tool functions for unit testing

## Dependencies

Key dependencies in pyproject.toml:
- pydantic: For input/output validation
- jsonschema: For JSON Schema validation
- typing-extensions: For advanced type hints
