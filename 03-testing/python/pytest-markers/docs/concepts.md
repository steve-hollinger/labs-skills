# Core Concepts

## Overview

pytest markers are decorators that attach metadata to test functions. This metadata can be used to skip tests, expect failures, generate test cases, or categorize tests for selective execution.

## Concept 1: Built-in Markers

### What They Are

pytest provides several built-in markers for common testing scenarios:

- `@pytest.mark.skip` - Always skip the test
- `@pytest.mark.skipif` - Skip if condition is True
- `@pytest.mark.xfail` - Expect the test to fail
- `@pytest.mark.parametrize` - Generate multiple test cases

### Why They Matter

Built-in markers help you:
- Handle platform-specific tests
- Document known issues without breaking CI
- Reduce test duplication through parameterization
- Control test execution based on environment

### How They Work

```python
import pytest
import sys

# Skip unconditionally
@pytest.mark.skip(reason="Feature not implemented")
def test_future_feature():
    pass

# Skip based on condition
@pytest.mark.skipif(
    sys.version_info < (3, 11),
    reason="Requires Python 3.11+ for match statement"
)
def test_match_statement():
    match value:
        case 1: pass

# Expected failure
@pytest.mark.xfail(reason="Bug #456 - division by zero not handled")
def test_known_bug():
    result = divide(1, 0)  # Will fail, but test passes

# Strict xfail - fails if test unexpectedly passes
@pytest.mark.xfail(reason="Should fail", strict=True)
def test_strict_expectation():
    assert False  # Passes because failure expected
```

## Concept 2: Custom Markers

### What They Are

Custom markers are user-defined labels you attach to tests. They have no built-in behavior but enable powerful test selection.

### Why They Matter

Custom markers let you:
- Categorize tests by type (unit, integration, e2e)
- Group tests by feature or component
- Control CI/CD pipelines (smoke tests first)
- Separate fast and slow tests

### How They Work

First, register markers in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow running",
    "integration: marks tests requiring external services",
    "unit: marks unit tests (fast, no I/O)",
    "database: marks tests needing database",
]
```

Then use them in tests:

```python
import pytest

@pytest.mark.unit
def test_pure_calculation():
    assert add(2, 2) == 4

@pytest.mark.slow
@pytest.mark.integration
def test_api_roundtrip():
    # Takes 30 seconds, needs network
    pass

@pytest.mark.database
@pytest.mark.integration
def test_user_creation():
    # Needs database connection
    pass
```

Run by marker:

```bash
pytest -m unit           # Fast unit tests only
pytest -m "not slow"     # Everything except slow
pytest -m "database"     # Database tests only
```

## Concept 3: Parametrize Marker

### What It Is

The `@pytest.mark.parametrize` decorator generates multiple test cases from a single test function, each with different inputs and expected outputs.

### Why It Matters

Parametrization:
- Eliminates copy-paste test code
- Makes adding test cases trivial
- Provides clear test IDs for failures
- Enables data-driven testing

### How It Works

```python
import pytest

# Basic parametrization
@pytest.mark.parametrize("input,expected", [
    (1, 1),
    (2, 4),
    (3, 9),
    (-1, 1),
    (0, 0),
])
def test_square(input, expected):
    assert input ** 2 == expected

# With custom IDs
@pytest.mark.parametrize("input,expected", [
    (1, 1),
    (2, 4),
    (3, 9),
], ids=["one_squared", "two_squared", "three_squared"])
def test_square_with_ids(input, expected):
    assert input ** 2 == expected

# Multiple parametrize = cartesian product
@pytest.mark.parametrize("x", [1, 2, 3])
@pytest.mark.parametrize("y", [10, 20])
def test_multiplication(x, y):
    # Runs 6 times: (1,10), (1,20), (2,10), (2,20), (3,10), (3,20)
    assert x * y == x * y

# Parametrize with marks
@pytest.mark.parametrize("value,expected", [
    (1, 1),
    pytest.param(0, 0, marks=pytest.mark.xfail(reason="Division by zero")),
    (-1, 1),
])
def test_inverse(value, expected):
    assert 1 / value == expected  # 0 case will xfail
```

## Concept 4: Marker Expressions

### What They Are

Marker expressions are boolean filters for selecting tests based on their markers.

### Why They Matter

Expressions enable:
- Complex test selection logic
- CI pipeline stages (smoke -> unit -> integration)
- Developer workflows (run fast tests during development)
- Environment-specific test runs

### How They Work

```bash
# Single marker
pytest -m slow

# NOT expression
pytest -m "not slow"

# AND expression
pytest -m "integration and database"

# OR expression
pytest -m "unit or smoke"

# Complex expressions
pytest -m "(unit or integration) and not slow"
pytest -m "smoke or (fast and unit)"
```

## Concept 5: Class and Module Level Markers

### What They Are

Markers can be applied at the function, class, or module level to affect multiple tests at once.

### Why They Matter

Level-based markers:
- Reduce decorator repetition
- Apply consistent categorization
- Enable inheritance patterns

### How They Work

```python
import pytest

# Module-level marker - affects all tests in file
pytestmark = pytest.mark.integration

# Can also be a list
pytestmark = [pytest.mark.integration, pytest.mark.slow]


# Class-level marker - affects all methods
@pytest.mark.database
class TestUserRepository:
    def test_create_user(self):
        pass  # Inherits @database marker

    def test_delete_user(self):
        pass  # Inherits @database marker

    @pytest.mark.slow  # Additional marker
    def test_bulk_import(self):
        pass  # Has both @database and @slow


# Inheritance works too
@pytest.mark.api
class TestAPIBase:
    pass

class TestUserAPI(TestAPIBase):
    def test_get_user(self):
        pass  # Inherits @api marker
```

## Summary

Key takeaways:

1. **Built-in markers** handle common scenarios: skip, xfail, parametrize
2. **Custom markers** enable test categorization without affecting behavior
3. **Registration** in pyproject.toml prevents warnings and documents markers
4. **Marker expressions** provide powerful test filtering with boolean logic
5. **Level inheritance** reduces repetition across related tests

Best practices:
- Register all custom markers
- Use meaningful marker names
- Provide IDs for parametrized tests
- Combine markers for fine-grained control
- Document marker meanings in your project
