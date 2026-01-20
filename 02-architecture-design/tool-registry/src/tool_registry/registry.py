"""Tool registry for managing tools."""

from typing import Any, Callable

from tool_registry.exceptions import (
    PermissionDeniedError,
    ToolExecutionError,
    ToolNotFoundError,
)
from tool_registry.middleware import Middleware, MiddlewareChain, ValidationMiddleware
from tool_registry.tool import Tool


class ToolRegistry:
    """Registry for managing tools.

    The registry handles:
    - Tool registration and lookup
    - Tool discovery and listing
    - Validated tool invocation
    - Middleware execution

    Example:
        registry = ToolRegistry()

        @registry.tool(name="greet")
        async def greet(name: str) -> str:
            return f"Hello, {name}!"

        result = await registry.invoke("greet", {"name": "Alice"})
    """

    def __init__(self, validate_inputs: bool = True) -> None:
        """Initialize the registry.

        Args:
            validate_inputs: Whether to validate inputs by default
        """
        self._tools: dict[str, Tool] = {}
        self._middleware = MiddlewareChain()

        # Add validation middleware by default
        if validate_inputs:
            self._middleware.use(ValidationMiddleware())

    def register(self, tool: Tool) -> None:
        """Register a tool with the registry.

        Args:
            tool: The tool to register

        Raises:
            ValueError: If a tool with the same name is already registered
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        """Unregister a tool from the registry.

        Args:
            name: The name of the tool to unregister

        Raises:
            ToolNotFoundError: If the tool is not found
        """
        if name not in self._tools:
            raise ToolNotFoundError(name)
        del self._tools[name]

    def get(self, name: str) -> Tool:
        """Get a tool by name.

        Args:
            name: The name of the tool

        Returns:
            The tool

        Raises:
            ToolNotFoundError: If the tool is not found
        """
        if name not in self._tools:
            raise ToolNotFoundError(name)
        return self._tools[name]

    def has(self, name: str) -> bool:
        """Check if a tool is registered.

        Args:
            name: The name of the tool

        Returns:
            True if the tool is registered
        """
        return name in self._tools

    def list_tools(self) -> list[Tool]:
        """List all registered tools.

        Returns:
            List of all registered tools
        """
        return list(self._tools.values())

    def list_tool_names(self) -> list[str]:
        """List names of all registered tools.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def find_by_tag(self, tag: str) -> list[Tool]:
        """Find tools with a specific tag.

        Args:
            tag: The tag to search for

        Returns:
            List of tools with the given tag
        """
        return [t for t in self._tools.values() if tag in t.tags]

    def get_schema(self, name: str) -> dict[str, Any]:
        """Get the schema for a tool.

        Args:
            name: The name of the tool

        Returns:
            The tool's schema as a dictionary

        Raises:
            ToolNotFoundError: If the tool is not found
        """
        tool = self.get(name)
        return tool.schema.to_dict()

    def use(self, middleware: Middleware) -> "ToolRegistry":
        """Add middleware to the registry.

        Args:
            middleware: The middleware to add

        Returns:
            Self for chaining
        """
        self._middleware.use(middleware)
        return self

    def can_invoke(self, name: str, user_permissions: list[str]) -> bool:
        """Check if a user can invoke a tool based on permissions.

        Args:
            name: The name of the tool
            user_permissions: The user's permissions

        Returns:
            True if the user can invoke the tool
        """
        tool = self.get(name)
        if not tool.permissions:
            return True  # No permissions required
        return any(p in user_permissions for p in tool.permissions)

    async def invoke(
        self,
        name: str,
        params: dict[str, Any],
        user_permissions: list[str] | None = None,
    ) -> Any:
        """Invoke a tool by name with the given parameters.

        Args:
            name: The name of the tool to invoke
            params: The input parameters
            user_permissions: Optional user permissions for access control

        Returns:
            The result of the tool execution

        Raises:
            ToolNotFoundError: If the tool is not found
            ValidationError: If input validation fails
            PermissionDeniedError: If user lacks required permissions
            ToolExecutionError: If the tool execution fails
        """
        tool = self.get(name)

        # Check permissions if provided
        if user_permissions is not None and tool.permissions:
            if not self.can_invoke(name, user_permissions):
                raise PermissionDeniedError(name, tool.permissions)

        # Execute through middleware chain
        async def execute(t: Tool, p: dict[str, Any]) -> Any:
            try:
                return await t.execute(p)
            except Exception as e:
                raise ToolExecutionError(t.name, e) from e

        return await self._middleware.execute(tool, params, execute)

    def tool(
        self,
        name: str | None = None,
        description: str | None = None,
        permissions: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> Callable[[Callable[..., Any]], Tool]:
        """Decorator for registering tools.

        This is a convenience method that combines the @tool decorator
        with automatic registration.

        Args:
            name: Tool name (defaults to function name)
            description: Tool description
            permissions: Required permissions
            tags: Tags for categorization

        Returns:
            A decorator that creates and registers the tool

        Example:
            registry = ToolRegistry()

            @registry.tool(name="greet")
            async def greet(name: str) -> str:
                return f"Hello, {name}!"
        """
        from tool_registry.tool import tool as tool_decorator

        def decorator(func: Callable[..., Any]) -> Tool:
            t = tool_decorator(
                name=name,
                description=description,
                permissions=permissions,
                tags=tags,
            )(func)
            self.register(t)
            return t

        return decorator

    def get_tools_json(self) -> list[dict[str, Any]]:
        """Get all tools as JSON-serializable dictionaries.

        This is useful for exposing tools to AI agents or APIs.

        Returns:
            List of tool definitions
        """
        return [tool.get_signature() for tool in self._tools.values()]

    def clear(self) -> None:
        """Remove all registered tools."""
        self._tools.clear()
