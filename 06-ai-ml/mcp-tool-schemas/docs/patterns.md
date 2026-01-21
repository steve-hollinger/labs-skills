# Common Patterns

## Overview

This document covers common patterns and best practices for defining MCP tool schemas.

## Pattern 1: CRUD Tool Set

### When to Use

When exposing a resource that supports Create, Read, Update, Delete operations.

### Implementation

```python
from mcp_tool_schemas import ToolDefinition, ToolParameter

# Define a consistent set of CRUD tools for a resource
def create_crud_tools(resource_name: str, resource_schema: dict) -> list[ToolDefinition]:
    """Generate CRUD tool definitions for a resource."""

    return [
        # CREATE
        ToolDefinition(
            name=f"create_{resource_name}",
            description=f"""Create a new {resource_name}.

            Creates a new {resource_name} with the provided data.
            Returns the created {resource_name} with its assigned ID.
            """,
            parameters=[
                ToolParameter(
                    name="data",
                    type="object",
                    description=f"The {resource_name} data to create",
                    properties=resource_schema,
                    required=True,
                ),
            ],
        ),

        # READ (single)
        ToolDefinition(
            name=f"get_{resource_name}",
            description=f"""Get a {resource_name} by ID.

            Retrieves a single {resource_name} by its unique identifier.
            Returns null if the {resource_name} doesn't exist.
            """,
            parameters=[
                ToolParameter(
                    name="id",
                    type="string",
                    description=f"The unique identifier of the {resource_name}",
                    required=True,
                ),
            ],
        ),

        # READ (list)
        ToolDefinition(
            name=f"list_{resource_name}s",
            description=f"""List all {resource_name}s.

            Returns a paginated list of {resource_name}s.
            Use filters to narrow results and pagination to handle large datasets.
            """,
            parameters=[
                ToolParameter(
                    name="filter",
                    type="object",
                    description="Filter criteria",
                ),
                ToolParameter(
                    name="page",
                    type="integer",
                    description="Page number (1-indexed)",
                    minimum=1,
                    default=1,
                ),
                ToolParameter(
                    name="page_size",
                    type="integer",
                    description="Items per page",
                    minimum=1,
                    maximum=100,
                    default=20,
                ),
            ],
        ),

        # UPDATE
        ToolDefinition(
            name=f"update_{resource_name}",
            description=f"""Update an existing {resource_name}.

            Updates a {resource_name} with the provided data.
            Only provided fields are updated (partial update).
            Returns the updated {resource_name}.
            """,
            parameters=[
                ToolParameter(
                    name="id",
                    type="string",
                    description=f"The unique identifier of the {resource_name}",
                    required=True,
                ),
                ToolParameter(
                    name="data",
                    type="object",
                    description="Fields to update",
                    properties=resource_schema,
                    required=True,
                ),
            ],
        ),

        # DELETE
        ToolDefinition(
            name=f"delete_{resource_name}",
            description=f"""Delete a {resource_name}.

            Permanently deletes a {resource_name} by ID.
            Returns true if deleted, false if not found.
            """,
            parameters=[
                ToolParameter(
                    name="id",
                    type="string",
                    description=f"The unique identifier of the {resource_name}",
                    required=True,
                ),
            ],
        ),
    ]


# Usage
user_schema = {
    "name": {"type": "string", "description": "User's full name"},
    "email": {"type": "string", "format": "email", "description": "User's email"},
    "role": {"type": "string", "enum": ["admin", "user", "guest"]},
}

user_tools = create_crud_tools("user", user_schema)
```

### Pitfalls to Avoid

- Inconsistent naming conventions across tools
- Missing pagination for list operations
- Not specifying which updates are partial vs full replacement

## Pattern 2: Search with Facets

### When to Use

When building search tools that need filtering, sorting, and aggregation.

### Implementation

```python
search_tool = ToolDefinition(
    name="search_products",
    description="""Search product catalog with filters and facets.

    Performs a full-text search on product names and descriptions.
    Supports filtering by category, price range, and attributes.
    Returns results with facet counts for refinement.
    """,
    parameters=[
        ToolParameter(
            name="query",
            type="string",
            description="Search query (natural language)",
            required=True,
        ),
        ToolParameter(
            name="filters",
            type="object",
            description="Filter criteria",
            properties={
                "category": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by category (OR within array)",
                },
                "price_min": {
                    "type": "number",
                    "description": "Minimum price",
                    "minimum": 0,
                },
                "price_max": {
                    "type": "number",
                    "description": "Maximum price",
                },
                "in_stock": {
                    "type": "boolean",
                    "description": "Only show in-stock items",
                },
                "attributes": {
                    "type": "object",
                    "description": "Filter by product attributes",
                    "additionalProperties": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
        ),
        ToolParameter(
            name="sort",
            type="object",
            description="Sort configuration",
            properties={
                "field": {
                    "type": "string",
                    "enum": ["relevance", "price", "name", "rating", "created"],
                    "default": "relevance",
                },
                "order": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "default": "desc",
                },
            },
        ),
        ToolParameter(
            name="facets",
            type="array",
            description="Facets to compute",
            items={
                "type": "string",
                "enum": ["category", "brand", "price_range", "rating"],
            },
            default=["category"],
        ),
        ToolParameter(
            name="page",
            type="integer",
            minimum=1,
            default=1,
        ),
        ToolParameter(
            name="page_size",
            type="integer",
            minimum=1,
            maximum=50,
            default=20,
        ),
    ],
)
```

### Pitfalls to Avoid

- Not documenting filter combination logic (AND vs OR)
- Missing facet documentation
- Unbounded result sizes

## Pattern 3: Action with Confirmation

### When to Use

For destructive or irreversible actions that might need confirmation.

### Implementation

```python
delete_tool = ToolDefinition(
    name="delete_user_data",
    description="""Permanently delete all user data.

    WARNING: This action is IRREVERSIBLE.

    This tool deletes all data associated with a user:
    - Account information
    - Saved preferences
    - Activity history
    - Uploaded files

    Use the 'preview' mode first to see what will be deleted.
    Then confirm with 'confirm_token' to execute.
    """,
    parameters=[
        ToolParameter(
            name="user_id",
            type="string",
            description="User ID to delete",
            required=True,
        ),
        ToolParameter(
            name="mode",
            type="string",
            description="Operation mode",
            enum=["preview", "execute"],
            default="preview",
        ),
        ToolParameter(
            name="confirm_token",
            type="string",
            description="Confirmation token from preview (required for execute)",
        ),
    ],
)


# Implementation that uses the confirmation pattern
def handle_delete_user_data(params: dict) -> dict:
    """Handle delete with confirmation."""
    user_id = params["user_id"]
    mode = params.get("mode", "preview")

    if mode == "preview":
        # Calculate what would be deleted
        stats = get_user_data_stats(user_id)

        # Generate confirmation token
        token = generate_confirmation_token(user_id, "delete")

        return {
            "mode": "preview",
            "user_id": user_id,
            "will_delete": stats,
            "confirm_token": token,
            "message": "Use this confirm_token with mode='execute' to proceed",
        }

    elif mode == "execute":
        token = params.get("confirm_token")
        if not token:
            raise ValueError("confirm_token required for execute mode")

        if not verify_confirmation_token(token, user_id, "delete"):
            raise ValueError("Invalid or expired confirmation token")

        # Perform deletion
        result = delete_user_data(user_id)

        return {
            "mode": "execute",
            "user_id": user_id,
            "deleted": result,
            "message": "User data permanently deleted",
        }
```

### Pitfalls to Avoid

- Not making destructive nature clear in description
- Missing preview/dry-run mode
- Confirmation tokens that don't expire

## Pattern 4: Batch Operations

### When to Use

When users need to perform the same operation on multiple items.

### Implementation

```python
batch_tool = ToolDefinition(
    name="batch_update_status",
    description="""Update status for multiple items at once.

    Efficiently updates the status of multiple items in a single call.
    Returns results for each item (success or error).

    Maximum 100 items per batch.
    Failed items don't affect successful ones (partial success possible).
    """,
    parameters=[
        ToolParameter(
            name="items",
            type="array",
            description="Items to update",
            items={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Item ID"},
                    "status": {
                        "type": "string",
                        "enum": ["pending", "approved", "rejected"],
                    },
                    "note": {"type": "string", "description": "Optional note"},
                },
                "required": ["id", "status"],
            },
            minItems=1,
            maxItems=100,
            required=True,
        ),
        ToolParameter(
            name="stop_on_error",
            type="boolean",
            description="Stop processing on first error",
            default=False,
        ),
    ],
)
```

### Pitfalls to Avoid

- No batch size limits
- All-or-nothing behavior without option
- Missing per-item error reporting

## Anti-Patterns

### Anti-Pattern 1: The "Do Everything" Tool

Description: A single tool that tries to handle too many operations.

```python
# BAD: One tool for everything
bad_tool = {
    "name": "manage_items",
    "description": "Create, read, update, or delete items",
    "parameters": [
        {"name": "action", "enum": ["create", "read", "update", "delete"]},
        {"name": "id", "type": "string"},
        {"name": "data", "type": "object"},
    ],
}
```

### Better Approach

```python
# GOOD: Separate tools with clear purposes
create_tool = {"name": "create_item", ...}
read_tool = {"name": "get_item", ...}
update_tool = {"name": "update_item", ...}
delete_tool = {"name": "delete_item", ...}
```

### Anti-Pattern 2: Missing Type Constraints

Description: Using generic types without validation constraints.

```python
# BAD: No constraints
bad_param = {
    "name": "limit",
    "type": "integer",
    "description": "Number of results",
}
```

### Better Approach

```python
# GOOD: With constraints
good_param = {
    "name": "limit",
    "type": "integer",
    "description": "Number of results to return",
    "minimum": 1,
    "maximum": 100,
    "default": 10,
}
```

### Anti-Pattern 3: Ambiguous Descriptions

Description: Descriptions that don't help the AI make decisions.

```python
# BAD: Vague
bad_description = "Gets data from the system"

# GOOD: Specific
good_description = """Retrieve user profile information by user ID.

Returns the user's public profile including name, avatar, bio, and join date.
Returns null if the user doesn't exist or has a private profile.

Use this tool when you need user information to personalize responses
or verify user identity.
"""
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Resource management | CRUD Tool Set |
| Searching/filtering | Search with Facets |
| Destructive actions | Action with Confirmation |
| Multiple item updates | Batch Operations |
| Complex workflows | Separate tools for each step |
| Read-only data access | Single focused tool |
