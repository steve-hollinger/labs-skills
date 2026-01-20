"""Base component class with lifecycle management.

This module provides the Component base class that all components inherit from.
"""

from abc import ABC
from typing import Any, ClassVar

from component_system.lifecycle import Lifecycle, validate_transition


class Component(ABC):
    """Base class for all components.

    Components are the building blocks of a component-based application.
    They have a defined lifecycle and can declare dependencies on other
    components.

    Example:
        class DatabaseComponent(Component):
            name = "database"

            async def start(self) -> None:
                await super().start()
                self.connection = await connect(self.config["url"])

            async def stop(self) -> None:
                await self.connection.close()
                await super().stop()
    """

    # Component name - should be unique within the registry
    name: ClassVar[str] = "component"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the component.

        Args:
            config: Optional configuration dictionary for this component
        """
        self._config = config or {}
        self._state = Lifecycle.CREATED
        self._injected_deps: dict[str, "Component"] = {}

    @property
    def config(self) -> dict[str, Any]:
        """Get the component's configuration."""
        return self._config

    @property
    def state(self) -> Lifecycle:
        """Get the current lifecycle state."""
        return self._state

    def _transition_to(self, target: Lifecycle) -> None:
        """Transition to a new lifecycle state.

        Args:
            target: The target lifecycle state

        Raises:
            LifecycleError: If the transition is not valid
        """
        validate_transition(self, self._state, target)
        self._state = target

    async def initialize(self) -> None:
        """Initialize the component.

        Called after dependencies are injected but before start().
        Override this to perform setup that doesn't require resources
        to be acquired (validation, configuration parsing, etc.).

        Always call super().initialize() first.
        """
        self._transition_to(Lifecycle.INITIALIZED)

    async def start(self) -> None:
        """Start the component.

        Called to start the component after initialization.
        Override this to acquire resources, open connections, etc.

        Always call super().start() first.
        """
        self._transition_to(Lifecycle.STARTED)

    async def stop(self) -> None:
        """Stop the component.

        Called to stop the component and release resources.
        Override this to close connections, release resources, etc.

        Always call super().stop() at the end (after cleanup).

        Note: This method should not raise exceptions. Log errors
        instead and continue with cleanup.
        """
        self._transition_to(Lifecycle.STOPPED)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name!r}, state={self._state.name})>"
