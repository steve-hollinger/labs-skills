"""Exercise 1: Configure Ruff for a New Project

Goal: Set up Ruff configuration for a new Python project from scratch.

Instructions:
1. Create a pyproject.toml with Ruff configuration
2. Configure appropriate rules for a web API project
3. Set up per-file ignores for tests
4. Create a Makefile with lint and format targets
5. Verify the configuration works

Requirements:
- Line length: 100
- Target Python version: 3.11
- Enable rules: E, W, F, I, N, UP, B, SIM
- Ignore E501 (let formatter handle line length)
- Allow assert (S101) in tests
- Allow unused imports (F401) in __init__.py

Expected Files:
    my-api-project/
    ├── pyproject.toml
    ├── Makefile
    ├── src/
    │   └── my_api/
    │       ├── __init__.py
    │       └── main.py
    └── tests/
        └── test_main.py

Hints:
- Use [tool.ruff] for general settings
- Use [tool.ruff.lint] for rule selection
- Use [tool.ruff.lint.per-file-ignores] for test exceptions
- Use [tool.ruff.format] for formatter options
"""

# Template pyproject.toml to complete
PYPROJECT_TEMPLATE = '''
[project]
name = "my-api"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.100",
    "uvicorn>=0.24",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.3",
]

# TODO: Add Ruff configuration below
# [tool.ruff]
# ...

'''

# Sample code to lint
SAMPLE_MAIN_PY = '''
"""Main API module."""
import json  # This should trigger F401 (unused import)
from typing import Optional

from fastapi import FastAPI

app = FastAPI()

def get_items():  # Missing return type annotation
    items = []
    for i in range(10):
        items.append(i)  # Could use list comprehension (SIM118)
    return items

@app.get("/")
async def root():
    return {"message": "Hello, World!"}
'''

SAMPLE_TEST_PY = '''
"""Tests for main module."""
import pytest
from my_api.main import app


def test_root():
    """Test root endpoint."""
    assert True  # S101 should be allowed in tests


def test_get_items():
    """Test get_items function."""
    from my_api.main import get_items
    result = get_items()
    assert len(result) == 10
'''


def verify_exercise() -> bool:
    """Verify the exercise was completed correctly."""
    import subprocess
    from pathlib import Path

    project = Path("my-api-project")

    checks = [
        ("Project directory exists", project.exists()),
        ("pyproject.toml exists", (project / "pyproject.toml").exists()),
        ("Makefile exists", (project / "Makefile").exists()),
    ]

    # Check pyproject.toml content
    if (project / "pyproject.toml").exists():
        content = (project / "pyproject.toml").read_text()
        checks.append(("[tool.ruff] section", "[tool.ruff]" in content))
        checks.append(("line-length = 100", "line-length = 100" in content))
        checks.append(("target-version", "target-version" in content))
        checks.append(("[tool.ruff.lint]", "[tool.ruff.lint]" in content))
        checks.append(("per-file-ignores", "per-file-ignores" in content))

    print("\nExercise Verification:")
    print("-" * 40)

    all_passed = True
    for name, passed in checks:
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False

    # Try running ruff
    if project.exists():
        result = subprocess.run(
            ["ruff", "check", "--select", "E,F", "."],
            cwd=project,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 or "F401" in result.stdout:
            print("  PASS: Ruff runs successfully")
        else:
            print("  WARN: Could not verify Ruff execution")

    print("-" * 40)
    if all_passed:
        print("Exercise 1 completed successfully!")
    else:
        print("Exercise 1 not yet complete. See instructions above.")

    return all_passed


if __name__ == "__main__":
    print(__doc__)
    print("\nTemplate pyproject.toml:")
    print(PYPROJECT_TEMPLATE)
    print("\nSample main.py to create:")
    print(SAMPLE_MAIN_PY)
