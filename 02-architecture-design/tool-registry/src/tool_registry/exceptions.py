"""Custom exceptions for the tool registry."""

from typing import Any


class ToolError(Exception):
    """Base exception for tool-related errors."""

    pass


class ToolNotFoundError(ToolError):
    """Exception raised when a tool is not found in the registry."""

    def __init__(self, tool_name: str) -> None:
        self.tool_name = tool_name
        super().__init__(f"Tool not found: {tool_name}")


class ValidationError(ToolError):
    """Exception raised when tool input validation fails."""

    def __init__(self, tool_name: str, errors: list[dict[str, Any]]) -> None:
        self.tool_name = tool_name
        self.errors = errors
        error_messages = "; ".join(
            f"{e.get('field', 'unknown')}: {e.get('message', 'validation failed')}"
            for e in errors
        )
        super().__init__(f"Validation failed for {tool_name}: {error_messages}")


class ToolExecutionError(ToolError):
    """Exception raised when tool execution fails."""

    def __init__(self, tool_name: str, original_error: Exception) -> None:
        self.tool_name = tool_name
        self.original_error = original_error
        super().__init__(f"Execution failed for {tool_name}: {original_error}")


class PermissionDeniedError(ToolError):
    """Exception raised when user lacks permission to invoke a tool."""

    def __init__(self, tool_name: str, required_permissions: list[str]) -> None:
        self.tool_name = tool_name
        self.required_permissions = required_permissions
        super().__init__(
            f"Permission denied for {tool_name}. "
            f"Required: {required_permissions}"
        )
