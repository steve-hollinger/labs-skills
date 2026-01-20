# CLAUDE.md - MCP Tool Schemas

This skill teaches how to define and validate tool schemas for the Model Context Protocol (MCP), enabling AI assistants to effectively use external tools.

## Key Concepts

- **Tool Definition**: The complete specification of a tool including name, description, and parameters
- **JSON Schema**: The standard used to define parameter types, constraints, and validation rules
- **Parameter Types**: string, number, integer, boolean, array, object, and null
- **Validation**: Ensuring tool inputs match the expected schema before execution
- **Error Handling**: Defining and returning structured errors from tools

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run basic tool definition example
make example-2  # Run complex schema example
make example-3  # Run tool server example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
mcp-tool-schemas/
├── src/mcp_tool_schemas/
│   ├── __init__.py
│   ├── schema.py          # Core schema definitions
│   ├── validation.py      # Schema validation
│   ├── server.py          # MCP server implementation
│   └── examples/
│       ├── example_1.py   # Basic tool definition
│       ├── example_2.py   # Complex schemas
│       └── example_3.py   # Tool server
├── exercises/
│   ├── exercise_1.py      # File search tool
│   ├── exercise_2.py      # Database query tool
│   ├── exercise_3.py      # Multi-tool server
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic Tool Definition
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

### Pattern 2: JSON Schema Generation
```python
schema = tool.to_json_schema()
# Returns:
# {
#     "name": "search",
#     "description": "Search documents by keyword",
#     "inputSchema": {
#         "type": "object",
#         "properties": {
#             "query": {
#                 "type": "string",
#                 "description": "Search query"
#             }
#         },
#         "required": ["query"]
#     }
# }
```

### Pattern 3: Input Validation
```python
from mcp_tool_schemas import validate_input

# Validate user input against schema
try:
    validated = validate_input(tool, {"query": "hello"})
except ValidationError as e:
    print(f"Invalid input: {e}")
```

## Common Mistakes

1. **Vague descriptions that don't help the AI**
   - Why it happens: Developers focus on code, not documentation
   - How to fix it: Write descriptions from the AI's perspective - what does it need to know to use this tool correctly?

2. **Not specifying required fields**
   - Why it happens: Assuming defaults will be used
   - How to fix it: Always explicitly list required parameters

3. **Using overly generic types**
   - Why it happens: Being lazy with schema definition
   - How to fix it: Add constraints (minLength, maximum, enum, pattern)

4. **Missing error documentation**
   - Why it happens: Only focusing on happy path
   - How to fix it: Document possible errors and when they occur

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make example-1` to see a basic tool definition.

### "What makes a good tool description?"
A good description should answer:
- What does the tool do?
- When should it be used vs. other tools?
- What does it return?
- What are the side effects (if any)?

### "How do I handle optional parameters?"
Don't include them in the `required` array, and provide a `default` value:
```python
ToolParameter(
    name="limit",
    type="integer",
    description="Max results",
    required=False,
    default=10,
)
```

### "How do I validate nested objects?"
Use the `properties` field for nested object schemas:
```python
ToolParameter(
    name="filter",
    type="object",
    description="Filter options",
    properties={
        "status": {"type": "string", "enum": ["active", "inactive"]},
        "created_after": {"type": "string", "format": "date"},
    },
)
```

## Testing Notes

- Tests use pytest with markers
- Run specific tests: `pytest -k "test_name"`
- Schema validation tests don't require external services
- Integration tests marked with `@pytest.mark.integration`

## Dependencies

Key dependencies in pyproject.toml:
- jsonschema: For JSON Schema validation
- pydantic: For data modeling and validation
- typing-extensions: For advanced type hints
