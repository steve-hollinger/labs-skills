"""Lifecycle management for components.

This module defines the lifecycle states and transitions for components.
"""

from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from component_system.component import Component


class Lifecycle(Enum):
    """Component lifecycle states.

    Components progress through these states in order:
    CREATED -> INITIALIZED -> STARTED -> STOPPED

    State transitions:
    - CREATED: Component instance exists but hasn't been initialized
    - INITIALIZED: Component has been configured, dependencies resolved
    - STARTED: Component is actively running and serving requests
    - STOPPED: Component has been shut down and resources released
    """

    CREATED = auto()
    INITIALIZED = auto()
    STARTED = auto()
    STOPPED = auto()


class LifecycleError(Exception):
    """Exception raised for invalid lifecycle transitions."""

    def __init__(
        self,
        component: "Component",
        current_state: Lifecycle,
        attempted_state: Lifecycle,
        message: str | None = None,
    ) -> None:
        self.component = component
        self.current_state = current_state
        self.attempted_state = attempted_state
        msg = message or (
            f"Invalid lifecycle transition for {component.name}: "
            f"{current_state.name} -> {attempted_state.name}"
        )
        super().__init__(msg)


# Valid state transitions
VALID_TRANSITIONS: dict[Lifecycle, set[Lifecycle]] = {
    Lifecycle.CREATED: {Lifecycle.INITIALIZED},
    Lifecycle.INITIALIZED: {Lifecycle.STARTED},
    Lifecycle.STARTED: {Lifecycle.STOPPED},
    Lifecycle.STOPPED: {Lifecycle.INITIALIZED},  # Allow restart
}


def validate_transition(
    component: "Component",
    current: Lifecycle,
    target: Lifecycle,
) -> None:
    """Validate a lifecycle state transition.

    Args:
        component: The component being transitioned
        current: Current lifecycle state
        target: Target lifecycle state

    Raises:
        LifecycleError: If the transition is not valid
    """
    valid_targets = VALID_TRANSITIONS.get(current, set())
    if target not in valid_targets:
        raise LifecycleError(component, current, target)
