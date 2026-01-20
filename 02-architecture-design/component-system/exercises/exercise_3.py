"""Exercise 3: Implement a Plugin Discovery System

Build a plugin discovery system that:
1. Scans a directory for Python plugin files
2. Loads plugins dynamically
3. Registers them with a plugin registry
4. Executes plugins through a pipeline

Instructions:
1. Complete the PluginLoader component that discovers plugins
2. Implement the PluginExecutor that runs plugins in sequence
3. Create sample plugins in the plugins/ directory structure
4. Handle plugin loading errors gracefully

Expected Output:
- Plugins should be discovered from the specified directory
- Each plugin should process data and pass it to the next
- Failed plugins should not break the pipeline

Hints:
- Use importlib to dynamically import modules
- Plugins should implement a common interface (process method)
- Consider using abstract base classes for the plugin interface
"""

import asyncio
import importlib.util
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, ClassVar

from component_system import Component, Requires


class PluginInterface(ABC):
    """Base interface for all plugins.

    All plugins must implement this interface to be loadable.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the plugin name."""
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Return the plugin version."""
        ...

    @abstractmethod
    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process data through the plugin.

        Args:
            data: Input data dictionary

        Returns:
            Processed data dictionary
        """
        ...

    async def initialize(self) -> None:
        """Initialize the plugin (optional override)."""
        pass

    async def shutdown(self) -> None:
        """Shutdown the plugin (optional override)."""
        pass


class PluginLoader(Component):
    """Component that discovers and loads plugins from a directory.

    TODO: Implement plugin discovery and loading.
    """

    name: ClassVar[str] = "plugin-loader"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._plugins: dict[str, PluginInterface] = {}
        self._plugin_dir: Path | None = None

    async def initialize(self) -> None:
        """Configure the plugin directory."""
        await super().initialize()
        # TODO: Get plugin directory from config
        # self._plugin_dir = Path(self.config.get("plugin_dir", "./plugins"))
        print(f"  [PluginLoader] Plugin directory: {self._plugin_dir}")

    async def start(self) -> None:
        """Discover and load plugins."""
        await super().start()
        # TODO: Implement plugin discovery
        # 1. Check if plugin directory exists
        # 2. Find all .py files in the directory
        # 3. Load each file as a module
        # 4. Find classes that implement PluginInterface
        # 5. Instantiate and store in self._plugins
        print(f"  [PluginLoader] Loaded {len(self._plugins)} plugins")

    async def stop(self) -> None:
        """Shutdown all loaded plugins."""
        # TODO: Call shutdown on each plugin
        print("  [PluginLoader] All plugins shutdown")
        await super().stop()

    def _load_plugin_from_file(self, filepath: Path) -> PluginInterface | None:
        """Load a plugin from a Python file.

        Args:
            filepath: Path to the plugin file

        Returns:
            Plugin instance or None if loading failed
        """
        # TODO: Implement dynamic module loading
        # 1. Use importlib.util.spec_from_file_location
        # 2. Load the module
        # 3. Find class implementing PluginInterface
        # 4. Instantiate and return
        pass

    @property
    def plugins(self) -> dict[str, PluginInterface]:
        """Get loaded plugins."""
        return self._plugins

    def get_plugin(self, name: str) -> PluginInterface | None:
        """Get a plugin by name."""
        return self._plugins.get(name)


class PluginExecutor(Component):
    """Component that executes plugins in a pipeline.

    TODO: Implement plugin execution with dependency on PluginLoader.
    """

    name: ClassVar[str] = "plugin-executor"

    # TODO: Declare dependency on PluginLoader
    # loader: PluginLoader = Requires()

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._execution_order: list[str] = []

    async def initialize(self) -> None:
        """Configure execution order."""
        await super().initialize()
        # TODO: Get execution order from config, or use all plugins
        # self._execution_order = self.config.get("execution_order", [])
        print("  [PluginExecutor] Configured")

    async def start(self) -> None:
        """Start the executor."""
        await super().start()
        print("  [PluginExecutor] Ready")

    async def stop(self) -> None:
        """Stop the executor."""
        print("  [PluginExecutor] Stopped")
        await super().stop()

    async def execute(self, data: dict[str, Any]) -> dict[str, Any]:
        """Execute all plugins on the data.

        Args:
            data: Input data

        Returns:
            Data after processing by all plugins
        """
        # TODO: Implement pipeline execution
        # 1. Determine plugin order (use _execution_order or all plugins)
        # 2. For each plugin in order:
        #    a. Get plugin from loader
        #    b. Call plugin.process(data)
        #    c. Handle errors (log and continue)
        #    d. Update data with result
        # 3. Return final data
        pass


# Sample plugin implementations (would normally be in separate files)


class UppercasePlugin(PluginInterface):
    """Sample plugin that uppercases string values."""

    @property
    def name(self) -> str:
        return "uppercase"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        result = data.copy()
        for key, value in result.items():
            if isinstance(value, str) and not key.startswith("_"):
                result[key] = value.upper()
        return result


class TimestampPlugin(PluginInterface):
    """Sample plugin that adds timestamps."""

    @property
    def name(self) -> str:
        return "timestamp"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        import time

        result = data.copy()
        result["_timestamp"] = time.time()
        result["_processed_by"] = self.name
        return result


class ValidationPlugin(PluginInterface):
    """Sample plugin that validates required fields."""

    def __init__(self, required_fields: list[str] | None = None) -> None:
        self._required_fields = required_fields or ["id"]

    @property
    def name(self) -> str:
        return "validation"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        result = data.copy()
        missing = [f for f in self._required_fields if f not in data]
        result["_valid"] = len(missing) == 0
        if missing:
            result["_validation_errors"] = f"Missing: {missing}"
        return result


# Test your implementation
async def main() -> None:
    """Test the plugin discovery system."""
    from component_system import Registry

    print("Testing Plugin Discovery System...")
    print("=" * 50)

    # For testing, we'll manually register plugins instead of file discovery
    # In a real implementation, plugins would be loaded from files

    print("\n1. Creating a simple plugin pipeline manually...")

    # Create plugins
    plugins = [
        ValidationPlugin(["id", "name"]),
        UppercasePlugin(),
        TimestampPlugin(),
    ]

    # Process data through plugins
    data = {"id": "123", "name": "test item", "description": "a test"}
    print(f"\n2. Initial data: {data}")

    print("\n3. Processing through plugins:")
    for plugin in plugins:
        await plugin.initialize()
        data = await plugin.process(data)
        print(f"   After {plugin.name}: {data}")
        await plugin.shutdown()

    print(f"\n4. Final data: {data}")

    # Now test with missing fields
    print("\n5. Testing validation with missing fields:")
    bad_data = {"description": "missing id and name"}
    for plugin in plugins:
        await plugin.initialize()
        bad_data = await plugin.process(bad_data)
        await plugin.shutdown()
    print(f"   Result: {bad_data}")

    print("\n" + "=" * 50)
    print("Test complete!")
    print("\nChallenge: Implement PluginLoader to discover plugins from files!")


if __name__ == "__main__":
    asyncio.run(main())
