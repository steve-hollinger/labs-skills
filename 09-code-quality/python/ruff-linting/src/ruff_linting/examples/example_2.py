"""Example 2: Rule Selection and Customization

This example demonstrates how to select, configure, and customize
Ruff rules for different project needs.
"""

import subprocess
import tempfile
from pathlib import Path


def demonstrate_rule_categories() -> None:
    """Show the different rule categories available in Ruff."""
    print("\n" + "=" * 60)
    print("STEP 1: Rule Categories")
    print("=" * 60)

    categories = """
Ruff implements 700+ rules from popular linters:

Core Rules (Essential):
    E    - pycodestyle errors (PEP 8 style)
    W    - pycodestyle warnings
    F    - Pyflakes (logic/syntax errors)
    I    - isort (import sorting)

Recommended Rules:
    N    - pep8-naming (naming conventions)
    UP   - pyupgrade (Python version upgrades)
    B    - flake8-bugbear (likely bugs)
    SIM  - flake8-simplify (simplifications)
    C4   - flake8-comprehensions (better comprehensions)

Advanced Rules:
    PL   - Pylint rules
    PTH  - flake8-use-pathlib
    PERF - Perflint (performance)
    RUF  - Ruff-specific rules
    S    - flake8-bandit (security)
    T    - flake8-debugger/print

Type Checking Related:
    ANN  - flake8-annotations
    TCH  - flake8-type-checking

Documentation:
    D    - pydocstyle (docstrings)
"""
    print(categories)


def demonstrate_rule_selection() -> None:
    """Show how to select and ignore rules."""
    print("\n" + "=" * 60)
    print("STEP 2: Rule Selection")
    print("=" * 60)

    print("""
Select rules using prefix codes in pyproject.toml:

# Select entire categories
[tool.ruff.lint]
select = ["E", "F", "I"]

# Select specific rules
select = ["E101", "E302", "F401"]

# Combine both
select = ["E", "F401", "I001"]

# Ignore specific rules
ignore = ["E501", "F841"]

# Command line override
ruff check --select E,F --ignore E501 .
""")


def demonstrate_per_file_ignores() -> None:
    """Show per-file ignore configuration."""
    print("\n" + "=" * 60)
    print("STEP 3: Per-File Ignores")
    print("=" * 60)

    config = '''
Different files often need different rules:

[tool.ruff.lint.per-file-ignores]
# Tests can use assert and magic values
"tests/*" = [
    "S101",     # Allow assert
    "PLR2004",  # Allow magic values
]

# __init__.py files often have unused imports (re-exports)
"__init__.py" = ["F401"]

# Migrations have their own style
"migrations/*" = [
    "E501",  # Long lines OK
    "N806",  # Non-lowercase variable
]

# Scripts can use print
"scripts/*" = ["T201"]

# Configuration files
"conftest.py" = ["F401", "E501"]
'''
    print(config)


def demonstrate_fixable_rules() -> None:
    """Show how to control which rules can be auto-fixed."""
    print("\n" + "=" * 60)
    print("STEP 4: Controlling Auto-Fix")
    print("=" * 60)

    print("""
Control which rules can be automatically fixed:

[tool.ruff.lint]
# Allow all rules to be fixed
fixable = ["ALL"]

# Or be specific
fixable = ["E", "F", "I", "UP"]

# Prevent auto-fix for certain rules
unfixable = [
    "F841",  # Don't auto-remove unused variables
    "B",     # Don't auto-fix bugbear rules
]

Command line:
    ruff check --fix .           # Safe fixes only
    ruff check --unsafe-fixes .  # Include unsafe fixes
""")


def demonstrate_isort_configuration() -> None:
    """Show isort-specific configuration."""
    print("\n" + "=" * 60)
    print("STEP 5: Import Sorting Configuration")
    print("=" * 60)

    config = '''
Configure import sorting (I rules):

[tool.ruff.lint.isort]
# First-party packages (your code)
known-first-party = ["mypackage", "mycompany"]

# Third-party packages (override detection)
known-third-party = ["google"]

# Force imports into sections
force-sort-within-sections = true

# Combine 'from X import a, b' vs separate lines
force-single-line = false
combine-as-imports = true

# Number of lines after imports
lines-after-imports = 2

# Import order: future, standard, third-party, first-party, local
section-order = [
    "future",
    "standard-library",
    "third-party",
    "first-party",
    "local-folder",
]
'''
    print(config)

    example = """
Example - Before sorting:
    from mypackage import helper
    import os
    from pathlib import Path
    import requests
    from . import local

After sorting:
    import os
    from pathlib import Path

    import requests

    from mypackage import helper

    from . import local
"""
    print(example)


def show_project_configurations() -> None:
    """Show configurations for different project types."""
    print("\n" + "=" * 60)
    print("STEP 6: Project-Specific Configurations")
    print("=" * 60)

    starter = '''
# Starter configuration (new projects)
[tool.ruff.lint]
select = ["E", "W", "F", "I", "UP", "B"]
ignore = ["E501"]
'''

    library = '''
# Library configuration (published packages)
[tool.ruff.lint]
select = [
    "E", "W", "F", "I", "N", "UP", "B",
    "SIM", "C4", "PTH",
    "D",    # Docstrings
    "ANN",  # Type annotations
]
ignore = ["E501", "ANN101", "D100"]

[tool.ruff.lint.pydocstyle]
convention = "google"
'''

    strict = '''
# Strict configuration (high-quality codebases)
[tool.ruff.lint]
select = [
    "E", "W", "F", "I", "N", "UP", "B",
    "SIM", "C4", "PTH", "RUF",
    "PL",    # Pylint
    "PERF",  # Performance
    "FURB",  # Refurbishing
]
ignore = ["E501", "PLR0913", "PLR2004"]
'''

    print("Starter configuration:")
    print(starter)
    print("\nLibrary configuration:")
    print(library)
    print("\nStrict configuration:")
    print(strict)


def run_rule_demo() -> None:
    """Run demonstrations with different rule selections."""
    print("\n" + "=" * 60)
    print("STEP 7: Live Rule Demo")
    print("=" * 60)

    sample_code = '''"""Sample module."""
import json
import os, sys
from pathlib import Path

def processData(input_list: list = []):
    """Process data."""
    unused_var = 1
    result = []
    for i in range(len(input_list)):
        result.append(input_list[i])
    return result

class myclass:
    X = 1
'''

    with tempfile.TemporaryDirectory() as tmpdir:
        sample_file = Path(tmpdir) / "sample.py"
        sample_file.write_text(sample_code)

        print("Sample code with multiple issue types:")
        print("-" * 40)
        print(sample_code)
        print("-" * 40)

        # Test with minimal rules
        print("\nWith minimal rules (F only):")
        result = subprocess.run(
            ["ruff", "check", str(sample_file), "--select", "F"],
            capture_output=True,
            text=True,
        )
        print(result.stdout or "(No issues)")

        # Test with naming rules
        print("\nWith naming rules (N):")
        result = subprocess.run(
            ["ruff", "check", str(sample_file), "--select", "N"],
            capture_output=True,
            text=True,
        )
        print(result.stdout or "(No issues)")

        # Test with bugbear rules
        print("\nWith bugbear rules (B):")
        result = subprocess.run(
            ["ruff", "check", str(sample_file), "--select", "B"],
            capture_output=True,
            text=True,
        )
        print(result.stdout or "(No issues)")

        # Test with simplify rules
        print("\nWith simplify rules (SIM):")
        result = subprocess.run(
            ["ruff", "check", str(sample_file), "--select", "SIM", "C4"],
            capture_output=True,
            text=True,
        )
        print(result.stdout or "(No issues)")


def main() -> None:
    """Run the rule selection and customization example."""
    print("Example 2: Rule Selection and Customization")
    print("=" * 60)

    print("""
This example covers how to select and customize Ruff rules
for different project needs.

Topics:
- Rule categories and what they check
- Selecting and ignoring rules
- Per-file rule overrides
- Auto-fix configuration
- Project-specific configurations
""")

    demonstrate_rule_categories()
    demonstrate_rule_selection()
    demonstrate_per_file_ignores()
    demonstrate_fixable_rules()
    demonstrate_isort_configuration()
    show_project_configurations()
    run_rule_demo()

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Try different rule selections on your own code")
    print("  2. Run 'make example-3' to learn about CI integration")
    print("  3. Complete Exercise 2 to migrate from flake8/black")


if __name__ == "__main__":
    main()
