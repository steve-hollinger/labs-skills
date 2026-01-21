# Core Concepts: Pytest Setup and Fixtures

## What

Pytest is a Python testing framework that provides a powerful fixture system for testing async FastAPI services. This skill focuses on configuring pytest with `pytest-asyncio` to test asynchronous code, using `httpx.AsyncClient` for FastAPI endpoint testing, and creating reusable fixtures for mocking external dependencies like Kafka and DynamoDB.

Key components:
- **pytest-asyncio**: Plugin that enables testing async functions with `@pytest.mark.asyncio`
- **httpx.AsyncClient**: Async HTTP client for testing FastAPI endpoints
- **Fixtures**: Reusable test components defined with `@pytest.fixture` decorator
- **AsyncMock**: Mock objects for async functions from `unittest.mock`

## Why

**Problem:**
Testing async FastAPI services presents unique challenges:
- Standard synchronous test clients don't properly handle async/await code paths
- External dependencies (Kafka MSK, DynamoDB) are expensive and slow to test against
- Async code requires proper event loop management to avoid "Event loop is closed" errors
- Test isolation is critical when services share global state or connections

**Solution:**
pytest-asyncio with proper fixture design solves these challenges by:
- Providing native support for async test functions with proper event loop handling
- Enabling comprehensive mocking of external services to isolate unit tests
- Offering flexible fixture scopes (session, module, function) to optimize test performance
- Supporting both unit tests (isolated components) and integration tests (full request/response cycle)

**Fetch Context:**
At Fetch, all Python microservices require >80% test coverage. Services typically integrate with:
- **Kafka MSK**: Event streaming for inter-service communication
- **DynamoDB**: NoSQL data storage
- **FastAPI**: Async HTTP endpoints for REST APIs

This testing approach ensures fast, reliable test suites that catch bugs before deployment while maintaining developer productivity.



## How

**Architecture:**

1. **Test Configuration (conftest.py)**
   - Session-scoped event loop fixture for async test execution
   - Application fixtures with dependency overrides for test settings
   - Mock fixtures for external services (Kafka, DynamoDB)
   - Data fixtures for consistent test data

2. **AsyncClient for FastAPI Testing**
   ```python
   @pytest.fixture
   async def async_client(app) -> AsyncGenerator:
       async with AsyncClient(app=app, base_url="http://test") as ac:
           yield ac
   ```
   - Properly handles async request/response cycle
   - Supports all HTTP methods (GET, POST, PUT, DELETE)
   - Returns real response objects with status codes and JSON data

3. **Mocking Strategies**
   - **Kafka Consumer**: Mock `__aiter__` to simulate message streams
   - **DynamoDB Client**: Mock `get_item`, `put_item`, `query` methods
   - **External APIs**: Use `AsyncMock` with `return_value` or `side_effect`
   - **Dependency Injection**: Override FastAPI dependencies in fixtures

4. **Test Organization**
   - `tests/unit/`: Test individual functions/classes with mocked dependencies
   - `tests/integration/`: Test full request/response cycles with `AsyncClient`
   - `tests/conftest.py`: Shared fixtures available to all tests
   - `tests/factories.py`: factory_boy factories for test data generation



## When to Use

**Use when:**
- Testing FastAPI services with async endpoints (`async def` route handlers)
- Your service integrates with Kafka MSK for event streaming
- Your service uses DynamoDB or other AWS services that need mocking
- You need to test async business logic or data processing
- Writing integration tests that verify full request/response cycles
- Aiming for >80% test coverage requirements

**Avoid when:**
- Testing purely synchronous Python code (regular pytest is sufficient)
- Your service has no external dependencies (simple unit tests may suffice)
- Doing end-to-end tests across multiple services (use contract testing instead)
- Performance testing (use locust or similar load testing tools)

## Key Terminology

- **Fixture** - Reusable test component providing data, mocks, or setup/teardown logic
- **AsyncClient** - httpx's async HTTP client for testing FastAPI applications
- **AsyncMock** - Mock object that supports async/await patterns
- **Event Loop** - Core async execution mechanism that must be properly managed in tests
- **Fixture Scope** - Defines fixture lifetime (function, module, session)
- **pytest-asyncio** - Plugin enabling pytest to run async test functions
- **Dependency Override** - FastAPI pattern for replacing dependencies in tests
- **factory_boy** - Library for generating test data with factories
