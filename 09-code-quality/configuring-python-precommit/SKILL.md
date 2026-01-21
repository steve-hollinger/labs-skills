---
name: configuring-python-precommit
description: Configure pre-commit hooks for Python code quality with Ruff, mypy, and type checking. Use when enforcing code standards in CI/CD pipelines.
tags: ['python', 'pre-commit', 'ruff', 'mypy', 'code-quality']
---

# Pre-commit Hook Configuration

## Quick Start
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.7.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, pydantic]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
```

## Key Points
- Run Ruff for linting and formatting (replaces Black + flake8 + isort)
- Use mypy in strict mode for type checking
- Keep hooks fast (<5 seconds) to avoid developer friction
- Run hooks locally before CI to catch issues early
- Install with `pre-commit install` to enable git hooks

## Common Mistakes
1. **Not installing hooks** - Run `pre-commit install` after cloning repo
2. **Too many slow hooks** - Keep total hook runtime under 10 seconds
3. **Skipping hooks** - Don't use `git commit --no-verify` except for emergencies
4. **Not updating hooks** - Run `pre-commit autoupdate` monthly
5. **Wrong Ruff line length** - Use 120 characters to match Fetch standards

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
