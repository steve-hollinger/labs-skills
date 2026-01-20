"""Solution for Exercise 1: File Search Tool Schema"""

from mcp_tool_schemas import ToolDefinition, ToolParameter, validate_input, ValidationError


def create_file_search_tool() -> ToolDefinition:
    """Create the file search tool definition."""
    return ToolDefinition(
        name="file_search",
        description="""Search for files in the filesystem by name, content, or metadata.

        Use this tool to find files based on various criteria:
        - Text search in file names and paths
        - Filter by file type/extension
        - Filter by file size range
        - Filter by modification date

        Returns a list of matching files with path, size, and modification date.
        Results are sorted by relevance/modification date.

        NOTE: This tool only searches, it does not read file contents.
        Use a separate tool to read file contents after finding them.
        """,
        parameters=[
            ToolParameter(
                name="query",
                type="string",
                description="Search query to match against file names and paths",
                required=True,
                min_length=1,
                max_length=500,
            ),
            ToolParameter(
                name="path",
                type="string",
                description="Starting directory path for search (recursive)",
                required=False,
                default="/",
            ),
            ToolParameter(
                name="file_types",
                type="array",
                description="List of file extensions to include (e.g., ['.py', '.txt'])",
                required=False,
                items={"type": "string", "pattern": r"^\.\w+$"},
                max_items=20,
            ),
            ToolParameter(
                name="max_size_mb",
                type="integer",
                description="Maximum file size in megabytes",
                required=False,
                minimum=1,
                maximum=1000,
            ),
            ToolParameter(
                name="min_size_mb",
                type="integer",
                description="Minimum file size in megabytes",
                required=False,
                minimum=0,
                maximum=1000,
            ),
            ToolParameter(
                name="modified_after",
                type="string",
                description="Only include files modified after this date (YYYY-MM-DD)",
                required=False,
                format="date",
            ),
            ToolParameter(
                name="modified_before",
                type="string",
                description="Only include files modified before this date (YYYY-MM-DD)",
                required=False,
                format="date",
            ),
            ToolParameter(
                name="include_hidden",
                type="boolean",
                description="Include hidden files (starting with .)",
                required=False,
                default=False,
            ),
            ToolParameter(
                name="max_results",
                type="integer",
                description="Maximum number of results to return",
                required=False,
                minimum=1,
                maximum=1000,
                default=100,
            ),
        ],
    )


def solution() -> None:
    """Demonstrate the solution."""
    print("Solution 1: File Search Tool Schema")
    print("=" * 50)

    tool = create_file_search_tool()

    # Print schema
    import json
    print("\nGenerated JSON Schema:")
    print(json.dumps(tool.to_json_schema(), indent=2))

    # Validate examples
    print("\nValidation Examples:")

    examples = [
        {"query": "*.py"},
        {"query": "config", "path": "/etc", "max_results": 10},
        {
            "query": "log",
            "file_types": [".log", ".txt"],
            "max_size_mb": 100,
            "modified_after": "2024-01-01",
        },
    ]

    for example in examples:
        try:
            result = validate_input(tool, example)
            print(f"\n  Input: {example}")
            print(f"  Valid! With defaults: {result}")
        except ValidationError as e:
            print(f"\n  Input: {example}")
            print(f"  Invalid: {e}")


if __name__ == "__main__":
    solution()
