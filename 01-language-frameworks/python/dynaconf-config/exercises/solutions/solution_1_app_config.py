"""Solution for Exercise 1: Basic App Configuration

This is the reference solution for the app configuration exercise.
"""

import os
import tempfile
from pathlib import Path

from dynaconf import Dynaconf


def create_config_file(base_dir: Path) -> Path:
    """Create the configuration file with all required settings."""
    settings_path = base_dir / "settings.toml"
    settings_path.write_text("""
[default]
app_name = "MyWebApp"
debug = false
log_level = "INFO"

[default.server]
host = "0.0.0.0"
port = 8000
workers = 4

[default.database]
host = "localhost"
port = 5432
name = "webapp_db"
pool_size = 5
""")
    return settings_path


def create_settings(settings_path: Path) -> Dynaconf:
    """Create the Dynaconf settings instance with proper configuration."""
    return Dynaconf(
        settings_files=[str(settings_path)],
        envvar_prefix="WEBAPP",
    )


def test_app_config() -> None:
    """Test the configuration implementation."""
    print("Testing App Configuration...")

    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        settings_path = create_config_file(base_dir)
        settings = create_settings(settings_path)

        # Test 1: Basic setting access
        assert settings.app_name == "MyWebApp"
        print("  Test 1 passed: Basic setting access works")

        # Test 2: Nested settings access
        assert settings.server.host == "0.0.0.0"
        assert settings.server.port == 8000
        assert settings.database.host == "localhost"
        assert settings.database.port == 5432
        print("  Test 2 passed: Nested settings access works")

        # Test 3: Boolean settings
        assert settings.debug is False
        print("  Test 3 passed: Boolean settings work")

        # Test 4: Default values for missing settings
        missing_value = settings.get("nonexistent", "default")
        assert missing_value == "default"
        print("  Test 4 passed: Default values work")

        # Test 5: Environment variable override
        os.environ["WEBAPP_DEBUG"] = "true"
        os.environ["WEBAPP_SERVER__PORT"] = "9000"

        # Create new instance to pick up env vars
        settings_with_env = create_settings(settings_path)

        assert settings_with_env.debug is True
        assert settings_with_env.server.port == 9000
        print("  Test 5 passed: Environment variable override works")

        # Clean up env vars
        del os.environ["WEBAPP_DEBUG"]
        del os.environ["WEBAPP_SERVER__PORT"]

        # Test 6: Settings exist check
        assert settings.exists("app_name")
        assert settings.exists("server.host")
        assert not settings.exists("nonexistent")
        print("  Test 6 passed: Settings existence check works")

        # Test 7: Convert to dict
        settings_dict = settings.as_dict()
        assert "APP_NAME" in settings_dict or "app_name" in settings_dict
        print("  Test 7 passed: Convert to dict works")

        # Test 8: Type preservation from TOML
        assert isinstance(settings.server.port, int)
        assert isinstance(settings.debug, bool)
        assert isinstance(settings.app_name, str)
        print("  Test 8 passed: Types preserved from TOML")

        print("\nAll tests passed!")


if __name__ == "__main__":
    test_app_config()
