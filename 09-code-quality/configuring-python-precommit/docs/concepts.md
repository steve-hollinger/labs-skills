# Core Concepts: Configuring Python Pre-commit Hooks

## What

Pre-commit hooks are automated checks that run before git commits to enforce code quality standards. For Python at Fetch:
- **Ruff** - Fast linter and formatter (replaces Black + flake8 + isort)
- **mypy** - Static type checking
- **pre-commit-hooks** - Basic file hygiene (trailing whitespace, EOF fixers)

Hooks run locally before commit and in CI to catch issues early.

## Why

**Problem**: Code quality issues slip into main branch:
- Inconsistent formatting (tabs vs spaces, line length)
- Missing type hints
- Linting errors not caught until CI
- Slow feedback loop (commit → CI failure → fix → recommit)

**Solution**: Pre-commit hooks provide:
- **Instant feedback** - Catches issues in <5 seconds locally
- **Consistency** - Enforces Fetch standards (120 char lines, type hints)
- **Fast CI** - Pre-commit catches 80% of issues before CI runs
- **Auto-fixing** - Ruff auto-fixes most issues (no manual work)

**Context at Fetch**:
- All Python repos use pre-commit with Ruff + mypy
- Standard line length: 120 characters (not 88)
- CI fails if pre-commit would fail
- Hooks installed automatically in dev setup scripts

## How

Pre-commit workflow:
1. Developer runs `git commit`
2. Pre-commit intercepts and runs configured hooks
3. Hooks check/fix files in staging area
4. If all pass → commit succeeds
5. If any fail → commit blocked, developer fixes issues

Ruff runs in two modes:
- `ruff check --fix` - Linting with auto-fixes
- `ruff format` - Code formatting (like Black)

mypy checks type annotations:
- Validates function signatures match type hints
- Catches None errors, type mismatches
- Requires `additional_dependencies` for third-party stubs

## When to Use

**Use pre-commit for:**
- All Python repositories with multiple contributors
- Projects that enforce code standards
- Repos with CI pipelines (pre-commit = first CI stage)

**Skip if:**
- Single developer, personal projects
- Prototype/exploratory code
- Non-Python projects (use language-specific tools)

## Key Terminology

- **Pre-commit hook** - Script that runs before git commit
- **Ruff** - Fast Rust-based linter/formatter for Python
- **mypy** - Static type checker for Python
- **Hook** - Individual check (e.g., ruff, mypy, trailing-whitespace)
- **Repo** - Collection of hooks from one source (e.g., ruff-pre-commit)
- **Stage** - Git staging area where hooks run

## Related Skills

- [building-fastapi-services](../../01-language-frameworks/python/building-fastapi-services/) - Code that follows these standards
