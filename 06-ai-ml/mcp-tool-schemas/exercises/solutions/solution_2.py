"""Solution for Exercise 2: Database Query Tool with Validation"""

import re
from typing import Any

from mcp_tool_schemas import ToolDefinition, ToolParameter, validate_input, ValidationError


def create_database_query_tool() -> ToolDefinition:
    """Create the database query tool definition."""
    return ToolDefinition(
        name="database_query",
        description="""Execute safe, parameterized database queries.

        Supports SELECT, INSERT, UPDATE, and DELETE operations with proper validation.
        All queries are parameterized to prevent SQL injection.

        SECURITY NOTES:
        - Table and column names are validated (alphanumeric + underscore only)
        - No raw SQL execution - all queries are parameterized
        - UPDATE and DELETE require conditions to prevent accidental data loss
        - Results are limited to prevent memory issues

        READ OPERATIONS (SELECT):
        - Returns array of matching rows
        - Use limit and offset for pagination
        - Supports ordering

        WRITE OPERATIONS (INSERT, UPDATE, DELETE):
        - Returns affected row count
        - UPDATE/DELETE require conditions (safety)
        """,
        parameters=[
            ToolParameter(
                name="operation",
                type="string",
                description="SQL operation to perform",
                required=True,
                enum=["SELECT", "INSERT", "UPDATE", "DELETE"],
            ),
            ToolParameter(
                name="table",
                type="string",
                description="Table name (alphanumeric and underscores only)",
                required=True,
                pattern=r"^[a-zA-Z][a-zA-Z0-9_]*$",
                min_length=1,
                max_length=64,
            ),
            ToolParameter(
                name="columns",
                type="array",
                description="Columns for SELECT or INSERT (default: all for SELECT)",
                items={"type": "string", "pattern": r"^[a-zA-Z][a-zA-Z0-9_]*$"},
                max_items=50,
            ),
            ToolParameter(
                name="values",
                type="object",
                description="Column-value pairs for INSERT or UPDATE",
            ),
            ToolParameter(
                name="conditions",
                type="object",
                description="WHERE conditions as column-value pairs (required for UPDATE/DELETE)",
            ),
            ToolParameter(
                name="order_by",
                type="object",
                description="Ordering for SELECT results",
                properties={
                    "column": {
                        "type": "string",
                        "pattern": r"^[a-zA-Z][a-zA-Z0-9_]*$",
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["ASC", "DESC"],
                        "default": "ASC",
                    },
                },
            ),
            ToolParameter(
                name="limit",
                type="integer",
                description="Maximum rows to return (SELECT only)",
                minimum=1,
                maximum=1000,
                default=100,
            ),
            ToolParameter(
                name="offset",
                type="integer",
                description="Number of rows to skip (SELECT only)",
                minimum=0,
                default=0,
            ),
        ],
    )


def validate_table_name(name: str) -> bool:
    """Validate table name is safe (alphanumeric + underscore, starts with letter)."""
    if not name:
        return False
    # Must start with letter, contain only alphanumeric and underscores
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", name))


def validate_column_name(name: str) -> bool:
    """Validate column name is safe (alphanumeric + underscore, starts with letter)."""
    if not name:
        return False
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", name))


def custom_validate_query(tool: ToolDefinition, input_data: dict[str, Any]) -> dict[str, Any]:
    """Perform custom validation beyond JSON Schema."""
    # First, do JSON Schema validation
    validated = validate_input(tool, input_data)

    operation = validated.get("operation")
    table = validated.get("table", "")
    values = validated.get("values")
    conditions = validated.get("conditions")
    columns = validated.get("columns", [])

    # Validate table name
    if not validate_table_name(table):
        raise ValueError(f"Invalid table name: {table}")

    # Validate column names
    for col in columns:
        if not validate_column_name(col):
            raise ValueError(f"Invalid column name: {col}")

    # Operation-specific validation
    if operation == "INSERT":
        if not values:
            raise ValueError("INSERT operation requires 'values' parameter")
        # Validate column names in values
        for col in values.keys():
            if not validate_column_name(col):
                raise ValueError(f"Invalid column name in values: {col}")

    elif operation == "UPDATE":
        if not conditions:
            raise ValueError(
                "UPDATE operation requires 'conditions' to prevent accidental "
                "full table update. Use conditions to specify which rows to update."
            )
        if not values:
            raise ValueError("UPDATE operation requires 'values' parameter")

    elif operation == "DELETE":
        if not conditions:
            raise ValueError(
                "DELETE operation requires 'conditions' to prevent accidental "
                "full table deletion. Use conditions to specify which rows to delete."
            )

    # Validate condition column names
    if conditions:
        for col in conditions.keys():
            if not validate_column_name(col):
                raise ValueError(f"Invalid column name in conditions: {col}")

    return validated


def solution() -> None:
    """Demonstrate the solution."""
    print("Solution 2: Database Query Tool")
    print("=" * 50)

    tool = create_database_query_tool()

    import json
    print("\nGenerated JSON Schema:")
    print(json.dumps(tool.to_json_schema(), indent=2))

    print("\nValidation Examples:")

    # Valid SELECT
    print("\n1. Valid SELECT:")
    select_input = {
        "operation": "SELECT",
        "table": "users",
        "columns": ["id", "name", "email"],
        "conditions": {"status": "active"},
        "limit": 50,
    }
    result = custom_validate_query(tool, select_input)
    print(f"   Input: {select_input}")
    print(f"   Valid!")

    # Valid INSERT
    print("\n2. Valid INSERT:")
    insert_input = {
        "operation": "INSERT",
        "table": "users",
        "values": {"name": "John", "email": "john@example.com"},
    }
    result = custom_validate_query(tool, insert_input)
    print(f"   Input: {insert_input}")
    print(f"   Valid!")

    # Valid UPDATE with conditions
    print("\n3. Valid UPDATE:")
    update_input = {
        "operation": "UPDATE",
        "table": "users",
        "values": {"status": "inactive"},
        "conditions": {"id": 123},
    }
    result = custom_validate_query(tool, update_input)
    print(f"   Input: {update_input}")
    print(f"   Valid!")

    # Invalid UPDATE without conditions
    print("\n4. Invalid UPDATE (no conditions):")
    try:
        custom_validate_query(tool, {
            "operation": "UPDATE",
            "table": "users",
            "values": {"status": "inactive"},
        })
    except ValueError as e:
        print(f"   Correctly rejected: {e}")


if __name__ == "__main__":
    solution()
