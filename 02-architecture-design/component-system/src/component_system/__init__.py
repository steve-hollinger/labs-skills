"""Component System - Modular component architecture patterns.

This module provides building blocks for creating component-based applications
with proper lifecycle management, dependency injection, and plugin support.
"""

from component_system.component import Component
from component_system.lifecycle import Lifecycle, LifecycleError
from component_system.registry import Registry
from component_system.requires import Requires

__all__ = [
    "Component",
    "Lifecycle",
    "LifecycleError",
    "Registry",
    "Requires",
]

__version__ = "0.1.0"
