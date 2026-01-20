"""Exercise 2: Configure Bandit for a Web Application

Goal: Create a proper Bandit configuration for a FastAPI web application.

Instructions:
1. Create a pyproject.toml with Bandit configuration
2. Configure appropriate rules for a web API
3. Set up per-file ignores for tests
4. Create a .bandit_baseline.json for existing issues
5. Verify the configuration works

Requirements:
- Exclude tests/ and migrations/ directories
- Skip B101 (assert) only in test files
- Focus on web-critical vulnerabilities:
  - B301-B303 (deserialization)
  - B501-B509 (SSL/TLS)
  - B601-B608 (injection)
  - B105-B107 (hardcoded secrets)
- Generate JSON output for CI

Expected Files:
    my-api/
    ├── pyproject.toml (with [tool.bandit] section)
    ├── .bandit_baseline.json
    └── src/
        └── api/
            └── main.py

Hints:
- Use [tool.bandit] in pyproject.toml
- Use exclude_dirs for directories
- Use [tool.bandit.assert_used] for test exceptions
"""

# Template pyproject.toml
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
    "bandit>=1.7",
    "ruff>=0.3",
]

# TODO: Add Bandit configuration below
# [tool.bandit]
# exclude_dirs = [...]
# skips = [...]

# [tool.bandit.assert_used]
# skips = [...]
'''

# Sample code to scan
SAMPLE_MAIN_PY = '''
"""FastAPI application."""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# This should trigger B105 - needs to be fixed
API_KEY = "sk-1234567890abcdef"

class User(BaseModel):
    username: str
    email: str

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.post("/users")
async def create_user(user: User):
    # This is safe - using ORM-style, not raw SQL
    return {"username": user.username}
'''

SAMPLE_TEST_PY = '''
"""Tests for API."""
import pytest

def test_root():
    """Test root endpoint."""
    # B101 should be allowed in tests
    assert True

def test_user_creation():
    """Test user creation."""
    assert 1 + 1 == 2
'''

EXPECTED_CONFIG = '''
[tool.bandit]
# Directories to exclude
exclude_dirs = [
    "tests",
    "migrations",
    ".venv",
    "venv",
]

# Global skips (use sparingly)
# skips = []

# Target directories
targets = ["src"]

# Recursive scanning
recursive = true

[tool.bandit.assert_used]
# Allow assert in test files
skips = [
    "*_test.py",
    "test_*.py",
    "**/tests/**",
]
'''

BASELINE_WORKFLOW = """
Baseline Workflow:

1. Create initial baseline:
   bandit -r src/ -f json -o .bandit_baseline.json

2. Review the baseline and fix critical issues

3. Use baseline in CI:
   bandit -r src/ -b .bandit_baseline.json -ll

4. Update baseline after fixing issues:
   bandit -r src/ -f json -o .bandit_baseline.json
"""


def verify_exercise() -> bool:
    """Verify the exercise was completed correctly."""
    from pathlib import Path

    project = Path("my-api")

    checks = [
        ("Project directory exists", project.exists()),
        ("pyproject.toml exists", (project / "pyproject.toml").exists()),
        ("Baseline exists", (project / ".bandit_baseline.json").exists()),
    ]

    # Check pyproject.toml content
    if (project / "pyproject.toml").exists():
        content = (project / "pyproject.toml").read_text()
        checks.append(("[tool.bandit] section", "[tool.bandit]" in content))
        checks.append(("exclude_dirs configured", "exclude_dirs" in content))
        checks.append(("assert_used configured", "assert_used" in content))

    print("\nExercise Verification:")
    print("-" * 40)

    all_passed = True
    for name, passed in checks:
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False

    print("-" * 40)
    if all_passed:
        print("Exercise 2 completed successfully!")
    else:
        print("Exercise 2 not yet complete. See instructions above.")

    return all_passed


if __name__ == "__main__":
    print(__doc__)
    print("\nTemplate pyproject.toml:")
    print(PYPROJECT_TEMPLATE)
    print("\nExpected configuration:")
    print(EXPECTED_CONFIG)
    print(BASELINE_WORKFLOW)
