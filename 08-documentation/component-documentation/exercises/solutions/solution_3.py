"""Solution for Exercise 3: Document the ConfigManager Module."""


def solution() -> str:
    """Reference solution for Exercise 3.

    Returns:
        Fully documented version of the ConfigManager module.
    """
    return '''"""Configuration management module.

This module provides a ConfigManager class for loading, saving, and
managing application configuration from JSON files. It supports
nested key access, default values, and lazy loading.

Example:
    >>> from config_manager import ConfigManager
    >>> config = ConfigManager("config.json", defaults={"debug": False})
    >>> print(config.get("debug"))
    False

Typical usage:
    >>> config = ConfigManager("app/config.json")
    >>> db_host = config.get("database.host", "localhost")
    >>> config.set("database.port", 5432)
    >>> config.save()
"""

import json
from pathlib import Path
from typing import Any, Optional


class ConfigManager:
    """Manager for application configuration stored in JSON files.

    ConfigManager provides a convenient interface for reading and writing
    configuration values. It supports:
    - Lazy loading (config is only read when first accessed)
    - Default values that are used when config file doesn't exist
    - Nested key access using dot notation (e.g., "database.host")
    - Automatic parent directory creation on save

    Attributes:
        config_path: Path to the configuration JSON file.
        defaults: Dictionary of default values.

    Example:
        >>> config = ConfigManager(
        ...     "settings.json",
        ...     defaults={"log_level": "INFO", "max_retries": 3}
        ... )
        >>> config.get("log_level")
        'INFO'
        >>> config.set("log_level", "DEBUG")
        >>> config.save()
    """

    def __init__(
        self,
        config_path: str,
        defaults: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize the ConfigManager.

        Args:
            config_path: Path to the JSON configuration file.
                Can be relative or absolute.
            defaults: Optional dictionary of default values.
                These are used when the config file doesn't exist
                or when a key is missing from the file.

        Example:
            >>> config = ConfigManager("app.json")
            >>> config = ConfigManager(
            ...     "/etc/myapp/config.json",
            ...     defaults={"port": 8080}
            ... )
        """
        self.config_path = Path(config_path)
        self.defaults = defaults or {}
        self._config: Optional[dict[str, Any]] = None

    @property
    def config(self) -> dict[str, Any]:
        """Get the current configuration dictionary.

        Lazily loads the configuration from file on first access.
        Subsequent accesses return the cached configuration.

        Returns:
            The configuration dictionary, merged with defaults.

        Example:
            >>> config.config["database"]["host"]
            'localhost'
        """
        if self._config is None:
            self._config = self._load_config()
        return self._config

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from file.

        If the file exists, loads and merges with defaults.
        If the file doesn't exist, returns a copy of defaults.

        Returns:
            Configuration dictionary.
        """
        if self.config_path.exists():
            with open(self.config_path) as f:
                loaded = json.load(f)
            return {**self.defaults, **loaded}
        return self.defaults.copy()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key.

        Supports dot notation for nested keys (e.g., "database.host").
        Returns the default value if the key doesn't exist.

        Args:
            key: The configuration key. Use dots for nested access.
            default: Value to return if key is not found.

        Returns:
            The configuration value, or default if not found.

        Example:
            >>> config.get("database.host")
            'localhost'
            >>> config.get("missing.key", "fallback")
            'fallback'
            >>> config.get("database.port", 5432)
            5432
        """
        keys = key.split(".")
        value: Any = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Supports dot notation for nested keys. Creates intermediate
        dictionaries as needed.

        Args:
            key: The configuration key. Use dots for nested access.
            value: The value to set.

        Example:
            >>> config.set("database.host", "db.example.com")
            >>> config.set("database.port", 5432)
            >>> config.set("new.nested.key", "value")

        Note:
            Changes are only persisted after calling save().
        """
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def save(self) -> None:
        """Save the current configuration to file.

        Creates parent directories if they don't exist.
        Writes JSON with 2-space indentation for readability.

        Raises:
            PermissionError: If the file or directory is not writable.
            OSError: If there's an I/O error during save.

        Example:
            >>> config.set("log_level", "DEBUG")
            >>> config.save()  # Changes are now persisted
        """
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def reload(self) -> None:
        """Reload configuration from file.

        Discards any unsaved changes and reloads from disk.
        Useful when the config file may have been modified externally.

        Example:
            >>> config.set("temp_value", "will be lost")
            >>> config.reload()  # temp_value is gone
            >>> config.get("temp_value")  # Returns None
        """
        self._config = None
        _ = self.config  # Trigger reload


def load_config(
    path: str,
    defaults: Optional[dict[str, Any]] = None,
) -> ConfigManager:
    """Convenience function to create a ConfigManager.

    Args:
        path: Path to the configuration file.
        defaults: Optional default values.

    Returns:
        Configured ConfigManager instance.

    Example:
        >>> config = load_config("settings.json", {"debug": False})
        >>> config.get("debug")
        False
    """
    return ConfigManager(path, defaults)
'''


if __name__ == "__main__":
    from component_documentation.code_docs import check_module_documentation
    from rich.console import Console

    console = Console()
    documented = solution()

    score = check_module_documentation(documented)

    console.print("[bold]Solution 3: ConfigManager Documentation[/bold]\n")
    console.print(f"Score: [green]{score.score}/100[/green]")

    if score.issues:
        console.print("\n[yellow]Minor issues:[/yellow]")
        for issue in score.issues:
            console.print(f"  - {issue}")
