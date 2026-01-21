---
name: testing-async-python
description: Asynchronous testing with pytest-asyncio for Python async/await code. Use when writing or improving tests.
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