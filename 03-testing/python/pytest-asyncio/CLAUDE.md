# CLAUDE.md - pytest-asyncio

This skill teaches asynchronous testing with pytest-asyncio for Python async/await code.

## Key Concepts

- **Async Tests**: Test functions using `async def` with `@pytest.mark.asyncio`
- **Async Fixtures**: Fixtures that perform async setup/teardown with `yield`
- **Event Loop Scope**: Control loop lifetime (function, class, module, session)
- **Auto Mode**: Automatically detect and run async tests without explicit markers

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run specific example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
pytest-asyncio/
├── src/pytest_asyncio_skill/
│   ├── __init__.py
│   └── examples/
│       ├── example_1_basic.py
│       ├── example_2_fixtures.py
│       ├── example_3_generators.py
│       └── example_4_concurrency.py
├── exercises/
│   ├── exercise_1.py
│   ├── exercise_2.py
│   ├── exercise_3.py
│   └── solutions/
├── tests/
│   ├── test_basic_async.py
│   ├── test_async_fixtures.py
│   └── test_concurrency.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic Async Test
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_operation()
    assert result == expected
```

### Pattern 2: Async Fixture
```python
@pytest.fixture
async def client():
    client = await Client.create()
    yield client
    await client.close()

@pytest.mark.asyncio
async def test_with_client(client):
    result = await client.fetch()
    assert result is not None
```

### Pattern 3: Testing with Timeout
```python
import asyncio

@pytest.mark.asyncio
async def test_with_timeout():
    async with asyncio.timeout(5.0):
        result = await slow_operation()
    assert result is not None
```

### Pattern 4: Testing Concurrent Operations
```python
@pytest.mark.asyncio
async def test_concurrent_operations():
    results = await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3),
    )
    assert len(results) == 3
```

## Common Mistakes

1. **Missing @pytest.mark.asyncio decorator**
   - Why: Test runs as sync function, await is syntax error
   - Fix: Add decorator or use asyncio_mode = "auto"

2. **Creating manual event loops**
   - Why: Conflicts with pytest-asyncio's loop management
   - Fix: Use async def tests, not asyncio.run() or run_until_complete()

3. **Forgetting to await coroutines**
   - Why: Returns coroutine object, not result
   - Fix: Always await async function calls

4. **Fixture scope mismatch with event loop**
   - Why: Session-scoped async fixture with function-scoped loop fails
   - Fix: Match fixture scope with loop scope

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make examples` and the README.md.

### "Why is my async test not running?"
Check for @pytest.mark.asyncio decorator or asyncio_mode setting.

### "How do I share fixtures across tests?"
Use session or module scoped fixtures with matching loop scope.

### "How do I test timeouts?"
Use `async with asyncio.timeout(seconds)` or pytest-timeout plugin.

### "How do I mock async functions?"
Use `unittest.mock.AsyncMock` or pytest-mock's `mocker.AsyncMock`.

## Testing Notes

- Tests use pytest with asyncio mode
- Auto mode detects async tests automatically
- Run specific tests: `pytest -k "test_name"`
- Check coverage: `make coverage`

## Dependencies

Key dependencies in pyproject.toml:
- pytest>=8.0.0: Core testing framework
- pytest-asyncio>=0.23.0: Async testing support
- pytest-cov>=4.1.0: Coverage reporting
