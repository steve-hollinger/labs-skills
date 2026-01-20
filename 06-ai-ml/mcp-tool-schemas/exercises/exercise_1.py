"""Exercise 1: Define a File Search Tool Schema

In this exercise, you'll define an MCP tool schema for a file search tool
that can search files by name, content, and metadata.

Instructions:
1. Create a ToolDefinition for a file search tool
2. Include parameters for: query, path, file_types, size constraints, date filters
3. Add proper descriptions and constraints
4. Validate your schema with test inputs

Expected Output:
When you run this file, the tests at the bottom should pass.

Hints:
- Use ToolParameter for each parameter
- Arrays need 'items' schema
- Objects need 'properties' schema
- Add appropriate constraints (min/max, patterns, enums)
"""

from mcp_tool_schemas import ToolDefinition, ToolParameter, validate_input, ValidationError


def create_file_search_tool() -> ToolDefinition:
    """Create the file search tool definition.

    The tool should support:
    - query: Required search query (string, 1-500 chars)
    - path: Optional starting directory (string, default "/")
    - file_types: Optional list of extensions to include (array of strings like ".py", ".txt")
    - max_size_mb: Optional max file size in MB (integer, 1-1000)
    - min_size_mb: Optional min file size in MB (integer, 0-1000)
    - modified_after: Optional date filter (string, date format)
    - modified_before: Optional date filter (string, date format)
    - include_hidden: Whether to include hidden files (boolean, default false)
    - max_results: Maximum results to return (integer, 1-1000, default 100)
    """
    # TODO: Implement the tool definition
    # Replace this with your implementation

    tool = ToolDefinition(
        name="file_search",
        description="TODO: Add a comprehensive description",
        parameters=[
            # TODO: Add parameters
        ],
    )

    return tool


def exercise() -> None:
    """Run exercise tests."""
    print("Exercise 1: File Search Tool Schema")
    print("=" * 50)

    tool = create_file_search_tool()

    # Test 1: Check tool name
    print("\nTest 1: Tool name")
    assert tool.name == "file_search", f"Expected name 'file_search', got '{tool.name}'"
    print("  PASSED!")

    # Test 2: Check description is not empty/placeholder
    print("\nTest 2: Tool description")
    assert len(tool.description) > 50, "Description should be comprehensive"
    assert "TODO" not in tool.description, "Description should not contain TODO"
    print("  PASSED!")

    # Test 3: Check required parameters
    print("\nTest 3: Required parameters")
    required_params = tool.get_required_parameters()
    assert "query" in required_params, "query should be required"
    print(f"  Required params: {required_params}")
    print("  PASSED!")

    # Test 4: Validate minimal valid input
    print("\nTest 4: Minimal valid input")
    try:
        result = validate_input(tool, {"query": "test search"})
        print(f"  Input: {{'query': 'test search'}}")
        print(f"  Result (with defaults): {result}")
        print("  PASSED!")
    except ValidationError as e:
        print(f"  FAILED: {e}")
        raise AssertionError("Minimal input should be valid")

    # Test 5: Validate full input
    print("\nTest 5: Full valid input")
    full_input = {
        "query": "python files",
        "path": "/home/user/projects",
        "file_types": [".py", ".pyx"],
        "max_size_mb": 10,
        "modified_after": "2024-01-01",
        "include_hidden": True,
        "max_results": 50,
    }
    try:
        result = validate_input(tool, full_input)
        print(f"  Input valid!")
        print("  PASSED!")
    except ValidationError as e:
        print(f"  FAILED: {e}")
        raise AssertionError("Full input should be valid")

    # Test 6: Invalid query (too short/empty)
    print("\nTest 6: Invalid query")
    try:
        validate_input(tool, {"query": ""})
        print("  FAILED: Should have rejected empty query")
        raise AssertionError("Empty query should be rejected")
    except ValidationError:
        print("  Empty query correctly rejected!")
        print("  PASSED!")

    # Test 7: Invalid max_results (out of range)
    print("\nTest 7: Invalid max_results")
    try:
        validate_input(tool, {"query": "test", "max_results": 5000})
        print("  FAILED: Should have rejected max_results > 1000")
        raise AssertionError("max_results > 1000 should be rejected")
    except ValidationError:
        print("  Out-of-range max_results correctly rejected!")
        print("  PASSED!")

    # Test 8: Check file_types is array
    print("\nTest 8: file_types array validation")
    try:
        validate_input(tool, {"query": "test", "file_types": ".py"})  # String, not array
        print("  FAILED: Should have rejected string for file_types")
        raise AssertionError("file_types should require array")
    except ValidationError:
        print("  String file_types correctly rejected!")
        print("  PASSED!")

    # Test 9: JSON Schema output
    print("\nTest 9: JSON Schema generation")
    schema = tool.to_json_schema()
    assert "name" in schema, "Schema should have name"
    assert "description" in schema, "Schema should have description"
    assert "inputSchema" in schema, "Schema should have inputSchema"
    assert "properties" in schema["inputSchema"], "inputSchema should have properties"
    print("  JSON Schema structure valid!")
    print("  PASSED!")

    print("\n" + "=" * 50)
    print("All tests passed! Great job!")


if __name__ == "__main__":
    exercise()
