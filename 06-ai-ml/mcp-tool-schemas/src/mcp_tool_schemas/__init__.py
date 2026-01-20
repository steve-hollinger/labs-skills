"""MCP Tool Schemas - Define and validate tool schemas for Model Context Protocol.

This module provides tools for creating well-structured MCP tool definitions
with proper JSON Schema validation.
"""

from mcp_tool_schemas.schema import (
    ToolDefinition,
    ToolParameter,
    ToolResult,
)
from mcp_tool_schemas.validation import (
    ValidationError,
    validate_input,
    validate_output,
)

__all__ = [
    "ToolDefinition",
    "ToolParameter",
    "ToolResult",
    "validate_input",
    "validate_output",
    "ValidationError",
]
