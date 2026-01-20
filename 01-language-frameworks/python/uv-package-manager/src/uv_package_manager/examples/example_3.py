"""Example 3: Multi-Environment and Python Version Management

This example demonstrates advanced UV features for managing multiple
environments and Python versions in a single project.
"""


def demonstrate_optional_dependencies() -> None:
    """Show how to structure optional dependency groups."""
    print("\n" + "=" * 60)
    print("STEP 1: Optional Dependency Groups")
    print("=" * 60)

    pyproject_example = '''
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.100",
    "pydantic>=2.0",
]

[project.optional-dependencies]
# Development tools
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.1",
    "ruff>=0.3",
    "mypy>=1.8",
    "pre-commit>=3.6",
]

# Testing extras (subset of dev)
test = [
    "pytest>=8.0",
    "pytest-cov>=4.1",
    "pytest-asyncio>=0.23",
    "httpx>=0.26",  # For testing FastAPI
]

# Documentation
docs = [
    "mkdocs>=1.5",
    "mkdocs-material>=9.5",
    "mkdocstrings[python]>=0.24",
]

# All extras combined
all = [
    "my-project[dev]",
    "my-project[docs]",
]
'''

    print("""
Organize dependencies by purpose using optional dependency groups:
""")
    print(pyproject_example)

    print("""
Installing specific groups:
    uv sync                    # Only [project.dependencies]
    uv sync --extra dev        # + dev dependencies
    uv sync --extra test       # + test dependencies
    uv sync --all-extras       # All optional dependencies
""")


def demonstrate_python_version_management() -> None:
    """Show Python version management with UV."""
    print("\n" + "=" * 60)
    print("STEP 2: Python Version Management")
    print("=" * 60)

    print("""
UV can download and manage Python interpreters:

Installing Python versions:
    uv python install 3.11        # Install Python 3.11
    uv python install 3.12 3.13   # Install multiple versions
    uv python install pypy@3.10   # Install PyPy

Listing versions:
    uv python list                # Show installed versions
    uv python list --all-versions # Show all available

Pinning project version:
    uv python pin 3.11            # Creates .python-version file
    uv python pin 3.12            # Switch project to 3.12

Running with specific version:
    uv run --python 3.11 pytest   # Run with Python 3.11
    uv run --python 3.12 pytest   # Run with Python 3.12

The .python-version file:
    - Plain text file containing version (e.g., "3.11")
    - Respected by uv sync and uv run
    - Commit to git for team consistency
""")


def demonstrate_matrix_testing() -> None:
    """Show how to test across Python versions."""
    print("\n" + "=" * 60)
    print("STEP 3: Testing Across Python Versions")
    print("=" * 60)

    github_action = '''
# .github/workflows/test.yml
name: Test Matrix

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12", "3.13"]

    steps:
      - uses: actions/checkout@v4

      - name: Install UV
        uses: astral-sh/setup-uv@v4

      - name: Install Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --all-extras --python ${{ matrix.python-version }}

      - name: Run tests
        run: uv run --python ${{ matrix.python-version }} pytest

      - name: Type check
        run: uv run --python ${{ matrix.python-version }} mypy src/
'''

    print("GitHub Actions matrix for testing multiple Python versions:")
    print(github_action)


def demonstrate_environment_separation() -> None:
    """Show separation between dev, test, and prod environments."""
    print("\n" + "=" * 60)
    print("STEP 4: Environment Separation Strategy")
    print("=" * 60)

    print("""
Recommended environment separation:

Production (minimal):
    uv sync                    # Only core dependencies

    Includes: fastapi, pydantic, etc.
    Excludes: pytest, dev tools, docs

Development (full):
    uv sync --all-extras       # Everything

    Includes: all production + dev + test + docs

CI Testing:
    uv sync --extra test       # Production + test tools

    Includes: production + pytest, coverage tools

Documentation Build:
    uv sync --extra docs       # Production + docs tools

    Includes: production + mkdocs, etc.

Docker example (production):
    FROM python:3.11-slim

    # Install UV
    COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

    COPY pyproject.toml uv.lock ./

    # Install production deps only (no extras)
    RUN uv sync --frozen --no-dev

    COPY src/ src/

    CMD ["uv", "run", "uvicorn", "app.main:app"]
""")


def demonstrate_workspace_setup() -> None:
    """Show monorepo workspace configuration."""
    print("\n" + "=" * 60)
    print("STEP 5: Workspace (Monorepo) Setup")
    print("=" * 60)

    print("""
UV supports workspaces for managing multiple packages:

Project structure:
    my-monorepo/
    ├── pyproject.toml          # Workspace root
    ├── uv.lock                 # Single lock file for all packages
    └── packages/
        ├── core/
        │   ├── pyproject.toml
        │   └── src/core/
        ├── api/
        │   ├── pyproject.toml
        │   └── src/api/
        └── cli/
            ├── pyproject.toml
            └── src/cli/

Root pyproject.toml:
    [tool.uv.workspace]
    members = ["packages/*"]

Package pyproject.toml (packages/api/):
    [project]
    name = "myproject-api"
    version = "0.1.0"
    dependencies = [
        "myproject-core",  # Local workspace dependency
        "fastapi>=0.100",
    ]

Working with workspaces:
    uv sync                         # Install all workspace packages
    uv run --package api pytest     # Run tests for specific package
    uv add --package cli click      # Add dep to specific package
""")


def demonstrate_advanced_config() -> None:
    """Show advanced UV configuration options."""
    print("\n" + "=" * 60)
    print("STEP 6: Advanced Configuration")
    print("=" * 60)

    print("""
UV can be configured via pyproject.toml [tool.uv] section:

[tool.uv]
# Use a private package index
index-url = "https://pypi.company.com/simple"
extra-index-url = ["https://pypi.org/simple"]

# Pin specific packages (override resolver)
override-dependencies = [
    "requests==2.31.0",
]

# Exclude packages from resolution
constraint-dependencies = [
    "setuptools<70",
]

# Development dependencies (alternative to optional-dependencies)
dev-dependencies = [
    "pytest>=8.0",
    "ruff>=0.3",
]

Environment variables:
    UV_INDEX_URL          # Default package index
    UV_EXTRA_INDEX_URL    # Additional indexes
    UV_CACHE_DIR          # Cache location
    UV_PYTHON             # Default Python version
    UV_NO_CACHE           # Disable caching
""")


def main() -> None:
    """Run the multi-environment example."""
    print("Example 3: Multi-Environment and Python Version Management")
    print("=" * 60)

    print("""
This example covers advanced UV features for managing complex
Python projects with multiple environments and Python versions.

Topics covered:
- Optional dependency groups
- Python version management
- CI/CD matrix testing
- Environment separation (dev/test/prod)
- Workspace configuration for monorepos
- Advanced UV configuration
""")

    demonstrate_optional_dependencies()
    demonstrate_python_version_management()
    demonstrate_matrix_testing()
    demonstrate_environment_separation()
    demonstrate_workspace_setup()
    demonstrate_advanced_config()

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Try setting up a project with multiple dependency groups")
    print("  2. Experiment with different Python versions")
    print("  3. Complete the exercises to practice these concepts")


if __name__ == "__main__":
    main()
