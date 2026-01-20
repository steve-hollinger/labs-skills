"""Example 1: Basic Configuration

This example demonstrates loading settings from files and environment variables
using Dynaconf's core features.
"""

import os
import tempfile
from pathlib import Path

from dynaconf import Dynaconf


def create_sample_config_files(base_dir: Path) -> tuple[Path, Path]:
    """Create sample configuration files for the example."""
    # Main settings file (TOML format)
    settings_path = base_dir / "settings.toml"
    settings_path.write_text("""
# Application settings
[default]
app_name = "MyApplication"
version = "1.0.0"
debug = false
log_level = "INFO"

# Server configuration
[default.server]
host = "0.0.0.0"
port = 8000
workers = 4

# Database configuration
[default.database]
driver = "postgresql"
host = "localhost"
port = 5432
name = "myapp"
pool_size = 5
""")

    # Secrets file (would be gitignored in real app)
    secrets_path = base_dir / ".secrets.toml"
    secrets_path.write_text("""
[default]
database_password = "dev-secret-password"
api_key = "dev-api-key-12345"
jwt_secret = "dev-jwt-secret-key"
""")

    return settings_path, secrets_path


def main() -> None:
    """Run the basic configuration example."""
    print("Example 1: Basic Dynaconf Configuration")
    print("=" * 50)

    # Create a temporary directory with config files
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        settings_path, secrets_path = create_sample_config_files(base_dir)

        # 1. Basic settings loading
        print("\n1. Loading settings from files:")
        settings = Dynaconf(
            settings_files=[str(settings_path), str(secrets_path)],
            envvar_prefix="MYAPP",  # Environment variables: MYAPP_*
        )

        print(f"   App Name: {settings.app_name}")
        print(f"   Version: {settings.version}")
        print(f"   Debug: {settings.debug}")
        print(f"   Log Level: {settings.log_level}")

        # 2. Nested settings access
        print("\n2. Accessing nested settings:")
        print(f"   Server Host: {settings.server.host}")
        print(f"   Server Port: {settings.server.port}")
        print(f"   Database Host: {settings.database.host}")
        print(f"   Database Name: {settings.database.name}")

        # Alternative access methods
        print("\n3. Alternative access methods:")
        print(f"   Attribute style: {settings.server.port}")
        print(f"   Dict style: {settings['server']['port']}")
        print(f"   Get with default: {settings.get('missing_key', 'default_value')}")

        # 4. Type information
        print("\n4. Automatic type casting from TOML:")
        print(f"   port type: {type(settings.server.port).__name__}")  # int
        print(f"   debug type: {type(settings.debug).__name__}")  # bool
        print(f"   host type: {type(settings.server.host).__name__}")  # str

        # 5. Secrets from separate file
        print("\n5. Secrets from .secrets.toml:")
        print(f"   API Key: {settings.api_key[:10]}...")  # Don't print full key
        print(f"   JWT Secret: {settings.jwt_secret[:10]}...")

        # 6. Environment variable override
        print("\n6. Environment variable override:")
        # Set environment variable
        os.environ["MYAPP_DEBUG"] = "true"
        os.environ["MYAPP_SERVER__PORT"] = "9000"  # Double underscore for nesting

        # Create new settings instance to pick up env vars
        settings_with_env = Dynaconf(
            settings_files=[str(settings_path)],
            envvar_prefix="MYAPP",
        )

        print(f"   Original debug: {settings.debug}")
        print(f"   With env var (MYAPP_DEBUG=true): {settings_with_env.debug}")
        print(f"   Original port: {settings.server.port}")
        print(f"   With env var (MYAPP_SERVER__PORT=9000): {settings_with_env.server.port}")

        # Clean up env vars
        del os.environ["MYAPP_DEBUG"]
        del os.environ["MYAPP_SERVER__PORT"]

        # 7. Checking if settings exist
        print("\n7. Checking settings existence:")
        print(f"   'app_name' exists: {settings.exists('app_name')}")
        print(f"   'missing_key' exists: {settings.exists('missing_key')}")
        print(f"   'server.host' exists: {settings.exists('server.host')}")

        # 8. Converting to dict
        print("\n8. Converting settings to dict:")
        settings_dict = settings.as_dict()
        print(f"   Top-level keys: {list(settings_dict.keys())[:5]}...")

        # 9. Runtime setting modification
        print("\n9. Runtime setting modification:")
        settings.set("runtime_value", "set at runtime")
        print(f"   Runtime value: {settings.runtime_value}")

        # Temporary override
        with settings.using_env("custom"):
            # This creates a temporary context (useful for testing)
            pass

        print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
