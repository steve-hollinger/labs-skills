# Core Concepts

## Overview

The Model Context Protocol (MCP) enables AI assistants to interact with external tools and data sources. Understanding how to define tool schemas is essential for building effective AI-powered applications.

## Concept 1: Tool Definition Structure

### What It Is

A tool definition is a complete specification that tells an AI assistant:
- What the tool does (name and description)
- What inputs it accepts (parameter schema)
- What outputs it produces (return type hints)
- What errors it might return

### Why It Matters

Well-defined tools enable AI assistants to:
- Choose the right tool for a task
- Construct valid API calls
- Handle responses appropriately
- Recover from errors gracefully

### How It Works

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class ToolDefinition:
    """Complete tool specification for MCP."""

    name: str                    # Unique identifier
    description: str             # What the tool does
    parameters: list[dict]       # Input schema
    returns: dict | None = None  # Output schema (optional)

# Example tool definition
search_tool = ToolDefinition(
    name="search_documents",
    description="""Search the document database for relevant content.

    Use this tool when the user asks to find information, documents,
    or answers that might be in the knowledge base.

    Returns a list of matching documents with relevance scores.
    Results are sorted by relevance, highest first.
    """,
    parameters=[
        {
            "name": "query",
            "type": "string",
            "description": "Natural language search query",
            "required": True,
        },
        {
            "name": "limit",
            "type": "integer",
            "description": "Maximum number of results (1-100)",
            "minimum": 1,
            "maximum": 100,
            "default": 10,
        },
        {
            "name": "filters",
            "type": "object",
            "description": "Optional filters to narrow results",
            "properties": {
                "category": {"type": "string"},
                "date_after": {"type": "string", "format": "date"},
            },
        },
    ],
    returns={
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "title": {"type": "string"},
                "snippet": {"type": "string"},
                "score": {"type": "number"},
            },
        },
    },
)
```

## Concept 2: JSON Schema for Parameters

### What It Is

JSON Schema is a vocabulary that allows you to annotate and validate JSON documents. MCP uses JSON Schema to define tool parameters.

### Why It Matters

JSON Schema provides:
- Type safety for tool inputs
- Validation before execution
- Self-documenting parameter definitions
- Constraints that prevent invalid calls

### How It Works

```python
# Basic types
string_param = {
    "name": "query",
    "type": "string",
    "description": "Search query",
    "minLength": 1,
    "maxLength": 500,
}

integer_param = {
    "name": "count",
    "type": "integer",
    "description": "Number of items",
    "minimum": 1,
    "maximum": 100,
}

# Enum constraint
status_param = {
    "name": "status",
    "type": "string",
    "description": "Filter by status",
    "enum": ["pending", "active", "completed", "cancelled"],
}

# Array type
tags_param = {
    "name": "tags",
    "type": "array",
    "description": "Filter by tags",
    "items": {"type": "string"},
    "minItems": 1,
    "maxItems": 10,
}

# Nested object
filter_param = {
    "name": "filter",
    "type": "object",
    "description": "Advanced filters",
    "properties": {
        "created_after": {
            "type": "string",
            "format": "date-time",
            "description": "Filter to items created after this date",
        },
        "author": {
            "type": "string",
            "description": "Filter by author name",
        },
    },
    "additionalProperties": False,
}

# Combined schema
full_schema = {
    "type": "object",
    "properties": {
        "query": string_param,
        "count": integer_param,
        "status": status_param,
        "tags": tags_param,
        "filter": filter_param,
    },
    "required": ["query"],
    "additionalProperties": False,
}
```

### Common JSON Schema Constraints

| Type | Constraints |
|------|-------------|
| string | minLength, maxLength, pattern, format, enum |
| integer/number | minimum, maximum, exclusiveMinimum, exclusiveMaximum, multipleOf |
| array | items, minItems, maxItems, uniqueItems |
| object | properties, required, additionalProperties, minProperties, maxProperties |

## Concept 3: Writing Effective Descriptions

### What It Is

Tool descriptions are natural language text that helps AI assistants understand:
- What the tool does
- When to use it
- How to use it correctly

### Why It Matters

The description is often the primary way an AI decides which tool to use. A poor description leads to:
- Wrong tool selection
- Incorrect parameter usage
- Confusion about tool capabilities

### How It Works

```python
# BAD: Vague, unhelpful description
bad_tool = {
    "name": "search",
    "description": "Searches for stuff",
}

# GOOD: Clear, comprehensive description
good_tool = {
    "name": "search_documents",
    "description": """Search the knowledge base for documents matching a query.

    USE THIS TOOL WHEN:
    - User asks to find specific information
    - User wants to look up documentation
    - User needs to verify facts from the knowledge base

    DO NOT USE THIS TOOL WHEN:
    - User is asking about current events (knowledge base is static)
    - User wants to perform an action (this is read-only)

    RETURNS:
    - List of matching documents with title, snippet, and relevance score
    - Empty list if no matches found
    - Results sorted by relevance (highest first)

    NOTES:
    - Supports natural language queries
    - Use filters to narrow results by category or date
    - Maximum 100 results per query
    """,
}
```

### Description Best Practices

1. **Start with a one-line summary** of what the tool does
2. **Explain when to use** (and when not to use) the tool
3. **Describe the return value** clearly
4. **Note any limitations** or important behaviors
5. **Use concrete examples** when helpful

## Concept 4: Validation Patterns

### What It Is

Validation ensures that tool inputs match the expected schema before the tool executes.

### Why It Matters

Proper validation:
- Prevents runtime errors
- Provides clear error messages
- Enables early failure with helpful feedback
- Protects against malicious inputs

### How It Works

```python
import jsonschema
from jsonschema import ValidationError

def validate_tool_input(schema: dict, input_data: dict) -> dict:
    """Validate input against JSON Schema.

    Args:
        schema: JSON Schema to validate against
        input_data: User-provided input

    Returns:
        Validated input (may include defaults)

    Raises:
        ValidationError: If input doesn't match schema
    """
    # Create validator with format checking
    validator = jsonschema.Draft7Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    )

    # Collect all errors
    errors = list(validator.iter_errors(input_data))

    if errors:
        # Format error messages
        messages = []
        for error in errors:
            path = ".".join(str(p) for p in error.absolute_path)
            if path:
                messages.append(f"{path}: {error.message}")
            else:
                messages.append(error.message)

        raise ValidationError("; ".join(messages))

    # Apply defaults for missing optional fields
    return apply_defaults(schema, input_data)


def apply_defaults(schema: dict, data: dict) -> dict:
    """Apply default values from schema to data."""
    result = data.copy()

    if "properties" in schema:
        for prop_name, prop_schema in schema["properties"].items():
            if prop_name not in result and "default" in prop_schema:
                result[prop_name] = prop_schema["default"]

    return result


# Usage example
schema = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "minLength": 1},
        "limit": {"type": "integer", "minimum": 1, "default": 10},
    },
    "required": ["query"],
}

# Valid input
valid_input = {"query": "hello"}
result = validate_tool_input(schema, valid_input)
print(result)  # {"query": "hello", "limit": 10}

# Invalid input
try:
    validate_tool_input(schema, {"query": ""})
except ValidationError as e:
    print(f"Validation error: {e}")
```

## Summary

Key takeaways from these concepts:

1. **Tool definitions** are complete specifications that enable AI assistants to use your tools correctly
2. **JSON Schema** provides type safety and validation for tool parameters
3. **Good descriptions** are essential for AI assistants to choose and use tools correctly
4. **Validation** should happen before execution to provide clear feedback
5. **Default values** should be documented and applied consistently
6. **Error handling** should be structured and informative
