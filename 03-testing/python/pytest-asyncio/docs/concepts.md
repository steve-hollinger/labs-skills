# Core Concepts

## Overview

pytest-asyncio is a pytest plugin that enables testing of asyncio code. It provides the ability to test coroutines, use async fixtures, and manage event loops in your test suite.

## Concept 1: Async Test Functions

### What They Are

Async test functions are test functions defined with `async def` that can use `await` to call coroutines.

### Why They Matter

Modern Python applications heavily use async/await for I/O operations. Testing this code requires the ability to await coroutines within tests.

### How They Work

```python
import pytest

# Method 1: Explicit marker
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_operation()
    assert result == "expected"

# Method 2: Auto mode (in pyproject.toml: asyncio_mode = "auto")
# No marker needed - pytest-asyncio detects async functions
async def test_auto_detected():
    result = await some_async_operation()
    assert result == "expected"
```

Under the hood, pytest-asyncio:
1. Creates an event loop for the test
2. Runs the coroutine in that loop
3. Cleans up the loop after the test

## Concept 2: Async Fixtures

### What They Are

Async fixtures are pytest fixtures that can perform async setup and teardown operations.

### Why They Matter

Many resources (database connections, HTTP clients, websockets) require async initialization. Async fixtures enable proper resource management.

### How They Work

```python
import pytest

@pytest.fixture
async def database_connection():
    """Async fixture with setup and teardown."""
    # Async setup
    conn = await create_connection("postgres://localhost/test")

    yield conn  # Provide the fixture value

    # Async teardown
    await conn.close()


@pytest.fixture
async def http_client():
    """Async fixture using async context manager."""
    async with aiohttp.ClientSession() as session:
        yield session
    # Session automatically closed after yield


async def test_with_fixtures(database_connection, http_client):
    """Test using multiple async fixtures."""
    # Both fixtures are ready to use
    result = await database_connection.execute("SELECT 1")
    assert result is not None
```

## Concept 3: Event Loop Scope

### What It Is

Event loop scope determines the lifetime of the asyncio event loop used by tests and fixtures.

### Why It Matters

- **function** scope: New loop per test (isolation, slower)
- **class** scope: Shared loop for class methods
- **module** scope: Shared loop for entire module
- **session** scope: Single loop for all tests (fastest, less isolation)

### How It Works

```python
# pyproject.toml
[tool.pytest.ini_options]
asyncio_default_fixture_loop_scope = "function"  # Default

# Or set per-fixture
@pytest.fixture(scope="session")
async def shared_client():
    """Session-scoped fixture needs session-scoped loop."""
    client = await Client.create()
    yield client
    await client.close()

# Mark the loop scope for session fixtures
@pytest.fixture(scope="session")
def event_loop_policy():
    """Use custom event loop policy for session scope."""
    return asyncio.DefaultEventLoopPolicy()
```

Scope matching is important:
- Session-scoped async fixtures need session-scoped loop
- Module-scoped async fixtures need at least module-scoped loop

## Concept 4: Testing Async Context Managers

### What They Are

Async context managers implement `__aenter__` and `__aexit__` for use with `async with`.

### Why They Matter

Many async resources use context managers for proper cleanup. Tests must verify both the happy path and cleanup behavior.

### How They Work

```python
import pytest
from contextlib import asynccontextmanager

@asynccontextmanager
async def managed_resource():
    """Async context manager to test."""
    resource = await acquire_resource()
    try:
        yield resource
    finally:
        await release_resource(resource)


async def test_context_manager():
    """Test using async context manager."""
    async with managed_resource() as resource:
        result = await resource.operation()
        assert result == "expected"
    # Context manager ensures cleanup


async def test_context_manager_exception():
    """Test context manager handles exceptions."""
    with pytest.raises(ValueError):
        async with managed_resource() as resource:
            raise ValueError("Test error")
    # Context manager should still clean up
```

## Concept 5: Testing Async Generators

### What They Are

Async generators yield values asynchronously, using `async def` with `yield`.

### Why They Matter

Async generators are common for streaming data, pagination, and event streams. Testing them requires iterating asynchronously.

### How They Work

```python
import pytest

async def number_stream(count: int):
    """Async generator that yields numbers."""
    for i in range(count):
        await asyncio.sleep(0.01)  # Simulate async work
        yield i


async def test_async_generator():
    """Test async generator produces expected values."""
    results = []
    async for num in number_stream(5):
        results.append(num)

    assert results == [0, 1, 2, 3, 4]


async def test_async_generator_with_list():
    """Convert async generator to list for easier testing."""
    # Helper to collect async generator results
    results = [num async for num in number_stream(3)]
    assert results == [0, 1, 2]


async def test_async_generator_early_exit():
    """Test breaking out of async generator."""
    results = []
    async for num in number_stream(100):
        results.append(num)
        if num >= 2:
            break

    assert results == [0, 1, 2]
```

## Concept 6: Timeouts in Async Tests

### What They Are

Timeouts ensure async operations don't hang indefinitely, providing bounds on test execution time.

### Why They Matter

Async code can deadlock or wait forever. Timeouts catch these issues and provide fast failure.

### How They Work

```python
import asyncio
import pytest

async def test_with_builtin_timeout():
    """Use asyncio.timeout for Python 3.11+."""
    async with asyncio.timeout(5.0):
        result = await potentially_slow_operation()
    assert result is not None


async def test_timeout_raises():
    """Test that timeout raises TimeoutError."""
    with pytest.raises(asyncio.TimeoutError):
        async with asyncio.timeout(0.1):
            await asyncio.sleep(10)  # Will timeout


async def test_with_wait_for():
    """Alternative using asyncio.wait_for."""
    result = await asyncio.wait_for(
        some_async_operation(),
        timeout=5.0
    )
    assert result is not None


# Using pytest-timeout plugin
@pytest.mark.timeout(10)
async def test_with_pytest_timeout():
    """Test with pytest-timeout marker."""
    result = await long_running_operation()
    assert result is not None
```

## Summary

Key takeaways:

1. **Async tests** use `async def` and require pytest-asyncio
2. **Auto mode** simplifies testing by detecting async functions
3. **Async fixtures** enable proper async resource management
4. **Event loop scope** controls isolation vs performance
5. **Async generators** require async iteration in tests
6. **Timeouts** prevent hanging tests and deadlocks

Best practices:
- Use `asyncio_mode = "auto"` for convenience
- Match fixture scope with loop scope
- Always use timeouts for network operations
- Test both success and error paths
- Clean up resources in fixture teardown
