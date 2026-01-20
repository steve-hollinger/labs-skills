# Core Concepts

## Overview

Ruff is an extremely fast Python linter and formatter written in Rust. It aims to be a drop-in replacement for flake8, isort, black, pyupgrade, autoflake, and many other tools.

## Concept 1: Linting vs Formatting

### What They Are

**Linting** analyzes code for errors, bugs, and style issues without modifying it.
**Formatting** automatically rewrites code to follow consistent style rules.

### Why It Matters

- Linting catches bugs before they reach production
- Formatting ensures consistent code style across teams
- Both improve code readability and maintainability

### How They Work

```bash
# Linting - analyze and report issues
ruff check src/

# Formatting - rewrite files for consistent style
ruff format src/
```

Ruff separates these concerns:
- `ruff check` - linting (700+ rules)
- `ruff format` - formatting (Black-compatible)

## Concept 2: Rule Selection

### What It Is

Ruff implements rules from many popular linters. Each rule has a prefix code identifying its source.

### Why It Matters

- Different projects need different rules
- Start minimal, add rules as needed
- Avoid overwhelming developers with too many rules

### How It Works

```toml
[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # Pyflakes
    "I",   # isort
]
ignore = ["E501"]  # Specific rules to skip
```

Key rule categories:

| Prefix | Source | Focus |
|--------|--------|-------|
| E, W | pycodestyle | Style (PEP 8) |
| F | Pyflakes | Logical errors |
| I | isort | Import sorting |
| N | pep8-naming | Naming conventions |
| UP | pyupgrade | Python upgrades |
| B | flake8-bugbear | Bug detection |
| SIM | flake8-simplify | Simplification |
| C4 | flake8-comprehensions | Comprehensions |

## Concept 3: Auto-fixing

### What It Is

Many Ruff rules come with automatic fixes that correct issues without manual intervention.

### Why It Matters

- Saves developer time
- Ensures consistent application of fixes
- Makes adoption of new rules easier

### How It Works

```bash
# Show what would be fixed
ruff check --diff src/

# Apply safe fixes
ruff check --fix src/

# Apply all fixes (including unsafe)
ruff check --fix --unsafe-fixes src/
```

Configure fixable rules:
```toml
[tool.ruff.lint]
fixable = ["ALL"]      # All rules can be auto-fixed
unfixable = ["F841"]   # Except unused variables
```

## Concept 4: Per-File Configuration

### What It Is

Override rules for specific files or directories without changing global settings.

### Why It Matters

- Tests need different rules (e.g., allow `assert`)
- Legacy code may need exceptions
- Generated code shouldn't be linted

### How It Works

```toml
[tool.ruff.lint.per-file-ignores]
# Allow assert in tests
"tests/*" = ["S101"]

# Allow unused imports in __init__.py (re-exports)
"__init__.py" = ["F401"]

# Ignore multiple rules in migrations
"migrations/*" = ["E501", "N806", "F401"]
```

Or inline:
```python
x = 1  # noqa: F841
```

## Concept 5: Integration with Editors

### What It Is

Ruff integrates with popular editors for real-time feedback.

### Why It Matters

- Immediate feedback while coding
- Fix issues before commit
- Consistent experience across team

### How It Works

**VS Code:**
```json
{
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll.ruff": true,
        "source.organizeImports.ruff": true
    }
}
```

**PyCharm:**
- Install Ruff plugin from marketplace
- Enable as external tool or file watcher

**Neovim:**
```lua
require('lspconfig').ruff_lsp.setup{}
```

## Summary

Key takeaways:

1. **Two tools in one**: `ruff check` (linting) and `ruff format` (formatting)
2. **Selective rules**: Choose relevant rules with `select`, disable with `ignore`
3. **Auto-fix**: Most issues can be automatically fixed with `--fix`
4. **Per-file control**: Customize rules for tests, migrations, etc.
5. **Editor integration**: Real-time feedback in VS Code, PyCharm, etc.
