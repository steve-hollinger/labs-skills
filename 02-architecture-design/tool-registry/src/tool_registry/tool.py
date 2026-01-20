"""Tool definition and decorator."""

import asyncio
import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

from tool_registry.schema import ToolSchema, create_schema_from_function

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class Tool:
    """A tool with metadata, schema, and execution function.

    Tools are the fundamental unit of the tool registry. Each tool has:
    - A unique name for identification
    - A description for documentation
    - A schema defining inputs and outputs
    - A function that executes the tool
    - Optional permissions for access control

    Example:
        tool = Tool(
            name="search",
            description="Search for documents",
            schema=ToolSchema(...),
            func=search_function,
        )
    """

    name: str
    description: str
    func: Callable[..., Any]
    schema: ToolSchema = field(default_factory=ToolSchema)
    permissions: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    @property
    def is_async(self) -> bool:
        """Check if the tool function is async."""
        return asyncio.iscoroutinefunction(self.func)

    async def execute(self, params: dict[str, Any]) -> Any:
        """Execute the tool with the given parameters.

        Args:
            params: The input parameters for the tool

        Returns:
            The result of the tool execution
        """
        if self.is_async:
            return await self.func(**params)
        else:
            # Run sync function in executor to not block event loop
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: self.func(**params))

    def validate_input(self, params: dict[str, Any]) -> None:
        """Validate input parameters against the tool's schema.

        Args:
            params: The parameters to validate

        Raises:
            ValidationError: If validation fails
        """
        self.schema.validate_input(self.name, params)

    def validate_output(self, result: Any) -> None:
        """Validate output against the tool's schema.

        Args:
            result: The result to validate

        Raises:
            ValidationError: If validation fails
        """
        self.schema.validate_output(self.name, result)

    def to_dict(self) -> dict[str, Any]:
        """Convert tool to dictionary representation.

        This is useful for serialization and documentation generation.
        """
        return {
            "name": self.name,
            "description": self.description,
            "schema": self.schema.to_dict(),
            "permissions": self.permissions,
            "tags": self.tags,
        }

    def get_signature(self) -> dict[str, Any]:
        """Get the tool's signature for documentation.

        Returns a simplified representation of inputs and outputs.
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.schema.get_input_properties(),
            "required": self.schema.get_required_inputs(),
        }


def tool(
    name: str | None = None,
    description: str | None = None,
    schema: ToolSchema | None = None,
    permissions: list[str] | None = None,
    tags: list[str] | None = None,
) -> Callable[[F], Tool]:
    """Decorator for creating tools from functions.

    This decorator transforms a function into a Tool object with metadata,
    schema, and execution capabilities.

    Args:
        name: Tool name (defaults to function name)
        description: Tool description (defaults to function docstring)
        schema: Tool schema (auto-generated from type hints if not provided)
        permissions: Required permissions to invoke this tool
        tags: Tags for categorization and discovery

    Returns:
        A decorator that creates a Tool from the function

    Example:
        @tool(
            name="greet",
            description="Greet a user by name",
        )
        async def greet(name: str) -> str:
            return f"Hello, {name}!"

        # greet is now a Tool object
        result = await greet.execute({"name": "Alice"})
    """

    def decorator(func: F) -> Tool:
        # Get name from function if not provided
        tool_name = name or func.__name__

        # Get description from docstring if not provided
        tool_description = description or (func.__doc__ or "").strip().split("\n")[0]

        # Auto-generate schema from type hints if not provided
        tool_schema = schema or create_schema_from_function(func)

        return Tool(
            name=tool_name,
            description=tool_description,
            func=func,
            schema=tool_schema,
            permissions=permissions or [],
            tags=tags or [],
        )

    return decorator


def from_function(
    func: Callable[..., Any],
    name: str | None = None,
    description: str | None = None,
) -> Tool:
    """Create a Tool from an existing function.

    This is an alternative to the @tool decorator for when you
    can't or don't want to modify the function definition.

    Args:
        func: The function to wrap
        name: Tool name (defaults to function name)
        description: Tool description (defaults to function docstring)

    Returns:
        A Tool wrapping the function
    """
    tool_name = name or func.__name__
    tool_description = description or (func.__doc__ or "").strip().split("\n")[0]
    tool_schema = create_schema_from_function(func)

    return Tool(
        name=tool_name,
        description=tool_description,
        func=func,
        schema=tool_schema,
    )
