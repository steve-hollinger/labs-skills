"""Exercise 2: Migrate a pip requirements.txt Project to UV

Goal: Convert an existing pip-based project to use UV.

Instructions:
1. Start with the sample requirements below
2. Create a new project using `uv init`
3. Migrate all dependencies to pyproject.toml
4. Organize dev dependencies separately
5. Generate and commit uv.lock

Sample requirements.txt to migrate:
```
# Production dependencies
requests>=2.28.0
pydantic>=2.0
python-dotenv>=1.0.0
structlog>=23.0.0

# Development dependencies
pytest>=8.0.0
pytest-cov>=4.1.0
ruff>=0.3.0
mypy>=1.8.0
black>=24.0.0
```

Expected Output:
- pyproject.toml with proper dependency sections
- uv.lock with all resolved dependencies
- Project that works with `uv sync && uv run pytest`

Hints:
- Create separate [project.dependencies] and [project.optional-dependencies]
- You can add multiple packages at once with `uv add pkg1 pkg2 pkg3`
- Use `uv add --dev` for development dependencies
- Consider which packages are redundant (e.g., black vs ruff)
"""

# Sample project structure to create
EXPECTED_PYPROJECT = '''
[project]
name = "migrated-project"
version = "0.1.0"
description = "A project migrated from pip to UV"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.28.0",
    "pydantic>=2.0",
    "python-dotenv>=1.0.0",
    "structlog>=23.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.3.0",
    "mypy>=1.8.0",
    # Note: black is redundant - ruff format does the same thing
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B"]

[tool.mypy]
python_version = "3.11"
strict = true
'''

# Sample code to test the migration
SAMPLE_CODE = '''
"""Sample module to verify migration."""
import structlog
from pydantic import BaseModel


class Config(BaseModel):
    """Application configuration."""
    debug: bool = False
    api_key: str


def setup_logging() -> structlog.BoundLogger:
    """Set up structured logging."""
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
    )
    return structlog.get_logger()


def main() -> None:
    """Main entry point."""
    logger = setup_logging()
    logger.info("Application started")


if __name__ == "__main__":
    main()
'''

MIGRATION_STEPS = """
Step-by-step migration process:

1. Initialize UV project in existing directory:
   $ uv init --name migrated-project .

2. Add production dependencies:
   $ uv add requests pydantic python-dotenv structlog

3. Add development dependencies:
   $ uv add --dev pytest pytest-cov ruff mypy

4. Remove old files:
   $ rm requirements.txt requirements-dev.txt

5. Verify installation:
   $ uv sync --all-extras
   $ uv run python -c "import requests; print('OK')"

6. Update CI/CD:
   - Replace `pip install -r requirements.txt`
   - With `uv sync --all-extras`

7. Update documentation:
   - Update README with UV instructions
   - Remove pip references
"""


def verify_exercise() -> bool:
    """Verify the exercise was completed correctly."""
    from pathlib import Path

    project_dir = Path("migrated-project")

    if not project_dir.exists():
        project_dir = Path(".")  # Check current directory

    checks = []

    # Check pyproject.toml exists and has required content
    pyproject = project_dir / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()
        checks.append(("pyproject.toml exists", True))
        checks.append(("Has requests dependency", "requests" in content))
        checks.append(("Has pydantic dependency", "pydantic" in content))
        checks.append(("Has dev dependencies", "optional-dependencies" in content))
    else:
        checks.append(("pyproject.toml exists", False))

    # Check uv.lock exists
    uv_lock = project_dir / "uv.lock"
    checks.append(("uv.lock exists", uv_lock.exists()))

    # Check requirements.txt is removed
    req_txt = project_dir / "requirements.txt"
    checks.append(("requirements.txt removed", not req_txt.exists()))

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
        print("Exercise 2 completed successfully!")
    else:
        print("Exercise 2 not yet complete. See instructions above.")

    return all_passed


if __name__ == "__main__":
    print(__doc__)
    print(MIGRATION_STEPS)
    print("\nExpected pyproject.toml structure:")
    print(EXPECTED_PYPROJECT)
