# Code Patterns: Configuring Python Pre-commit Hooks

## Pattern 1: Complete Pre-commit Configuration for Fetch

**When to Use:** Standard configuration for all Python projects at Fetch.

```yaml
# .pre-commit-config.yaml
repos:
  # Ruff for linting and formatting (replaces Black + flake8 + isort)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.7.0
    hooks:
      - id: ruff
        args: [--fix, --line-length=120]
      - id: ruff-format
        args: [--line-length=120]

  # mypy for type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        args: [--strict, --ignore-missing-imports]
        additional_dependencies:
          - types-requests
          - pydantic
          - types-boto3

  # Basic file hygiene
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: [--maxkb=1000]
      - id: check-merge-conflict
      - id: detect-private-key
```

**pyproject.toml configuration:**
```toml
[tool.ruff]
line-length = 120
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501"]  # Line length handled by formatter

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
```

**Installation:**
```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files

# Update hook versions
pre-commit autoupdate
```

**Pitfalls:**
- **Forgetting to install hooks** - Run `pre-commit install` after cloning
- **Wrong line length** - Use 120 (Fetch standard), not 88 (Black default)
- **Missing type stubs** - Add `additional_dependencies` for third-party libraries

---

## Pattern 2: CI Integration with GitHub Actions

**When to Use:** Ensuring pre-commit runs in CI to catch issues before merge.

```yaml
# .github/workflows/pre-commit.yml
name: Pre-commit Checks

on:
  pull_request:
  push:
    branches: [main, staging]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - uses: pre-commit/action@v3.0.0
```

**Pitfalls:**
- **Not running in CI** - Developers can skip local hooks with `--no-verify`
- **Different versions** - CI should use same pre-commit version as local

---

## Pattern 3: Skip Hooks for Emergencies

**When to Use:** Emergency hotfixes that can't wait for hook fixes.

```bash
# Skip all hooks (use sparingly!)
git commit --no-verify -m "Hotfix: urgent production issue"

# Skip specific hooks via environment variable
SKIP=mypy git commit -m "WIP: incomplete types"

# Disable hooks temporarily
pre-commit uninstall

# Re-enable hooks
pre-commit install
```

**When to skip hooks:**
- **Emergency hotfixes** - Production down, need immediate fix
- **WIP commits** - Work-in-progress on feature branch (but clean before PR)
- **Generated files** - Files from code generators that don't pass hooks

**Pitfalls:**
- **Skipping too often** - If hooks are too slow, optimize them instead
- **Forgetting to fix** - Create follow-up issue to fix skipped checks
- **CI still fails** - Skipping locally doesn't skip CI checks

---

## Common Commands

```bash
# Install hooks
pre-commit install

# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files
pre-commit run mypy --all-files

# Update hook versions to latest
pre-commit autoupdate

# Uninstall hooks
pre-commit uninstall

# Skip hooks for one commit
git commit --no-verify

# Skip specific hook
SKIP=mypy git commit -m "message"
```

## References

- [pre-commit documentation](https://pre-commit.com/)
- [Ruff documentation](https://docs.astral.sh/ruff/)
- [mypy documentation](https://mypy.readthedocs.io/)
