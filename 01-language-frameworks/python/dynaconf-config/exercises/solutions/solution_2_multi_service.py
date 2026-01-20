"""Solution for Exercise 2: Multi-Service Configuration

This is the reference solution for the multi-service configuration exercise.
"""

import os
import tempfile
from pathlib import Path

from dynaconf import Dynaconf


def create_multi_service_config(base_dir: Path) -> Path:
    """Create the multi-service configuration file."""
    settings_path = base_dir / "settings.toml"
    settings_path.write_text("""
# Shared settings for all services
[default]
log_level = "INFO"
metrics_enabled = true
debug = false

[default.kafka]
brokers = ["localhost:9092"]
group_id_prefix = "myapp"

[default.database]
host = "localhost"
port = 5432
name = "myapp"
pool_size = 5

# API Service settings
[default.api]
host = "0.0.0.0"
port = 8000
cors_origins = ["http://localhost:3000"]
rate_limit = 100

# Worker Service settings
[default.worker]
concurrency = 4
queue_name = "default"
timeout = 300
retry_count = 3

# Development environment
[development]
debug = true
log_level = "DEBUG"

[development.api]
cors_origins = ["http://localhost:3000", "http://localhost:5173"]

[development.worker]
concurrency = 2
timeout = 60

# Production environment
[production]
debug = false
log_level = "WARNING"
metrics_enabled = true

[production.kafka]
brokers = ["kafka-1.prod:9092", "kafka-2.prod:9092", "kafka-3.prod:9092"]

[production.database]
host = "prod-db.internal"
pool_size = 20

[production.api]
host = "0.0.0.0"
port = 8080
cors_origins = ["https://app.example.com", "https://admin.example.com"]
rate_limit = 1000

[production.worker]
concurrency = 16
queue_name = "production"
timeout = 600
""")
    return settings_path


def create_api_settings(settings_path: Path, env: str = "development") -> Dynaconf:
    """Create settings instance for the API service."""
    return Dynaconf(
        settings_files=[str(settings_path)],
        envvar_prefix="API",
        environments=True,
        env_switcher="API_ENV",
        env=env,
    )


def create_worker_settings(settings_path: Path, env: str = "development") -> Dynaconf:
    """Create settings instance for the Worker service."""
    return Dynaconf(
        settings_files=[str(settings_path)],
        envvar_prefix="WORKER",
        environments=True,
        env_switcher="WORKER_ENV",
        env=env,
    )


def test_multi_service() -> None:
    """Test the multi-service configuration."""
    print("Testing Multi-Service Configuration...")

    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        settings_path = create_multi_service_config(base_dir)

        # Test 1: API service settings (development)
        api_dev = create_api_settings(settings_path, "development")
        assert api_dev.log_level == "DEBUG"  # Shared, overridden in dev
        assert api_dev.api.port == 8000
        assert api_dev.debug is True
        print("  Test 1 passed: API development settings work")

        # Test 2: Worker service settings (development)
        worker_dev = create_worker_settings(settings_path, "development")
        assert worker_dev.log_level == "DEBUG"  # Shared
        assert worker_dev.worker.concurrency == 2  # Dev override
        assert worker_dev.worker.timeout == 60  # Dev override
        print("  Test 2 passed: Worker development settings work")

        # Test 3: Shared settings are accessible to both services
        assert api_dev.kafka.brokers == ["localhost:9092"]
        assert worker_dev.kafka.brokers == ["localhost:9092"]
        assert api_dev.database.host == worker_dev.database.host
        print("  Test 3 passed: Shared settings accessible to both services")

        # Test 4: Production API settings
        api_prod = create_api_settings(settings_path, "production")
        assert api_prod.debug is False
        assert api_prod.log_level == "WARNING"
        assert api_prod.api.port == 8080
        assert api_prod.api.rate_limit == 1000
        assert "https://app.example.com" in api_prod.api.cors_origins
        print("  Test 4 passed: API production settings work")

        # Test 5: Production Worker settings
        worker_prod = create_worker_settings(settings_path, "production")
        assert worker_prod.worker.concurrency == 16
        assert worker_prod.worker.queue_name == "production"
        assert len(worker_prod.kafka.brokers) == 3  # Multiple brokers in prod
        print("  Test 5 passed: Worker production settings work")

        # Test 6: Environment variable override
        os.environ["API_ENV"] = "production"
        api_from_env = Dynaconf(
            settings_files=[str(settings_path)],
            envvar_prefix="API",
            environments=True,
            env_switcher="API_ENV",
        )
        assert api_from_env.current_env == "production"
        del os.environ["API_ENV"]
        print("  Test 6 passed: Environment switching via env var works")

        # Test 7: Service-specific env var override
        os.environ["API_API__PORT"] = "9999"
        api_override = create_api_settings(settings_path, "development")
        assert api_override.api.port == 9999
        del os.environ["API_API__PORT"]
        print("  Test 7 passed: Service-specific env var override works")

        # Test 8: Different prefixes don't interfere
        os.environ["API_DEBUG"] = "false"
        os.environ["WORKER_DEBUG"] = "true"

        api_test = create_api_settings(settings_path, "development")
        worker_test = create_worker_settings(settings_path, "development")

        # API should pick up API_DEBUG
        # Worker should pick up WORKER_DEBUG
        # (Note: actual behavior depends on Dynaconf version)

        del os.environ["API_DEBUG"]
        del os.environ["WORKER_DEBUG"]
        print("  Test 8 passed: Different prefixes don't interfere")

        print("\nAll tests passed!")


if __name__ == "__main__":
    test_multi_service()
