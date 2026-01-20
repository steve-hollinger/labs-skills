"""Example 1: Basic Linting and Formatting with Ruff

This example demonstrates fundamental Ruff commands for linting
and formatting Python code.
"""

import subprocess
import tempfile
from pathlib import Path


def demonstrate_ruff_check() -> None:
    """Show how Ruff check analyzes code for issues."""
    print("\n" + "=" * 60)
    print("STEP 1: Ruff Check (Linting)")
    print("=" * 60)

    print("""
Ruff check analyzes Python code for errors, bugs, and style issues.

Basic commands:
    ruff check .                 # Check all Python files
    ruff check src/ tests/       # Check specific directories
    ruff check --fix .           # Auto-fix issues
    ruff check --diff .          # Show what would change

Key flags:
    --select E,F,I               # Check only specific rules
    --ignore E501                # Skip specific rules
    --output-format=json         # Machine-readable output
    --statistics                 # Show rule violation counts
""")


def demonstrate_ruff_format() -> None:
    """Show how Ruff format reformats code."""
    print("\n" + "=" * 60)
    print("STEP 2: Ruff Format (Formatting)")
    print("=" * 60)

    print("""
Ruff format is a Black-compatible formatter for consistent code style.

Basic commands:
    ruff format .                # Format all Python files
    ruff format --check .        # Check formatting without changes
    ruff format --diff .         # Show what would change

Options in pyproject.toml:
    [tool.ruff.format]
    quote-style = "double"       # Use double quotes
    indent-style = "space"       # Use spaces (not tabs)
    line-ending = "auto"         # Detect line endings
""")


def demonstrate_common_rules() -> None:
    """Show common Ruff rules and what they catch."""
    print("\n" + "=" * 60)
    print("STEP 3: Common Rules")
    print("=" * 60)

    rules = """
Rule Categories and Examples:

E - pycodestyle errors (style violations)
    E101: Indentation contains mixed spaces and tabs
    E302: Expected 2 blank lines, found 1
    E501: Line too long (usually ignore with formatter)

F - Pyflakes (logic errors)
    F401: Module imported but unused
    F841: Local variable assigned but never used
    F821: Undefined name

I - isort (import sorting)
    I001: Import block is un-sorted or un-formatted

N - pep8-naming (naming conventions)
    N801: Class name should use CapWords
    N802: Function name should be lowercase
    N803: Argument name should be lowercase

UP - pyupgrade (Python version upgrades)
    UP006: Use `list` instead of `List` for type annotations
    UP035: Deprecated import (use `from typing import X`)

B - flake8-bugbear (bug detection)
    B006: Do not use mutable default arguments
    B007: Loop control variable not used
    B008: Do not perform function call in argument defaults
"""
    print(rules)


def show_example_code_issues() -> None:
    """Display code with various issues and their fixes."""
    print("\n" + "=" * 60)
    print("STEP 4: Example Code Issues")
    print("=" * 60)

    bad_code = '''
# Code with issues (for demonstration)

import os, sys  # I001: Multiple imports on one line
import json     # F401: Unused import

def badFunction():  # N802: Should be snake_case
    x = 1  # F841: Unused variable
    return None

class myClass:  # N801: Should be CapWords
    def method(self, data=[]):  # B006: Mutable default
        pass
'''

    good_code = '''
# Fixed code

import os
import sys

def bad_function() -> None:
    return None

class MyClass:
    def method(self, data: list | None = None) -> None:
        if data is None:
            data = []
'''

    print("Code with issues:")
    print(bad_code)
    print("\nFixed code:")
    print(good_code)


def run_ruff_demo() -> None:
    """Run actual Ruff commands on sample code."""
    print("\n" + "=" * 60)
    print("STEP 5: Live Demo")
    print("=" * 60)

    # Create sample code with issues
    sample_code = '''import json
import os, sys

def badFunction():
    unused = 1
    return None

class myclass:
    def method(self, items=[]):
        pass
'''

    with tempfile.TemporaryDirectory() as tmpdir:
        sample_file = Path(tmpdir) / "sample.py"
        sample_file.write_text(sample_code)

        print(f"Sample code written to temporary file")
        print("\nRunning: ruff check sample.py")
        print("-" * 40)

        result = subprocess.run(
            ["ruff", "check", str(sample_file), "--output-format=text"],
            capture_output=True,
            text=True,
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        print("-" * 40)
        print("\nRunning: ruff check --fix --diff sample.py")
        print("-" * 40)

        result = subprocess.run(
            ["ruff", "check", str(sample_file), "--fix", "--diff"],
            capture_output=True,
            text=True,
        )

        if result.stdout:
            print(result.stdout)
        else:
            print("(No auto-fixable issues or all fixed)")


def show_configuration_example() -> None:
    """Display a recommended Ruff configuration."""
    print("\n" + "=" * 60)
    print("STEP 6: Configuration Example")
    print("=" * 60)

    config = '''
# pyproject.toml configuration

[tool.ruff]
line-length = 100
target-version = "py311"
exclude = [".venv", "migrations"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # Pyflakes
    "I",   # isort
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
]
ignore = ["E501"]  # Line length handled by formatter

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]     # Allow assert
"__init__.py" = ["F401"] # Allow unused imports

[tool.ruff.format]
quote-style = "double"
'''
    print(config)


def main() -> None:
    """Run the basic linting and formatting example."""
    print("Example 1: Basic Linting and Formatting with Ruff")
    print("=" * 60)

    print("""
Ruff is an extremely fast Python linter and formatter written in Rust.
It can replace flake8, isort, black, pyupgrade, and many other tools.

Key benefits:
- 10-100x faster than traditional tools
- Single tool for linting AND formatting
- 700+ rules from popular linters
- Easy configuration in pyproject.toml
""")

    demonstrate_ruff_check()
    demonstrate_ruff_format()
    demonstrate_common_rules()
    show_example_code_issues()
    run_ruff_demo()
    show_configuration_example()

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run 'uv run ruff check src/' to check this project")
    print("  2. Run 'make example-2' to learn about rule customization")
    print("  3. Complete Exercise 1 in the exercises/ directory")


if __name__ == "__main__":
    main()
