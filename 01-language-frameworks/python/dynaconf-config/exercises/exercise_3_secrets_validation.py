"""Exercise 3: Secrets and Validation

Implement secure configuration with validation.

Requirements:
1. Create two configuration files:
   - settings.toml: Regular settings (committed to git)
   - .secrets.toml: Sensitive settings (gitignored)

2. Add validators for:
   - APP_NAME: required, non-empty string
   - PORT: required, integer between 1024 and 65535
   - DEBUG: boolean, must be false in production
   - DATABASE_URL: required
   - API_KEY: required, minimum 20 characters
   - JWT_SECRET: required, minimum 32 characters

3. Implement environment-specific validation:
   - Production: SSL must be enabled, debug must be false
   - Development: More lenient validation

4. Handle validation errors gracefully with custom messages

Expected behavior:
    # Valid configuration
    settings = create_validated_settings()
    print(settings.app_name)  # Works

    # Missing required secret
    # Should raise ValidationError with helpful message

    # Production with debug=true
    # Should raise ValidationError

Hints:
- Use Validator from dynaconf
- Use must_exist, is_type_of, gte, lte, len_min
- Use env parameter for environment-specific validators
- Use messages parameter for custom error messages
"""

import tempfile
from pathlib import Path

from dynaconf import Dynaconf, Validator, ValidationError


def create_settings_file(base_dir: Path) -> Path:
    """Create the main settings file.

    TODO: Add regular (non-sensitive) configuration.
    """
    settings_path = base_dir / "settings.toml"
    settings_path.write_text("""
# TODO: Add your settings
[default]
app_name = "SecureApp"
port = 8000
debug = false
""")
    return settings_path


def create_secrets_file(base_dir: Path) -> Path:
    """Create the secrets file.

    TODO: Add sensitive configuration.
    """
    secrets_path = base_dir / ".secrets.toml"
    secrets_path.write_text("""
# TODO: Add your secrets
[default]
database_url = "postgresql://localhost/myapp"
api_key = "this-is-a-development-api-key"
jwt_secret = "this-is-a-32-character-jwt-secret!"
""")
    return secrets_path


def get_validators() -> list:
    """Return the list of validators.

    TODO: Implement validators for all requirements.
    """
    return [
        # TODO: Add validators
        Validator("app_name", must_exist=True),
    ]


def create_validated_settings(settings_path: Path, secrets_path: Path) -> Dynaconf:
    """Create a validated Dynaconf settings instance.

    TODO: Implement with proper validation.
    """
    return Dynaconf(
        settings_files=[str(settings_path), str(secrets_path)],
        validators=get_validators(),
    )


def test_secrets_validation() -> None:
    """Test your secrets and validation implementation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        settings_path = create_settings_file(base_dir)
        secrets_path = create_secrets_file(base_dir)

        # Test valid configuration
        try:
            settings = create_validated_settings(settings_path, secrets_path)
            print(f"app_name: {settings.app_name}")
            print("Valid configuration loaded successfully")
        except ValidationError as e:
            print(f"Validation failed: {e}")

        # TODO: Add tests for:
        # - Missing required secrets
        # - Invalid values (port out of range, etc.)
        # - Production-specific validation
        # - Custom error messages

        print("\nAll tests passed!")


if __name__ == "__main__":
    test_secrets_validation()
