# Common Patterns

## Overview

This document covers common patterns and best practices for using UV in Python projects.

## Pattern 1: Application Project Setup

### When to Use

When creating a new Python application (CLI tool, web service, script collection).

### Implementation

```bash
# Create the project
uv init my-app
cd my-app

# Add dependencies
uv add fastapi uvicorn
uv add --dev pytest ruff mypy

# Run the application
uv run uvicorn my_app.main:app
```

### Example

```toml
# pyproject.toml for an application
[project]
name = "my-app"
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
    "mypy>=1.8",
]

[project.scripts]
my-app = "my_app.cli:main"
```

### Pitfalls to Avoid

- Don't forget to commit uv.lock
- Don't mix pip install with uv add

## Pattern 2: Library Project Setup

### When to Use

When creating a reusable Python library to be published to PyPI.

### Implementation

```bash
# Create a library project (uses src layout)
uv init --lib my-library
cd my-library

# Add dependencies
uv add pydantic  # Runtime dependency
uv add --dev pytest pytest-cov

# Build the package
uv build
```

### Example

```toml
# pyproject.toml for a library
[project]
name = "my-library"
version = "0.1.0"
description = "A helpful Python library"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0",
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov>=4.1"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Pitfalls to Avoid

- Keep runtime dependencies minimal
- Use version ranges, not pins, for libraries

## Pattern 3: Dependency Groups for Different Environments

### When to Use

When you need different dependencies for development, testing, documentation, etc.

### Implementation

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.3",
    "mypy>=1.8",
]
test = [
    "pytest>=8.0",
    "pytest-cov>=4.1",
    "pytest-asyncio>=0.23",
]
docs = [
    "mkdocs>=1.5",
    "mkdocs-material>=9.0",
]
```

```bash
# Install specific groups
uv sync --extra dev
uv sync --extra test
uv sync --all-extras  # Everything
```

### Pitfalls to Avoid

- Don't duplicate common packages across groups
- Consider a "dev" group that includes all others

## Pattern 4: CI/CD Integration

### When to Use

For GitHub Actions, GitLab CI, or other CI systems.

### Implementation

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install UV
        uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Run tests
        run: uv run pytest

      - name: Run linting
        run: |
          uv run ruff check .
          uv run mypy src/
```

### Example

```yaml
# Matrix testing across Python versions
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv python install ${{ matrix.python-version }}
      - run: uv sync --all-extras --python ${{ matrix.python-version }}
      - run: uv run pytest
```

### Pitfalls to Avoid

- Don't forget to cache UV's global cache
- Don't skip uv.lock in CI

## Pattern 5: Migrating from pip/requirements.txt

### When to Use

When converting an existing project to UV.

### Implementation

```bash
# Initialize UV in existing project
uv init --name existing-project .

# Add packages from requirements.txt
uv add $(cat requirements.txt | grep -v "^#" | grep -v "^$" | tr '\n' ' ')

# Or do it more carefully, one by one
while read requirement; do
    [[ "$requirement" =~ ^# ]] && continue
    [[ -z "$requirement" ]] && continue
    uv add "$requirement"
done < requirements.txt
```

### Pitfalls to Avoid

- Review version constraints after migration
- Remove requirements.txt only after verifying uv.lock

## Pattern 6: Workspaces (Monorepo)

### When to Use

When managing multiple related packages in one repository.

### Implementation

```toml
# Root pyproject.toml
[tool.uv.workspace]
members = ["packages/*"]

# packages/core/pyproject.toml
[project]
name = "myproject-core"
version = "0.1.0"

# packages/api/pyproject.toml
[project]
name = "myproject-api"
dependencies = ["myproject-core"]
```

```bash
# Sync all workspace members
uv sync

# Run command in specific package
uv run --package myproject-api pytest
```

### Pitfalls to Avoid

- Keep shared dependencies at workspace root
- Version workspace members consistently

## Anti-Patterns

### Anti-Pattern 1: Using pip install in UV Projects

Why it's bad: Bypasses lock file, causes version drift.

```bash
# Bad
pip install requests
uv run python  # Now out of sync

# Good
uv add requests
uv run python
```

### Better Approach

Always use `uv add` for new dependencies and `uv sync` to install from lock.

### Anti-Pattern 2: Ignoring uv.lock in Git

Why it's bad: Loses reproducibility, defeats purpose of UV.

```gitignore
# Bad .gitignore
uv.lock

# Good .gitignore
.venv/
```

### Better Approach

Always commit uv.lock. It ensures everyone gets the same versions.

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| New web service | Application Project Setup |
| Reusable package | Library Project Setup |
| Team project | Dependency Groups + CI/CD |
| Legacy project | Migration Pattern |
| Multiple packages | Workspaces |
