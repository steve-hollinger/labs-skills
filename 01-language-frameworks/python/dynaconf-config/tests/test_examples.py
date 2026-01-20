"""Tests for Dynaconf Config examples."""

import os
import tempfile
from pathlib import Path

import pytest
from dynaconf import Dynaconf, ValidationError, Validator


class TestExample1BasicConfig:
    """Tests for Example 1: Basic Configuration."""

    def test_basic_settings_loading(self) -> None:
        """Test loading settings from TOML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.toml"
            settings_path.write_text("""
[default]
app_name = "TestApp"
debug = false
port = 8000
""")
            settings = Dynaconf(settings_files=[str(settings_path)])

            assert settings.app_name == "TestApp"
            assert settings.debug is False
            assert settings.port == 8000

    def test_nested_settings(self) -> None:
        """Test accessing nested settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.toml"
            settings_path.write_text("""
[default.database]
host = "localhost"
port = 5432
name = "testdb"
""")
            settings = Dynaconf(settings_files=[str(settings_path)])

            assert settings.database.host == "localhost"
            assert settings.database.port == 5432
            assert settings.database.name == "testdb"

    def test_environment_variable_override(self) -> None:
        """Test environment variable override."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.toml"
            settings_path.write_text("""
[default]
debug = false
port = 8000
""")
            os.environ["TEST_DEBUG"] = "true"
            os.environ["TEST_PORT"] = "9000"

            try:
                settings = Dynaconf(
                    settings_files=[str(settings_path)],
                    envvar_prefix="TEST",
                )
                assert settings.debug is True
                assert settings.port == 9000
            finally:
                del os.environ["TEST_DEBUG"]
                del os.environ["TEST_PORT"]

    def test_secrets_file_loading(self) -> None:
        """Test loading secrets from separate file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.toml"
            secrets_path = Path(tmpdir) / ".secrets.toml"

            settings_path.write_text("""
[default]
app_name = "TestApp"
""")
            secrets_path.write_text("""
[default]
api_key = "secret-key-123"
""")

            settings = Dynaconf(
                settings_files=[str(settings_path), str(secrets_path)]
            )

            assert settings.app_name == "TestApp"
            assert settings.api_key == "secret-key-123"


class TestExample2Environments:
    """Tests for Example 2: Multi-Environment Configuration."""

    def test_default_environment(self) -> None:
        """Test default environment settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.toml"
            settings_path.write_text("""
[default]
debug = false
log_level = "INFO"

[development]
debug = true
log_level = "DEBUG"
""")
            settings = Dynaconf(
                settings_files=[str(settings_path)],
                environments=True,
                env="development",
            )

            assert settings.debug is True
            assert settings.log_level == "DEBUG"

    def test_environment_switching(self) -> None:
        """Test switching between environments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.toml"
            settings_path.write_text("""
[default]
workers = 2

[development]
workers = 2

[production]
workers = 8
""")
            settings_dev = Dynaconf(
                settings_files=[str(settings_path)],
                environments=True,
                env="development",
            )
            settings_prod = Dynaconf(
                settings_files=[str(settings_path)],
                environments=True,
                env="production",
            )

            assert settings_dev.workers == 2
            assert settings_prod.workers == 8

    def test_environment_inheritance(self) -> None:
        """Test that environments inherit from default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.toml"
            settings_path.write_text("""
[default]
app_name = "MyApp"
version = "1.0.0"
debug = false

[development]
debug = true
""")
            settings = Dynaconf(
                settings_files=[str(settings_path)],
                environments=True,
                env="development",
            )

            # Inherited from default
            assert settings.app_name == "MyApp"
            assert settings.version == "1.0.0"
            # Overridden in development
            assert settings.debug is True


class TestExample3Validation:
    """Tests for Example 3: Settings Validation."""

    def test_required_validator(self) -> None:
        """Test must_exist validator."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.toml"
            settings_path.write_text("""
[default]
app_name = "TestApp"
""")
            # Should pass - required field exists
            settings = Dynaconf(
                settings_files=[str(settings_path)],
                validators=[Validator("app_name", must_exist=True)],
            )
            assert settings.app_name == "TestApp"

    def test_missing_required_raises_error(self) -> None:
        """Test that missing required field raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.toml"
            settings_path.write_text("""
[default]
other_setting = "value"
""")
            with pytest.raises(ValidationError):
                Dynaconf(
                    settings_files=[str(settings_path)],
                    validators=[Validator("required_field", must_exist=True)],
                )

    def test_range_validator(self) -> None:
        """Test range validation (gte, lte)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.toml"
            settings_path.write_text("""
[default]
port = 8000
""")
            settings = Dynaconf(
                settings_files=[str(settings_path)],
                validators=[Validator("port", gte=1024, lte=65535)],
            )
            assert settings.port == 8000

    def test_invalid_range_raises_error(self) -> None:
        """Test that value outside range raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.toml"
            settings_path.write_text("""
[default]
port = 80
""")
            with pytest.raises(ValidationError):
                Dynaconf(
                    settings_files=[str(settings_path)],
                    validators=[Validator("port", gte=1024)],
                )

    def test_default_validator(self) -> None:
        """Test validator with default value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.toml"
            settings_path.write_text("""
[default]
app_name = "TestApp"
""")
            settings = Dynaconf(
                settings_files=[str(settings_path)],
                validators=[
                    Validator("missing_field", default="default_value"),
                ],
            )
            assert settings.missing_field == "default_value"


class TestExample4Advanced:
    """Tests for Example 4: Advanced Features."""

    def test_yaml_format(self) -> None:
        """Test loading YAML configuration."""
        import yaml

        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.yaml"
            config = {
                "default": {
                    "app_name": "YAMLApp",
                    "features": ["auth", "logging"],
                }
            }
            with open(settings_path, "w") as f:
                yaml.dump(config, f)

            settings = Dynaconf(settings_files=[str(settings_path)])

            assert settings.app_name == "YAMLApp"
            assert settings.features == ["auth", "logging"]

    def test_json_format(self) -> None:
        """Test loading JSON configuration."""
        import json

        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.json"
            config = {"default": {"app_name": "JSONApp", "version": 1}}
            with open(settings_path, "w") as f:
                json.dump(config, f)

            settings = Dynaconf(settings_files=[str(settings_path)])

            assert settings.app_name == "JSONApp"
            assert settings.version == 1

    def test_programmatic_setting(self) -> None:
        """Test setting values programmatically."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.toml"
            settings_path.write_text("""
[default]
app_name = "TestApp"
""")
            settings = Dynaconf(settings_files=[str(settings_path)])

            settings.set("runtime_value", "set at runtime")
            assert settings.runtime_value == "set at runtime"

    def test_settings_clone(self) -> None:
        """Test cloning settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.toml"
            settings_path.write_text("""
[default]
value = "original"
""")
            settings = Dynaconf(settings_files=[str(settings_path)])
            clone = settings.dynaconf_clone()

            clone.set("value", "modified")

            assert settings.value == "original"
            assert clone.value == "modified"

    def test_as_dict(self) -> None:
        """Test converting settings to dict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.toml"
            settings_path.write_text("""
[default]
key1 = "value1"
key2 = "value2"
""")
            settings = Dynaconf(settings_files=[str(settings_path)])
            settings_dict = settings.as_dict()

            assert isinstance(settings_dict, dict)
            # Keys might be uppercased depending on Dynaconf version
            assert "KEY1" in settings_dict or "key1" in settings_dict
