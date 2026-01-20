"""Example 3: Plugin System with Dynamic Discovery

This example demonstrates building a plugin system where plugins are
discovered and registered dynamically. This pattern is used in many
real-world applications to allow extensibility.

Key concepts:
- Plugin base class with registration
- Plugin discovery and loading
- Plugin registry with factory pattern
- Lifecycle management for plugins
"""

import asyncio
from abc import abstractmethod
from typing import Any, ClassVar

from component_system import Component, Registry


class Plugin(Component):
    """Base class for plugins.

    Plugins are components that:
    - Have a unique plugin_id
    - Can be enabled/disabled
    - Process data through a common interface
    """

    name: ClassVar[str] = "plugin"
    plugin_id: ClassVar[str] = "base"
    description: ClassVar[str] = "Base plugin"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._enabled = True

    @property
    def enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self._enabled

    def enable(self) -> None:
        """Enable the plugin."""
        self._enabled = True

    def disable(self) -> None:
        """Disable the plugin."""
        self._enabled = False

    @abstractmethod
    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process data through the plugin.

        Args:
            data: Input data dictionary

        Returns:
            Processed data dictionary
        """
        ...


# Plugin Registry for dynamic discovery
class PluginRegistry:
    """Registry for plugin discovery and management.

    This registry maintains a catalog of available plugins
    and can instantiate them on demand.
    """

    _plugins: ClassVar[dict[str, type[Plugin]]] = {}

    @classmethod
    def register(cls, plugin_class: type[Plugin]) -> type[Plugin]:
        """Register a plugin class (decorator).

        Usage:
            @PluginRegistry.register
            class MyPlugin(Plugin):
                plugin_id = "my-plugin"
        """
        plugin_id = plugin_class.plugin_id
        if plugin_id in cls._plugins:
            raise ValueError(f"Plugin '{plugin_id}' already registered")
        cls._plugins[plugin_id] = plugin_class
        return plugin_class

    @classmethod
    def get(cls, plugin_id: str) -> type[Plugin] | None:
        """Get a plugin class by ID."""
        return cls._plugins.get(plugin_id)

    @classmethod
    def list_plugins(cls) -> list[str]:
        """List all registered plugin IDs."""
        return list(cls._plugins.keys())

    @classmethod
    def create(cls, plugin_id: str, config: dict[str, Any] | None = None) -> Plugin:
        """Create a plugin instance by ID."""
        plugin_class = cls.get(plugin_id)
        if not plugin_class:
            raise KeyError(f"Plugin '{plugin_id}' not found")
        return plugin_class(config)


# Define some plugins using the decorator pattern


@PluginRegistry.register
class ValidationPlugin(Plugin):
    """Plugin that validates data fields."""

    plugin_id: ClassVar[str] = "validation"
    name: ClassVar[str] = "validation-plugin"
    description: ClassVar[str] = "Validates required fields in data"

    async def initialize(self) -> None:
        """Load validation rules."""
        await super().initialize()
        self._required_fields = self.config.get("required_fields", ["id"])
        print(f"  [Validation] Required fields: {self._required_fields}")

    async def start(self) -> None:
        """Start validation plugin."""
        await super().start()
        print("  [Validation] Ready")

    async def stop(self) -> None:
        """Stop validation plugin."""
        print("  [Validation] Stopped")
        await super().stop()

    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Validate data has required fields."""
        if not self.enabled:
            return data

        missing = [f for f in self._required_fields if f not in data]
        if missing:
            data["_validation_errors"] = f"Missing fields: {missing}"
            data["_valid"] = False
        else:
            data["_valid"] = True
        return data


@PluginRegistry.register
class TransformPlugin(Plugin):
    """Plugin that transforms data fields."""

    plugin_id: ClassVar[str] = "transform"
    name: ClassVar[str] = "transform-plugin"
    description: ClassVar[str] = "Transforms data fields (uppercase, lowercase, etc.)"

    async def initialize(self) -> None:
        """Load transformation rules."""
        await super().initialize()
        self._transforms = self.config.get("transforms", {})
        print(f"  [Transform] Configured {len(self._transforms)} transforms")

    async def start(self) -> None:
        """Start transform plugin."""
        await super().start()
        print("  [Transform] Ready")

    async def stop(self) -> None:
        """Stop transform plugin."""
        print("  [Transform] Stopped")
        await super().stop()

    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Apply transformations to data."""
        if not self.enabled:
            return data

        for field, transform in self._transforms.items():
            if field in data and isinstance(data[field], str):
                if transform == "uppercase":
                    data[field] = data[field].upper()
                elif transform == "lowercase":
                    data[field] = data[field].lower()
                elif transform == "strip":
                    data[field] = data[field].strip()
        return data


@PluginRegistry.register
class EnrichmentPlugin(Plugin):
    """Plugin that enriches data with additional fields."""

    plugin_id: ClassVar[str] = "enrichment"
    name: ClassVar[str] = "enrichment-plugin"
    description: ClassVar[str] = "Adds computed or lookup fields to data"

    async def initialize(self) -> None:
        """Load enrichment configuration."""
        await super().initialize()
        self._enrichments = self.config.get("enrichments", {})
        print(f"  [Enrichment] Configured {len(self._enrichments)} enrichments")

    async def start(self) -> None:
        """Start enrichment plugin."""
        await super().start()
        print("  [Enrichment] Ready")

    async def stop(self) -> None:
        """Stop enrichment plugin."""
        print("  [Enrichment] Stopped")
        await super().stop()

    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Add enrichment fields to data."""
        if not self.enabled:
            return data

        for field, value in self._enrichments.items():
            if callable(value):
                data[field] = value(data)
            else:
                data[field] = value

        # Add timestamp
        import time

        data["_processed_at"] = time.time()
        return data


class PluginPipeline(Component):
    """A pipeline that runs data through multiple plugins.

    This component manages a sequence of plugins and processes
    data through all of them in order.
    """

    name: ClassVar[str] = "plugin-pipeline"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._plugins: list[Plugin] = []
        self._plugin_registry: Registry = Registry()

    async def initialize(self) -> None:
        """Initialize the pipeline and load plugins."""
        await super().initialize()

        # Get plugin configuration
        plugin_configs = self.config.get("plugins", [])
        print(f"  [Pipeline] Loading {len(plugin_configs)} plugins...")

        for pconfig in plugin_configs:
            plugin_id = pconfig.get("id")
            plugin_settings = pconfig.get("config", {})

            # Create plugin from registry
            plugin = PluginRegistry.create(plugin_id, plugin_settings)
            self._plugins.append(plugin)
            self._plugin_registry.register(type(plugin), plugin_settings)
            print(f"    - Loaded: {plugin.plugin_id}")

    async def start(self) -> None:
        """Start all plugins in the pipeline."""
        await super().start()

        # Start all plugins
        for plugin in self._plugins:
            await plugin.initialize()
            await plugin.start()

        print(f"  [Pipeline] Started with {len(self._plugins)} plugins")

    async def stop(self) -> None:
        """Stop all plugins in reverse order."""
        for plugin in reversed(self._plugins):
            await plugin.stop()
        print("  [Pipeline] All plugins stopped")
        await super().stop()

    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process data through all plugins in order."""
        result = data.copy()
        for plugin in self._plugins:
            result = await plugin.process(result)
        return result


async def main() -> None:
    """Run the plugin system example."""
    print("Example 3: Plugin System with Dynamic Discovery")
    print("=" * 50)

    # Show available plugins
    print("\n1. Available plugins:")
    for plugin_id in PluginRegistry.list_plugins():
        plugin_class = PluginRegistry.get(plugin_id)
        if plugin_class:
            print(f"   - {plugin_id}: {plugin_class.description}")

    # Create a pipeline with plugins
    print("\n2. Creating plugin pipeline...")
    registry = Registry()

    pipeline_config = {
        "plugins": [
            {
                "id": "validation",
                "config": {"required_fields": ["id", "name", "email"]},
            },
            {
                "id": "transform",
                "config": {"transforms": {"email": "lowercase", "name": "strip"}},
            },
            {
                "id": "enrichment",
                "config": {"enrichments": {"source": "api", "version": "1.0"}},
            },
        ]
    }

    registry.register(PluginPipeline, config=pipeline_config)

    print("\n3. Starting pipeline...")
    await registry.start_all()

    pipeline = registry.get(PluginPipeline)

    # Process some test data
    print("\n4. Processing data through pipeline:")

    # Valid data
    data1 = {"id": "123", "name": "  Alice  ", "email": "ALICE@EXAMPLE.COM"}
    print(f"\n   Input: {data1}")
    result1 = await pipeline.process(data1)
    print(f"   Output: {result1}")

    # Invalid data (missing required field)
    data2 = {"id": "456", "name": "Bob"}
    print(f"\n   Input: {data2}")
    result2 = await pipeline.process(data2)
    print(f"   Output: {result2}")

    # Disable a plugin and process again
    print("\n5. Disabling validation plugin...")
    validation_plugin = pipeline._plugins[0]
    validation_plugin.disable()

    data3 = {"id": "789"}  # Would fail validation
    print(f"\n   Input: {data3}")
    result3 = await pipeline.process(data3)
    print(f"   Output: {result3}")

    # Stop pipeline
    print("\n6. Stopping pipeline...")
    await registry.stop_all()

    print("\n" + "=" * 50)
    print("Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
