# Common Patterns

## Overview

This document covers common patterns and best practices for using Ruff effectively.

## Pattern 1: Starter Configuration

### When to Use

For new projects that need a sensible default configuration.

### Implementation

```toml
[tool.ruff]
line-length = 100
target-version = "py311"
exclude = [".venv", "migrations", "build"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # Pyflakes
    "I",   # isort
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
]
ignore = ["E501"]  # Let formatter handle line length

[tool.ruff.format]
quote-style = "double"
```

### Pitfalls to Avoid

- Don't enable too many rules initially
- Don't forget to ignore E501 when using formatter

## Pattern 2: Strict Configuration

### When to Use

For projects requiring high code quality standards.

### Implementation

```toml
[tool.ruff.lint]
select = [
    "E", "W",     # Style
    "F",          # Errors
    "I",          # Imports
    "N",          # Naming
    "UP",         # Upgrades
    "B",          # Bugs
    "SIM",        # Simplify
    "C4",         # Comprehensions
    "PTH",        # Pathlib
    "RUF",        # Ruff-specific
    "PL",         # Pylint
    "PERF",       # Performance
    "FURB",       # Refurbishing
]

ignore = [
    "E501",       # Line length (formatter)
    "PLR0913",    # Too many arguments
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101", "PLR2004"]
```

### Pitfalls to Avoid

- May require significant code changes
- Can slow down development if too strict

## Pattern 3: Migration from Flake8/Black

### When to Use

When moving existing projects to Ruff.

### Implementation

```toml
# Old flake8 config (setup.cfg or .flake8):
# [flake8]
# max-line-length = 100
# ignore = E501,W503
# per-file-ignores = tests/*:S101

# Equivalent Ruff config:
[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "W", "F"]
ignore = ["E501", "W503"]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]

# Old black config:
# [tool.black]
# line-length = 100

# Already covered by [tool.ruff] line-length

# Old isort config:
# [tool.isort]
# profile = "black"
# known_first_party = ["mypackage"]

# Equivalent Ruff config:
[tool.ruff.lint.isort]
known-first-party = ["mypackage"]
```

### Pitfalls to Avoid

- Remove old tool configurations after migration
- Test thoroughly after migration

## Pattern 4: CI/CD Integration

### When to Use

For automated code quality checks in pipelines.

### Implementation

```yaml
# .github/workflows/lint.yml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install UV
        uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Run Ruff check
        run: uv run ruff check --output-format=github .

      - name: Run Ruff format check
        run: uv run ruff format --check .
```

Key CI flags:
- `--output-format=github`: GitHub annotations
- `--output-format=json`: Machine-readable
- `--exit-zero`: Don't fail on errors (warnings only)

### Pitfalls to Avoid

- Don't use `--fix` in CI (should be done locally)
- Match local and CI Ruff versions

## Pattern 5: Pre-commit Hook

### When to Use

To enforce standards before commits.

### Implementation

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

Or with UV:
```yaml
repos:
  - repo: local
    hooks:
      - id: ruff-check
        name: ruff check
        entry: uv run ruff check --fix
        language: system
        types: [python]

      - id: ruff-format
        name: ruff format
        entry: uv run ruff format
        language: system
        types: [python]
```

### Pitfalls to Avoid

- Keep pre-commit version in sync with pyproject.toml
- Don't make hooks too slow

## Pattern 6: Monorepo Configuration

### When to Use

For repositories with multiple Python packages.

### Implementation

```toml
# Root pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py311"

# Package-specific config can extend
extend-exclude = [
    "packages/legacy/*",  # Legacy code
]

[tool.ruff.lint.per-file-ignores]
"packages/api/*" = ["B008"]  # FastAPI Depends
"packages/cli/*" = ["T201"]  # Allow print in CLI
```

Or use separate pyproject.toml per package.

### Pitfalls to Avoid

- Avoid conflicting configurations
- Document any package-specific rules

## Anti-Patterns

### Anti-Pattern 1: Ignoring Everything

```toml
# Bad - defeats the purpose
[tool.ruff.lint]
select = ["E", "F"]
ignore = ["E", "F"]  # Why even enable?
```

### Better Approach

Be selective about what to ignore:
```toml
[tool.ruff.lint]
select = ["E", "F"]
ignore = ["E501"]  # Only specific rules
```

### Anti-Pattern 2: Global noqa Comments

```python
# Bad - hides all issues
# noqa: F401, F841, E501, B006...

import unused_module
```

### Better Approach

Use specific ignores:
```python
from module import used_function
from module import reexported_function  # noqa: F401 - re-export
```

## Choosing the Right Configuration

| Project Type | Recommended Rules |
|--------------|-------------------|
| New project | E, W, F, I, UP, B |
| Library | Add N, SIM, C4, PTH |
| Strict | Add PL, PERF, RUF |
| Legacy migration | Start with F only |
