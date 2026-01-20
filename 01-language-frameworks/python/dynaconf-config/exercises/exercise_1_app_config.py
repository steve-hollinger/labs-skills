"""Exercise 1: Basic App Configuration

Set up configuration for a web application using Dynaconf.

Requirements:
1. Create a settings.toml file (programmatically) with:
   - app_name: string
   - debug: boolean (default false)
   - log_level: string (default "INFO")
   - server.host: string (default "0.0.0.0")
   - server.port: integer (default 8000)
   - database.host: string
   - database.port: integer (default 5432)
   - database.name: string

2. Create a Dynaconf settings instance that:
   - Loads from the settings.toml file
   - Uses "WEBAPP" as the envvar_prefix
   - Supports environment variable overrides

3. Demonstrate:
   - Accessing nested settings (server.host, database.port)
   - Using environment variables to override settings
   - Getting settings with defaults for missing values

Expected behavior:
    # Load settings
    settings = create_settings()

    # Access settings
    print(settings.app_name)  # "MyWebApp"
    print(settings.server.port)  # 8000

    # Override with env var
    os.environ["WEBAPP_SERVER__PORT"] = "9000"
    # New settings instance should show 9000

Hints:
- Use tempfile to create temporary config files
- Use pathlib.Path for file operations
- Double underscore (__) for nested env var keys
"""

import os
import tempfile
from pathlib import Path

from dynaconf import Dynaconf


def create_config_file(base_dir: Path) -> Path:
    """Create the configuration file.

    TODO: Implement this function to create a settings.toml file
    with the required settings.
    """
    settings_path = base_dir / "settings.toml"
    # TODO: Write the TOML content to settings_path
    settings_path.write_text("""
# TODO: Add your configuration here
[default]
app_name = "MyWebApp"
""")
    return settings_path


def create_settings(settings_path: Path) -> Dynaconf:
    """Create the Dynaconf settings instance.

    TODO: Implement this function to create a properly configured
    Dynaconf instance.
    """
    # TODO: Create and return Dynaconf instance with proper configuration
    return Dynaconf(
        settings_files=[str(settings_path)],
    )


def test_app_config() -> None:
    """Test your configuration implementation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        settings_path = create_config_file(base_dir)
        settings = create_settings(settings_path)

        # Test 1: Basic setting access
        assert settings.app_name == "MyWebApp"
        print("Test 1 passed: Basic setting access works")

        # TODO: Add more tests for:
        # - Nested settings (server.host, database.port)
        # - Default values
        # - Environment variable overrides

        print("\nAll tests passed!")


if __name__ == "__main__":
    test_app_config()
