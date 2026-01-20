"""Solution for Exercise 1: Initialize a FastAPI Project with UV

This solution demonstrates the complete setup of a FastAPI project using UV.
"""

import subprocess
import tempfile
from pathlib import Path


def create_fastapi_project(project_path: Path) -> None:
    """Create a complete FastAPI project with UV."""

    # Step 1: Initialize the project
    print("Step 1: Initializing project with UV...")
    subprocess.run(["uv", "init", str(project_path)], check=True)

    # Step 2: Add dependencies
    print("Step 2: Adding dependencies...")
    subprocess.run(
        ["uv", "add", "fastapi", "uvicorn[standard]"],
        cwd=project_path,
        check=True,
    )

    # Step 3: Add dev dependencies
    print("Step 3: Adding dev dependencies...")
    subprocess.run(
        ["uv", "add", "--dev", "pytest", "httpx", "pytest-asyncio"],
        cwd=project_path,
        check=True,
    )

    # Step 4: Create the application code
    print("Step 4: Creating application code...")
    src_dir = project_path / "src" / "fastapi_demo"
    src_dir.mkdir(parents=True, exist_ok=True)

    # Main application
    main_py = src_dir / "main.py"
    main_py.write_text('''"""FastAPI Demo Application."""
from fastapi import FastAPI

app = FastAPI(title="FastAPI Demo", version="0.1.0")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint returning a greeting."""
    return {"message": "Hello, World!"}


@app.get("/items/{item_id}")
async def get_item(item_id: int, q: str | None = None) -> dict[str, int | str | None]:
    """Get an item by ID with optional query parameter."""
    return {"item_id": item_id, "query": q}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
''')

    # Init file
    init_py = src_dir / "__init__.py"
    init_py.write_text('"""FastAPI Demo package."""\n')

    # Step 5: Create tests
    print("Step 5: Creating tests...")
    tests_dir = project_path / "tests"
    tests_dir.mkdir(exist_ok=True)

    test_main = tests_dir / "test_main.py"
    test_main.write_text('''"""Tests for FastAPI Demo Application."""
import pytest
from httpx import ASGITransport, AsyncClient

from fastapi_demo.main import app


@pytest.fixture
def anyio_backend() -> str:
    """Use asyncio for async tests."""
    return "asyncio"


@pytest.mark.asyncio
async def test_root() -> None:
    """Test the root endpoint returns hello world."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


@pytest.mark.asyncio
async def test_get_item() -> None:
    """Test the get_item endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/items/42?q=test")

    assert response.status_code == 200
    data = response.json()
    assert data["item_id"] == 42
    assert data["query"] == "test"


@pytest.mark.asyncio
async def test_get_item_no_query() -> None:
    """Test the get_item endpoint without query parameter."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/items/1")

    assert response.status_code == 200
    data = response.json()
    assert data["item_id"] == 1
    assert data["query"] is None


@pytest.mark.asyncio
async def test_health_check() -> None:
    """Test the health check endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
''')

    # Test init file
    (tests_dir / "__init__.py").write_text("")

    # Step 6: Update pyproject.toml with proper config
    print("Step 6: Updating pyproject.toml...")
    pyproject = project_path / "pyproject.toml"
    pyproject_content = pyproject.read_text()

    # Add pytest and tool configurations
    additional_config = '''

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B"]

[tool.mypy]
python_version = "3.11"
strict = true
'''
    pyproject.write_text(pyproject_content + additional_config)

    # Step 7: Create Makefile
    print("Step 7: Creating Makefile...")
    makefile = project_path / "Makefile"
    makefile.write_text('''.PHONY: setup run test lint format clean

setup:
\tuv sync --all-extras

run:
\tuv run uvicorn fastapi_demo.main:app --reload

test:
\tuv run pytest -v

lint:
\tuv run ruff check src/ tests/
\tuv run ruff format --check src/ tests/

format:
\tuv run ruff format src/ tests/
\tuv run ruff check --fix src/ tests/

clean:
\trm -rf __pycache__ .pytest_cache .ruff_cache
''')

    print("\nProject created successfully!")
    print(f"Location: {project_path}")
    print("\nTo run the project:")
    print(f"  cd {project_path}")
    print("  uv run uvicorn fastapi_demo.main:app --reload")
    print("\nTo run tests:")
    print("  uv run pytest -v")


def main() -> None:
    """Run the solution."""
    print("Solution for Exercise 1: FastAPI Project Setup")
    print("=" * 50)

    # Create in a temporary directory for demonstration
    # In practice, you'd run this in your working directory
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "fastapi-demo"
        create_fastapi_project(project_path)

        # Verify the setup
        print("\nVerifying setup...")
        result = subprocess.run(
            ["uv", "run", "pytest", "-v"],
            cwd=project_path,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("All tests passed!")
            print(result.stdout)
        else:
            print("Tests failed:")
            print(result.stderr)


if __name__ == "__main__":
    main()
