"""Exercise 2: Multi-Service Configuration

Configure multiple services with shared and unique settings.

Requirements:
1. Create a configuration file with:
   - Shared settings (log_level, metrics_enabled, kafka brokers)
   - API service settings (host, port, cors_origins)
   - Worker service settings (concurrency, queue_name, timeout)
   - Database settings (host, port, credentials)

2. Create separate settings instances for:
   - API service (envvar_prefix="API")
   - Worker service (envvar_prefix="WORKER")

3. Implement environment switching:
   - Development: local hosts, debug enabled
   - Production: production hosts, debug disabled

4. Each service should:
   - Have access to shared settings
   - Have its own specific settings
   - Support environment-specific overrides

Expected behavior:
    # API service
    api_settings = create_api_settings()
    print(api_settings.api.port)  # 8000
    print(api_settings.log_level)  # "INFO" (shared)

    # Worker service
    worker_settings = create_worker_settings()
    print(worker_settings.worker.concurrency)  # 4
    print(worker_settings.log_level)  # "INFO" (shared)

    # Production environment
    os.environ["API_ENV"] = "production"
    prod_settings = create_api_settings()
    print(prod_settings.api.port)  # Different in production

Hints:
- Use [default] for shared settings
- Use [default.api] and [default.worker] for service-specific
- Use [production.api] for environment+service overrides
"""

import os
import tempfile
from pathlib import Path

from dynaconf import Dynaconf


def create_multi_service_config(base_dir: Path) -> Path:
    """Create the multi-service configuration file.

    TODO: Implement this function to create a settings.toml file
    with shared and service-specific settings.
    """
    settings_path = base_dir / "settings.toml"
    # TODO: Write the configuration
    settings_path.write_text("""
# TODO: Add your multi-service configuration
[default]
log_level = "INFO"
""")
    return settings_path


def create_api_settings(settings_path: Path) -> Dynaconf:
    """Create settings instance for the API service.

    TODO: Implement with API-specific configuration.
    """
    return Dynaconf(
        settings_files=[str(settings_path)],
        # TODO: Add proper configuration
    )


def create_worker_settings(settings_path: Path) -> Dynaconf:
    """Create settings instance for the Worker service.

    TODO: Implement with Worker-specific configuration.
    """
    return Dynaconf(
        settings_files=[str(settings_path)],
        # TODO: Add proper configuration
    )


def test_multi_service() -> None:
    """Test your multi-service configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        settings_path = create_multi_service_config(base_dir)

        # Test API settings
        api = create_api_settings(settings_path)
        print(f"API log_level: {api.log_level}")

        # Test Worker settings
        worker = create_worker_settings(settings_path)
        print(f"Worker log_level: {worker.log_level}")

        # TODO: Add tests for:
        # - Service-specific settings
        # - Environment switching
        # - Shared vs unique settings

        print("\nAll tests passed!")


if __name__ == "__main__":
    test_multi_service()
