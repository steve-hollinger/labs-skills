"""Dependency descriptor for component injection.

This module provides the Requires descriptor for declaring component dependencies.
"""

from typing import TYPE_CHECKING, Any, Generic, TypeVar, get_type_hints, overload

if TYPE_CHECKING:
    from component_system.component import Component

T = TypeVar("T", bound="Component")


class Requires(Generic[T]):
    """Descriptor for declaring component dependencies.

    Usage:
        class MyService(Component):
            database: DatabaseComponent = Requires()
            cache: CacheComponent = Requires()

    The registry will automatically inject the required components
    before the dependent component is initialized.
    """

    def __init__(self, *, optional: bool = False) -> None:
        """Initialize the Requires descriptor.

        Args:
            optional: If True, the dependency is optional and won't
                     raise an error if not found. Defaults to False.
        """
        self.optional = optional
        self._name: str | None = None
        self._owner: type["Component"] | None = None

    def __set_name__(self, owner: type["Component"], name: str) -> None:
        """Called when the descriptor is assigned to a class attribute.

        Args:
            owner: The class that owns this descriptor
            name: The attribute name
        """
        self._name = name
        self._owner = owner

    @overload
    def __get__(self, obj: None, objtype: type["Component"]) -> "Requires[T]": ...

    @overload
    def __get__(self, obj: "Component", objtype: type["Component"]) -> T: ...

    def __get__(
        self, obj: "Component | None", objtype: type["Component"]
    ) -> "Requires[T] | T":
        """Get the injected dependency.

        Args:
            obj: The instance accessing the attribute, or None if class access
            objtype: The class type

        Returns:
            The injected component instance, or self if accessed on class
        """
        if obj is None:
            return self

        # Get from instance's injected dependencies
        if self._name is None:
            raise RuntimeError("Descriptor not properly initialized")

        injected = getattr(obj, "_injected_deps", {})
        if self._name in injected:
            return injected[self._name]  # type: ignore[return-value]

        if self.optional:
            return None  # type: ignore[return-value]

        raise AttributeError(
            f"Dependency '{self._name}' not injected. "
            f"Ensure the component is registered with a Registry."
        )

    def __set__(self, obj: "Component", value: T) -> None:
        """Set the injected dependency.

        Args:
            obj: The instance
            value: The component to inject
        """
        if not hasattr(obj, "_injected_deps"):
            obj._injected_deps = {}  # type: ignore[attr-defined]
        if self._name is None:
            raise RuntimeError("Descriptor not properly initialized")
        obj._injected_deps[self._name] = value  # type: ignore[attr-defined]

    def get_required_type(self, owner: type["Component"]) -> type["Component"]:
        """Get the type of the required component.

        Args:
            owner: The class that owns this descriptor

        Returns:
            The type annotation of this dependency
        """
        if self._name is None:
            raise RuntimeError("Descriptor not properly initialized")

        hints = get_type_hints(owner)
        return hints.get(self._name, Any)  # type: ignore[return-value]


def get_dependencies(component_class: type["Component"]) -> dict[str, type["Component"]]:
    """Get all dependencies declared on a component class.

    Args:
        component_class: The component class to inspect

    Returns:
        Dictionary mapping attribute names to required component types
    """
    dependencies: dict[str, type["Component"]] = {}
    hints = get_type_hints(component_class)

    for name, value in vars(component_class).items():
        if isinstance(value, Requires):
            if name in hints:
                dependencies[name] = hints[name]

    return dependencies
