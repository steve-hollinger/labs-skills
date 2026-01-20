"""Solution for Exercise 2: Migrate a pip requirements.txt Project to UV

This solution demonstrates migrating an existing pip-based project to UV.
"""

import subprocess
import tempfile
from pathlib import Path


def create_legacy_project(project_path: Path) -> None:
    """Create a legacy pip-based project structure."""
    project_path.mkdir(parents=True, exist_ok=True)

    # Create requirements.txt
    requirements = project_path / "requirements.txt"
    requirements.write_text("""# Production dependencies
requests>=2.28.0
pydantic>=2.0
python-dotenv>=1.0.0
structlog>=23.0.0
""")

    # Create requirements-dev.txt
    requirements_dev = project_path / "requirements-dev.txt"
    requirements_dev.write_text("""-r requirements.txt
# Development dependencies
pytest>=8.0.0
pytest-cov>=4.1.0
ruff>=0.3.0
mypy>=1.8.0
""")

    # Create source code
    src_dir = project_path / "src" / "myapp"
    src_dir.mkdir(parents=True, exist_ok=True)

    (src_dir / "__init__.py").write_text('"""My Application."""\n')

    main_py = src_dir / "main.py"
    main_py.write_text('''"""Main application module."""
import structlog
from pydantic import BaseModel


class Config(BaseModel):
    """Application configuration."""
    debug: bool = False
    api_url: str = "https://api.example.com"


def setup_logging() -> structlog.BoundLogger:
    """Configure structured logging."""
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
    )
    return structlog.get_logger()


def main() -> None:
    """Application entry point."""
    logger = setup_logging()
    config = Config()
    logger.info("Application started", debug=config.debug)


if __name__ == "__main__":
    main()
''')

    # Create tests
    tests_dir = project_path / "tests"
    tests_dir.mkdir(exist_ok=True)
    (tests_dir / "__init__.py").write_text("")

    test_main = tests_dir / "test_main.py"
    test_main.write_text('''"""Tests for main module."""
from myapp.main import Config, setup_logging


def test_config_defaults() -> None:
    """Test Config has sensible defaults."""
    config = Config()
    assert config.debug is False
    assert "api.example.com" in config.api_url


def test_config_override() -> None:
    """Test Config can be overridden."""
    config = Config(debug=True, api_url="http://localhost")
    assert config.debug is True
    assert config.api_url == "http://localhost"


def test_setup_logging() -> None:
    """Test logging setup returns a logger."""
    logger = setup_logging()
    assert logger is not None
''')


def migrate_to_uv(project_path: Path) -> None:
    """Migrate the project from pip to UV."""

    print("Step 1: Initialize UV project...")
    subprocess.run(
        ["uv", "init", "--name", "migrated-project", "."],
        cwd=project_path,
        check=True,
    )

    print("Step 2: Add production dependencies...")
    subprocess.run(
        ["uv", "add", "requests>=2.28.0", "pydantic>=2.0", "python-dotenv>=1.0.0", "structlog>=23.0.0"],
        cwd=project_path,
        check=True,
    )

    print("Step 3: Add development dependencies...")
    subprocess.run(
        ["uv", "add", "--dev", "pytest>=8.0.0", "pytest-cov>=4.1.0", "ruff>=0.3.0", "mypy>=1.8.0"],
        cwd=project_path,
        check=True,
    )

    print("Step 4: Remove old requirements files...")
    (project_path / "requirements.txt").unlink()
    (project_path / "requirements-dev.txt").unlink()

    print("Step 5: Update pyproject.toml with tool configurations...")
    pyproject = project_path / "pyproject.toml"
    content = pyproject.read_text()

    # Add tool configurations
    tool_config = '''

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
'''
    pyproject.write_text(content + tool_config)

    print("Step 6: Create Makefile...")
    makefile = project_path / "Makefile"
    makefile.write_text('''.PHONY: setup test lint format clean

setup:
\tuv sync --all-extras

test:
\tuv run pytest -v

coverage:
\tuv run pytest --cov=myapp --cov-report=term-missing

lint:
\tuv run ruff check src/ tests/
\tuv run ruff format --check src/ tests/
\tuv run mypy src/

format:
\tuv run ruff format src/ tests/
\tuv run ruff check --fix src/ tests/

clean:
\trm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache .coverage
\tfind . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
''')

    print("Step 7: Update .gitignore...")
    gitignore = project_path / ".gitignore"
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Virtual environments
.venv/
venv/
ENV/

# Testing
.pytest_cache/
.coverage
htmlcov/

# Mypy
.mypy_cache/

# Ruff
.ruff_cache/

# IDE
.idea/
.vscode/
*.swp

# Distribution
dist/
build/
*.egg-info/

# Environment
.env
.env.local
"""
    gitignore.write_text(gitignore_content)

    print("\nMigration complete!")


def verify_migration(project_path: Path) -> bool:
    """Verify the migration was successful."""
    print("\nVerifying migration...")

    checks = [
        ("pyproject.toml exists", (project_path / "pyproject.toml").exists()),
        ("uv.lock exists", (project_path / "uv.lock").exists()),
        ("requirements.txt removed", not (project_path / "requirements.txt").exists()),
        ("requirements-dev.txt removed", not (project_path / "requirements-dev.txt").exists()),
    ]

    # Verify dependencies in pyproject.toml
    if (project_path / "pyproject.toml").exists():
        content = (project_path / "pyproject.toml").read_text()
        checks.append(("Has requests", "requests" in content))
        checks.append(("Has pydantic", "pydantic" in content))
        checks.append(("Has pytest in dev", "pytest" in content))

    all_passed = True
    for name, passed in checks:
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False

    # Run tests
    print("\nRunning tests...")
    result = subprocess.run(
        ["uv", "run", "pytest", "-v"],
        cwd=project_path,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("  PASS: All tests pass")
    else:
        print("  FAIL: Tests failed")
        print(result.stderr)
        all_passed = False

    return all_passed


def main() -> None:
    """Run the migration solution."""
    print("Solution for Exercise 2: pip to UV Migration")
    print("=" * 50)

    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "legacy-project"

        print("\nCreating legacy pip-based project...")
        create_legacy_project(project_path)

        print("\nMigrating to UV...")
        migrate_to_uv(project_path)

        if verify_migration(project_path):
            print("\nMigration completed successfully!")
        else:
            print("\nMigration had issues - check output above.")


if __name__ == "__main__":
    main()
