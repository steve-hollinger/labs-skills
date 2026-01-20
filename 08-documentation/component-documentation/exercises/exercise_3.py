"""Exercise 3: Add Documentation to Undocumented Code

Below is a Python module with minimal documentation. Your task is to
add comprehensive docstrings to all public functions and the class.

The code works correctly - you just need to document it.

Requirements:
1. Add module-level docstring
2. Add class docstring with attributes
3. Add docstrings to all public methods
4. Include Args, Returns, Raises, and Example sections
5. Add type hints where missing

Target:
- Module documentation score: 80+
- All public functions documented
- At least one example per function
"""

# Original undocumented code
UNDOCUMENTED_CODE = '''
import json
from pathlib import Path
from typing import Any


class ConfigManager:
    def __init__(self, config_path: str, defaults: dict | None = None):
        self.config_path = Path(config_path)
        self.defaults = defaults or {}
        self._config = None

    @property
    def config(self) -> dict:
        if self._config is None:
            self._config = self._load_config()
        return self._config

    def _load_config(self) -> dict:
        if self.config_path.exists():
            with open(self.config_path) as f:
                loaded = json.load(f)
            return {**self.defaults, **loaded}
        return self.defaults.copy()

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def save(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def reload(self) -> None:
        self._config = None
        _ = self.config


def load_config(path: str, defaults: dict | None = None) -> ConfigManager:
    return ConfigManager(path, defaults)
'''


def exercise() -> str:
    """Add documentation to the undocumented code.

    Returns:
        The documented version of the code as a string.
    """
    # TODO: Rewrite the code above with proper documentation
    documented_code = '''"""TODO: Add module docstring."""

import json
from pathlib import Path
from typing import Any


class ConfigManager:
    """TODO: Add class docstring."""

    def __init__(self, config_path: str, defaults: dict | None = None):
        # TODO: Add docstring
        self.config_path = Path(config_path)
        self.defaults = defaults or {}
        self._config = None

    # ... add documentation to all methods ...
'''
    return documented_code


def validate_solution() -> None:
    """Validate your documented code."""
    from component_documentation.code_docs import check_module_documentation
    from rich.console import Console

    console = Console()
    documented = exercise()

    console.print("\n[bold]Exercise 3: Document the ConfigManager Module[/bold]\n")

    # Check the documented code
    score = check_module_documentation(documented)

    console.print(f"Score: [{('green' if score.is_passing else 'red')}]{score.score}/100[/]")

    # Check for specific documentation
    checks = [
        ("Module docstring", '"""' in documented.split("import")[0]),
        ("Class docstring", 'class ConfigManager:' in documented and '"""' in documented.split("class ConfigManager:")[1].split("def")[0]),
        ("get() documented", 'def get(' in documented and '"""' in documented.split("def get(")[1].split("def ")[0] if "def get(" in documented else False),
        ("set() documented", 'def set(' in documented and '"""' in documented.split("def set(")[1].split("def ")[0] if "def set(" in documented else False),
        ("save() documented", 'def save(' in documented and '"""' in documented.split("def save(")[1].split("def ")[0] if "def save(" in documented else False),
        ("Has Args section", "Args:" in documented),
        ("Has Returns section", "Returns:" in documented),
        ("Has Example section", "Example:" in documented or ">>>" in documented),
    ]

    console.print("\n[bold]Documentation Checklist:[/bold]")
    for name, passed in checks:
        status = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
        console.print(f"  {status} - {name}")

    if score.issues:
        console.print("\n[red]Issues:[/red]")
        for issue in score.issues[:5]:
            console.print(f"  - {issue}")

    if score.suggestions:
        console.print("\n[yellow]Suggestions:[/yellow]")
        for suggestion in score.suggestions[:3]:
            console.print(f"  - {suggestion}")

    passed_count = sum(1 for _, passed in checks if passed)
    if passed_count >= 6 and score.is_passing:
        console.print("\n[bold green]All requirements met![/bold green]")
    else:
        console.print(f"\n[yellow]Progress: {passed_count}/{len(checks)} checks passed[/yellow]")


if __name__ == "__main__":
    validate_solution()
