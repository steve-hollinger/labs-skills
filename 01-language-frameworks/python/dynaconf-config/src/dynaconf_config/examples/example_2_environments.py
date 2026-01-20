"""Example 2: Multi-Environment Configuration

This example demonstrates working with multiple environments
(development, staging, production) using Dynaconf.
"""

import os
import tempfile
from pathlib import Path

from dynaconf import Dynaconf


def create_multi_env_config(base_dir: Path) -> Path:
    """Create a configuration file with multiple environment sections."""
    settings_path = base_dir / "settings.toml"
    settings_path.write_text("""
# Default settings - inherited by all environments
[default]
app_name = "MultiEnvApp"
version = "2.0.0"
debug = false
log_level = "INFO"
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

[default.server]
host = "0.0.0.0"
port = 8000
workers = 2
timeout = 30

[default.database]
driver = "postgresql"
host = "localhost"
port = 5432
pool_size = 5
pool_timeout = 30

[default.cache]
enabled = true
backend = "redis"
host = "localhost"
port = 6379
ttl = 300

[default.features]
enable_api_v2 = false
enable_metrics = true
enable_tracing = false

# Development environment overrides
[development]
debug = true
log_level = "DEBUG"
database.name = "myapp_dev"
cache.ttl = 60

[development.features]
enable_api_v2 = true
enable_tracing = true

# Staging environment overrides
[staging]
debug = false
log_level = "INFO"
server.workers = 4

[staging.database]
host = "staging-db.internal"
name = "myapp_staging"
pool_size = 10

[staging.cache]
host = "staging-redis.internal"

[staging.features]
enable_api_v2 = true

# Production environment overrides
[production]
debug = false
log_level = "WARNING"
server.workers = 8
server.timeout = 60

[production.database]
host = "prod-db.internal"
name = "myapp_prod"
pool_size = 20
pool_timeout = 60

[production.cache]
host = "prod-redis.internal"
ttl = 600

[production.features]
enable_metrics = true
enable_tracing = true
""")
    return settings_path


def show_environment_settings(settings: Dynaconf, env_name: str) -> None:
    """Display key settings for an environment."""
    print(f"\n   [{env_name.upper()}] Environment:")
    print(f"   Debug: {settings.debug}")
    print(f"   Log Level: {settings.log_level}")
    print(f"   Server Workers: {settings.server.workers}")
    print(f"   Database Host: {settings.database.host}")
    print(f"   Database Name: {settings.database.name}")
    print(f"   Cache TTL: {settings.cache.ttl}")
    print(f"   Feature API v2: {settings.features.enable_api_v2}")


def main() -> None:
    """Run the multi-environment example."""
    print("Example 2: Multi-Environment Configuration")
    print("=" * 50)

    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        settings_path = create_multi_env_config(base_dir)

        # 1. Default environment (development)
        print("\n1. Loading with environments enabled:")
        settings = Dynaconf(
            settings_files=[str(settings_path)],
            environments=True,  # Enable environment sections
            env_switcher="APP_ENV",  # Environment variable to switch envs
            env="development",  # Default environment
        )

        print(f"   Current environment: {settings.current_env}")
        show_environment_settings(settings, "development")

        # 2. Switching to staging via env var
        print("\n2. Switching to STAGING environment:")
        os.environ["APP_ENV"] = "staging"

        settings_staging = Dynaconf(
            settings_files=[str(settings_path)],
            environments=True,
            env_switcher="APP_ENV",
        )

        print(f"   Current environment: {settings_staging.current_env}")
        show_environment_settings(settings_staging, "staging")

        # 3. Switching to production
        print("\n3. Switching to PRODUCTION environment:")
        os.environ["APP_ENV"] = "production"

        settings_prod = Dynaconf(
            settings_files=[str(settings_path)],
            environments=True,
            env_switcher="APP_ENV",
        )

        print(f"   Current environment: {settings_prod.current_env}")
        show_environment_settings(settings_prod, "production")

        # Clean up
        del os.environ["APP_ENV"]

        # 4. Explicit environment specification
        print("\n4. Explicit environment specification (no env var needed):")
        for env in ["development", "staging", "production"]:
            settings_explicit = Dynaconf(
                settings_files=[str(settings_path)],
                environments=True,
                env=env,
            )
            print(f"   {env}: workers={settings_explicit.server.workers}, "
                  f"db_host={settings_explicit.database.host}")

        # 5. Default section inheritance
        print("\n5. Default section inheritance:")
        settings_dev = Dynaconf(
            settings_files=[str(settings_path)],
            environments=True,
            env="development",
        )

        print("   Settings from [default] section:")
        print(f"   app_name: {settings_dev.app_name}")  # From default
        print(f"   version: {settings_dev.version}")  # From default
        print(f"   log_format: {settings_dev.log_format}")  # From default
        print("   Settings overridden in [development]:")
        print(f"   debug: {settings_dev.debug}")  # Overridden
        print(f"   log_level: {settings_dev.log_level}")  # Overridden

        # 6. Environment-specific feature flags
        print("\n6. Feature flags by environment:")
        for env in ["development", "staging", "production"]:
            s = Dynaconf(
                settings_files=[str(settings_path)],
                environments=True,
                env=env,
            )
            print(f"   {env}:")
            print(f"     - API v2: {s.features.enable_api_v2}")
            print(f"     - Metrics: {s.features.enable_metrics}")
            print(f"     - Tracing: {s.features.enable_tracing}")

        # 7. Using from_env for temporary environment switch
        print("\n7. Temporary environment context:")
        settings_base = Dynaconf(
            settings_files=[str(settings_path)],
            environments=True,
            env="development",
        )

        print(f"   Base env: {settings_base.current_env}")
        print(f"   Dev workers: {settings_base.server.workers}")

        # Get settings from a different environment
        prod_settings = settings_base.from_env("production")
        print(f"   Production workers (from_env): {prod_settings.server.workers}")

        print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
