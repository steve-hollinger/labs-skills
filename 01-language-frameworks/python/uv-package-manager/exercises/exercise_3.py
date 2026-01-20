"""Exercise 3: Set Up a Monorepo with Multiple Packages

Goal: Create a UV workspace with multiple related packages.

Instructions:
1. Create a monorepo structure with three packages:
   - core: Shared utilities and models
   - api: FastAPI service using core
   - cli: Command-line tool using core
2. Configure UV workspace at the root
3. Set up local dependencies between packages
4. Verify you can run tests for each package

Expected Project Structure:
```
my-monorepo/
├── pyproject.toml          # Workspace configuration
├── uv.lock                 # Single lock file
├── README.md
└── packages/
    ├── core/
    │   ├── pyproject.toml
    │   ├── src/core/
    │   │   ├── __init__.py
    │   │   └── models.py
    │   └── tests/
    ├── api/
    │   ├── pyproject.toml
    │   ├── src/api/
    │   │   ├── __init__.py
    │   │   └── main.py
    │   └── tests/
    └── cli/
        ├── pyproject.toml
        ├── src/cli/
        │   ├── __init__.py
        │   └── main.py
        └── tests/
```

Hints:
- Root pyproject.toml uses [tool.uv.workspace]
- Package dependencies reference other workspace packages by name
- Use `uv run --package <name>` to run commands in specific packages
"""

# Root pyproject.toml template
ROOT_PYPROJECT = '''
[project]
name = "my-monorepo"
version = "0.1.0"
description = "A UV workspace monorepo"
requires-python = ">=3.11"

[tool.uv.workspace]
members = ["packages/*"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B"]

[tool.mypy]
python_version = "3.11"
strict = true
'''

# Core package pyproject.toml
CORE_PYPROJECT = '''
[project]
name = "monorepo-core"
version = "0.1.0"
description = "Core utilities and models"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/core"]
'''

# API package pyproject.toml
API_PYPROJECT = '''
[project]
name = "monorepo-api"
version = "0.1.0"
description = "FastAPI service"
requires-python = ">=3.11"
dependencies = [
    "monorepo-core",  # Local workspace dependency
    "fastapi>=0.100",
    "uvicorn>=0.24",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "httpx>=0.26",
    "pytest-asyncio>=0.23",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/api"]
'''

# CLI package pyproject.toml
CLI_PYPROJECT = '''
[project]
name = "monorepo-cli"
version = "0.1.0"
description = "Command-line interface"
requires-python = ">=3.11"
dependencies = [
    "monorepo-core",  # Local workspace dependency
    "click>=8.0",
    "rich>=13.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
]

[project.scripts]
my-cli = "cli.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/cli"]
'''

# Core package code
CORE_MODELS_PY = '''
"""Shared models for the monorepo."""
from pydantic import BaseModel


class User(BaseModel):
    """User model shared across packages."""
    id: int
    name: str
    email: str


class Item(BaseModel):
    """Item model shared across packages."""
    id: int
    name: str
    price: float
'''

# API package code
API_MAIN_PY = '''
"""FastAPI application."""
from fastapi import FastAPI
from core.models import User, Item

app = FastAPI(title="Monorepo API")


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int) -> User:
    """Get a user by ID."""
    return User(id=user_id, name="Test User", email="test@example.com")


@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int) -> Item:
    """Get an item by ID."""
    return Item(id=item_id, name="Test Item", price=9.99)
'''

# CLI package code
CLI_MAIN_PY = '''
"""Command-line interface."""
import click
from rich.console import Console
from rich.table import Table
from core.models import User

console = Console()


@click.group()
def main() -> None:
    """My Monorepo CLI."""
    pass


@main.command()
@click.argument("name")
def greet(name: str) -> None:
    """Greet a user."""
    user = User(id=1, name=name, email=f"{name.lower()}@example.com")
    table = Table(title="User Info")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("ID", str(user.id))
    table.add_row("Name", user.name)
    table.add_row("Email", user.email)
    console.print(table)


if __name__ == "__main__":
    main()
'''

SETUP_COMMANDS = """
Commands to set up the monorepo:

1. Create directory structure:
   $ mkdir -p my-monorepo/packages/{core,api,cli}/{src,tests}
   $ mkdir -p my-monorepo/packages/core/src/core
   $ mkdir -p my-monorepo/packages/api/src/api
   $ mkdir -p my-monorepo/packages/cli/src/cli

2. Create root pyproject.toml (see template above)

3. Create each package's pyproject.toml

4. Create source files and __init__.py files

5. Sync the workspace:
   $ cd my-monorepo
   $ uv sync

6. Verify workspace:
   $ uv tree                           # Show all packages
   $ uv run --package monorepo-api pytest
   $ uv run --package monorepo-cli my-cli greet World
"""


def verify_exercise() -> bool:
    """Verify the exercise was completed correctly."""
    from pathlib import Path

    root = Path("my-monorepo")

    checks = [
        ("Root directory exists", root.exists()),
        ("Root pyproject.toml exists", (root / "pyproject.toml").exists()),
        ("uv.lock exists", (root / "uv.lock").exists()),
        ("Core package exists", (root / "packages/core/pyproject.toml").exists()),
        ("API package exists", (root / "packages/api/pyproject.toml").exists()),
        ("CLI package exists", (root / "packages/cli/pyproject.toml").exists()),
    ]

    # Check workspace configuration
    if (root / "pyproject.toml").exists():
        content = (root / "pyproject.toml").read_text()
        checks.append(("Workspace configured", "[tool.uv.workspace]" in content))

    print("\nExercise Verification:")
    print("-" * 40)

    all_passed = True
    for check_name, passed in checks:
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {check_name}")
        if not passed:
            all_passed = False

    print("-" * 40)
    if all_passed:
        print("Exercise 3 completed successfully!")
    else:
        print("Exercise 3 not yet complete. See instructions above.")

    return all_passed


if __name__ == "__main__":
    print(__doc__)
    print(SETUP_COMMANDS)
    print("\n" + "=" * 60)
    print("Template files:")
    print("=" * 60)
    print("\n--- Root pyproject.toml ---")
    print(ROOT_PYPROJECT)
    print("\n--- packages/core/pyproject.toml ---")
    print(CORE_PYPROJECT)
    print("\n--- packages/api/pyproject.toml ---")
    print(API_PYPROJECT)
    print("\n--- packages/cli/pyproject.toml ---")
    print(CLI_PYPROJECT)
