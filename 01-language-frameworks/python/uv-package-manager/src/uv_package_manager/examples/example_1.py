"""Example 1: Basic Project Setup with UV

This example demonstrates how to set up a new Python project with UV,
including project initialization, adding dependencies, and running code.
"""

import subprocess
import sys
import tempfile
from pathlib import Path


def run_command(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def demonstrate_project_init() -> None:
    """Show how UV initializes a new project."""
    print("\n" + "=" * 60)
    print("STEP 1: Project Initialization")
    print("=" * 60)

    print("""
UV can initialize new Python projects with standardized structure.

Commands:
    uv init my-project          # Create application project
    uv init --lib my-library    # Create library project (src layout)
    uv init --python 3.12 proj  # Specify Python version

This creates:
    my-project/
    ├── pyproject.toml    # Project configuration (PEP 621)
    ├── README.md         # Documentation
    ├── .python-version   # Python version pin
    └── src/
        └── my_project/
            └── __init__.py
""")


def demonstrate_dependency_management() -> None:
    """Show how UV manages dependencies."""
    print("\n" + "=" * 60)
    print("STEP 2: Dependency Management")
    print("=" * 60)

    print("""
UV provides simple commands for managing dependencies:

Adding dependencies:
    uv add requests           # Add production dependency
    uv add --dev pytest       # Add development dependency
    uv add "fastapi>=0.100"   # Add with version constraint
    uv add requests httpx     # Add multiple at once

Removing dependencies:
    uv remove requests        # Remove a package

Viewing dependencies:
    uv tree                   # Show dependency tree
    uv pip list               # List installed packages

Each command updates both pyproject.toml and uv.lock automatically.
""")


def demonstrate_virtual_environments() -> None:
    """Show how UV handles virtual environments."""
    print("\n" + "=" * 60)
    print("STEP 3: Virtual Environment Management")
    print("=" * 60)

    print("""
UV manages virtual environments automatically:

Automatic creation:
    uv sync                   # Creates .venv and installs deps

Running in venv:
    uv run python script.py   # Runs in .venv without activation
    uv run pytest             # Run pytest in venv
    uv run python -m module   # Run a module

Manual activation (optional):
    source .venv/bin/activate # Activate on macOS/Linux
    .venv\\Scripts\\activate    # Activate on Windows

The .venv directory should be in .gitignore.
""")


def demonstrate_practical_workflow() -> None:
    """Show a practical UV workflow."""
    print("\n" + "=" * 60)
    print("STEP 4: Practical Workflow Example")
    print("=" * 60)

    print("""
Typical development workflow with UV:

1. Clone a project:
    git clone https://github.com/example/project
    cd project

2. Install dependencies:
    uv sync                   # Install from uv.lock

3. Add a new dependency:
    uv add httpx              # Add and update lock file

4. Run tests:
    uv run pytest             # Run in isolated venv

5. Update dependencies:
    uv lock --upgrade         # Update all to latest compatible

6. Commit changes:
    git add pyproject.toml uv.lock
    git commit -m "Update dependencies"
""")


def show_pyproject_example() -> None:
    """Display an example pyproject.toml."""
    print("\n" + "=" * 60)
    print("EXAMPLE: pyproject.toml Structure")
    print("=" * 60)

    example_pyproject = '''
[project]
name = "my-project"
version = "0.1.0"
description = "A modern Python project"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.100",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.3",
    "mypy>=1.8",
]

[project.scripts]
my-cli = "my_project.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
strict = true
'''
    print(example_pyproject)


def main() -> None:
    """Run the basic project setup example."""
    print("Example 1: Basic Project Setup with UV")
    print("=" * 60)

    print("""
This example covers the fundamentals of using UV for Python projects.
UV is a fast Python package manager written in Rust by Astral.

Key benefits:
- 10-100x faster than pip
- Built-in virtual environment management
- Lock files for reproducible builds
- Python version management
""")

    demonstrate_project_init()
    demonstrate_dependency_management()
    demonstrate_virtual_environments()
    demonstrate_practical_workflow()
    show_pyproject_example()

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Try 'uv init test-project' in a temporary directory")
    print("  2. Run 'make example-2' to learn about lock files")
    print("  3. Complete Exercise 1 in the exercises/ directory")


if __name__ == "__main__":
    main()
