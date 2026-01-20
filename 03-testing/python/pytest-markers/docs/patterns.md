# Common Patterns

## Overview

This document covers common patterns and best practices for using pytest markers effectively in real-world projects.

## Pattern 1: Test Categorization by Speed

### When to Use

When you need to separate fast tests (for development) from slow tests (for CI).

### Implementation

```python
# pyproject.toml
[tool.pytest.ini_options]
markers = [
    "slow: tests taking more than 1 second",
    "fast: tests completing in under 100ms",
]
```

```python
import pytest

@pytest.mark.fast
def test_simple_calculation():
    assert 2 + 2 == 4

@pytest.mark.slow
def test_complex_algorithm():
    result = expensive_computation()
    assert result == expected
```

### Example

```bash
# During development - run only fast tests
pytest -m "not slow"

# In CI - run everything
pytest

# Nightly builds - run specifically slow tests
pytest -m slow
```

### Pitfalls to Avoid

- Don't mark everything - only mark outliers
- "slow" is relative - document your threshold
- Consider using pytest-timeout instead for enforcement

## Pattern 2: Environment-Based Test Selection

### When to Use

When tests require specific environments, services, or configurations.

### Implementation

```python
# conftest.py
import pytest
import os

def pytest_configure(config):
    config.addinivalue_line("markers", "requires_docker: test needs Docker")
    config.addinivalue_line("markers", "requires_aws: test needs AWS credentials")


# Auto-skip based on environment
@pytest.fixture(autouse=True)
def skip_without_docker(request):
    if request.node.get_closest_marker("requires_docker"):
        if not os.path.exists("/var/run/docker.sock"):
            pytest.skip("Docker not available")


@pytest.fixture(autouse=True)
def skip_without_aws(request):
    if request.node.get_closest_marker("requires_aws"):
        if not os.environ.get("AWS_ACCESS_KEY_ID"):
            pytest.skip("AWS credentials not configured")
```

```python
@pytest.mark.requires_docker
def test_container_deployment():
    # Only runs if Docker is available
    pass

@pytest.mark.requires_aws
def test_s3_upload():
    # Only runs if AWS credentials exist
    pass
```

### Pitfalls to Avoid

- Always provide skip reasons
- Consider using skipif for simple checks
- Document what "requires_docker" actually means

## Pattern 3: Data-Driven Testing

### When to Use

When testing the same logic with many different inputs.

### Implementation

```python
import pytest

# Simple data-driven test
TEST_CASES = [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("PyTest", "PYTEST"),
    ("", ""),
]

@pytest.mark.parametrize("input,expected", TEST_CASES)
def test_uppercase(input, expected):
    assert input.upper() == expected


# Load test data from external source
def load_test_cases():
    """Load test cases from JSON or database."""
    return [
        {"input": "a", "expected": "A"},
        {"input": "b", "expected": "B"},
    ]

@pytest.mark.parametrize("case", load_test_cases(), ids=lambda c: c["input"])
def test_from_external_data(case):
    assert case["input"].upper() == case["expected"]
```

### Pitfalls to Avoid

- Keep test data close to tests (same file or adjacent)
- Use descriptive IDs for failure messages
- Don't load data from network in parametrize (runs at collection time)

## Pattern 4: Feature Flags with Markers

### When to Use

When testing features under development or behind feature flags.

### Implementation

```python
import pytest

# Mark tests for features in development
@pytest.mark.feature_new_checkout
def test_new_checkout_flow():
    pass

@pytest.mark.feature_dark_mode
def test_dark_mode_toggle():
    pass

# In CI, control which features are tested
# pytest -m "not feature_new_checkout"  # Exclude WIP feature
# pytest -m "feature_dark_mode"          # Test specific feature
```

```python
# conftest.py - Auto-skip based on feature flag
import os

def pytest_collection_modifyitems(config, items):
    disabled_features = os.environ.get("DISABLED_FEATURES", "").split(",")

    for item in items:
        for marker in item.iter_markers():
            if marker.name.startswith("feature_"):
                feature_name = marker.name[8:]  # Remove "feature_" prefix
                if feature_name in disabled_features:
                    item.add_marker(pytest.mark.skip(
                        reason=f"Feature {feature_name} is disabled"
                    ))
```

### Pitfalls to Avoid

- Clean up feature markers when features are complete
- Document what each feature marker means
- Don't use for permanent test categories

## Pattern 5: Test Matrix with Multiple Parametrize

### When to Use

When testing combinations of inputs (cartesian product).

### Implementation

```python
import pytest

# Test all combinations of browser and OS
@pytest.mark.parametrize("browser", ["chrome", "firefox", "safari"])
@pytest.mark.parametrize("os", ["windows", "macos", "linux"])
def test_browser_compatibility(browser, os):
    # Runs 9 times (3 browsers x 3 operating systems)
    pass

# With conditional skips for invalid combinations
@pytest.mark.parametrize("browser", ["chrome", "firefox", "safari"])
@pytest.mark.parametrize("os", ["windows", "macos", "linux"])
def test_with_skip(browser, os):
    if browser == "safari" and os != "macos":
        pytest.skip("Safari only available on macOS")
    pass
```

### Better Approach for Complex Matrices

```python
import pytest

# Define valid combinations explicitly
BROWSER_OS_MATRIX = [
    pytest.param("chrome", "windows", id="chrome-win"),
    pytest.param("chrome", "macos", id="chrome-mac"),
    pytest.param("chrome", "linux", id="chrome-linux"),
    pytest.param("firefox", "windows", id="firefox-win"),
    pytest.param("firefox", "macos", id="firefox-mac"),
    pytest.param("firefox", "linux", id="firefox-linux"),
    pytest.param("safari", "macos", id="safari-mac"),  # Only valid combo
]

@pytest.mark.parametrize("browser,os", BROWSER_OS_MATRIX)
def test_explicit_matrix(browser, os):
    pass
```

### Pitfalls to Avoid

- Cartesian products grow quickly (3x3x3 = 27 tests)
- Invalid combinations waste time
- Consider explicit matrices for complex cases

## Pattern 6: Progressive Test Stages

### When to Use

When you want tests to run in stages (smoke -> unit -> integration -> e2e).

### Implementation

```python
import pytest

# pyproject.toml markers
# [tool.pytest.ini_options]
# markers = [
#     "smoke: quick sanity checks",
#     "unit: fast isolated tests",
#     "integration: tests with dependencies",
#     "e2e: end-to-end tests",
# ]

@pytest.mark.smoke
def test_app_starts():
    """Basic sanity check."""
    assert create_app() is not None

@pytest.mark.unit
def test_user_validation():
    """Fast isolated test."""
    assert validate_email("test@example.com")

@pytest.mark.integration
def test_user_database_creation():
    """Requires database."""
    user = create_user_in_db("test@example.com")
    assert user.id is not None

@pytest.mark.e2e
def test_user_signup_flow():
    """Full workflow test."""
    # Browser automation, API calls, etc.
    pass
```

```bash
# CI Pipeline stages
pytest -m smoke        # Stage 1: Quick sanity (30 seconds)
pytest -m unit         # Stage 2: Unit tests (2 minutes)
pytest -m integration  # Stage 3: Integration (10 minutes)
pytest -m e2e          # Stage 4: E2E tests (30 minutes)
```

### Pitfalls to Avoid

- Don't over-categorize - keep it simple
- Ensure smoke tests are truly fast
- Consider parallel execution for later stages

## Anti-Patterns

### Anti-Pattern 1: Unmarked Tests

Tests without any markers make filtering impossible.

```python
# Bad - no markers, can't filter
def test_something():
    pass

# Good - categorized
@pytest.mark.unit
def test_something():
    pass
```

### Better Approach

Set a default marker for all tests:

```python
# conftest.py
def pytest_collection_modifyitems(items):
    for item in items:
        if not list(item.iter_markers()):
            item.add_marker(pytest.mark.unit)  # Default to unit
```

### Anti-Pattern 2: Too Many Markers

Over-categorization makes tests hard to manage.

```python
# Bad - too granular
@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.pure
@pytest.mark.math
@pytest.mark.calculator
@pytest.mark.addition
def test_add():
    assert 1 + 1 == 2
```

### Better Approach

```python
# Good - minimal, meaningful markers
@pytest.mark.unit
def test_add():
    assert 1 + 1 == 2
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Development vs CI tests | Speed-based markers (slow/fast) |
| Platform-specific tests | Environment-based with skipif |
| Testing many inputs | Data-driven with parametrize |
| WIP features | Feature flag markers |
| Browser/platform matrix | Explicit matrix or skip invalid |
| CI pipeline stages | Progressive stages (smoke -> e2e) |
| Default categorization | Auto-marker in conftest.py |
