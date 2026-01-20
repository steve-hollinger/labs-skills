# Common Patterns

## Overview

This document covers common patterns and best practices for testing async code with pytest-asyncio.

## Pattern 1: Mock Async Functions

### When to Use

When you need to mock async functions or methods for isolated unit testing.

### Implementation

```python
import pytest
from unittest.mock import AsyncMock, patch

class APIClient:
    async def fetch_user(self, user_id: int) -> dict:
        # Real implementation makes HTTP call
        pass

async def test_with_async_mock():
    """Mock an async method."""
    client = APIClient()
    client.fetch_user = AsyncMock(return_value={"id": 1, "name": "Test"})

    result = await client.fetch_user(1)

    assert result["name"] == "Test"
    client.fetch_user.assert_awaited_once_with(1)


async def test_with_patch():
    """Patch an async function."""
    with patch.object(
        APIClient, "fetch_user",
        new_callable=AsyncMock,
        return_value={"id": 1, "name": "Patched"}
    ):
        client = APIClient()
        result = await client.fetch_user(1)
        assert result["name"] == "Patched"
```

### Example with Side Effects

```python
async def test_mock_with_side_effects():
    """Mock with multiple return values or exceptions."""
    mock = AsyncMock(side_effect=[
        {"id": 1, "name": "First"},
        {"id": 2, "name": "Second"},
        ValueError("API Error"),
    ])

    result1 = await mock()
    assert result1["name"] == "First"

    result2 = await mock()
    assert result2["name"] == "Second"

    with pytest.raises(ValueError, match="API Error"):
        await mock()
```

### Pitfalls to Avoid

- Use `AsyncMock`, not regular `Mock` for async functions
- Remember to use `assert_awaited_*` not `assert_called_*`
- Don't forget to await the mocked function

## Pattern 2: Testing HTTP Clients

### When to Use

When testing code that makes async HTTP requests.

### Implementation

```python
import pytest
import aiohttp
from aioresponses import aioresponses

async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


@pytest.fixture
def mock_aiohttp():
    """Fixture for mocking aiohttp requests."""
    with aioresponses() as m:
        yield m


async def test_http_client(mock_aiohttp):
    """Test HTTP client with mocked responses."""
    mock_aiohttp.get(
        "https://api.example.com/users/1",
        payload={"id": 1, "name": "Test User"}
    )

    result = await fetch_data("https://api.example.com/users/1")

    assert result["id"] == 1
    assert result["name"] == "Test User"


async def test_http_error(mock_aiohttp):
    """Test HTTP client handles errors."""
    mock_aiohttp.get(
        "https://api.example.com/users/999",
        status=404
    )

    with pytest.raises(aiohttp.ClientResponseError):
        await fetch_data("https://api.example.com/users/999")
```

### Pitfalls to Avoid

- Always mock external HTTP calls in unit tests
- Test error responses (404, 500, timeouts)
- Don't forget to test retry logic if applicable

## Pattern 3: Testing Database Operations

### When to Use

When testing async database operations with connection pooling.

### Implementation

```python
import pytest
import asyncpg

@pytest.fixture
async def db_pool():
    """Create a test database connection pool."""
    pool = await asyncpg.create_pool(
        "postgresql://test:test@localhost/test_db",
        min_size=1,
        max_size=5
    )
    yield pool
    await pool.close()


@pytest.fixture
async def db_connection(db_pool):
    """Get a connection from the pool with transaction rollback."""
    async with db_pool.acquire() as conn:
        # Start a transaction that will be rolled back
        tr = conn.transaction()
        await tr.start()
        try:
            yield conn
        finally:
            await tr.rollback()


async def test_database_insert(db_connection):
    """Test database insert operation."""
    await db_connection.execute(
        "INSERT INTO users (name, email) VALUES ($1, $2)",
        "Test User", "test@example.com"
    )

    result = await db_connection.fetchrow(
        "SELECT * FROM users WHERE email = $1",
        "test@example.com"
    )

    assert result["name"] == "Test User"
    # Transaction rolls back, no cleanup needed
```

### Pitfalls to Avoid

- Always use transactions for test isolation
- Clean up connections to prevent pool exhaustion
- Consider using a test database

## Pattern 4: Testing WebSocket Connections

### When to Use

When testing async WebSocket clients or servers.

### Implementation

```python
import pytest
import asyncio
from websockets import connect, serve

@pytest.fixture
async def websocket_server():
    """Start a test WebSocket server."""
    async def handler(websocket, path):
        async for message in websocket:
            await websocket.send(f"Echo: {message}")

    server = await serve(handler, "localhost", 8765)
    yield server
    server.close()
    await server.wait_closed()


async def test_websocket_communication(websocket_server):
    """Test WebSocket client-server communication."""
    async with connect("ws://localhost:8765") as ws:
        await ws.send("Hello")
        response = await ws.recv()
        assert response == "Echo: Hello"


async def test_websocket_timeout():
    """Test WebSocket connection timeout."""
    with pytest.raises(asyncio.TimeoutError):
        async with asyncio.timeout(0.1):
            async with connect("ws://nonexistent:9999"):
                pass
```

### Pitfalls to Avoid

- Always close WebSocket connections in tests
- Use timeouts for connection attempts
- Test disconnection handling

## Pattern 5: Testing Concurrent Operations

### When to Use

When testing code that runs multiple async operations concurrently.

### Implementation

```python
import pytest
import asyncio

async def fetch_all_users(user_ids: list[int]) -> list[dict]:
    """Fetch multiple users concurrently."""
    async def fetch_one(uid: int) -> dict:
        await asyncio.sleep(0.1)  # Simulate API call
        return {"id": uid, "name": f"User {uid}"}

    return await asyncio.gather(*[fetch_one(uid) for uid in user_ids])


async def test_concurrent_fetches():
    """Test concurrent operations complete correctly."""
    results = await fetch_all_users([1, 2, 3])

    assert len(results) == 3
    assert all(r["id"] in [1, 2, 3] for r in results)


async def test_concurrent_with_errors():
    """Test concurrent operations with some failures."""
    async def maybe_fail(n: int) -> int:
        if n == 2:
            raise ValueError(f"Failed for {n}")
        return n * 2

    with pytest.raises(ValueError, match="Failed for 2"):
        await asyncio.gather(
            maybe_fail(1),
            maybe_fail(2),
            maybe_fail(3),
        )


async def test_concurrent_return_exceptions():
    """Test gathering with return_exceptions=True."""
    async def maybe_fail(n: int) -> int:
        if n == 2:
            raise ValueError(f"Failed for {n}")
        return n * 2

    results = await asyncio.gather(
        maybe_fail(1),
        maybe_fail(2),
        maybe_fail(3),
        return_exceptions=True
    )

    assert results[0] == 2
    assert isinstance(results[1], ValueError)
    assert results[2] == 6
```

### Pitfalls to Avoid

- Test both success and partial failure scenarios
- Use `return_exceptions=True` when you need all results
- Be careful with shared state in concurrent operations

## Pattern 6: Testing Event-Driven Code

### When to Use

When testing code that uses asyncio Events, Queues, or similar primitives.

### Implementation

```python
import pytest
import asyncio

class EventDrivenProcessor:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.results = []
        self._running = False

    async def process(self):
        self._running = True
        while self._running:
            try:
                item = await asyncio.wait_for(
                    self.queue.get(),
                    timeout=0.1
                )
                self.results.append(item * 2)
                self.queue.task_done()
            except asyncio.TimeoutError:
                continue

    async def stop(self):
        self._running = False


@pytest.fixture
async def processor():
    """Create and start processor."""
    p = EventDrivenProcessor()
    task = asyncio.create_task(p.process())
    yield p
    await p.stop()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


async def test_event_processing(processor):
    """Test event-driven processor."""
    await processor.queue.put(1)
    await processor.queue.put(2)
    await processor.queue.put(3)

    # Wait for processing
    await processor.queue.join()

    assert processor.results == [2, 4, 6]
```

### Pitfalls to Avoid

- Always clean up background tasks
- Use timeouts to prevent hanging
- Test queue overflow scenarios

## Anti-Patterns

### Anti-Pattern 1: Blocking Calls in Async Tests

```python
# BAD - blocks the event loop
async def test_with_blocking_call():
    import requests  # Blocking library!
    response = requests.get("https://example.com")  # Blocks!
    assert response.status_code == 200

# GOOD - use async HTTP client
async def test_with_async_call():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://example.com") as response:
            assert response.status == 200
```

### Anti-Pattern 2: Manual Event Loop Management

```python
# BAD - manual loop management
def test_manual_loop():
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(async_func())
    loop.close()

# GOOD - let pytest-asyncio manage the loop
async def test_auto_loop():
    result = await async_func()
```

### Anti-Pattern 3: Ignoring Cleanup

```python
# BAD - no cleanup
async def test_no_cleanup():
    client = await AsyncClient.create()
    result = await client.fetch()
    assert result is not None
    # Client never closed!

# GOOD - proper cleanup with fixture
@pytest.fixture
async def client():
    client = await AsyncClient.create()
    yield client
    await client.close()

async def test_with_cleanup(client):
    result = await client.fetch()
    assert result is not None
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Mock async dependencies | AsyncMock with patch |
| Test HTTP clients | aioresponses or custom fixtures |
| Test database code | Transaction-wrapped fixtures |
| Test WebSockets | Server fixture with cleanup |
| Test concurrent code | asyncio.gather with error handling |
| Test event-driven code | Background task fixtures |
| Test timeouts | asyncio.timeout or wait_for |
