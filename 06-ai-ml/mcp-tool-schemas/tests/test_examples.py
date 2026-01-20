"""Tests for MCP Tool Schemas examples and core functionality."""

import pytest

from mcp_tool_schemas import (
    ToolDefinition,
    ToolParameter,
    ToolResult,
    ValidationError,
    validate_input,
    validate_output,
)
from mcp_tool_schemas.server import ToolServer, create_server
from mcp_tool_schemas.validation import (
    check_tool_definition,
    generate_example_input,
    validate_schema,
)


class TestToolParameter:
    """Tests for ToolParameter."""

    def test_basic_string_parameter(self) -> None:
        """Test basic string parameter."""
        param = ToolParameter(
            name="query",
            type="string",
            description="Search query",
            required=True,
        )

        schema = param.to_json_schema()

        assert schema["type"] == "string"
        assert schema["description"] == "Search query"

    def test_string_with_constraints(self) -> None:
        """Test string parameter with constraints."""
        param = ToolParameter(
            name="email",
            type="string",
            description="Email address",
            format="email",
            min_length=5,
            max_length=100,
        )

        schema = param.to_json_schema()

        assert schema["format"] == "email"
        assert schema["minLength"] == 5
        assert schema["maxLength"] == 100

    def test_integer_parameter(self) -> None:
        """Test integer parameter with range."""
        param = ToolParameter(
            name="limit",
            type="integer",
            description="Max results",
            minimum=1,
            maximum=100,
            default=10,
        )

        schema = param.to_json_schema()

        assert schema["type"] == "integer"
        assert schema["minimum"] == 1
        assert schema["maximum"] == 100
        assert schema["default"] == 10

    def test_enum_parameter(self) -> None:
        """Test enum parameter."""
        param = ToolParameter(
            name="status",
            type="string",
            description="Item status",
            enum=["active", "inactive", "pending"],
        )

        schema = param.to_json_schema()

        assert schema["enum"] == ["active", "inactive", "pending"]

    def test_array_parameter(self) -> None:
        """Test array parameter."""
        param = ToolParameter(
            name="tags",
            type="array",
            description="List of tags",
            items={"type": "string"},
            min_items=1,
            max_items=10,
        )

        schema = param.to_json_schema()

        assert schema["type"] == "array"
        assert schema["items"] == {"type": "string"}
        assert schema["minItems"] == 1
        assert schema["maxItems"] == 10

    def test_object_parameter(self) -> None:
        """Test object parameter."""
        param = ToolParameter(
            name="filter",
            type="object",
            description="Filter options",
            properties={
                "status": {"type": "string"},
                "priority": {"type": "integer"},
            },
        )

        schema = param.to_json_schema()

        assert schema["type"] == "object"
        assert "status" in schema["properties"]
        assert "priority" in schema["properties"]


class TestToolDefinition:
    """Tests for ToolDefinition."""

    def test_basic_tool(self) -> None:
        """Test basic tool definition."""
        tool = ToolDefinition(
            name="search",
            description="Search documents",
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="Search query",
                    required=True,
                ),
            ],
        )

        schema = tool.to_json_schema()

        assert schema["name"] == "search"
        assert schema["description"] == "Search documents"
        assert "inputSchema" in schema
        assert schema["inputSchema"]["required"] == ["query"]

    def test_multiple_parameters(self) -> None:
        """Test tool with multiple parameters."""
        tool = ToolDefinition(
            name="find",
            description="Find items",
            parameters=[
                ToolParameter(
                    name="query", type="string", description="Query", required=True
                ),
                ToolParameter(
                    name="limit", type="integer", description="Limit", default=10
                ),
                ToolParameter(
                    name="category", type="string", description="Category"
                ),
            ],
        )

        assert tool.get_required_parameters() == ["query"]
        assert set(tool.get_optional_parameters()) == {"limit", "category"}

    def test_input_schema(self) -> None:
        """Test input schema extraction."""
        tool = ToolDefinition(
            name="test",
            description="Test tool",
            parameters=[
                ToolParameter(name="a", type="string", description="A", required=True),
                ToolParameter(name="b", type="integer", description="B"),
            ],
        )

        input_schema = tool.get_input_schema()

        assert input_schema["type"] == "object"
        assert "a" in input_schema["properties"]
        assert "b" in input_schema["properties"]
        assert input_schema["required"] == ["a"]


class TestValidation:
    """Tests for input validation."""

    @pytest.fixture
    def search_tool(self) -> ToolDefinition:
        """Create a search tool for testing."""
        return ToolDefinition(
            name="search",
            description="Search documents",
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="Search query",
                    required=True,
                    min_length=1,
                ),
                ToolParameter(
                    name="limit",
                    type="integer",
                    description="Max results",
                    minimum=1,
                    maximum=100,
                    default=10,
                ),
                ToolParameter(
                    name="category",
                    type="string",
                    description="Category filter",
                    enum=["all", "docs", "code"],
                    default="all",
                ),
            ],
        )

    def test_valid_minimal_input(self, search_tool: ToolDefinition) -> None:
        """Test validation of minimal valid input."""
        result = validate_input(search_tool, {"query": "test"})

        assert result["query"] == "test"
        assert result["limit"] == 10  # default applied
        assert result["category"] == "all"  # default applied

    def test_valid_full_input(self, search_tool: ToolDefinition) -> None:
        """Test validation of full valid input."""
        result = validate_input(
            search_tool,
            {"query": "test", "limit": 50, "category": "docs"},
        )

        assert result["query"] == "test"
        assert result["limit"] == 50
        assert result["category"] == "docs"

    def test_missing_required(self, search_tool: ToolDefinition) -> None:
        """Test validation fails for missing required field."""
        with pytest.raises(ValidationError) as exc_info:
            validate_input(search_tool, {})

        assert "query" in str(exc_info.value).lower()

    def test_invalid_type(self, search_tool: ToolDefinition) -> None:
        """Test validation fails for wrong type."""
        with pytest.raises(ValidationError):
            validate_input(search_tool, {"query": "test", "limit": "not a number"})

    def test_constraint_violation(self, search_tool: ToolDefinition) -> None:
        """Test validation fails for constraint violation."""
        with pytest.raises(ValidationError):
            validate_input(search_tool, {"query": "test", "limit": 500})

    def test_invalid_enum(self, search_tool: ToolDefinition) -> None:
        """Test validation fails for invalid enum value."""
        with pytest.raises(ValidationError):
            validate_input(search_tool, {"query": "test", "category": "invalid"})

    def test_empty_string_constraint(self, search_tool: ToolDefinition) -> None:
        """Test validation fails for empty string with minLength."""
        with pytest.raises(ValidationError):
            validate_input(search_tool, {"query": ""})


class TestToolResult:
    """Tests for ToolResult."""

    def test_success_result(self) -> None:
        """Test creating success result."""
        result = ToolResult.success_result({"data": "value"})

        assert result.success is True
        assert result.data == {"data": "value"}
        assert result.error is None

    def test_error_result(self) -> None:
        """Test creating error result."""
        result = ToolResult.error_result("Something went wrong", "ERROR_CODE")

        assert result.success is False
        assert result.error == "Something went wrong"
        assert result.error_code == "ERROR_CODE"
        assert result.data is None

    def test_to_dict(self) -> None:
        """Test result serialization."""
        result = ToolResult.success_result({"key": "value"}, metadata={"time": 100})
        data = result.to_dict()

        assert data["success"] is True
        assert data["data"] == {"key": "value"}
        assert data["metadata"] == {"time": 100}


class TestToolServer:
    """Tests for ToolServer."""

    def test_create_server(self) -> None:
        """Test server creation."""
        server = create_server("test-server", "1.0.0")

        assert server.name == "test-server"
        assert server.version == "1.0.0"

    def test_register_tool(self) -> None:
        """Test tool registration."""
        server = create_server("test", "1.0.0")
        tool = ToolDefinition(
            name="greet",
            description="Greet user",
            parameters=[
                ToolParameter(name="name", type="string", description="Name", required=True)
            ],
        )

        server.register_tool(tool, lambda name: {"message": f"Hello, {name}!"})

        assert "greet" in server.tools
        assert server.get_tool("greet") == tool

    def test_decorator_registration(self) -> None:
        """Test tool registration via decorator."""
        server = create_server("test", "1.0.0")
        tool = ToolDefinition(
            name="add",
            description="Add numbers",
            parameters=[
                ToolParameter(name="a", type="integer", description="First", required=True),
                ToolParameter(name="b", type="integer", description="Second", required=True),
            ],
        )

        @server.tool(tool)
        def add_numbers(a: int, b: int) -> dict:
            return {"result": a + b}

        assert "add" in server.tools

    def test_call_tool(self) -> None:
        """Test tool execution."""
        server = create_server("test", "1.0.0")
        tool = ToolDefinition(
            name="multiply",
            description="Multiply numbers",
            parameters=[
                ToolParameter(name="x", type="integer", description="X", required=True),
                ToolParameter(name="y", type="integer", description="Y", required=True),
            ],
        )

        server.register_tool(tool, lambda x, y: {"result": x * y})

        result = server.call_tool("multiply", {"x": 3, "y": 4})

        assert result.success
        assert result.data == {"result": 12}

    def test_call_nonexistent_tool(self) -> None:
        """Test calling nonexistent tool."""
        server = create_server("test", "1.0.0")

        result = server.call_tool("nonexistent", {})

        assert not result.success
        assert result.error_code == "TOOL_NOT_FOUND"

    def test_call_tool_validation_error(self) -> None:
        """Test tool call with invalid input."""
        server = create_server("test", "1.0.0")
        tool = ToolDefinition(
            name="echo",
            description="Echo message",
            parameters=[
                ToolParameter(name="msg", type="string", description="Message", required=True)
            ],
        )

        server.register_tool(tool, lambda msg: {"echo": msg})

        result = server.call_tool("echo", {})  # Missing required

        assert not result.success
        assert result.error_code == "VALIDATION_ERROR"

    def test_call_tool_execution_error(self) -> None:
        """Test tool call with execution error."""
        server = create_server("test", "1.0.0")
        tool = ToolDefinition(
            name="fail",
            description="Always fails",
            parameters=[],
        )

        def failing_handler() -> dict:
            raise RuntimeError("Intentional failure")

        server.register_tool(tool, failing_handler)

        result = server.call_tool("fail", {})

        assert not result.success
        assert result.error_code == "EXECUTION_ERROR"

    def test_list_tools(self) -> None:
        """Test listing registered tools."""
        server = create_server("test", "1.0.0")

        for name in ["tool1", "tool2", "tool3"]:
            tool = ToolDefinition(name=name, description=f"Tool {name}")
            server.register_tool(tool, lambda: {})

        tools = server.list_tools()

        assert len(tools) == 3
        assert all("name" in t and "description" in t for t in tools)

    def test_manifest(self) -> None:
        """Test server manifest generation."""
        server = create_server("my-server", "2.0.0")
        tool = ToolDefinition(name="test", description="Test tool")
        server.register_tool(tool, lambda: {})

        manifest = server.to_manifest()

        assert manifest["name"] == "my-server"
        assert manifest["version"] == "2.0.0"
        assert len(manifest["tools"]) == 1


class TestToolDefinitionChecks:
    """Tests for tool definition linting."""

    def test_check_good_tool(self) -> None:
        """Test checking a well-defined tool."""
        tool = ToolDefinition(
            name="search_documents",
            description="Search documents in the knowledge base by keyword or semantic similarity.",
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="Search query",
                    required=True,
                    min_length=1,
                    max_length=500,
                ),
                ToolParameter(
                    name="limit",
                    type="integer",
                    description="Max results",
                    minimum=1,
                    maximum=100,
                    default=10,
                ),
            ],
        )

        issues = check_tool_definition(tool)

        assert len(issues) == 0

    def test_check_bad_name(self) -> None:
        """Test checking tool with bad name."""
        tool = ToolDefinition(
            name="123-bad-name!",
            description="A tool with a bad name",
        )

        issues = check_tool_definition(tool)

        assert any("name" in issue.lower() for issue in issues)

    def test_check_short_description(self) -> None:
        """Test checking tool with short description."""
        tool = ToolDefinition(
            name="test",
            description="Does stuff",
        )

        issues = check_tool_definition(tool)

        assert any("description" in issue.lower() for issue in issues)

    def test_check_unconstrained_string(self) -> None:
        """Test checking unconstrained string parameter."""
        tool = ToolDefinition(
            name="test",
            description="A test tool that does something useful",
            parameters=[
                ToolParameter(
                    name="input",
                    type="string",
                    description="User input",
                    required=True,
                ),
            ],
        )

        issues = check_tool_definition(tool)

        assert any("unconstrained" in issue.lower() for issue in issues)


class TestExampleGeneration:
    """Tests for example input generation."""

    def test_generate_basic_example(self) -> None:
        """Test generating example for basic tool."""
        tool = ToolDefinition(
            name="test",
            description="Test tool",
            parameters=[
                ToolParameter(
                    name="query", type="string", description="Query", required=True
                ),
                ToolParameter(
                    name="limit",
                    type="integer",
                    description="Limit",
                    default=10,
                ),
            ],
        )

        example = generate_example_input(tool)

        assert "query" in example
        assert isinstance(example["query"], str)
        # limit has default, might not be in example

    def test_generate_example_with_enum(self) -> None:
        """Test generating example with enum."""
        tool = ToolDefinition(
            name="test",
            description="Test tool",
            parameters=[
                ToolParameter(
                    name="status",
                    type="string",
                    description="Status",
                    enum=["active", "inactive"],
                    required=True,
                ),
            ],
        )

        example = generate_example_input(tool)

        assert example["status"] == "active"  # First enum value

    def test_generate_example_with_format(self) -> None:
        """Test generating example with format hints."""
        tool = ToolDefinition(
            name="test",
            description="Test tool",
            parameters=[
                ToolParameter(
                    name="email",
                    type="string",
                    description="Email",
                    format="email",
                    required=True,
                ),
            ],
        )

        example = generate_example_input(tool)

        assert "@" in example["email"]
