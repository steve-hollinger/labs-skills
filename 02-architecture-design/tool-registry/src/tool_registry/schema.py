"""Schema definition and validation for tools."""

from dataclasses import dataclass, field
from typing import Any

import jsonschema
from jsonschema import Draft7Validator

from tool_registry.exceptions import ValidationError


@dataclass
class ToolSchema:
    """Schema definition for tool inputs and outputs.

    Uses JSON Schema format for defining the structure of inputs and outputs.

    Example:
        schema = ToolSchema(
            input={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "default": 10},
                },
                "required": ["query"],
            },
            output={
                "type": "array",
                "items": {"type": "object"},
            },
        )
    """

    input: dict[str, Any] = field(default_factory=lambda: {"type": "object"})
    output: dict[str, Any] = field(default_factory=lambda: {})

    def __post_init__(self) -> None:
        """Validate that schemas are valid JSON Schema."""
        # Ensure input is an object type if not specified
        if "type" not in self.input:
            self.input["type"] = "object"

        # Validate schemas are valid JSON Schema
        Draft7Validator.check_schema(self.input)
        if self.output:
            Draft7Validator.check_schema(self.output)

    def validate_input(self, tool_name: str, params: dict[str, Any]) -> None:
        """Validate input parameters against the schema.

        Args:
            tool_name: Name of the tool (for error messages)
            params: Parameters to validate

        Raises:
            ValidationError: If validation fails
        """
        validator = Draft7Validator(self.input)
        errors = list(validator.iter_errors(params))

        if errors:
            error_list = []
            for error in errors:
                path = ".".join(str(p) for p in error.absolute_path) or "root"
                error_list.append({
                    "field": path,
                    "message": error.message,
                })
            raise ValidationError(tool_name, error_list)

    def validate_output(self, tool_name: str, result: Any) -> None:
        """Validate output against the schema.

        Args:
            tool_name: Name of the tool (for error messages)
            result: Result to validate

        Raises:
            ValidationError: If validation fails
        """
        if not self.output:
            return  # No output schema defined

        validator = Draft7Validator(self.output)
        errors = list(validator.iter_errors(result))

        if errors:
            error_list = []
            for error in errors:
                path = ".".join(str(p) for p in error.absolute_path) or "root"
                error_list.append({
                    "field": path,
                    "message": error.message,
                })
            raise ValidationError(tool_name, error_list)

    def get_input_properties(self) -> dict[str, Any]:
        """Get the input property definitions."""
        return self.input.get("properties", {})

    def get_required_inputs(self) -> list[str]:
        """Get the list of required input parameters."""
        return self.input.get("required", [])

    def to_dict(self) -> dict[str, Any]:
        """Convert schema to dictionary representation."""
        return {
            "input": self.input,
            "output": self.output,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolSchema":
        """Create schema from dictionary representation."""
        return cls(
            input=data.get("input", {"type": "object"}),
            output=data.get("output", {}),
        )


def create_schema_from_function(func: Any) -> ToolSchema:
    """Create a schema from function type hints.

    This is a simplified version that creates basic schemas from
    function annotations. For complex cases, define schemas explicitly.

    Args:
        func: The function to create a schema from

    Returns:
        A ToolSchema based on the function's type hints
    """
    import inspect
    from typing import get_type_hints

    # Get function signature
    sig = inspect.signature(func)
    hints = get_type_hints(func) if hasattr(func, "__annotations__") else {}

    # Build input schema
    properties: dict[str, Any] = {}
    required: list[str] = []

    for param_name, param in sig.parameters.items():
        if param_name in ("self", "cls"):
            continue

        param_schema: dict[str, Any] = {}
        param_type = hints.get(param_name)

        # Map Python types to JSON Schema types
        if param_type is str:
            param_schema["type"] = "string"
        elif param_type is int:
            param_schema["type"] = "integer"
        elif param_type is float:
            param_schema["type"] = "number"
        elif param_type is bool:
            param_schema["type"] = "boolean"
        elif param_type is list:
            param_schema["type"] = "array"
        elif param_type is dict:
            param_schema["type"] = "object"
        else:
            # Default to any type
            param_schema = {}

        # Check if parameter has a default
        if param.default is inspect.Parameter.empty:
            required.append(param_name)
        else:
            param_schema["default"] = param.default

        properties[param_name] = param_schema

    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": properties,
    }
    if required:
        input_schema["required"] = required

    # Build output schema from return type
    output_schema: dict[str, Any] = {}
    return_type = hints.get("return")
    if return_type is str:
        output_schema["type"] = "string"
    elif return_type is int:
        output_schema["type"] = "integer"
    elif return_type is float:
        output_schema["type"] = "number"
    elif return_type is bool:
        output_schema["type"] = "boolean"
    elif return_type is list:
        output_schema["type"] = "array"
    elif return_type is dict:
        output_schema["type"] = "object"

    return ToolSchema(input=input_schema, output=output_schema)
