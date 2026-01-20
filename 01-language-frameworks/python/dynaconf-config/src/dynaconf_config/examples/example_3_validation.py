"""Example 3: Settings Validation

This example demonstrates using Dynaconf validators to ensure
configuration values meet requirements at startup.
"""

import tempfile
from pathlib import Path

from dynaconf import Dynaconf, Validator, ValidationError


def create_config_for_validation(base_dir: Path) -> Path:
    """Create a configuration file for validation examples."""
    settings_path = base_dir / "settings.toml"
    settings_path.write_text("""
[default]
app_name = "ValidatedApp"
debug = false
log_level = "INFO"
port = 8000
workers = 4
timeout = 30
max_connections = 100

[default.database]
host = "localhost"
port = 5432
name = "myapp"
pool_size = 10
ssl_enabled = false

[default.api]
rate_limit = 100
api_version = "v1"

[development]
debug = true
log_level = "DEBUG"
workers = 2

[production]
debug = false
log_level = "WARNING"
workers = 8
database.ssl_enabled = true
""")
    return settings_path


def create_invalid_config(base_dir: Path) -> Path:
    """Create a configuration with validation errors."""
    settings_path = base_dir / "invalid_settings.toml"
    settings_path.write_text("""
[default]
app_name = ""
debug = "not-a-boolean"
port = 80
workers = 0
timeout = -5
""")
    return settings_path


def main() -> None:
    """Run the validation example."""
    print("Example 3: Settings Validation")
    print("=" * 50)

    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        settings_path = create_config_for_validation(base_dir)

        # 1. Basic validators
        print("\n1. Basic validators (must_exist, is_type_of):")
        settings = Dynaconf(
            settings_files=[str(settings_path)],
            validators=[
                # Required settings
                Validator("app_name", must_exist=True),
                Validator("port", must_exist=True),

                # Type validation
                Validator("debug", is_type_of=bool),
                Validator("port", is_type_of=int),
                Validator("workers", is_type_of=int),
                Validator("log_level", is_type_of=str),
            ],
        )
        print("   All basic validations passed!")
        print(f"   app_name: {settings.app_name}")
        print(f"   debug: {settings.debug} (type: {type(settings.debug).__name__})")

        # 2. Range validators
        print("\n2. Range validators (gt, gte, lt, lte, eq, ne):")
        settings_range = Dynaconf(
            settings_files=[str(settings_path)],
            validators=[
                # Port must be in valid range
                Validator("port", gte=1024, lte=65535),

                # Workers must be positive
                Validator("workers", gte=1, lte=32),

                # Timeout must be positive
                Validator("timeout", gt=0),

                # Pool size constraints
                Validator("database.pool_size", gte=1, lte=100),
            ],
        )
        print("   All range validations passed!")
        print(f"   port: {settings_range.port} (1024-65535)")
        print(f"   workers: {settings_range.workers} (1-32)")
        print(f"   timeout: {settings_range.timeout} (>0)")

        # 3. Default values
        print("\n3. Default values for missing settings:")
        settings_defaults = Dynaconf(
            settings_files=[str(settings_path)],
            validators=[
                # Provide defaults for optional settings
                Validator("optional_feature", default=False),
                Validator("cache_ttl", default=300),
                Validator("retry_count", default=3, is_type_of=int),
                Validator("api.timeout", default=30),
            ],
        )
        print(f"   optional_feature: {settings_defaults.optional_feature} (default)")
        print(f"   cache_ttl: {settings_defaults.cache_ttl} (default)")
        print(f"   retry_count: {settings_defaults.retry_count} (default)")

        # 4. Conditional validators
        print("\n4. Conditional validators (when, condition):")
        settings_conditional = Dynaconf(
            settings_files=[str(settings_path)],
            environments=True,
            env="production",
            validators=[
                # SSL is required when in production
                Validator(
                    "database.ssl_enabled",
                    eq=True,
                    env="production",
                    messages={"operations": "SSL must be enabled in production"},
                ),

                # More workers required in production
                Validator(
                    "workers",
                    gte=4,
                    env="production",
                ),
            ],
        )
        print("   Production validations passed!")
        print(f"   SSL enabled: {settings_conditional.database.ssl_enabled}")
        print(f"   Workers: {settings_conditional.workers}")

        # 5. Validators with custom messages
        print("\n5. Custom error messages:")

        try:
            Dynaconf(
                settings_files=[str(settings_path)],
                validators=[
                    Validator(
                        "missing_required_setting",
                        must_exist=True,
                        messages={
                            "must_exist_true": (
                                "CRITICAL: {name} is required! "
                                "Please set it in settings.toml or via environment variable."
                            )
                        },
                    ),
                ],
            )
        except ValidationError as e:
            print(f"   Custom error message shown: {str(e)[:80]}...")

        # 6. String validators
        print("\n6. String validators (len_min, len_max, startswith, etc.):")
        settings_str = Dynaconf(
            settings_files=[str(settings_path)],
            validators=[
                # Log level must be specific values
                Validator(
                    "log_level",
                    is_in=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                ),

                # API version format
                Validator("api.api_version", startswith="v"),

                # App name length
                Validator("app_name", len_min=1, len_max=100),
            ],
        )
        print(f"   log_level: {settings_str.log_level} (in allowed list)")
        print(f"   api_version: {settings_str.api.api_version} (starts with 'v')")

        # 7. Validation error handling
        print("\n7. Handling validation errors:")
        invalid_path = create_invalid_config(base_dir)

        try:
            Dynaconf(
                settings_files=[str(invalid_path)],
                validators=[
                    Validator("app_name", len_min=1),  # Empty string fails
                    Validator("port", gte=1024),  # Port 80 fails
                    Validator("workers", gte=1),  # Workers 0 fails
                    Validator("timeout", gt=0),  # Negative timeout fails
                ],
            )
        except ValidationError as e:
            print(f"   Caught ValidationError:")
            # Parse and display each error
            error_str = str(e)
            print(f"   {error_str[:200]}...")

        # 8. Registering validators after creation
        print("\n8. Registering validators dynamically:")
        settings_dynamic = Dynaconf(
            settings_files=[str(settings_path)],
        )

        # Add validators after creation
        settings_dynamic.validators.register(
            Validator("max_connections", gte=1, lte=1000),
            Validator("database.host", must_exist=True),
        )

        # Validate
        settings_dynamic.validators.validate()
        print("   Dynamic validators passed!")
        print(f"   max_connections: {settings_dynamic.max_connections}")

        # 9. Combined validators
        print("\n9. Combined validators (multiple conditions):")
        settings_combined = Dynaconf(
            settings_files=[str(settings_path)],
            validators=[
                # Combine multiple checks on same field
                Validator("workers", must_exist=True)
                & Validator("workers", is_type_of=int)
                & Validator("workers", gte=1),

                # Or conditions
                Validator("log_level", eq="DEBUG")
                | Validator("log_level", eq="INFO")
                | Validator("log_level", eq="WARNING"),
            ],
        )
        print("   Combined validators passed!")

        print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
