"""Exercise 1: Initialize a FastAPI Project with UV

Goal: Create a new FastAPI project from scratch using UV.

Instructions:
1. Use UV to initialize a new project called "fastapi-demo"
2. Add FastAPI and uvicorn as dependencies
3. Add pytest and httpx as dev dependencies
4. Create a simple API endpoint
5. Run the application

Expected Output:
- A working FastAPI application at http://localhost:8000
- API docs at http://localhost:8000/docs
- Tests that verify the endpoint works

Hints:
- Use `uv init` to create the project
- Use `uv add` for production dependencies
- Use `uv add --dev` for development dependencies
- Use `uv run uvicorn` to start the server

Commands you'll need:
    uv init fastapi-demo
    cd fastapi-demo
    uv add fastapi uvicorn[standard]
    uv add --dev pytest httpx pytest-asyncio
"""

# This file serves as instructions for the exercise.
# The actual implementation should be done in a new directory.

# Here's a skeleton of what your main.py should look like:

MAIN_PY_SKELETON = '''
"""FastAPI Demo Application."""
from fastapi import FastAPI

app = FastAPI(title="FastAPI Demo")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Hello, World!"}


@app.get("/items/{item_id}")
async def get_item(item_id: int, q: str | None = None):
    """Get an item by ID."""
    return {"item_id": item_id, "query": q}
'''

TEST_SKELETON = '''
"""Tests for FastAPI Demo."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_root():
    """Test the root endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


@pytest.mark.asyncio
async def test_get_item():
    """Test the get_item endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/items/42?q=test")

    assert response.status_code == 200
    assert response.json() == {"item_id": 42, "query": "test"}
'''


def verify_exercise() -> bool:
    """Verify the exercise was completed correctly."""
    import subprocess
    from pathlib import Path

    project_dir = Path("fastapi-demo")

    checks = [
        ("Project directory exists", project_dir.exists()),
        ("pyproject.toml exists", (project_dir / "pyproject.toml").exists()),
        ("uv.lock exists", (project_dir / "uv.lock").exists()),
    ]

    print("\nExercise Verification:")
    print("-" * 40)

    all_passed = True
    for check_name, passed in checks:
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {check_name}")
        if not passed:
            all_passed = False

    if all_passed:
        # Additional check: verify dependencies
        try:
            result = subprocess.run(
                ["uv", "tree"],
                cwd=project_dir,
                capture_output=True,
                text=True,
            )
            if "fastapi" in result.stdout.lower():
                print("  PASS: FastAPI dependency found")
            else:
                print("  FAIL: FastAPI dependency not found")
                all_passed = False
        except Exception as e:
            print(f"  SKIP: Could not verify dependencies ({e})")

    print("-" * 40)
    if all_passed:
        print("Exercise 1 completed successfully!")
    else:
        print("Exercise 1 not yet complete. See instructions above.")

    return all_passed


if __name__ == "__main__":
    print(__doc__)
    print("\nSkeleton code for reference:")
    print("\n--- main.py ---")
    print(MAIN_PY_SKELETON)
    print("\n--- test_main.py ---")
    print(TEST_SKELETON)
