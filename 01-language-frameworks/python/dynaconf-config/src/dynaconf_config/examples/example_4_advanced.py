"""Example 4: Advanced Features

This example demonstrates advanced Dynaconf features including
programmatic settings, computed values, hooks, and multiple formats.
"""

import os
import tempfile
from pathlib import Path
from typing import Any

import yaml
from dynaconf import Dynaconf


def create_toml_config(base_dir: Path) -> Path:
    """Create a TOML configuration file."""
    settings_path = base_dir / "settings.toml"
    settings_path.write_text("""
[default]
app_name = "AdvancedApp"
format = "toml"
database_url = "@format {this.database.driver}://{this.database.host}:{this.database.port}/{this.database.name}"

[default.database]
driver = "postgresql"
host = "localhost"
port = 5432
name = "myapp"
""")
    return settings_path


def create_yaml_config(base_dir: Path) -> Path:
    """Create a YAML configuration file."""
    settings_path = base_dir / "settings.yaml"
    config = {
        "default": {
            "app_name": "YAMLApp",
            "format": "yaml",
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
            },
            "features": ["auth", "logging", "metrics"],
            "limits": {
                "max_requests": 1000,
                "rate_limit": 100,
            },
        }
    }
    with open(settings_path, "w") as f:
        yaml.dump(config, f)
    return settings_path


def create_json_config(base_dir: Path) -> Path:
    """Create a JSON configuration file."""
    import json

    settings_path = base_dir / "settings.json"
    config = {
        "default": {
            "app_name": "JSONApp",
            "format": "json",
            "cors": {
                "allowed_origins": ["http://localhost:3000", "https://app.example.com"],
                "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
            },
        }
    }
    with open(settings_path, "w") as f:
        json.dump(config, f)
    return settings_path


def main() -> None:
    """Run the advanced features example."""
    print("Example 4: Advanced Dynaconf Features")
    print("=" * 50)

    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)

        # 1. Multiple file formats
        print("\n1. Multiple file formats (TOML, YAML, JSON):")
        toml_path = create_toml_config(base_dir)
        yaml_path = create_yaml_config(base_dir)
        json_path = create_json_config(base_dir)

        # TOML
        settings_toml = Dynaconf(settings_files=[str(toml_path)])
        print(f"   TOML: app_name={settings_toml.app_name}, format={settings_toml.format}")

        # YAML
        settings_yaml = Dynaconf(settings_files=[str(yaml_path)])
        print(f"   YAML: app_name={settings_yaml.app_name}, format={settings_yaml.format}")

        # JSON
        settings_json = Dynaconf(settings_files=[str(json_path)])
        print(f"   JSON: app_name={settings_json.app_name}, format={settings_json.format}")

        # 2. Merging multiple files
        print("\n2. Merging settings from multiple files:")
        settings_merged = Dynaconf(
            settings_files=[
                str(toml_path),
                str(yaml_path),
                str(json_path),
            ],
            merge_enabled=True,  # Enable merging
        )
        print(f"   Final app_name: {settings_merged.app_name}")  # From last file
        print(f"   Has database (from TOML): {settings_merged.exists('database')}")
        print(f"   Has server (from YAML): {settings_merged.exists('server')}")
        print(f"   Has cors (from JSON): {settings_merged.exists('cors')}")

        # 3. Programmatic settings
        print("\n3. Programmatic settings manipulation:")
        settings_prog = Dynaconf(settings_files=[str(toml_path)])

        # Set individual values
        settings_prog.set("runtime_key", "runtime_value")
        print(f"   Set runtime_key: {settings_prog.runtime_key}")

        # Set nested values
        settings_prog.set("cache.host", "redis.local")
        settings_prog.set("cache.port", 6379)
        print(f"   Set cache.host: {settings_prog.cache.host}")
        print(f"   Set cache.port: {settings_prog.cache.port}")

        # Update from dict
        settings_prog.update({
            "new_section": {
                "key1": "value1",
                "key2": "value2",
            }
        })
        print(f"   Updated new_section: {dict(settings_prog.new_section)}")

        # 4. Environment variable special syntax
        print("\n4. Environment variable special syntax:")
        os.environ["MYAPP_PORT"] = "@int 9000"  # Type casting
        os.environ["MYAPP_DEBUG"] = "@bool true"  # Boolean
        os.environ["MYAPP_HOSTS"] = "@json [\"host1\", \"host2\"]"  # JSON

        settings_env = Dynaconf(
            settings_files=[str(toml_path)],
            envvar_prefix="MYAPP",
        )
        print(f"   PORT (@int): {settings_env.port} (type: {type(settings_env.port).__name__})")
        print(f"   DEBUG (@bool): {settings_env.debug}")
        print(f"   HOSTS (@json): {settings_env.hosts}")

        # Clean up
        del os.environ["MYAPP_PORT"]
        del os.environ["MYAPP_DEBUG"]
        del os.environ["MYAPP_HOSTS"]

        # 5. Lazy settings and @format
        print("\n5. Dynamic values with @format:")
        settings_format = Dynaconf(settings_files=[str(toml_path)])
        print(f"   Database URL (computed): {settings_format.database_url}")

        # 6. Settings inspection
        print("\n6. Settings inspection:")
        settings_inspect = Dynaconf(settings_files=[str(yaml_path)])

        # Get all keys
        print(f"   Top-level keys: {list(settings_inspect.keys())}")

        # Check types
        print(f"   features is list: {isinstance(settings_inspect.features, list)}")
        print(f"   limits is dict-like: {hasattr(settings_inspect.limits, 'keys')}")

        # Iterate
        print("   Iterating limits:")
        for key in settings_inspect.limits.keys():
            print(f"     - {key}: {settings_inspect.limits[key]}")

        # 7. Box dotted access vs dict access
        print("\n7. Box dotted access vs dict access:")
        settings_box = Dynaconf(settings_files=[str(yaml_path)])

        # Dotted access
        print(f"   Dotted: settings.server.host = {settings_box.server.host}")

        # Dict-style access
        print(f"   Dict: settings['server']['host'] = {settings_box['server']['host']}")

        # Mixed access
        print(f"   Mixed: settings.server['port'] = {settings_box.server['port']}")

        # 8. Clone/copy settings
        print("\n8. Cloning settings:")
        settings_base = Dynaconf(settings_files=[str(toml_path)])
        settings_clone = settings_base.dynaconf_clone()

        # Modify clone
        settings_clone.set("modified", True)
        print(f"   Original has 'modified': {settings_base.exists('modified')}")
        print(f"   Clone has 'modified': {settings_clone.modified}")

        # 9. Convert to standard Python types
        print("\n9. Converting to Python types:")
        settings_convert = Dynaconf(settings_files=[str(yaml_path)])

        # To dict
        as_dict = settings_convert.as_dict()
        print(f"   as_dict type: {type(as_dict).__name__}")
        print(f"   as_dict keys: {list(as_dict.keys())}")

        # Specific section to dict
        server_dict = dict(settings_convert.server)
        print(f"   server as dict: {server_dict}")

        # 10. Settings with includes
        print("\n10. Settings file includes:")

        # Create base config
        base_config = base_dir / "base.toml"
        base_config.write_text("""
[default]
base_setting = "from base"
shared_value = 100
""")

        # Create main config that references base
        main_config = base_dir / "main.toml"
        main_config.write_text(f"""
dynaconf_include = ["{base_config}"]

[default]
main_setting = "from main"
override_value = "main wins"
""")

        settings_include = Dynaconf(
            settings_files=[str(main_config)],
        )
        print(f"   base_setting: {settings_include.base_setting}")
        print(f"   main_setting: {settings_include.main_setting}")
        print(f"   shared_value: {settings_include.shared_value}")

        print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
