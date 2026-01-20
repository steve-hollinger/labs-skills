"""Core schema definitions for MCP tools."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolParameter:
    """Definition of a tool parameter.

    Represents a single parameter that a tool accepts, including its
    type, constraints, and documentation.
    """

    name: str
    type: str  # string, integer, number, boolean, array, object
    description: str
    required: bool = False
    default: Any = None
    enum: list[Any] | None = None

    # String constraints
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    format: str | None = None  # date, date-time, email, uri, etc.

    # Number constraints
    minimum: float | None = None
    maximum: float | None = None
    exclusive_minimum: float | None = None
    exclusive_maximum: float | None = None
    multiple_of: float | None = None

    # Array constraints
    items: dict[str, Any] | None = None
    min_items: int | None = None
    max_items: int | None = None
    unique_items: bool | None = None

    # Object constraints
    properties: dict[str, dict[str, Any]] | None = None
    additional_properties: bool | dict[str, Any] | None = None

    def to_json_schema(self) -> dict[str, Any]:
        """Convert parameter to JSON Schema format."""
        schema: dict[str, Any] = {
            "type": self.type,
            "description": self.description,
        }

        # Add default if specified
        if self.default is not None:
            schema["default"] = self.default

        # Add enum if specified
        if self.enum is not None:
            schema["enum"] = self.enum

        # String constraints
        if self.min_length is not None:
            schema["minLength"] = self.min_length
        if self.max_length is not None:
            schema["maxLength"] = self.max_length
        if self.pattern is not None:
            schema["pattern"] = self.pattern
        if self.format is not None:
            schema["format"] = self.format

        # Number constraints
        if self.minimum is not None:
            schema["minimum"] = self.minimum
        if self.maximum is not None:
            schema["maximum"] = self.maximum
        if self.exclusive_minimum is not None:
            schema["exclusiveMinimum"] = self.exclusive_minimum
        if self.exclusive_maximum is not None:
            schema["exclusiveMaximum"] = self.exclusive_maximum
        if self.multiple_of is not None:
            schema["multipleOf"] = self.multiple_of

        # Array constraints
        if self.items is not None:
            schema["items"] = self.items
        if self.min_items is not None:
            schema["minItems"] = self.min_items
        if self.max_items is not None:
            schema["maxItems"] = self.max_items
        if self.unique_items is not None:
            schema["uniqueItems"] = self.unique_items

        # Object constraints
        if self.properties is not None:
            schema["properties"] = self.properties
        if self.additional_properties is not None:
            schema["additionalProperties"] = self.additional_properties

        return schema


@dataclass
class ToolDefinition:
    """Complete definition of an MCP tool.

    Includes the tool's name, description, parameters, and optional
    return type specification.
    """

    name: str
    description: str
    parameters: list[ToolParameter] = field(default_factory=list)
    returns: dict[str, Any] | None = None

    def to_json_schema(self) -> dict[str, Any]:
        """Convert tool definition to MCP JSON Schema format."""
        # Build properties and required list
        properties: dict[str, Any] = {}
        required: list[str] = []

        for param in self.parameters:
            properties[param.name] = param.to_json_schema()
            if param.required:
                required.append(param.name)

        # Build input schema
        input_schema: dict[str, Any] = {
            "type": "object",
            "properties": properties,
        }

        if required:
            input_schema["required"] = required

        # Build complete tool schema
        tool_schema: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "inputSchema": input_schema,
        }

        return tool_schema

    def get_input_schema(self) -> dict[str, Any]:
        """Get just the input schema for validation."""
        return self.to_json_schema()["inputSchema"]

    def get_required_parameters(self) -> list[str]:
        """Get list of required parameter names."""
        return [p.name for p in self.parameters if p.required]

    def get_optional_parameters(self) -> list[str]:
        """Get list of optional parameter names."""
        return [p.name for p in self.parameters if not p.required]


@dataclass
class ToolResult:
    """Result from a tool execution.

    Wraps the tool output with metadata about the execution.
    """

    success: bool
    data: Any | None = None
    error: str | None = None
    error_code: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary format."""
        result: dict[str, Any] = {
            "success": self.success,
        }

        if self.success:
            result["data"] = self.data
        else:
            result["error"] = self.error
            if self.error_code:
                result["error_code"] = self.error_code

        if self.metadata:
            result["metadata"] = self.metadata

        return result

    @classmethod
    def success_result(
        cls,
        data: Any,
        metadata: dict[str, Any] | None = None,
    ) -> "ToolResult":
        """Create a success result."""
        return cls(
            success=True,
            data=data,
            metadata=metadata or {},
        )

    @classmethod
    def error_result(
        cls,
        error: str,
        error_code: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "ToolResult":
        """Create an error result."""
        return cls(
            success=False,
            error=error,
            error_code=error_code,
            metadata=metadata or {},
        )


def create_tool(
    name: str,
    description: str,
    **parameters: ToolParameter,
) -> ToolDefinition:
    """Convenience function to create a tool definition.

    Args:
        name: Tool name
        description: Tool description
        **parameters: Keyword arguments mapping parameter names to ToolParameter

    Returns:
        ToolDefinition with the specified parameters
    """
    param_list = []
    for param_name, param in parameters.items():
        # Update name if not set
        if param.name != param_name:
            param = ToolParameter(
                name=param_name,
                type=param.type,
                description=param.description,
                required=param.required,
                default=param.default,
                enum=param.enum,
                min_length=param.min_length,
                max_length=param.max_length,
                pattern=param.pattern,
                format=param.format,
                minimum=param.minimum,
                maximum=param.maximum,
                exclusive_minimum=param.exclusive_minimum,
                exclusive_maximum=param.exclusive_maximum,
                multiple_of=param.multiple_of,
                items=param.items,
                min_items=param.min_items,
                max_items=param.max_items,
                unique_items=param.unique_items,
                properties=param.properties,
                additional_properties=param.additional_properties,
            )
        param_list.append(param)

    return ToolDefinition(
        name=name,
        description=description,
        parameters=param_list,
    )
