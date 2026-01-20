# MCP Tool Schemas

Learn how to define and validate tool schemas for the Model Context Protocol (MCP). This skill teaches you to create well-structured tool definitions that enable AI assistants to use your tools effectively.

## Learning Objectives

After completing this skill, you will be able to:
- Understand the MCP tool schema structure
- Define JSON Schema for tool parameters
- Write effective tool descriptions for AI consumption
- Validate tool inputs and outputs
- Handle errors gracefully in MCP tools
- Build a complete MCP tool server

## Prerequisites

- Python 3.11+
- UV package manager
- Basic understanding of JSON Schema
- Familiarity with REST APIs and function signatures

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

### What is MCP?

The Model Context Protocol (MCP) is a standard for enabling AI assistants to interact with external tools and data sources. MCP defines how tools are described (schemas) and how they're invoked.

```python
from mcp_tool_schemas import ToolDefinition, ToolParameter

# Define a simple tool
weather_tool = ToolDefinition(
    name="get_weather",
    description="Get current weather for a location",
    parameters=[
        ToolParameter(
            name="location",
            type="string",
            description="City name or coordinates",
            required=True,
        ),
        ToolParameter(
            name="units",
            type="string",
            description="Temperature units",
            enum=["celsius", "fahrenheit"],
            default="celsius",
        ),
    ],
)
```

### Why Good Schemas Matter

AI assistants use your tool descriptions to:
1. **Decide when to use the tool** - Clear descriptions help the AI choose the right tool
2. **Construct valid parameters** - Well-defined schemas prevent errors
3. **Understand tool output** - Return type hints help interpret results
4. **Handle errors** - Error schemas enable graceful failure handling

### JSON Schema for Parameters

MCP uses JSON Schema to define parameter types and constraints:

```python
{
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "Search query",
            "minLength": 1,
            "maxLength": 500
        },
        "limit": {
            "type": "integer",
            "description": "Maximum results to return",
            "minimum": 1,
            "maximum": 100,
            "default": 10
        }
    },
    "required": ["query"]
}
```

## Examples

### Example 1: Basic Tool Definition

Create a simple tool with validated parameters.

```bash
make example-1
```

### Example 2: Complex Schemas

Define tools with nested objects, arrays, and conditional logic.

```bash
make example-2
```

### Example 3: Tool Server Implementation

Build a complete MCP tool server with multiple tools.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Define a file search tool schema
2. **Exercise 2**: Create a database query tool with validation
3. **Exercise 3**: Build a multi-tool MCP server

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Vague Tool Descriptions
Bad: "Searches for things"
Good: "Searches the knowledge base for documents matching the query. Returns up to 10 results with title, snippet, and relevance score."

### Missing Required Fields
Always specify which parameters are required. Don't assume the AI will guess correctly.

### Overly Permissive Types
Use specific types and constraints. `"type": "string"` with no constraints accepts anything - add `minLength`, `maxLength`, `pattern`, or `enum` where appropriate.

### Not Handling Errors
Define what errors your tool can return and when. This helps the AI recover gracefully.

## Further Reading

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [JSON Schema Documentation](https://json-schema.org/)
- Related skills in this repository:
  - [LLM Integration Patterns](../llm-integration/)
  - [API Design](../../02-architecture-design/api-design/)
