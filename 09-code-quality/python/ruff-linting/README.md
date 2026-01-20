# Ruff Linting

Learn Ruff, the extremely fast Python linter and formatter written in Rust. Ruff replaces flake8, isort, black, pyupgrade, and many other tools with a single, fast binary.

## Learning Objectives

After completing this skill, you will be able to:
- Configure Ruff for linting and formatting in pyproject.toml
- Select and customize rule sets for your project
- Use per-file configuration and ignores
- Integrate Ruff with editors and CI/CD pipelines
- Migrate from existing tools (flake8, black, isort)

## Prerequisites

- Python 3.11+
- UV package manager
- Basic Python development experience

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Concepts

### Basic Linting

Ruff analyzes your code for errors, style issues, and potential bugs:

```bash
# Check all Python files
ruff check .

# Check specific files
ruff check src/ tests/

# Show fixes (but don't apply)
ruff check --diff .

# Auto-fix safe issues
ruff check --fix .
```

### Formatting

Ruff includes a formatter compatible with Black:

```bash
# Format all files
ruff format .

# Check formatting (don't modify)
ruff format --check .

# Show what would change
ruff format --diff .
```

### Configuration

Configure Ruff in pyproject.toml:

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM"]
ignore = ["E501"]  # Line too long (handled by formatter)

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

## Examples

### Example 1: Basic Linting and Formatting

Set up basic Ruff configuration and run checks.

```bash
make example-1
```

### Example 2: Rule Selection and Customization

Configure specific rule sets and per-file ignores.

```bash
make example-2
```

### Example 3: Editor and CI Integration

Integrate Ruff with VS Code and GitHub Actions.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Configure Ruff for a new project
2. **Exercise 2**: Migrate from flake8/black to Ruff
3. **Exercise 3**: Set up pre-commit hooks with Ruff

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Rule Categories

Ruff supports rules from many popular linters:

| Prefix | Source | Description |
|--------|--------|-------------|
| E, W | pycodestyle | Style conventions (PEP 8) |
| F | Pyflakes | Logical errors |
| I | isort | Import sorting |
| N | pep8-naming | Naming conventions |
| UP | pyupgrade | Python version upgrades |
| B | flake8-bugbear | Bug detection |
| SIM | flake8-simplify | Code simplification |
| C4 | flake8-comprehensions | Better comprehensions |

## Common Mistakes

### Mistake 1: Conflicting line-length settings

Ensure formatter and linter use same line length:

```toml
# Wrong - different settings
[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E501"]  # Conflicts with formatter

# Correct - consistent settings
[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F"]
ignore = ["E501"]  # Let formatter handle line length
```

### Mistake 2: Using legacy configuration

Ruff uses a different configuration structure than older tools:

```toml
# Wrong (old black/isort style)
[tool.black]
line-length = 100

# Correct (Ruff style)
[tool.ruff]
line-length = 100
```

## Further Reading

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Rule Reference](https://docs.astral.sh/ruff/rules/)
- [Configuration Reference](https://docs.astral.sh/ruff/configuration/)
- Related skills in this repository:
  - [UV Package Manager](../../../01-language-frameworks/python/uv-package-manager/)
  - [MyPy Type Checking](../mypy-type-checking/)
