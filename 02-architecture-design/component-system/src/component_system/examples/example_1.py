"""Example 1: Basic Component with Lifecycle

This example demonstrates creating a simple component with proper lifecycle
management. We'll build a configuration component that loads and validates
settings during initialization.

Key concepts:
- Creating a component by extending Component
- Implementing lifecycle hooks (initialize, start, stop)
- Proper state transitions
"""

import asyncio
from typing import Any, ClassVar

from component_system import Component, Lifecycle, Registry


class ConfigComponent(Component):
    """A configuration component that loads settings.

    This component demonstrates the basic lifecycle:
    - initialize(): Load and validate configuration
    - start(): Make config available
    - stop(): Clear sensitive data
    """

    name: ClassVar[str] = "config"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._settings: dict[str, Any] = {}

    @property
    def settings(self) -> dict[str, Any]:
        """Get loaded settings."""
        return self._settings

    async def initialize(self) -> None:
        """Load and validate configuration."""
        await super().initialize()

        # Simulate loading from file/env
        self._settings = {
            "app_name": self.config.get("app_name", "MyApp"),
            "debug": self.config.get("debug", False),
            "log_level": self.config.get("log_level", "INFO"),
            "api_url": self.config.get("api_url", "https://api.example.com"),
        }

        # Validate required settings
        if not self._settings["app_name"]:
            raise ValueError("app_name is required")

        print(f"  [Config] Loaded {len(self._settings)} settings")

    async def start(self) -> None:
        """Make configuration active."""
        await super().start()
        print(f"  [Config] Configuration active for '{self._settings['app_name']}'")

    async def stop(self) -> None:
        """Clear sensitive configuration data."""
        sensitive_keys = {"api_key", "password", "secret"}
        for key in sensitive_keys:
            if key in self._settings:
                self._settings[key] = "***CLEARED***"
        print("  [Config] Sensitive data cleared")
        await super().stop()


class LoggingComponent(Component):
    """A logging component that sets up logging based on config.

    Demonstrates:
    - Simple lifecycle with start/stop
    - Using component state for behavior
    """

    name: ClassVar[str] = "logging"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._log_level = "INFO"

    async def initialize(self) -> None:
        """Set up logging configuration."""
        await super().initialize()
        self._log_level = self.config.get("level", "INFO")
        print(f"  [Logging] Configured with level: {self._log_level}")

    async def start(self) -> None:
        """Start logging."""
        await super().start()
        print(f"  [Logging] Started with level {self._log_level}")

    async def stop(self) -> None:
        """Flush and close log handlers."""
        print("  [Logging] Flushing logs...")
        await super().stop()

    def log(self, message: str) -> None:
        """Log a message (only works when started)."""
        if self.state == Lifecycle.STARTED:
            print(f"  [LOG] {message}")
        else:
            print(f"  [WARNING] Logger not started, cannot log: {message}")


async def main() -> None:
    """Run the basic component example."""
    print("Example 1: Basic Component with Lifecycle")
    print("=" * 50)

    # Create a registry
    registry = Registry()

    # Register components with configuration
    print("\n1. Registering components...")
    registry.register(
        ConfigComponent,
        config={
            "app_name": "ComponentDemo",
            "debug": True,
            "log_level": "DEBUG",
        },
    )
    registry.register(
        LoggingComponent,
        config={"level": "DEBUG"},
    )

    # Show initial state
    config = registry.get(ConfigComponent)
    logging = registry.get(LoggingComponent)
    print(f"   Config state: {config.state.name}")
    print(f"   Logging state: {logging.state.name}")

    # Start all components
    print("\n2. Starting components...")
    await registry.start_all()

    # Show running state
    print(f"\n3. Components running:")
    print(f"   Config state: {config.state.name}")
    print(f"   Logging state: {logging.state.name}")

    # Use the logging component
    print("\n4. Using components:")
    logging.log("Application started successfully!")
    print(f"   App name from config: {config.settings['app_name']}")

    # Stop all components
    print("\n5. Stopping components...")
    await registry.stop_all()

    # Show final state
    print(f"\n6. Final state:")
    print(f"   Config state: {config.state.name}")
    print(f"   Logging state: {logging.state.name}")

    # Try to log after stop (should warn)
    print("\n7. Attempting to use stopped component:")
    logging.log("This won't work properly")

    print("\n" + "=" * 50)
    print("Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
