# pytest-asyncio

Master asynchronous testing with pytest-asyncio. Learn to test async functions, use async fixtures, manage event loops, and avoid common pitfalls in async testing.

## Learning Objectives

After completing this skill, you will be able to:
- Test async functions and coroutines with pytest
- Create and use async fixtures
- Understand event loop management in tests
- Test async generators and context managers
- Handle timeouts and concurrency in tests
- Debug common async testing issues

## Prerequisites

- Python 3.11+
- UV package manager
- Basic pytest knowledge
- Understanding of Python async/await syntax

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

### Basic Async Test

pytest-asyncio allows you to write async test functions:

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_operation()
    assert result == expected
```

### Async Fixtures

Create fixtures that perform async setup and teardown:

```python
import pytest

@pytest.fixture
async def async_client():
    client = await create_client()
    yield client
    await client.close()

@pytest.mark.asyncio
async def test_with_client(async_client):
    result = await async_client.fetch("/api/data")
    assert result.status == 200
```

### Event Loop Modes

pytest-asyncio supports different event loop scopes:

```python
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"  # Automatically detect async tests
# OR use "strict" to require explicit @pytest.mark.asyncio

asyncio_default_fixture_loop_scope = "function"  # New event loop per test
```

## Examples

### Example 1: Basic Async Testing

Testing simple async functions and coroutines.

```bash
make example-1
```

### Example 2: Async Fixtures

Creating and using async fixtures for setup/teardown.

```bash
make example-2
```

### Example 3: Testing Async Generators

Testing async iterators and generators.

```bash
make example-3
```

### Example 4: Concurrency Patterns

Testing concurrent operations with asyncio.gather and timeouts.

```bash
make example-4
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Test an async HTTP client wrapper
2. **Exercise 2**: Create async fixtures for a database connection
3. **Exercise 3**: Test an async message queue consumer

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Forgetting the async Marker

Without the marker, your test runs synchronously and fails:

```python
# WRONG - runs synchronously, await fails
def test_async_operation():
    result = await fetch_data()  # SyntaxError!

# RIGHT - properly marked as async
@pytest.mark.asyncio
async def test_async_operation():
    result = await fetch_data()
    assert result is not None
```

### Mixing Event Loops

Don't create your own event loop in tests:

```python
# WRONG - creates new loop, conflicts with pytest-asyncio
def test_with_manual_loop():
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(fetch_data())

# RIGHT - use the provided event loop
@pytest.mark.asyncio
async def test_async_operation():
    result = await fetch_data()
```

### Not Awaiting Coroutines

Forgetting to await returns a coroutine object, not the result:

```python
@pytest.mark.asyncio
async def test_forgot_await():
    # WRONG - result is a coroutine, not the actual value
    result = some_async_function()
    assert result == expected  # Fails!

    # RIGHT - await the coroutine
    result = await some_async_function()
    assert result == expected
```

## Further Reading

- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- Related skills in this repository:
  - [pytest-markers](../pytest-markers/)
  - [aws-mocking-moto](../aws-mocking-moto/)
