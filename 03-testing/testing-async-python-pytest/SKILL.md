---
name: testing-async-python-pytest
description: Test async Python services with pytest, fixtures, and mocking strategies. Use when writing tests for FastAPI services or async code.
tags: ['python', 'pytest', 'testing', 'async', 'fixtures', 'mocking']
---

# Pytest Setup and Fixtures

## Quick Start
```python
# tests/integration/test_api.py
import pytest
from httpx import AsyncClient


class TestCategorySearchAPI:
    """Integration tests for category search API."""

    @pytest.mark.asyncio
    async def test_search_endpoint_returns_results(self, async_client: AsyncClient):
        """Test search endpoint with valid input."""
        response = await async_client.post(
            "/api/v1/search",
            json={"query": "beverage", "top_k": 5}
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) <= 5
```

## Key Points
- Use `pytest-asyncio` with `@pytest.mark.asyncio` for async test functions
- `AsyncClient` from httpx is required for testing FastAPI async endpoints
- Mock external services (Kafka, DynamoDB) with `AsyncMock` to isolate tests
- Separate `conftest.py` fixtures by scope (session, module, function) for efficiency
- Aim for >80% code coverage as per Fetch standards

## Common Mistakes
1. **Using sync TestClient for async endpoints** - FastAPI's TestClient doesn't support async properly. Use `httpx.AsyncClient` with `@pytest.mark.asyncio` instead
2. **Not cleaning up event loops** - Create a session-scoped event loop fixture to avoid "Event loop is closed" errors across tests
3. **Forgetting to mock external dependencies** - Always mock Kafka consumers, DynamoDB clients, and external APIs. Unmocked services cause tests to fail or hang
4. **Incorrect AsyncMock usage** - Use `AsyncMock()` for async functions, not regular `Mock()`. Set return values with `return_value`, not `side_effect` for single calls
5. **Missing pytest-asyncio markers** - Every async test function must have `@pytest.mark.asyncio` decorator, or configure `asyncio_mode = auto` in pytest.ini

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
