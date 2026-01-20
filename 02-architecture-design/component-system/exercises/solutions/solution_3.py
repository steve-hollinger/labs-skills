"""Solution for Exercise 3: Implement a Plugin Discovery System

This solution demonstrates a complete plugin discovery and execution system
with dynamic loading from files.
"""

import asyncio
import importlib.util
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, ClassVar

from component_system import Component, Registry, Requires


class PluginInterface(ABC):
    """Base interface for all plugins."""

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
        """Process data through the plugin."""
        ...

    async def initialize(self) -> None:
        """Initialize the plugin (optional override)."""
        pass

    async def shutdown(self) -> None:
        """Shutdown the plugin (optional override)."""
        pass


class PluginLoader(Component):
    """Component that discovers and loads plugins from a directory."""

    name: ClassVar[str] = "plugin-loader"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._plugins: dict[str, PluginInterface] = {}
        self._plugin_dir: Path | None = None
        self._load_errors: list[str] = []

    async def initialize(self) -> None:
        """Configure the plugin directory."""
        await super().initialize()
        plugin_dir = self.config.get("plugin_dir", "./plugins")
        self._plugin_dir = Path(plugin_dir)
        print(f"  [PluginLoader] Plugin directory: {self._plugin_dir}")

    async def start(self) -> None:
        """Discover and load plugins."""
        await super().start()

        if self._plugin_dir is None:
            print("  [PluginLoader] No plugin directory configured")
            return

        # Check if plugin directory exists
        if not self._plugin_dir.exists():
            print(f"  [PluginLoader] Creating plugin directory: {self._plugin_dir}")
            self._plugin_dir.mkdir(parents=True, exist_ok=True)

        # Find all .py files
        plugin_files = list(self._plugin_dir.glob("*.py"))
        print(f"  [PluginLoader] Found {len(plugin_files)} plugin files")

        # Load each plugin file
        for filepath in plugin_files:
            if filepath.name.startswith("_"):
                continue  # Skip __init__.py and private files

            plugin = self._load_plugin_from_file(filepath)
            if plugin:
                self._plugins[plugin.name] = plugin
                await plugin.initialize()
                print(f"  [PluginLoader] Loaded: {plugin.name} v{plugin.version}")

        print(f"  [PluginLoader] Loaded {len(self._plugins)} plugins")

        if self._load_errors:
            print(f"  [PluginLoader] {len(self._load_errors)} plugins failed to load")

    async def stop(self) -> None:
        """Shutdown all loaded plugins."""
        for plugin in self._plugins.values():
            try:
                await plugin.shutdown()
            except Exception as e:
                print(f"  [PluginLoader] Error shutting down {plugin.name}: {e}")

        self._plugins.clear()
        print("  [PluginLoader] All plugins shutdown")
        await super().stop()

    def _load_plugin_from_file(self, filepath: Path) -> PluginInterface | None:
        """Load a plugin from a Python file."""
        try:
            # Create module name from filename
            module_name = f"plugin_{filepath.stem}"

            # Load the module spec
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if spec is None or spec.loader is None:
                self._load_errors.append(f"{filepath}: Could not load spec")
                return None

            # Create and execute the module
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find classes implementing PluginInterface
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, PluginInterface)
                    and attr is not PluginInterface
                ):
                    # Found a plugin class, instantiate it
                    return attr()

            self._load_errors.append(f"{filepath}: No PluginInterface class found")
            return None

        except Exception as e:
            self._load_errors.append(f"{filepath}: {e}")
            return None

    @property
    def plugins(self) -> dict[str, PluginInterface]:
        """Get loaded plugins."""
        return self._plugins

    def get_plugin(self, name: str) -> PluginInterface | None:
        """Get a plugin by name."""
        return self._plugins.get(name)

    def register_plugin(self, plugin: PluginInterface) -> None:
        """Manually register a plugin instance."""
        self._plugins[plugin.name] = plugin


class PluginExecutor(Component):
    """Component that executes plugins in a pipeline."""

    name: ClassVar[str] = "plugin-executor"

    loader: PluginLoader = Requires()

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._execution_order: list[str] = []
        self._continue_on_error: bool = True

    async def initialize(self) -> None:
        """Configure execution order."""
        await super().initialize()
        self._execution_order = self.config.get("execution_order", [])
        self._continue_on_error = self.config.get("continue_on_error", True)
        print(f"  [PluginExecutor] Execution order: {self._execution_order or 'all plugins'}")

    async def start(self) -> None:
        """Start the executor."""
        await super().start()
        print("  [PluginExecutor] Ready")

    async def stop(self) -> None:
        """Stop the executor."""
        print("  [PluginExecutor] Stopped")
        await super().stop()

    async def execute(self, data: dict[str, Any]) -> dict[str, Any]:
        """Execute all plugins on the data."""
        result = data.copy()

        # Determine plugin order
        if self._execution_order:
            plugin_names = self._execution_order
        else:
            plugin_names = list(self.loader.plugins.keys())

        # Track execution metadata
        result["_pipeline"] = {
            "plugins_executed": [],
            "plugins_failed": [],
        }

        # Execute each plugin
        for plugin_name in plugin_names:
            plugin = self.loader.get_plugin(plugin_name)
            if plugin is None:
                print(f"  [PluginExecutor] Plugin not found: {plugin_name}")
                result["_pipeline"]["plugins_failed"].append(plugin_name)
                continue

            try:
                result = await plugin.process(result)
                result["_pipeline"]["plugins_executed"].append(plugin_name)
            except Exception as e:
                print(f"  [PluginExecutor] Error in {plugin_name}: {e}")
                result["_pipeline"]["plugins_failed"].append(plugin_name)
                if not self._continue_on_error:
                    break

        return result


# Sample plugin implementations


class UppercasePlugin(PluginInterface):
    """Plugin that uppercases string values."""

    @property
    def name(self) -> str:
        return "uppercase"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        result = data.copy()
        for key, value in list(result.items()):
            if isinstance(value, str) and not key.startswith("_"):
                result[key] = value.upper()
        return result


class TimestampPlugin(PluginInterface):
    """Plugin that adds timestamps."""

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
    """Plugin that validates required fields."""

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


class SanitizerPlugin(PluginInterface):
    """Plugin that sanitizes data by stripping whitespace."""

    @property
    def name(self) -> str:
        return "sanitizer"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        result = data.copy()
        for key, value in list(result.items()):
            if isinstance(value, str) and not key.startswith("_"):
                result[key] = value.strip()
        return result


async def main() -> None:
    """Test the plugin discovery system solution."""
    print("Solution 3: Plugin Discovery System")
    print("=" * 50)

    registry = Registry()

    # Create a temporary plugin directory
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        plugin_dir = Path(tmpdir) / "plugins"
        plugin_dir.mkdir()

        # Write a sample plugin file
        sample_plugin = '''
from abc import ABC, abstractmethod
from typing import Any


class PluginInterface(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def version(self) -> str: ...

    @abstractmethod
    async def process(self, data: dict[str, Any]) -> dict[str, Any]: ...

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass


class LowercasePlugin(PluginInterface):
    """Plugin loaded from file that lowercases strings."""

    @property
    def name(self) -> str:
        return "lowercase"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        result = data.copy()
        for key, value in list(result.items()):
            if isinstance(value, str) and not key.startswith("_"):
                result[key] = value.lower()
        return result
'''

        (plugin_dir / "lowercase_plugin.py").write_text(sample_plugin)
        print(f"\n1. Created sample plugin file in {plugin_dir}")

        # Register components
        print("\n2. Registering components...")
        registry.register(
            PluginLoader,
            config={"plugin_dir": str(plugin_dir)},
        )
        registry.register(
            PluginExecutor,
            config={"continue_on_error": True},
        )

        # Start components
        print("\n3. Starting components...")
        await registry.start_all()

        # Manually register additional plugins for testing
        loader = registry.get(PluginLoader)
        loader.register_plugin(ValidationPlugin(["id", "name"]))
        await loader.plugins["validation"].initialize()

        loader.register_plugin(SanitizerPlugin())
        await loader.plugins["sanitizer"].initialize()

        loader.register_plugin(TimestampPlugin())
        await loader.plugins["timestamp"].initialize()

        print(f"\n4. All loaded plugins: {list(loader.plugins.keys())}")

        # Execute pipeline
        executor = registry.get(PluginExecutor)

        print("\n5. Executing plugin pipeline...")
        data = {
            "id": "123",
            "name": "  Test Item  ",
            "description": "A TEST description",
        }
        print(f"   Input: {data}")

        result = await executor.execute(data)
        print(f"\n   Output: {result}")
        print(f"\n   Plugins executed: {result['_pipeline']['plugins_executed']}")

        # Test with invalid data
        print("\n6. Testing with invalid data (missing required fields)...")
        invalid_data = {"description": "no id or name"}
        result2 = await executor.execute(invalid_data)
        print(f"   Valid: {result2.get('_valid')}")
        print(f"   Errors: {result2.get('_validation_errors')}")

        # Stop all
        print("\n7. Stopping components...")
        await registry.stop_all()

    print("\n" + "=" * 50)
    print("Solution demonstration complete!")


if __name__ == "__main__":
    asyncio.run(main())
