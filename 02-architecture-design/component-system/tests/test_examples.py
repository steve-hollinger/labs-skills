"""Tests for Component System examples."""

import pytest

from component_system import Component, Lifecycle, LifecycleError, Registry, Requires
from component_system.registry import DependencyError


class TestLifecycle:
    """Tests for component lifecycle management."""

    @pytest.mark.asyncio
    async def test_initial_state_is_created(self) -> None:
        """Test that new components start in CREATED state."""

        class SimpleComponent(Component):
            name = "simple"

        component = SimpleComponent()
        assert component.state == Lifecycle.CREATED

    @pytest.mark.asyncio
    async def test_lifecycle_transitions(self) -> None:
        """Test valid lifecycle transitions."""

        class SimpleComponent(Component):
            name = "simple"

        component = SimpleComponent()

        await component.initialize()
        assert component.state == Lifecycle.INITIALIZED

        await component.start()
        assert component.state == Lifecycle.STARTED

        await component.stop()
        assert component.state == Lifecycle.STOPPED

    @pytest.mark.asyncio
    async def test_invalid_transition_raises_error(self) -> None:
        """Test that invalid transitions raise LifecycleError."""

        class SimpleComponent(Component):
            name = "simple"

        component = SimpleComponent()

        # Can't go from CREATED directly to STARTED
        with pytest.raises(LifecycleError):
            await component.start()

    @pytest.mark.asyncio
    async def test_component_config(self) -> None:
        """Test that component receives configuration."""

        class ConfiguredComponent(Component):
            name = "configured"

        config = {"key": "value", "number": 42}
        component = ConfiguredComponent(config)

        assert component.config == config
        assert component.config["key"] == "value"
        assert component.config["number"] == 42


class TestRegistry:
    """Tests for the component registry."""

    @pytest.mark.asyncio
    async def test_register_and_get(self) -> None:
        """Test registering and retrieving components."""

        class TestComponent(Component):
            name = "test"

        registry = Registry()
        registry.register(TestComponent)

        component = registry.get(TestComponent)
        assert isinstance(component, TestComponent)

    @pytest.mark.asyncio
    async def test_duplicate_registration_raises_error(self) -> None:
        """Test that duplicate registration raises ValueError."""

        class TestComponent(Component):
            name = "test"

        registry = Registry()
        registry.register(TestComponent)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(TestComponent)

    @pytest.mark.asyncio
    async def test_get_unregistered_raises_error(self) -> None:
        """Test that getting unregistered component raises KeyError."""

        class TestComponent(Component):
            name = "test"

        registry = Registry()

        with pytest.raises(KeyError, match="not registered"):
            registry.get(TestComponent)

    @pytest.mark.asyncio
    async def test_has_component(self) -> None:
        """Test checking if component is registered."""

        class TestComponent(Component):
            name = "test"

        registry = Registry()
        assert not registry.has(TestComponent)

        registry.register(TestComponent)
        assert registry.has(TestComponent)

    @pytest.mark.asyncio
    async def test_start_all_initializes_and_starts(self) -> None:
        """Test that start_all initializes and starts components."""

        class TestComponent(Component):
            name = "test"
            started = False

            async def start(self) -> None:
                await super().start()
                self.started = True

        registry = Registry()
        registry.register(TestComponent)

        await registry.start_all()

        component = registry.get(TestComponent)
        assert component.state == Lifecycle.STARTED
        assert component.started

    @pytest.mark.asyncio
    async def test_stop_all_stops_components(self) -> None:
        """Test that stop_all stops all components."""

        class TestComponent(Component):
            name = "test"
            stopped = False

            async def stop(self) -> None:
                self.stopped = True
                await super().stop()

        registry = Registry()
        registry.register(TestComponent)

        await registry.start_all()
        await registry.stop_all()

        component = registry.get(TestComponent)
        assert component.state == Lifecycle.STOPPED
        assert component.stopped


class TestDependencyInjection:
    """Tests for dependency injection."""

    @pytest.mark.asyncio
    async def test_dependency_injection(self) -> None:
        """Test that dependencies are injected correctly."""

        class DatabaseComponent(Component):
            name = "database"
            connected = False

            async def start(self) -> None:
                await super().start()
                self.connected = True

        class ServiceComponent(Component):
            name = "service"
            database: DatabaseComponent = Requires()

        registry = Registry()
        registry.register(DatabaseComponent)
        registry.register(ServiceComponent)

        await registry.start_all()

        service = registry.get(ServiceComponent)
        assert service.database is not None
        assert service.database.connected

    @pytest.mark.asyncio
    async def test_dependency_order(self) -> None:
        """Test that dependencies start before dependents."""
        start_order: list[str] = []

        class FirstComponent(Component):
            name = "first"

            async def start(self) -> None:
                await super().start()
                start_order.append("first")

        class SecondComponent(Component):
            name = "second"
            first: FirstComponent = Requires()

            async def start(self) -> None:
                await super().start()
                start_order.append("second")

        registry = Registry()
        # Register in reverse order
        registry.register(SecondComponent)
        registry.register(FirstComponent)

        await registry.start_all()

        # First should start before Second
        assert start_order == ["first", "second"]

    @pytest.mark.asyncio
    async def test_missing_dependency_raises_error(self) -> None:
        """Test that missing dependencies raise DependencyError."""

        class DatabaseComponent(Component):
            name = "database"

        class ServiceComponent(Component):
            name = "service"
            database: DatabaseComponent = Requires()

        registry = Registry()
        registry.register(ServiceComponent)
        # Note: DatabaseComponent not registered

        with pytest.raises(DependencyError, match="Missing dependency"):
            await registry.start_all()

    @pytest.mark.asyncio
    async def test_circular_dependency_raises_error(self) -> None:
        """Test that circular dependencies raise DependencyError."""

        # We need to use forward references for circular deps
        class ComponentA(Component):
            name = "a"
            b: "ComponentB" = Requires()

        class ComponentB(Component):
            name = "b"
            a: ComponentA = Requires()

        registry = Registry()
        registry.register(ComponentA)
        registry.register(ComponentB)

        with pytest.raises(DependencyError, match="Circular dependency"):
            await registry.start_all()


class TestComponentRepr:
    """Tests for component string representation."""

    def test_repr(self) -> None:
        """Test component repr."""

        class MyComponent(Component):
            name = "my-component"

        component = MyComponent()
        repr_str = repr(component)

        assert "MyComponent" in repr_str
        assert "my-component" in repr_str
        assert "CREATED" in repr_str


class TestIterator:
    """Tests for registry iteration."""

    def test_iterate_components(self) -> None:
        """Test iterating over registered components."""

        class ComponentA(Component):
            name = "a"

        class ComponentB(Component):
            name = "b"

        registry = Registry()
        registry.register(ComponentA)
        registry.register(ComponentB)

        components = list(registry)
        assert len(components) == 2
        names = {c.name for c in components}
        assert names == {"a", "b"}
