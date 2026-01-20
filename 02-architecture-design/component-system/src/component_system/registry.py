"""Component registry for managing component lifecycle.

This module provides the Registry class that manages component registration,
dependency resolution, and lifecycle orchestration.
"""

from collections.abc import Iterator
from typing import Any, TypeVar

from component_system.component import Component
from component_system.lifecycle import Lifecycle
from component_system.requires import Requires, get_dependencies

T = TypeVar("T", bound=Component)


class DependencyError(Exception):
    """Exception raised for dependency resolution errors."""

    pass


class Registry:
    """Registry for managing components.

    The registry handles:
    - Component registration
    - Dependency resolution and injection
    - Lifecycle management (start/stop in correct order)
    - Component discovery

    Example:
        registry = Registry()
        registry.register(DatabaseComponent, config={"url": "..."})
        registry.register(UserService)

        await registry.start_all()

        user_service = registry.get(UserService)
        # Use user_service...

        await registry.stop_all()
    """

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._components: dict[type[Component], Component] = {}
        self._configs: dict[type[Component], dict[str, Any]] = {}
        self._start_order: list[type[Component]] = []

    def register(
        self,
        component_class: type[T],
        config: dict[str, Any] | None = None,
    ) -> None:
        """Register a component class.

        Args:
            component_class: The component class to register
            config: Optional configuration for the component

        Raises:
            ValueError: If the component is already registered
        """
        if component_class in self._components:
            raise ValueError(f"Component {component_class.__name__} already registered")

        self._configs[component_class] = config or {}

        # Create instance but don't initialize yet
        instance = component_class(config)
        self._components[component_class] = instance

    def get(self, component_class: type[T]) -> T:
        """Get a registered component instance.

        Args:
            component_class: The component class to retrieve

        Returns:
            The component instance

        Raises:
            KeyError: If the component is not registered
        """
        if component_class not in self._components:
            raise KeyError(f"Component {component_class.__name__} not registered")
        return self._components[component_class]  # type: ignore[return-value]

    def has(self, component_class: type[Component]) -> bool:
        """Check if a component is registered.

        Args:
            component_class: The component class to check

        Returns:
            True if registered, False otherwise
        """
        return component_class in self._components

    def __iter__(self) -> Iterator[Component]:
        """Iterate over registered components."""
        return iter(self._components.values())

    def _resolve_dependencies(self) -> list[type[Component]]:
        """Resolve component dependencies and return start order.

        Returns:
            List of component classes in dependency order

        Raises:
            DependencyError: If there's a circular dependency or missing dependency
        """
        resolved: list[type[Component]] = []
        seen: set[type[Component]] = set()
        visiting: set[type[Component]] = set()

        def visit(cls: type[Component]) -> None:
            if cls in resolved:
                return
            if cls in visiting:
                raise DependencyError(f"Circular dependency detected involving {cls.__name__}")

            visiting.add(cls)

            # Get dependencies for this component
            deps = get_dependencies(cls)
            for dep_name, dep_type in deps.items():
                if dep_type not in self._components:
                    # Check if it's optional
                    descriptor = getattr(cls, dep_name, None)
                    if isinstance(descriptor, Requires) and descriptor.optional:
                        continue
                    raise DependencyError(
                        f"Missing dependency: {cls.__name__} requires "
                        f"{dep_type.__name__} but it's not registered"
                    )
                visit(dep_type)

            visiting.remove(cls)
            resolved.append(cls)

        for cls in self._components:
            if cls not in seen:
                visit(cls)
                seen.add(cls)

        return resolved

    def _inject_dependencies(self, component: Component) -> None:
        """Inject dependencies into a component.

        Args:
            component: The component to inject dependencies into
        """
        deps = get_dependencies(type(component))
        for dep_name, dep_type in deps.items():
            if dep_type in self._components:
                dep_instance = self._components[dep_type]
                setattr(component, dep_name, dep_instance)

    async def start_all(self) -> None:
        """Start all registered components in dependency order.

        Components are initialized and started in the order that
        respects their dependencies.

        Raises:
            DependencyError: If dependencies cannot be resolved
        """
        self._start_order = self._resolve_dependencies()

        for cls in self._start_order:
            component = self._components[cls]

            # Inject dependencies before initialization
            self._inject_dependencies(component)

            # Initialize if not already initialized
            if component.state == Lifecycle.CREATED:
                await component.initialize()

            # Start the component
            if component.state == Lifecycle.INITIALIZED:
                await component.start()

    async def stop_all(self) -> None:
        """Stop all components in reverse dependency order.

        Components are stopped in reverse order of how they were started,
        ensuring dependencies are stopped after their dependents.
        """
        # Stop in reverse order
        for cls in reversed(self._start_order):
            component = self._components[cls]
            if component.state == Lifecycle.STARTED:
                try:
                    await component.stop()
                except Exception as e:
                    # Log but continue stopping other components
                    print(f"Error stopping {component.name}: {e}")

    def clear(self) -> None:
        """Clear all registered components.

        This removes all components from the registry. Make sure to
        call stop_all() first if components are running.
        """
        self._components.clear()
        self._configs.clear()
        self._start_order.clear()
