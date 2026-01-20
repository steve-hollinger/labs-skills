"""Solution for Exercise 1: Configure Ruff for a New Project

This solution creates a complete project with Ruff configuration.
"""

import subprocess
import tempfile
from pathlib import Path


def create_project(project_path: Path) -> None:
    """Create a complete project with Ruff configuration."""

    # Create directory structure
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / "src" / "my_api").mkdir(parents=True, exist_ok=True)
    (project_path / "tests").mkdir(parents=True, exist_ok=True)

    # Create pyproject.toml with Ruff configuration
    pyproject = project_path / "pyproject.toml"
    pyproject.write_text('''[project]
name = "my-api"
version = "0.1.0"
description = "A sample API project with Ruff"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.100",
    "uvicorn>=0.24",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "httpx>=0.26",
    "ruff>=0.3",
    "mypy>=1.8",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/my_api"]

# Ruff Configuration
[tool.ruff]
line-length = 100
target-version = "py311"
exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
]

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # Pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
]
ignore = [
    "E501",  # Line too long - handled by formatter
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101", "PLR2004"]
"__init__.py" = ["F401"]

[tool.ruff.lint.isort]
known-first-party = ["my_api"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
''')

    # Create Makefile
    makefile = project_path / "Makefile"
    makefile.write_text('''.PHONY: setup lint format test clean

setup:
\tuv sync --all-extras

lint:
\tuv run ruff check src/ tests/
\tuv run ruff format --check src/ tests/
\tuv run mypy src/

format:
\tuv run ruff format src/ tests/
\tuv run ruff check --fix src/ tests/

test:
\tuv run pytest -v

clean:
\trm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
''')

    # Create source files
    init_file = project_path / "src" / "my_api" / "__init__.py"
    init_file.write_text('"""My API package."""\n\nfrom my_api.main import app\n\n__all__ = ["app"]\n')

    main_file = project_path / "src" / "my_api" / "main.py"
    main_file.write_text('''"""Main API module."""
from fastapi import FastAPI

app = FastAPI(title="My API", version="0.1.0")


def get_items() -> list[int]:
    """Get a list of items."""
    return [i for i in range(10)]


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Hello, World!"}


@app.get("/items")
async def list_items() -> dict[str, list[int]]:
    """List all items."""
    return {"items": get_items()}
''')

    # Create test files
    test_init = project_path / "tests" / "__init__.py"
    test_init.write_text("")

    test_main = project_path / "tests" / "test_main.py"
    test_main.write_text('''"""Tests for main module."""
import pytest
from httpx import ASGITransport, AsyncClient

from my_api.main import app, get_items


def test_get_items() -> None:
    """Test get_items function."""
    result = get_items()
    assert len(result) == 10
    assert result[0] == 0
    assert result[-1] == 9


@pytest.mark.asyncio
async def test_root() -> None:
    """Test root endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


@pytest.mark.asyncio
async def test_list_items() -> None:
    """Test list items endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/items")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 10
''')

    # Create .gitignore
    gitignore = project_path / ".gitignore"
    gitignore.write_text("""__pycache__/
*.py[cod]
.venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/
dist/
build/
*.egg-info/
""")


def verify_project(project_path: Path) -> bool:
    """Verify the project is correctly configured."""
    print("\nVerifying project...")

    # Run Ruff check
    result = subprocess.run(
        ["ruff", "check", "src/", "tests/"],
        cwd=project_path,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("  PASS: Ruff check passes")
    else:
        print(f"  FAIL: Ruff check found issues:\n{result.stdout}")
        return False

    # Run Ruff format check
    result = subprocess.run(
        ["ruff", "format", "--check", "src/", "tests/"],
        cwd=project_path,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("  PASS: Ruff format check passes")
    else:
        print(f"  FAIL: Ruff format check found issues")
        return False

    return True


def main() -> None:
    """Run the solution."""
    print("Solution for Exercise 1: Configure Ruff for a New Project")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "my-api-project"

        print("\nCreating project...")
        create_project(project_path)

        print(f"\nProject created at: {project_path}")
        print("\nProject structure:")
        for item in sorted(project_path.rglob("*")):
            if item.is_file():
                rel = item.relative_to(project_path)
                print(f"  {rel}")

        if verify_project(project_path):
            print("\nProject created and verified successfully!")
        else:
            print("\nProject had issues - check output above.")


if __name__ == "__main__":
    main()
