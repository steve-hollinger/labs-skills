"""Exercise 2: Create a Database Query Tool with Validation

In this exercise, you'll create a database query tool that supports
various SQL-like operations with proper validation.

Instructions:
1. Define a ToolDefinition for database queries
2. Support SELECT, INSERT, UPDATE, DELETE operations
3. Include table name, columns, conditions, and ordering
4. Add security considerations in the description
5. Implement custom validation beyond JSON Schema

Expected Output:
When you run this file, the tests at the bottom should pass.

Hints:
- Different operations need different parameters
- Table and column names should have safe patterns
- Limit result sets to prevent overload
- Document what operations are read-only vs write
"""

from typing import Any

from mcp_tool_schemas import ToolDefinition, ToolParameter, validate_input, ValidationError


def create_database_query_tool() -> ToolDefinition:
    """Create the database query tool definition.

    The tool should support:
    - operation: Required (enum: SELECT, INSERT, UPDATE, DELETE)
    - table: Required table name (string, alphanumeric + underscore only)
    - columns: Optional list of columns for SELECT/INSERT (array)
    - values: Required for INSERT, object with column: value pairs
    - conditions: Optional WHERE conditions (object)
    - order_by: Optional for SELECT (object with column and direction)
    - limit: Optional for SELECT (integer 1-1000, default 100)

    Security considerations:
    - Table names must be alphanumeric with underscores
    - Column names must be alphanumeric with underscores
    - No raw SQL execution (parameterized only)
    """
    # TODO: Implement the tool definition
    tool = ToolDefinition(
        name="database_query",
        description="TODO: Add comprehensive description with security notes",
        parameters=[
            # TODO: Add parameters
        ],
    )

    return tool


def validate_table_name(name: str) -> bool:
    """Validate table name is safe (alphanumeric + underscore)."""
    # TODO: Implement validation
    # Should return True if valid, False if not
    pass


def validate_column_name(name: str) -> bool:
    """Validate column name is safe (alphanumeric + underscore)."""
    # TODO: Implement validation
    pass


def custom_validate_query(tool: ToolDefinition, input_data: dict[str, Any]) -> dict[str, Any]:
    """Perform custom validation beyond JSON Schema.

    Additional validations:
    1. INSERT requires 'values' parameter
    2. UPDATE requires 'conditions' (prevent accidental full table update)
    3. DELETE requires 'conditions' (prevent accidental full table delete)
    4. Table and column names pass security validation
    """
    # First, do JSON Schema validation
    validated = validate_input(tool, input_data)

    # TODO: Add custom validation logic
    # Hint: Check operation-specific requirements

    return validated


def exercise() -> None:
    """Run exercise tests."""
    print("Exercise 2: Database Query Tool")
    print("=" * 50)

    tool = create_database_query_tool()

    # Test 1: Tool basics
    print("\nTest 1: Tool name and description")
    assert tool.name == "database_query"
    assert len(tool.description) > 100, "Description should be comprehensive"
    assert "security" in tool.description.lower() or "safe" in tool.description.lower(), \
        "Description should mention security"
    print("  PASSED!")

    # Test 2: SELECT query
    print("\nTest 2: Valid SELECT query")
    select_input = {
        "operation": "SELECT",
        "table": "users",
        "columns": ["id", "name", "email"],
        "conditions": {"status": "active"},
        "order_by": {"column": "created_at", "direction": "DESC"},
        "limit": 50,
    }
    try:
        result = custom_validate_query(tool, select_input)
        print("  SELECT query validated!")
        print("  PASSED!")
    except (ValidationError, ValueError) as e:
        print(f"  FAILED: {e}")
        raise

    # Test 3: INSERT query
    print("\nTest 3: Valid INSERT query")
    insert_input = {
        "operation": "INSERT",
        "table": "users",
        "values": {
            "name": "John Doe",
            "email": "john@example.com",
        },
    }
    try:
        result = custom_validate_query(tool, insert_input)
        print("  INSERT query validated!")
        print("  PASSED!")
    except (ValidationError, ValueError) as e:
        print(f"  FAILED: {e}")
        raise

    # Test 4: UPDATE without conditions should fail
    print("\nTest 4: UPDATE without conditions")
    update_no_conditions = {
        "operation": "UPDATE",
        "table": "users",
        "values": {"status": "inactive"},
    }
    try:
        custom_validate_query(tool, update_no_conditions)
        print("  FAILED: Should require conditions for UPDATE")
        raise AssertionError("UPDATE without conditions should be rejected")
    except (ValidationError, ValueError):
        print("  UPDATE without conditions correctly rejected!")
        print("  PASSED!")

    # Test 5: DELETE without conditions should fail
    print("\nTest 5: DELETE without conditions")
    delete_no_conditions = {
        "operation": "DELETE",
        "table": "users",
    }
    try:
        custom_validate_query(tool, delete_no_conditions)
        print("  FAILED: Should require conditions for DELETE")
        raise AssertionError("DELETE without conditions should be rejected")
    except (ValidationError, ValueError):
        print("  DELETE without conditions correctly rejected!")
        print("  PASSED!")

    # Test 6: Invalid table name
    print("\nTest 6: Invalid table name")
    assert validate_table_name("users") is True, "valid table name"
    assert validate_table_name("user_accounts") is True, "valid with underscore"
    assert validate_table_name("users123") is True, "valid with numbers"
    assert validate_table_name("users; DROP TABLE") is False, "SQL injection"
    assert validate_table_name("table-name") is False, "hyphens not allowed"
    assert validate_table_name("") is False, "empty not allowed"
    print("  Table name validation working!")
    print("  PASSED!")

    # Test 7: Invalid column name
    print("\nTest 7: Invalid column name")
    assert validate_column_name("email") is True
    assert validate_column_name("user_id") is True
    assert validate_column_name("1column") is False, "can't start with number"
    assert validate_column_name("col*") is False, "no special chars"
    print("  Column name validation working!")
    print("  PASSED!")

    # Test 8: Invalid operation
    print("\nTest 8: Invalid operation")
    try:
        validate_input(tool, {
            "operation": "DROP",  # Not allowed!
            "table": "users",
        })
        print("  FAILED: Should reject DROP operation")
        raise AssertionError("DROP should not be allowed")
    except ValidationError:
        print("  DROP operation correctly rejected!")
        print("  PASSED!")

    # Test 9: JSON Schema output
    print("\nTest 9: JSON Schema structure")
    schema = tool.to_json_schema()
    input_schema = schema["inputSchema"]

    assert "operation" in input_schema["properties"]
    assert "table" in input_schema["properties"]
    assert "enum" in input_schema["properties"]["operation"]
    print("  Schema structure valid!")
    print("  PASSED!")

    print("\n" + "=" * 50)
    print("All tests passed! Great job!")


if __name__ == "__main__":
    exercise()
