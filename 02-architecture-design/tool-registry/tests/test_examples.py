"""Tests for Tool Registry examples."""

import pytest

from tool_registry import (
    Middleware,
    ToolRegistry,
    ToolSchema,
    ValidationError,
    tool,
)
from tool_registry.exceptions import PermissionDeniedError, ToolNotFoundError


class TestToolDecorator:
    """Tests for the @tool decorator."""

    def test_tool_decorator_creates_tool(self) -> None:
        """Test that decorator creates a Tool object."""

        @tool(name="test_tool", description="A test tool")
        async def my_func(x: int) -> int:
            return x * 2

        assert my_func.name == "test_tool"
        assert my_func.description == "A test tool"
        assert callable(my_func.func)

    def test_tool_decorator_uses_function_name(self) -> None:
        """Test that decorator uses function name as default."""

        @tool()
        async def some_function() -> str:
            return "test"

        assert some_function.name == "some_function"

    def test_tool_decorator_uses_docstring(self) -> None:
        """Test that decorator uses docstring as description."""

        @tool()
        async def documented_func() -> str:
            """This is the description."""
            return "test"

        assert documented_func.description == "This is the description."


class TestToolSchema:
    """Tests for ToolSchema."""

    def test_schema_validation_passes(self) -> None:
        """Test that valid input passes validation."""
        schema = ToolSchema(
            input={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            }
        )

        # Should not raise
        schema.validate_input("test", {"name": "Alice"})

    def test_schema_validation_fails_missing_required(self) -> None:
        """Test that missing required field fails validation."""
        schema = ToolSchema(
            input={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            }
        )

        with pytest.raises(ValidationError) as exc_info:
            schema.validate_input("test", {})

        assert "name" in str(exc_info.value)

    def test_schema_validation_fails_wrong_type(self) -> None:
        """Test that wrong type fails validation."""
        schema = ToolSchema(
            input={
                "type": "object",
                "properties": {"count": {"type": "integer"}},
            }
        )

        with pytest.raises(ValidationError):
            schema.validate_input("test", {"count": "not an integer"})


class TestToolRegistry:
    """Tests for ToolRegistry."""

    @pytest.fixture
    def registry(self) -> ToolRegistry:
        """Create a fresh registry for each test."""
        return ToolRegistry(validate_inputs=False)

    @pytest.mark.asyncio
    async def test_register_and_invoke(self, registry: ToolRegistry) -> None:
        """Test registering and invoking a tool."""

        @tool(name="double")
        async def double(x: int) -> int:
            return x * 2

        registry.register(double)
        result = await registry.invoke("double", {"x": 21})

        assert result == 42

    @pytest.mark.asyncio
    async def test_invoke_nonexistent_raises(self, registry: ToolRegistry) -> None:
        """Test that invoking nonexistent tool raises error."""
        with pytest.raises(ToolNotFoundError):
            await registry.invoke("nonexistent", {})

    def test_duplicate_registration_raises(self, registry: ToolRegistry) -> None:
        """Test that duplicate registration raises error."""

        @tool(name="dup")
        async def dup1() -> None:
            pass

        @tool(name="dup")
        async def dup2() -> None:
            pass

        registry.register(dup1)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(dup2)

    def test_list_tools(self, registry: ToolRegistry) -> None:
        """Test listing registered tools."""

        @tool(name="a")
        async def tool_a() -> None:
            pass

        @tool(name="b")
        async def tool_b() -> None:
            pass

        registry.register(tool_a)
        registry.register(tool_b)

        tools = registry.list_tools()
        names = [t.name for t in tools]

        assert "a" in names
        assert "b" in names

    def test_find_by_tag(self, registry: ToolRegistry) -> None:
        """Test finding tools by tag."""

        @tool(name="tagged", tags=["special", "test"])
        async def tagged_tool() -> None:
            pass

        @tool(name="untagged")
        async def untagged_tool() -> None:
            pass

        registry.register(tagged_tool)
        registry.register(untagged_tool)

        found = registry.find_by_tag("special")
        assert len(found) == 1
        assert found[0].name == "tagged"


class TestPermissions:
    """Tests for permission-based access control."""

    @pytest.fixture
    def registry_with_permissions(self) -> ToolRegistry:
        """Create registry with permission-protected tool."""
        registry = ToolRegistry(validate_inputs=False)

        @tool(name="admin_only", permissions=["admin"])
        async def admin_tool() -> str:
            return "admin access"

        @tool(name="public")
        async def public_tool() -> str:
            return "public access"

        registry.register(admin_tool)
        registry.register(public_tool)

        return registry

    def test_can_invoke_with_permission(
        self, registry_with_permissions: ToolRegistry
    ) -> None:
        """Test permission check passes with correct permission."""
        assert registry_with_permissions.can_invoke("admin_only", ["admin"])
        assert registry_with_permissions.can_invoke("admin_only", ["admin", "user"])

    def test_cannot_invoke_without_permission(
        self, registry_with_permissions: ToolRegistry
    ) -> None:
        """Test permission check fails without permission."""
        assert not registry_with_permissions.can_invoke("admin_only", ["user"])
        assert not registry_with_permissions.can_invoke("admin_only", [])

    def test_public_tool_no_permission_needed(
        self, registry_with_permissions: ToolRegistry
    ) -> None:
        """Test public tool needs no permissions."""
        assert registry_with_permissions.can_invoke("public", [])

    @pytest.mark.asyncio
    async def test_invoke_with_permissions_denied(
        self, registry_with_permissions: ToolRegistry
    ) -> None:
        """Test that invoke raises when permissions denied."""
        with pytest.raises(PermissionDeniedError):
            await registry_with_permissions.invoke(
                "admin_only", {}, user_permissions=["user"]
            )


class TestMiddleware:
    """Tests for middleware functionality."""

    @pytest.mark.asyncio
    async def test_middleware_is_called(self) -> None:
        """Test that middleware is called during invocation."""
        called = []

        class TestMiddleware(Middleware):
            async def __call__(self, tool, params, next):
                called.append("before")
                result = await next(tool, params)
                called.append("after")
                return result

        registry = ToolRegistry(validate_inputs=False)
        registry.use(TestMiddleware())

        @tool(name="test")
        async def test_func() -> str:
            called.append("execute")
            return "done"

        registry.register(test_func)
        await registry.invoke("test", {})

        assert called == ["before", "execute", "after"]

    @pytest.mark.asyncio
    async def test_middleware_can_modify_result(self) -> None:
        """Test that middleware can modify the result."""

        class DoubleMiddleware(Middleware):
            async def __call__(self, tool, params, next):
                result = await next(tool, params)
                return result * 2

        registry = ToolRegistry(validate_inputs=False)
        registry.use(DoubleMiddleware())

        @tool(name="get_number")
        async def get_number() -> int:
            return 21

        registry.register(get_number)
        result = await registry.invoke("get_number", {})

        assert result == 42


class TestToolExecution:
    """Tests for tool execution."""

    @pytest.mark.asyncio
    async def test_async_tool_execution(self) -> None:
        """Test executing async tool."""

        @tool(name="async_tool")
        async def async_func(x: int) -> int:
            return x + 1

        result = await async_func.execute({"x": 5})
        assert result == 6

    @pytest.mark.asyncio
    async def test_sync_tool_execution(self) -> None:
        """Test executing sync tool."""

        @tool(name="sync_tool")
        def sync_func(x: int) -> int:
            return x + 1

        result = await sync_func.execute({"x": 5})
        assert result == 6


class TestToolSerialization:
    """Tests for tool serialization."""

    def test_tool_to_dict(self) -> None:
        """Test converting tool to dictionary."""

        @tool(name="serializable", description="A tool", tags=["test"])
        async def serializable_func(x: int) -> int:
            return x

        data = serializable_func.to_dict()

        assert data["name"] == "serializable"
        assert data["description"] == "A tool"
        assert data["tags"] == ["test"]
        assert "schema" in data

    def test_get_signature(self) -> None:
        """Test getting tool signature."""

        @tool(
            name="sig_test",
            description="Test signature",
            schema=ToolSchema(
                input={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"},
                    },
                    "required": ["name"],
                }
            ),
        )
        async def sig_func(name: str, age: int = 0) -> str:
            return f"{name}: {age}"

        sig = sig_func.get_signature()

        assert sig["name"] == "sig_test"
        assert sig["description"] == "Test signature"
        assert "name" in sig["parameters"]
        assert "age" in sig["parameters"]
        assert sig["required"] == ["name"]
