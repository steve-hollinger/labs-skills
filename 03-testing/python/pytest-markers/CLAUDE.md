# CLAUDE.md - pytest Markers

This skill teaches pytest markers for test organization, categorization, and selective execution.

## Key Concepts

- **Built-in Markers**: skip, xfail, skipif, parametrize for common test scenarios
- **Custom Markers**: User-defined markers for test categorization (slow, integration, unit)
- **Marker Expressions**: Boolean expressions to filter tests (-m "slow and not integration")
- **Marker Registration**: Declaring markers in pyproject.toml to avoid warnings

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run specific example
make test       # Run pytest
make test-slow  # Run only slow-marked tests
make test-fast  # Run tests not marked slow
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
pytest-markers/
├── src/pytest_markers/
│   ├── __init__.py
│   └── examples/
│       ├── example_1_builtin.py
│       ├── example_2_custom.py
│       ├── example_3_parametrize.py
│       └── example_4_combinations.py
├── exercises/
│   ├── exercise_1.py
│   ├── exercise_2.py
│   ├── exercise_3.py
│   └── solutions/
├── tests/
│   ├── test_builtin_markers.py
│   ├── test_custom_markers.py
│   └── test_parametrize.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Skip Tests Conditionally
```python
import pytest
import sys

@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Unix-only feature"
)
def test_unix_specific():
    pass
```

### Pattern 2: Expected Failures
```python
@pytest.mark.xfail(reason="Bug #123 not fixed yet", strict=True)
def test_known_bug():
    assert buggy_code() == expected
```

### Pattern 3: Parametrized Tests
```python
@pytest.mark.parametrize("input,expected", [
    (1, 1),
    (2, 4),
    (3, 9),
], ids=["one", "two", "three"])
def test_square(input, expected):
    assert input ** 2 == expected
```

### Pattern 4: Multiple Custom Markers
```python
@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.database
def test_full_db_sync():
    pass
```

## Common Mistakes

1. **Unregistered markers cause warnings**
   - Why: pytest warns about unknown markers
   - Fix: Add markers to pyproject.toml [tool.pytest.ini_options] markers list

2. **Using skipif when xfail is appropriate**
   - Why: skipif skips entirely; xfail still runs and reports
   - Fix: Use xfail for known bugs to track when they get fixed

3. **Parametrize without ids**
   - Why: Test names become hard to read with auto-generated IDs
   - Fix: Always provide meaningful ids for parametrize

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make examples` and the README.md.

### "Why am I seeing marker warnings?"
Check that all custom markers are registered in pyproject.toml under [tool.pytest.ini_options] markers.

### "How do I run only certain tests?"
Use `pytest -m "marker_name"` or combinations like `pytest -m "slow and not integration"`.

### "What's the difference between skip and xfail?"
- skip: Test doesn't run at all
- xfail: Test runs but failure is expected (useful for tracking known bugs)

### "How do I parametrize with multiple parameters?"
Use multiple @pytest.mark.parametrize decorators or a list of tuples with multiple values.

## Testing Notes

- Tests use pytest with markers
- Run specific tests: `pytest -k "test_name"`
- Run by marker: `pytest -m "marker_name"`
- Check coverage: `make coverage`

## Dependencies

Key dependencies in pyproject.toml:
- pytest>=8.0.0: Core testing framework
- pytest-cov>=4.1.0: Coverage reporting
