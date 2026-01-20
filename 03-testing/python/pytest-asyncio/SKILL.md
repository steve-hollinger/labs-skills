---
name: testing-async-python
description: This skill teaches asynchronous testing with pytest-asyncio for Python async/await code. Use when writing or improving tests.
---

# Pytest Asyncio

## Quick Start
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_operation()
    assert result == expected
```

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run specific example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Key Points
- Async Tests
- Async Fixtures
- Event Loop Scope

## Common Mistakes
1. **Missing @pytest.mark.asyncio decorator** - Add decorator or use asyncio_mode = "auto"
2. **Creating manual event loops** - Use async def tests, not asyncio.run() or run_until_complete()
3. **Forgetting to await coroutines** - Always await async function calls

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples