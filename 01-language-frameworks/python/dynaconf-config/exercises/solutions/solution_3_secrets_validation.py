"""Solution for Exercise 3: Secrets and Validation

This is the reference solution for the secrets and validation exercise.
"""

import tempfile
from pathlib import Path

from dynaconf import Dynaconf, ValidationError, Validator


def create_settings_file(base_dir: Path) -> Path:
    """Create the main settings file with non-sensitive configuration."""
    settings_path = base_dir / "settings.toml"
    settings_path.write_text("""
[default]
app_name = "SecureApp"
port = 8000
debug = false
log_level = "INFO"
ssl_enabled = false

[default.server]
host = "0.0.0.0"
workers = 4

[development]
debug = true
ssl_enabled = false

[production]
debug = false
ssl_enabled = true
log_level = "WARNING"
server.workers = 8
""")
    return settings_path


def create_secrets_file(base_dir: Path) -> Path:
    """Create the secrets file with sensitive configuration."""
    secrets_path = base_dir / ".secrets.toml"
    secrets_path.write_text("""
[default]
database_url = "postgresql://user:pass@localhost:5432/myapp"
api_key = "dev-api-key-at-least-20-chars"
jwt_secret = "this-is-a-very-secure-32-char-jwt!!"

[production]
database_url = "postgresql://user:pass@prod-db:5432/myapp"
api_key = "prod-api-key-very-secure-key-here"
jwt_secret = "prod-jwt-secret-must-be-32-characters!!"
""")
    return secrets_path


def get_validators() -> list[Validator]:
    """Return the list of validators for all requirements."""
    return [
        # Required settings with custom messages
        Validator(
            "app_name",
            must_exist=True,
            len_min=1,
            messages={
                "must_exist_true": "APP_NAME is required. Set it in settings.toml",
                "len_min": "APP_NAME cannot be empty",
            },
        ),
        # Port validation - integer in valid range
        Validator(
            "port",
            must_exist=True,
            is_type_of=int,
            gte=1024,
            lte=65535,
            messages={
                "must_exist_true": "PORT is required",
                "operations": "PORT must be between 1024 and 65535",
            },
        ),
        # Boolean with type check
        Validator("debug", is_type_of=bool, default=False),
        # Required database URL
        Validator(
            "database_url",
            must_exist=True,
            messages={"must_exist_true": "DATABASE_URL is required in .secrets.toml"},
        ),
        # API key with minimum length
        Validator(
            "api_key",
            must_exist=True,
            len_min=20,
            messages={
                "must_exist_true": "API_KEY is required in .secrets.toml",
                "len_min": "API_KEY must be at least 20 characters for security",
            },
        ),
        # JWT secret with minimum length
        Validator(
            "jwt_secret",
            must_exist=True,
            len_min=32,
            messages={
                "must_exist_true": "JWT_SECRET is required in .secrets.toml",
                "len_min": "JWT_SECRET must be at least 32 characters",
            },
        ),
        # Production-specific: debug must be false
        Validator(
            "debug",
            eq=False,
            env="production",
            messages={"operations": "DEBUG must be False in production"},
        ),
        # Production-specific: SSL must be enabled
        Validator(
            "ssl_enabled",
            eq=True,
            env="production",
            messages={"operations": "SSL must be enabled in production"},
        ),
        # Log level validation
        Validator(
            "log_level",
            is_in=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            default="INFO",
        ),
    ]


def create_validated_settings(
    settings_path: Path, secrets_path: Path, env: str = "development"
) -> Dynaconf:
    """Create a validated Dynaconf settings instance."""
    return Dynaconf(
        settings_files=[str(settings_path), str(secrets_path)],
        envvar_prefix="SECURE",
        environments=True,
        env=env,
        validators=get_validators(),
    )


def test_secrets_validation() -> None:
    """Test the secrets and validation implementation."""
    print("Testing Secrets and Validation...")

    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        settings_path = create_settings_file(base_dir)
        secrets_path = create_secrets_file(base_dir)

        # Test 1: Valid development configuration
        try:
            settings_dev = create_validated_settings(
                settings_path, secrets_path, "development"
            )
            assert settings_dev.app_name == "SecureApp"
            assert settings_dev.debug is True  # Development allows debug
            print("  Test 1 passed: Valid development config loads")
        except ValidationError as e:
            print(f"  Test 1 FAILED: {e}")

        # Test 2: Valid production configuration
        try:
            settings_prod = create_validated_settings(
                settings_path, secrets_path, "production"
            )
            assert settings_prod.debug is False
            assert settings_prod.ssl_enabled is True
            print("  Test 2 passed: Valid production config loads")
        except ValidationError as e:
            print(f"  Test 2 FAILED: {e}")

        # Test 3: Secrets are loaded
        settings = create_validated_settings(settings_path, secrets_path)
        assert settings.database_url.startswith("postgresql://")
        assert len(settings.api_key) >= 20
        assert len(settings.jwt_secret) >= 32
        print("  Test 3 passed: Secrets loaded correctly")

        # Test 4: Missing required secret
        invalid_secrets = base_dir / ".invalid_secrets.toml"
        invalid_secrets.write_text("""
[default]
database_url = "postgresql://localhost/myapp"
# Missing api_key and jwt_secret
""")
        try:
            Dynaconf(
                settings_files=[str(settings_path), str(invalid_secrets)],
                validators=get_validators(),
            )
            print("  Test 4 FAILED: Should have raised ValidationError")
        except ValidationError:
            print("  Test 4 passed: Missing secret raises ValidationError")

        # Test 5: API key too short
        short_key_secrets = base_dir / ".short_key_secrets.toml"
        short_key_secrets.write_text("""
[default]
database_url = "postgresql://localhost/myapp"
api_key = "short"
jwt_secret = "this-is-a-very-secure-32-char-jwt!!"
""")
        try:
            Dynaconf(
                settings_files=[str(settings_path), str(short_key_secrets)],
                validators=get_validators(),
            )
            print("  Test 5 FAILED: Should have raised ValidationError for short API key")
        except ValidationError as e:
            assert "20 characters" in str(e) or "len_min" in str(e).lower()
            print("  Test 5 passed: Short API key raises ValidationError")

        # Test 6: Invalid port
        invalid_port_settings = base_dir / "invalid_port.toml"
        invalid_port_settings.write_text("""
[default]
app_name = "TestApp"
port = 80
debug = false
""")
        try:
            Dynaconf(
                settings_files=[str(invalid_port_settings), str(secrets_path)],
                validators=get_validators(),
            )
            print("  Test 6 FAILED: Should have raised ValidationError for port < 1024")
        except ValidationError:
            print("  Test 6 passed: Invalid port raises ValidationError")

        # Test 7: Production with debug=true should fail
        debug_prod_settings = base_dir / "debug_prod.toml"
        debug_prod_settings.write_text("""
[default]
app_name = "TestApp"
port = 8000
debug = false
ssl_enabled = false

[production]
debug = true
ssl_enabled = true
""")
        try:
            Dynaconf(
                settings_files=[str(debug_prod_settings), str(secrets_path)],
                environments=True,
                env="production",
                validators=get_validators(),
            )
            print("  Test 7 FAILED: Should have raised ValidationError for debug=true in prod")
        except ValidationError as e:
            assert "production" in str(e).lower() or "debug" in str(e).lower()
            print("  Test 7 passed: Debug=true in production raises ValidationError")

        # Test 8: Verify secrets not in main settings file
        settings_content = settings_path.read_text()
        assert "api_key" not in settings_content.lower()
        assert "jwt_secret" not in settings_content.lower()
        assert "password" not in settings_content.lower()
        print("  Test 8 passed: Secrets not in main settings file")

        print("\nAll tests passed!")


if __name__ == "__main__":
    test_secrets_validation()
