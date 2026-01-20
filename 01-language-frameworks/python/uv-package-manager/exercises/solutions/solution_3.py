"""Solution for Exercise 3: Set Up a Monorepo with Multiple Packages

This solution demonstrates creating a UV workspace with multiple packages.
"""

import subprocess
import tempfile
from pathlib import Path


def create_monorepo(root: Path) -> None:
    """Create a complete monorepo structure."""

    print("Creating directory structure...")
    root.mkdir(parents=True, exist_ok=True)

    # Create package directories
    packages = ["core", "api", "cli"]
    for pkg in packages:
        pkg_dir = root / "packages" / pkg
        (pkg_dir / "src" / pkg).mkdir(parents=True, exist_ok=True)
        (pkg_dir / "tests").mkdir(parents=True, exist_ok=True)

    # Create root pyproject.toml
    print("Creating root pyproject.toml...")
    root_pyproject = root / "pyproject.toml"
    root_pyproject.write_text('''[project]
name = "my-monorepo"
version = "0.1.0"
description = "A UV workspace monorepo example"
requires-python = ">=3.11"

[tool.uv.workspace]
members = ["packages/*"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
''')

    # Create core package
    print("Creating core package...")
    create_core_package(root / "packages" / "core")

    # Create api package
    print("Creating api package...")
    create_api_package(root / "packages" / "api")

    # Create cli package
    print("Creating cli package...")
    create_cli_package(root / "packages" / "cli")

    # Create root README
    readme = root / "README.md"
    readme.write_text('''# My Monorepo

A UV workspace with multiple packages.

## Packages

- **core**: Shared models and utilities
- **api**: FastAPI service
- **cli**: Command-line interface

## Setup

```bash
uv sync
```

## Running

```bash
# Run API
uv run --package monorepo-api uvicorn api.main:app --reload

# Run CLI
uv run --package monorepo-cli my-cli --help

# Run tests for specific package
uv run --package monorepo-core pytest
```
''')


def create_core_package(pkg_dir: Path) -> None:
    """Create the core package."""

    # pyproject.toml
    pyproject = pkg_dir / "pyproject.toml"
    pyproject.write_text('''[project]
name = "monorepo-core"
version = "0.1.0"
description = "Shared models and utilities"
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
''')

    # Source code
    src_dir = pkg_dir / "src" / "core"

    (src_dir / "__init__.py").write_text('''"""Core package - shared models and utilities."""
from core.models import Item, User

__all__ = ["User", "Item"]
''')

    (src_dir / "models.py").write_text('''"""Shared data models."""
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    """User model shared across packages."""
    id: int
    name: str
    email: str

    def greet(self) -> str:
        """Return a greeting for the user."""
        return f"Hello, {self.name}!"


class Item(BaseModel):
    """Item model shared across packages."""
    id: int
    name: str
    price: float
    in_stock: bool = True

    def display_price(self) -> str:
        """Return formatted price."""
        return f"${self.price:.2f}"
''')

    (src_dir / "utils.py").write_text('''"""Shared utility functions."""
from typing import TypeVar

T = TypeVar("T")


def ensure_list(value: T | list[T]) -> list[T]:
    """Ensure a value is a list."""
    if isinstance(value, list):
        return value
    return [value]


def truncate(text: str, max_length: int = 50) -> str:
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
''')

    # Tests
    tests_dir = pkg_dir / "tests"
    (tests_dir / "__init__.py").write_text("")

    (tests_dir / "test_models.py").write_text('''"""Tests for core models."""
from core.models import Item, User


def test_user_creation() -> None:
    """Test User model creation."""
    user = User(id=1, name="Alice", email="alice@example.com")
    assert user.id == 1
    assert user.name == "Alice"


def test_user_greet() -> None:
    """Test User greeting."""
    user = User(id=1, name="Bob", email="bob@example.com")
    assert user.greet() == "Hello, Bob!"


def test_item_creation() -> None:
    """Test Item model creation."""
    item = Item(id=1, name="Widget", price=9.99)
    assert item.id == 1
    assert item.in_stock is True


def test_item_display_price() -> None:
    """Test Item price formatting."""
    item = Item(id=1, name="Widget", price=9.99)
    assert item.display_price() == "$9.99"
''')


def create_api_package(pkg_dir: Path) -> None:
    """Create the API package."""

    pyproject = pkg_dir / "pyproject.toml"
    pyproject.write_text('''[project]
name = "monorepo-api"
version = "0.1.0"
description = "FastAPI service"
requires-python = ">=3.11"
dependencies = [
    "monorepo-core",
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
''')

    src_dir = pkg_dir / "src" / "api"

    (src_dir / "__init__.py").write_text('"""API package."""\n')

    (src_dir / "main.py").write_text('''"""FastAPI application."""
from fastapi import FastAPI, HTTPException

from core.models import Item, User

app = FastAPI(title="Monorepo API", version="0.1.0")

# In-memory storage for demo
USERS: dict[int, User] = {
    1: User(id=1, name="Alice", email="alice@example.com"),
    2: User(id=2, name="Bob", email="bob@example.com"),
}

ITEMS: dict[int, Item] = {
    1: Item(id=1, name="Widget", price=9.99),
    2: Item(id=2, name="Gadget", price=19.99),
}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Welcome to Monorepo API"}


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int) -> User:
    """Get a user by ID."""
    if user_id not in USERS:
        raise HTTPException(status_code=404, detail="User not found")
    return USERS[user_id]


@app.get("/users", response_model=list[User])
async def list_users() -> list[User]:
    """List all users."""
    return list(USERS.values())


@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int) -> Item:
    """Get an item by ID."""
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail="Item not found")
    return ITEMS[item_id]


@app.get("/items", response_model=list[Item])
async def list_items() -> list[Item]:
    """List all items."""
    return list(ITEMS.values())
''')

    # Tests
    tests_dir = pkg_dir / "tests"
    (tests_dir / "__init__.py").write_text("")

    (tests_dir / "test_api.py").write_text('''"""Tests for API."""
import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app


@pytest.fixture
def anyio_backend() -> str:
    """Use asyncio."""
    return "asyncio"


@pytest.mark.asyncio
async def test_root() -> None:
    """Test root endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_get_user() -> None:
    """Test get user endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/users/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Alice"


@pytest.mark.asyncio
async def test_get_user_not_found() -> None:
    """Test get user not found."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/users/999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_items() -> None:
    """Test list items endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/items")

    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 2
''')


def create_cli_package(pkg_dir: Path) -> None:
    """Create the CLI package."""

    pyproject = pkg_dir / "pyproject.toml"
    pyproject.write_text('''[project]
name = "monorepo-cli"
version = "0.1.0"
description = "Command-line interface"
requires-python = ">=3.11"
dependencies = [
    "monorepo-core",
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
''')

    src_dir = pkg_dir / "src" / "cli"

    (src_dir / "__init__.py").write_text('"""CLI package."""\n')

    (src_dir / "main.py").write_text('''"""Command-line interface."""
import click
from rich.console import Console
from rich.table import Table

from core.models import Item, User

console = Console()


@click.group()
def main() -> None:
    """My Monorepo CLI - manage users and items."""
    pass


@main.command()
@click.argument("name")
@click.option("--email", "-e", default=None, help="User email")
def greet(name: str, email: str | None) -> None:
    """Greet a user by name."""
    user_email = email or f"{name.lower()}@example.com"
    user = User(id=1, name=name, email=user_email)

    table = Table(title=f"[bold]Welcome, {name}![/bold]")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("ID", str(user.id))
    table.add_row("Name", user.name)
    table.add_row("Email", user.email)

    console.print(table)
    console.print(f"\\n{user.greet()}")


@main.command()
@click.argument("name")
@click.argument("price", type=float)
def create_item(name: str, price: float) -> None:
    """Create a new item."""
    item = Item(id=1, name=name, price=price)

    table = Table(title="[bold]Item Created[/bold]")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("ID", str(item.id))
    table.add_row("Name", item.name)
    table.add_row("Price", item.display_price())
    table.add_row("In Stock", "Yes" if item.in_stock else "No")

    console.print(table)


@main.command()
def version() -> None:
    """Show version information."""
    console.print("[bold]My Monorepo CLI[/bold] v0.1.0")
    console.print("Using monorepo-core for shared models")


if __name__ == "__main__":
    main()
''')

    # Tests
    tests_dir = pkg_dir / "tests"
    (tests_dir / "__init__.py").write_text("")

    (tests_dir / "test_cli.py").write_text('''"""Tests for CLI."""
from click.testing import CliRunner

from cli.main import main


def test_greet() -> None:
    """Test greet command."""
    runner = CliRunner()
    result = runner.invoke(main, ["greet", "Alice"])

    assert result.exit_code == 0
    assert "Alice" in result.output


def test_greet_with_email() -> None:
    """Test greet command with email."""
    runner = CliRunner()
    result = runner.invoke(main, ["greet", "Bob", "-e", "bob@test.com"])

    assert result.exit_code == 0
    assert "Bob" in result.output


def test_create_item() -> None:
    """Test create-item command."""
    runner = CliRunner()
    result = runner.invoke(main, ["create-item", "Widget", "9.99"])

    assert result.exit_code == 0
    assert "Widget" in result.output
    assert "$9.99" in result.output


def test_version() -> None:
    """Test version command."""
    runner = CliRunner()
    result = runner.invoke(main, ["version"])

    assert result.exit_code == 0
    assert "0.1.0" in result.output
''')


def verify_monorepo(root: Path) -> bool:
    """Verify the monorepo setup."""
    print("\nVerifying monorepo...")

    # Sync workspace
    print("Running uv sync...")
    result = subprocess.run(
        ["uv", "sync"],
        cwd=root,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"  FAIL: uv sync failed: {result.stderr}")
        return False
    print("  PASS: uv sync succeeded")

    # Check uv.lock was created
    if (root / "uv.lock").exists():
        print("  PASS: uv.lock created")
    else:
        print("  FAIL: uv.lock not created")
        return False

    # Run tests for each package
    for pkg in ["monorepo-core", "monorepo-api", "monorepo-cli"]:
        result = subprocess.run(
            ["uv", "run", "--package", pkg, "pytest", "-v"],
            cwd=root,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(f"  PASS: {pkg} tests pass")
        else:
            print(f"  FAIL: {pkg} tests failed")
            print(result.stderr)
            return False

    return True


def main() -> None:
    """Run the monorepo solution."""
    print("Solution for Exercise 3: UV Workspace Monorepo")
    print("=" * 50)

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir) / "my-monorepo"

        print("\nCreating monorepo structure...")
        create_monorepo(root)

        if verify_monorepo(root):
            print("\nMonorepo created and verified successfully!")
            print(f"\nLocation: {root}")
            print("\nTo explore:")
            print("  uv tree                                    # Show dependency tree")
            print("  uv run --package monorepo-cli my-cli --help  # Run CLI")
        else:
            print("\nMonorepo setup had issues - check output above.")


if __name__ == "__main__":
    main()
