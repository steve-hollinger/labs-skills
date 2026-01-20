"""Solution for Exercise 1: Create a Logging Component

This solution demonstrates a complete logging component implementation
with proper lifecycle management.
"""

import asyncio
from datetime import datetime
from typing import Any, ClassVar, TextIO

from component_system import Component, Lifecycle, Registry


# Log level priorities
LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
}


class LoggingComponent(Component):
    """A file-based logging component with proper lifecycle management."""

    name: ClassVar[str] = "logging"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._log_level: str = "INFO"
        self._log_level_priority: int = LOG_LEVELS["INFO"]
        self._file: TextIO | None = None
        self._filename: str = "/tmp/app.log"

    async def initialize(self) -> None:
        """Configure the logging component."""
        await super().initialize()

        # Set log level from config
        self._log_level = self.config.get("level", "INFO").upper()
        self._log_level_priority = LOG_LEVELS.get(self._log_level, 20)

        # Get filename from config
        self._filename = self.config.get("filename", "/tmp/app.log")

        print(f"  [Logging] Configured with level: {self._log_level}")
        print(f"  [Logging] Log file: {self._filename}")

    async def start(self) -> None:
        """Open the log file."""
        await super().start()

        # Open file in append mode
        self._file = open(self._filename, "a")

        # Write startup message
        self._write_to_file("INFO", "Logging started")
        print(f"  [Logging] File opened: {self._filename}")

    async def stop(self) -> None:
        """Close the log file."""
        if self._file:
            # Write shutdown message
            self._write_to_file("INFO", "Logging stopped")

            # Flush and close
            self._file.flush()
            self._file.close()
            self._file = None
            print("  [Logging] File closed")

        await super().stop()

    def _write_to_file(self, level: str, message: str) -> None:
        """Write a formatted message to the log file."""
        if self._file:
            timestamp = datetime.now().isoformat()
            log_line = f"[{timestamp}] [{level}] {message}\n"
            self._file.write(log_line)
            self._file.flush()  # Ensure immediate write

    def log(self, level: str, message: str) -> None:
        """Write a log message.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Message to log
        """
        # Check if component is started
        if self.state != Lifecycle.STARTED:
            print(f"  [WARNING] Logger not started, cannot log: {message}")
            return

        # Check if level should be logged
        level = level.upper()
        level_priority = LOG_LEVELS.get(level, 20)

        if level_priority < self._log_level_priority:
            # Level is below threshold, skip
            return

        # Write to file
        self._write_to_file(level, message)

    # Convenience methods
    def debug(self, message: str) -> None:
        """Log a debug message."""
        self.log("DEBUG", message)

    def info(self, message: str) -> None:
        """Log an info message."""
        self.log("INFO", message)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self.log("WARNING", message)

    def error(self, message: str) -> None:
        """Log an error message."""
        self.log("ERROR", message)

    def critical(self, message: str) -> None:
        """Log a critical message."""
        self.log("CRITICAL", message)


async def main() -> None:
    """Test the logging component solution."""
    print("Solution 1: Logging Component")
    print("=" * 50)

    registry = Registry()

    # Register with DEBUG level to see all messages
    registry.register(
        LoggingComponent,
        config={"filename": "/tmp/test.log", "level": "DEBUG"},
    )

    print("\n1. Starting logging component...")
    await registry.start_all()

    logger = registry.get(LoggingComponent)

    print("\n2. Logging messages at various levels...")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    print("\n3. Stopping logging component...")
    await registry.stop_all()

    print("\n4. Verifying log file content:")
    try:
        with open("/tmp/test.log") as f:
            content = f.read()
            print("-" * 40)
            print(content)
            print("-" * 40)
    except FileNotFoundError:
        print("ERROR: Log file was not created")

    # Test with higher log level
    print("\n5. Testing with WARNING level (DEBUG/INFO filtered)...")

    registry2 = Registry()
    registry2.register(
        LoggingComponent,
        config={"filename": "/tmp/test2.log", "level": "WARNING"},
    )

    await registry2.start_all()
    logger2 = registry2.get(LoggingComponent)

    logger2.debug("This won't appear")  # Below threshold
    logger2.info("This won't appear either")  # Below threshold
    logger2.warning("This will appear")
    logger2.error("This will also appear")

    await registry2.stop_all()

    print("\n   Content of WARNING-level log:")
    with open("/tmp/test2.log") as f:
        content = f.read()
        print("-" * 40)
        print(content)
        print("-" * 40)

    print("\n" + "=" * 50)
    print("Solution demonstration complete!")


if __name__ == "__main__":
    asyncio.run(main())
