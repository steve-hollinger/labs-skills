# pytest Markers

Master pytest markers for organizing and selectively running tests. Learn built-in markers, create custom markers, and build well-organized test suites.

## Learning Objectives

After completing this skill, you will be able to:
- Use built-in markers (skip, xfail, parametrize, skipif)
- Create and register custom markers for test categorization
- Run specific tests using marker filters
- Combine markers for flexible test organization
- Apply markers at function, class, and module levels

## Prerequisites

- Python 3.11+
- UV package manager
- Basic pytest knowledge (writing simple tests)

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test

# Run only slow tests
make test-slow

# Run only fast tests
make test-fast
```

## Concepts

### Built-in Markers

pytest provides several built-in markers for common testing scenarios:

```python
import pytest

@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

@pytest.mark.skipif(sys.version_info < (3, 11), reason="Requires Python 3.11+")
def test_new_syntax():
    pass

@pytest.mark.xfail(reason="Known bug in library")
def test_with_known_issue():
    assert buggy_function() == expected

@pytest.mark.parametrize("input,expected", [(1, 2), (2, 4), (3, 6)])
def test_double(input, expected):
    assert input * 2 == expected
```

### Custom Markers

Define your own markers for test categorization:

```python
# In pyproject.toml or pytest.ini
# [tool.pytest.ini_options]
# markers = [
#     "slow: marks tests as slow running",
#     "integration: marks tests requiring external services",
#     "unit: marks unit tests",
# ]

@pytest.mark.slow
def test_complex_algorithm():
    # Takes several seconds
    pass

@pytest.mark.integration
def test_database_connection():
    # Requires database
    pass
```

### Running Tests by Marker

```bash
# Run only tests marked as slow
pytest -m slow

# Run tests NOT marked as slow
pytest -m "not slow"

# Run tests marked as either unit or fast
pytest -m "unit or fast"

# Run tests marked as both integration and database
pytest -m "integration and database"
```

## Examples

### Example 1: Built-in Markers

Demonstrates skip, xfail, skipif, and their variations.

```bash
make example-1
```

### Example 2: Custom Markers

Creating and using custom markers for test organization.

```bash
make example-2
```

### Example 3: Parametrize Marker

Advanced parametrization patterns including nested parametrize.

```bash
make example-3
```

### Example 4: Marker Combinations

Combining multiple markers and using marker expressions.

```bash
make example-4
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Organize a test suite with appropriate markers
2. **Exercise 2**: Create custom markers for a testing workflow
3. **Exercise 3**: Build a parametrized test matrix for edge cases

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Forgetting to Register Custom Markers

If you use a marker without registering it, pytest will show a warning:

```
PytestUnknownMarkWarning: Unknown pytest.mark.slow
```

**Fix**: Register all custom markers in pyproject.toml or pytest.ini.

### Applying Markers to Non-Test Functions

Markers only affect test functions, not fixtures or helper functions.

```python
# WRONG - marker has no effect on fixture
@pytest.mark.slow
@pytest.fixture
def setup_data():
    pass

# RIGHT - mark tests that use slow fixtures
@pytest.mark.slow
def test_using_slow_setup(slow_fixture):
    pass
```

### Confusing skipif and xfail

- `skipif`: Test won't run at all if condition is True
- `xfail`: Test runs but expected to fail; passes if it fails

## Further Reading

- [pytest Markers Documentation](https://docs.pytest.org/en/stable/how-to/mark.html)
- [pytest Parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- Related skills in this repository:
  - [pytest-asyncio](../pytest-asyncio/)
  - [aws-mocking-moto](../aws-mocking-moto/)
