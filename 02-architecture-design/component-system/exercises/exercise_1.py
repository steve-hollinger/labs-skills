"""Exercise 1: Create a Logging Component

Build a logging component with proper lifecycle management that:
1. Configures log level during initialization
2. Opens a log file during start
3. Provides a log() method for writing messages
4. Properly closes the file during stop

Instructions:
1. Create a LoggingComponent class that extends Component
2. Implement initialize() to set the log level from config
3. Implement start() to open a log file (use config["filename"] or default)
4. Implement stop() to flush and close the file
5. Add a log(level, message) method that writes to the file

Expected Output:
- Component should transition through lifecycle states correctly
- Log messages should be written to the file
- File should be properly closed on stop

Hints:
- Use self.config.get("key", default) for optional config
- Remember to call await super().method() in lifecycle methods
- Handle the case where log() is called before start()
"""

import asyncio
from typing import Any, ClassVar, TextIO

from component_system import Component, Lifecycle


class LoggingComponent(Component):
    """A file-based logging component.

    TODO: Implement this component following the instructions above.
    """

    name: ClassVar[str] = "logging"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        # TODO: Initialize instance variables
        self._log_level: str = "INFO"
        self._file: TextIO | None = None

    async def initialize(self) -> None:
        """Configure the logging component."""
        # TODO: Implement initialization
        # - Call super().initialize()
        # - Set log level from config
        pass

    async def start(self) -> None:
        """Open the log file."""
        # TODO: Implement start
        # - Call super().start()
        # - Open the log file
        pass

    async def stop(self) -> None:
        """Close the log file."""
        # TODO: Implement stop
        # - Flush and close the file
        # - Call super().stop()
        pass

    def log(self, level: str, message: str) -> None:
        """Write a log message.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            message: Message to log
        """
        # TODO: Implement logging
        # - Check if component is started
        # - Check if level should be logged based on log_level
        # - Write to file with timestamp
        pass


# Test your implementation
async def main() -> None:
    """Test the logging component."""
    from component_system import Registry

    print("Testing LoggingComponent...")

    registry = Registry()
    registry.register(
        LoggingComponent,
        config={"filename": "/tmp/test.log", "level": "DEBUG"},
    )

    await registry.start_all()

    logger = registry.get(LoggingComponent)
    logger.log("INFO", "Application started")
    logger.log("DEBUG", "Debug message")
    logger.log("ERROR", "An error occurred")

    await registry.stop_all()

    # Verify log file was created and has content
    try:
        with open("/tmp/test.log") as f:
            content = f.read()
            print(f"Log file content:\n{content}")
    except FileNotFoundError:
        print("ERROR: Log file was not created")


if __name__ == "__main__":
    asyncio.run(main())
