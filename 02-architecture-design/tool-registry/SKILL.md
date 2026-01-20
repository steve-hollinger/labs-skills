---
name: building-tool-registries
description: Dynamic tool management patterns in Python, including registration, discovery, validation, and invocation systems. Use when implementing authentication or verifying tokens.
---

# Tool Registry

## Quick Start
```python
from tool_registry import tool

@tool(
    name="greet",
    description="Greet a user by name",
)
async def greet(name: str) -> str:
    return f"Hello, {name}!"
```


## Key Points
- Tool
- Registry
- Schema

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples