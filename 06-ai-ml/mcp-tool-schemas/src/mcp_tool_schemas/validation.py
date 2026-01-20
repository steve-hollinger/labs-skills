"""Schema validation for MCP tool inputs and outputs."""

from typing import Any

import jsonschema
from jsonschema import Draft7Validator, FormatChecker

from mcp_tool_schemas.schema import ToolDefinition


class ValidationError(Exception):
    """Raised when input validation fails."""

    def __init__(self, message: str, errors: list[str] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.errors = errors or []


def validate_input(
    tool: ToolDefinition,
    input_data: dict[str, Any],
    apply_defaults: bool = True,
) -> dict[str, Any]:
    """Validate input data against a tool's schema.

    Args:
        tool: The tool definition to validate against
        input_data: User-provided input data
        apply_defaults: Whether to fill in default values

    Returns:
        Validated input data (with defaults applied if requested)

    Raises:
        ValidationError: If the input doesn't match the schema
    """
    schema = tool.get_input_schema()

    # Create validator with format checking
    validator = Draft7Validator(
        schema,
        format_checker=FormatChecker(),
    )

    # Collect all errors
    errors: list[str] = []

    for error in validator.iter_errors(input_data):
        path = ".".join(str(p) for p in error.absolute_path)
        if path:
            errors.append(f"{path}: {error.message}")
        else:
            errors.append(error.message)

    if errors:
        raise ValidationError(
            f"Invalid input for tool '{tool.name}': {'; '.join(errors)}",
            errors=errors,
        )

    # Apply defaults if requested
    if apply_defaults:
        return _apply_defaults(tool, input_data)

    return input_data


def _apply_defaults(tool: ToolDefinition, data: dict[str, Any]) -> dict[str, Any]:
    """Apply default values from tool definition to input data."""
    result = data.copy()

    for param in tool.parameters:
        if param.name not in result and param.default is not None:
            result[param.name] = param.default

    return result


def validate_output(
    schema: dict[str, Any],
    output_data: Any,
) -> Any:
    """Validate output data against a schema.

    Args:
        schema: JSON Schema to validate against
        output_data: Tool output to validate

    Returns:
        The validated output data

    Raises:
        ValidationError: If the output doesn't match the schema
    """
    validator = Draft7Validator(
        schema,
        format_checker=FormatChecker(),
    )

    errors: list[str] = []

    for error in validator.iter_errors(output_data):
        path = ".".join(str(p) for p in error.absolute_path)
        if path:
            errors.append(f"{path}: {error.message}")
        else:
            errors.append(error.message)

    if errors:
        raise ValidationError(
            f"Invalid output: {'; '.join(errors)}",
            errors=errors,
        )

    return output_data


def validate_schema(schema: dict[str, Any]) -> list[str]:
    """Validate that a schema is valid JSON Schema.

    Args:
        schema: The schema to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors: list[str] = []

    try:
        # Try to create a validator - this checks schema validity
        Draft7Validator.check_schema(schema)
    except jsonschema.SchemaError as e:
        errors.append(str(e.message))

    return errors


def check_tool_definition(tool: ToolDefinition) -> list[str]:
    """Check a tool definition for common issues.

    Performs lint-like checks on a tool definition to catch
    common mistakes and best practice violations.

    Args:
        tool: The tool definition to check

    Returns:
        List of warnings/issues found
    """
    issues: list[str] = []

    # Check name
    if not tool.name:
        issues.append("Tool name is empty")
    elif not tool.name.replace("_", "").isalnum():
        issues.append(f"Tool name '{tool.name}' should use only alphanumeric characters and underscores")
    elif tool.name[0].isdigit():
        issues.append(f"Tool name '{tool.name}' should not start with a digit")

    # Check description
    if not tool.description:
        issues.append("Tool description is empty")
    elif len(tool.description) < 20:
        issues.append("Tool description is very short - consider adding more detail")
    elif "todo" in tool.description.lower() or "fixme" in tool.description.lower():
        issues.append("Tool description contains TODO/FIXME")

    # Check parameters
    param_names = set()
    for param in tool.parameters:
        # Check for duplicate names
        if param.name in param_names:
            issues.append(f"Duplicate parameter name: {param.name}")
        param_names.add(param.name)

        # Check parameter description
        if not param.description:
            issues.append(f"Parameter '{param.name}' has no description")

        # Check for overly permissive types
        if param.type == "string":
            if (
                param.min_length is None
                and param.max_length is None
                and param.pattern is None
                and param.enum is None
                and param.format is None
            ):
                issues.append(
                    f"Parameter '{param.name}' is an unconstrained string - "
                    "consider adding minLength, maxLength, pattern, enum, or format"
                )

        if param.type in ("integer", "number"):
            if param.minimum is None and param.maximum is None:
                issues.append(
                    f"Parameter '{param.name}' has no range constraints - "
                    "consider adding minimum/maximum"
                )

        if param.type == "array":
            if param.max_items is None:
                issues.append(
                    f"Parameter '{param.name}' is an unbounded array - "
                    "consider adding maxItems"
                )

    # Check for required parameters without descriptions
    required_params = [p for p in tool.parameters if p.required]
    if not required_params:
        # Not necessarily an issue, but worth noting
        pass

    return issues


def generate_example_input(tool: ToolDefinition) -> dict[str, Any]:
    """Generate example input data for a tool.

    Creates sample input that would pass validation, useful for
    documentation and testing.

    Args:
        tool: The tool definition

    Returns:
        Example input dictionary
    """
    example: dict[str, Any] = {}

    for param in tool.parameters:
        if not param.required and param.default is not None:
            continue  # Skip optional params with defaults

        value = _generate_example_value(param)
        example[param.name] = value

    return example


def _generate_example_value(param: Any) -> Any:
    """Generate an example value for a parameter."""
    # Use enum first choice if available
    if param.enum:
        return param.enum[0]

    # Use default if available
    if param.default is not None:
        return param.default

    # Generate based on type
    if param.type == "string":
        if param.format == "email":
            return "user@example.com"
        elif param.format == "uri":
            return "https://example.com"
        elif param.format == "date":
            return "2024-01-15"
        elif param.format == "date-time":
            return "2024-01-15T10:30:00Z"
        elif param.min_length:
            return "x" * param.min_length
        else:
            return "example"

    elif param.type == "integer":
        if param.minimum is not None:
            return int(param.minimum)
        elif param.maximum is not None:
            return int(param.maximum)
        else:
            return 1

    elif param.type == "number":
        if param.minimum is not None:
            return float(param.minimum)
        elif param.maximum is not None:
            return float(param.maximum)
        else:
            return 1.0

    elif param.type == "boolean":
        return True

    elif param.type == "array":
        if param.items:
            return ["item1"]
        return []

    elif param.type == "object":
        if param.properties:
            return {k: "value" for k in param.properties}
        return {}

    return None
