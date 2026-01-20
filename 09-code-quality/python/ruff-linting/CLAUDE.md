# CLAUDE.md - Ruff Linting

This skill teaches Ruff, the fast Python linter and formatter from Astral (creators of UV).

## Key Concepts

- **Linting**: `ruff check` finds errors, style issues, and bugs
- **Formatting**: `ruff format` formats code (Black-compatible)
- **Configuration**: All settings in pyproject.toml under `[tool.ruff]`
- **Rule Selection**: Choose from 700+ rules via prefix codes
- **Auto-fix**: Many issues can be automatically fixed with `--fix`

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run specific example (basic linting)
make example-2  # Run specific example (rule customization)
make example-3  # Run specific example (CI integration)
make test       # Run pytest
make lint       # Run ruff check and format --check
make format     # Auto-format code
make clean      # Remove build artifacts
```

## Project Structure

```
ruff-linting/
├── src/ruff_linting/
│   ├── __init__.py
│   └── examples/
│       ├── example_1.py    # Basic linting/formatting
│       ├── example_2.py    # Rule customization
│       └── example_3.py    # CI integration
├── exercises/
│   ├── exercise_1.py       # Configure new project
│   ├── exercise_2.py       # Migration from flake8
│   ├── exercise_3.py       # Pre-commit hooks
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Standard Project Configuration
```toml
[tool.ruff]
line-length = 100
target-version = "py311"
exclude = [".venv", "migrations"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "W",   # pycodestyle warnings
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "SIM", # flake8-simplify
]
ignore = ["E501"]  # Line length handled by formatter

[tool.ruff.format]
quote-style = "double"
```

### Pattern 2: Per-File Ignores
```toml
[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]     # Allow assert in tests
"__init__.py" = ["F401"] # Allow unused imports
"migrations/*" = ["E501", "N806"]  # Legacy migrations
```

### Pattern 3: Running Ruff via UV
```bash
# Lint and show errors
uv run ruff check src/ tests/

# Format code
uv run ruff format src/ tests/

# Check and auto-fix
uv run ruff check --fix src/ tests/
```

## Common Mistakes

1. **Selecting too many rules initially**
   - Why it happens: Trying to enable everything at once
   - How to fix it: Start with core rules (E, F, I), add more gradually

2. **Not ignoring E501 with formatter**
   - Why it happens: Expecting linter to enforce line length
   - How to fix it: Let `ruff format` handle line length, ignore E501

3. **Using deprecated isort/black config**
   - Why it happens: Migration from old tools
   - How to fix it: Move settings to `[tool.ruff]` section

4. **Forgetting exclude patterns**
   - Why it happens: Not accounting for generated code
   - How to fix it: Add migrations, .venv, build dirs to exclude

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make lint` and:
```bash
uv run ruff check src/        # Find issues
uv run ruff check --fix src/  # Auto-fix
uv run ruff format src/       # Format
```

### "What rules should I enable?"
Recommended starter set:
- E, W: Style (PEP 8)
- F: Errors (Pyflakes)
- I: Import sorting
- UP: Python upgrades
- B: Bug detection

### "How do I migrate from flake8/black?"
1. Remove old tool configs from pyproject.toml
2. Add `[tool.ruff]` section
3. Map old rules to Ruff equivalents
4. Run `ruff check --fix` to update code
5. Run `ruff format` to standardize style

### "Why is Ruff so fast?"
- Written in Rust (compiled, not interpreted)
- Parallel processing
- Single pass for multiple checks
- Efficient AST parsing

### "How do I ignore specific lines?"
```python
x = 1  # noqa: F841  # Ignore unused variable
```
Or use per-file-ignores in config for patterns.

## Testing Notes

- Tests verify Ruff commands work correctly
- Run specific tests: `pytest -k "test_name"`
- Check coverage: `make coverage`
- Examples demonstrate both valid and intentionally-invalid code

## Dependencies

Key dependencies in pyproject.toml:
- ruff: The linter/formatter itself
- pytest: Testing framework
- mypy: Type checking (complementary tool)
