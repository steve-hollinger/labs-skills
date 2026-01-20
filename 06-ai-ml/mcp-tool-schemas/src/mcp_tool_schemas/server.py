"""MCP Tool Server implementation."""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from mcp_tool_schemas.schema import ToolDefinition, ToolResult
from mcp_tool_schemas.validation import ValidationError, validate_input


@dataclass
class RegisteredTool:
    """A tool registered with the server."""

    definition: ToolDefinition
    handler: Callable[..., Any]


@dataclass
class ToolServer:
    """MCP Tool Server that manages tool registration and execution.

    This is a simplified implementation demonstrating the core concepts
    of an MCP tool server.
    """

    name: str
    version: str = "1.0.0"
    tools: dict[str, RegisteredTool] = field(default_factory=dict)

    def register_tool(
        self,
        definition: ToolDefinition,
        handler: Callable[..., Any],
    ) -> None:
        """Register a tool with the server.

        Args:
            definition: The tool's schema definition
            handler: Function to call when the tool is invoked
        """
        if definition.name in self.tools:
            raise ValueError(f"Tool '{definition.name}' is already registered")

        self.tools[definition.name] = RegisteredTool(
            definition=definition,
            handler=handler,
        )

    def tool(
        self,
        definition: ToolDefinition,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to register a tool handler.

        Usage:
            @server.tool(my_tool_definition)
            def my_handler(param1: str, param2: int) -> dict:
                return {"result": "value"}
        """
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.register_tool(definition, func)
            return func

        return decorator

    def list_tools(self) -> list[dict[str, Any]]:
        """List all registered tools in MCP format."""
        return [
            tool.definition.to_json_schema()
            for tool in self.tools.values()
        ]

    def get_tool(self, name: str) -> ToolDefinition | None:
        """Get a tool definition by name."""
        if name in self.tools:
            return self.tools[name].definition
        return None

    def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """Call a tool with the given arguments.

        Args:
            name: Name of the tool to call
            arguments: Input arguments for the tool

        Returns:
            ToolResult with success/error information
        """
        # Check if tool exists
        if name not in self.tools:
            return ToolResult.error_result(
                f"Tool '{name}' not found",
                error_code="TOOL_NOT_FOUND",
            )

        registered_tool = self.tools[name]

        # Validate input
        try:
            validated_args = validate_input(
                registered_tool.definition,
                arguments,
                apply_defaults=True,
            )
        except ValidationError as e:
            return ToolResult.error_result(
                str(e),
                error_code="VALIDATION_ERROR",
                metadata={"validation_errors": e.errors},
            )

        # Call the handler
        try:
            result = registered_tool.handler(**validated_args)
            return ToolResult.success_result(result)
        except Exception as e:
            return ToolResult.error_result(
                str(e),
                error_code="EXECUTION_ERROR",
            )

    def to_manifest(self) -> dict[str, Any]:
        """Generate MCP server manifest."""
        return {
            "name": self.name,
            "version": self.version,
            "tools": self.list_tools(),
        }


def create_server(name: str, version: str = "1.0.0") -> ToolServer:
    """Create a new MCP tool server.

    Args:
        name: Server name
        version: Server version

    Returns:
        Configured ToolServer instance
    """
    return ToolServer(name=name, version=version)
