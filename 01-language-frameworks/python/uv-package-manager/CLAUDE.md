# CLAUDE.md - UV Package Manager

This skill teaches UV, the fast Python package and project manager from Astral (creators of Ruff).

## Key Concepts

- **Project Initialization**: `uv init` creates new Python projects with pyproject.toml
- **Dependency Management**: `uv add/remove` manages packages with automatic lock file updates
- **Virtual Environments**: UV creates and manages .venv automatically
- **Lock Files**: uv.lock ensures reproducible builds across environments
- **Python Versions**: UV can install and manage Python interpreters

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run specific example (project setup)
make example-2  # Run specific example (lock files)
make example-3  # Run specific example (multi-env)
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
uv-package-manager/
├── src/uv_package_manager/
│   ├── __init__.py
│   └── examples/
│       ├── example_1.py    # Basic project setup
│       ├── example_2.py    # Lock files demo
│       └── example_3.py    # Multi-environment
├── exercises/
│   ├── exercise_1.py       # FastAPI project
│   ├── exercise_2.py       # Migration from pip
│   ├── exercise_3.py       # Monorepo setup
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Project Initialization
```bash
# New application project
uv init my-app
cd my-app

# New library project (creates src layout)
uv init --lib my-lib
```

### Pattern 2: Dependency Groups
```toml
# pyproject.toml
[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]
test = ["pytest-cov", "pytest-asyncio"]
docs = ["mkdocs", "mkdocs-material"]
```

```bash
# Install with specific groups
uv sync --all-extras
uv sync --extra dev
```

### Pattern 3: Running Commands
```bash
# Always use uv run for venv isolation
uv run python script.py
uv run pytest
uv run ruff check .
```

## Common Mistakes

1. **Running python directly instead of uv run**
   - Why it happens: Habit from pip workflows
   - How to fix it: Always prefix with `uv run` or activate the venv

2. **Editing uv.lock manually**
   - Why it happens: Trying to pin specific versions
   - How to fix it: Use version constraints in pyproject.toml

3. **Forgetting to commit uv.lock**
   - Why it happens: Treating it like .venv
   - How to fix it: Always commit uv.lock for reproducible builds

4. **Using pip install in a UV project**
   - Why it happens: Old habits
   - How to fix it: Use `uv add` instead

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make examples` and explain:
1. UV auto-creates .venv
2. `uv sync` installs all dependencies from uv.lock
3. `uv run` executes commands in the venv

### "Why is UV faster than pip?"
- Written in Rust with parallel resolution
- Uses a global cache for packages
- Optimized dependency resolver

### "How do I migrate from pip?"
```bash
# If you have requirements.txt
uv init
uv add $(cat requirements.txt | tr '\n' ' ')
```

### "How do I migrate from poetry?"
```bash
# UV can read pyproject.toml with poetry format
uv sync  # Will create uv.lock from existing dependencies
```

### "How do I use different Python versions?"
```bash
# Install a Python version
uv python install 3.12

# Pin version for project
uv python pin 3.12

# Run with specific version
uv run --python 3.11 python script.py
```

## Testing Notes

- Tests verify UV command outputs and behaviors
- Run specific tests: `pytest -k "test_name"`
- Check coverage: `make coverage`
- Tests mock subprocess calls for UV commands

## Dependencies

Key dependencies in pyproject.toml:
- pytest: Testing framework
- pytest-subprocess: Mock subprocess calls for UV commands
- ruff: Linting (from Astral, same as UV)
- mypy: Type checking
