"""Example 1: Basic Tool Definition

This example demonstrates how to define simple MCP tools with
validated parameters using ToolDefinition and ToolParameter.
"""

import json

from mcp_tool_schemas import (
    ToolDefinition,
    ToolParameter,
    ValidationError,
    validate_input,
)


def main() -> None:
    """Run the basic tool definition example."""
    print("Example 1: Basic Tool Definition")
    print("=" * 60)

    # Define a simple search tool
    search_tool = ToolDefinition(
        name="search_documents",
        description="""Search the document database for relevant content.

        Use this tool when you need to find documents, articles, or
        information from the knowledge base.

        Returns a list of matching documents with relevance scores.
        """,
        parameters=[
            ToolParameter(
                name="query",
                type="string",
                description="Natural language search query",
                required=True,
                min_length=1,
                max_length=500,
            ),
            ToolParameter(
                name="limit",
                type="integer",
                description="Maximum number of results to return",
                required=False,
                minimum=1,
                maximum=100,
                default=10,
            ),
            ToolParameter(
                name="category",
                type="string",
                description="Filter results by category",
                required=False,
                enum=["all", "articles", "tutorials", "reference"],
                default="all",
            ),
        ],
    )

    print("\n1. Tool Definition")
    print("-" * 40)
    print(f"Name: {search_tool.name}")
    print(f"Required params: {search_tool.get_required_parameters()}")
    print(f"Optional params: {search_tool.get_optional_parameters()}")

    # Convert to JSON Schema
    print("\n2. JSON Schema Output")
    print("-" * 40)
    schema = search_tool.to_json_schema()
    print(json.dumps(schema, indent=2))

    # Validate input examples
    print("\n3. Input Validation")
    print("-" * 40)

    # Valid input (minimal)
    valid_input_1 = {"query": "python tutorials"}
    print(f"\nInput: {valid_input_1}")
    try:
        result = validate_input(search_tool, valid_input_1)
        print(f"Valid! With defaults: {result}")
    except ValidationError as e:
        print(f"Invalid: {e}")

    # Valid input (all parameters)
    valid_input_2 = {
        "query": "machine learning basics",
        "limit": 20,
        "category": "tutorials",
    }
    print(f"\nInput: {valid_input_2}")
    try:
        result = validate_input(search_tool, valid_input_2)
        print(f"Valid! Result: {result}")
    except ValidationError as e:
        print(f"Invalid: {e}")

    # Invalid input (missing required)
    invalid_input_1: dict[str, str | int] = {"limit": 10}
    print(f"\nInput: {invalid_input_1}")
    try:
        result = validate_input(search_tool, invalid_input_1)
        print(f"Valid! Result: {result}")
    except ValidationError as e:
        print(f"Invalid: {e}")

    # Invalid input (wrong type)
    invalid_input_2 = {"query": "test", "limit": "not a number"}
    print(f"\nInput: {invalid_input_2}")
    try:
        result = validate_input(search_tool, invalid_input_2)
        print(f"Valid! Result: {result}")
    except ValidationError as e:
        print(f"Invalid: {e}")

    # Invalid input (constraint violation)
    invalid_input_3 = {"query": "test", "limit": 500}  # max is 100
    print(f"\nInput: {invalid_input_3}")
    try:
        result = validate_input(search_tool, invalid_input_3)
        print(f"Valid! Result: {result}")
    except ValidationError as e:
        print(f"Invalid: {e}")

    # Invalid input (invalid enum value)
    invalid_input_4 = {"query": "test", "category": "invalid_category"}
    print(f"\nInput: {invalid_input_4}")
    try:
        result = validate_input(search_tool, invalid_input_4)
        print(f"Valid! Result: {result}")
    except ValidationError as e:
        print(f"Invalid: {e}")

    # Define another tool: get_weather
    print("\n4. Another Example: Weather Tool")
    print("-" * 40)

    weather_tool = ToolDefinition(
        name="get_weather",
        description="""Get current weather conditions for a location.

        Returns temperature, conditions, humidity, and wind information.
        Supports both city names and coordinates.
        """,
        parameters=[
            ToolParameter(
                name="location",
                type="string",
                description="City name (e.g., 'San Francisco') or coordinates (e.g., '37.7749,-122.4194')",
                required=True,
            ),
            ToolParameter(
                name="units",
                type="string",
                description="Temperature units",
                enum=["celsius", "fahrenheit"],
                default="celsius",
            ),
            ToolParameter(
                name="include_forecast",
                type="boolean",
                description="Include 5-day forecast in response",
                default=False,
            ),
        ],
    )

    print(json.dumps(weather_tool.to_json_schema(), indent=2))

    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
