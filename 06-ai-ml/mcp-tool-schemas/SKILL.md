---
name: designing-mcp-tool-schemas
description: This skill teaches how to define and validate tool schemas for the Model Context Protocol (MCP), enabling AI assistants to effectively use external tools. Use when writing or improving tests.
---

# Mcp Tool Schemas

## Quick Start
```python
from mcp_tool_schemas import ToolDefinition, ToolParameter

tool = ToolDefinition(
    name="search",
    description="Search documents by keyword",
    parameters=[
        ToolParameter(
            name="query",
            type="string",
            description="Search query",
            required=True,
        ),
    ],
)
```

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run basic tool definition example
make example-2  # Run complex schema example
make example-3  # Run tool server example
make test       # Run pytest
```

## Key Points
- Tool Definition
- JSON Schema
- Parameter Types

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples