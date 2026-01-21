# Code Patterns: Pytest Setup and Fixtures

## Pattern 1: AsyncClient Fixtures for FastAPI Testing

**When to Use:** Testing FastAPI endpoints that use async route handlers. Use this pattern for integration tests that verify full HTTP request/response cycles.

```python
# tests/conftest.py
import asyncio
from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient

from src.main import create_app
from src.config import Settings, get_settings


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Override settings for testing."""
    return Settings(
        service_name="test-service",
        environment="dev",
        kafka_brokers="localhost:9092",
        kafka_topic="test-topic",
        log_level="DEBUG",
    )


@pytest.fixture
def app(test_settings: Settings):
    """Create FastAPI app with test settings."""
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: test_settings
    return app


@pytest.fixture
async def async_client(app) -> AsyncGenerator:
    """Create async test client for FastAPI."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# tests/integration/test_search_api.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_endpoint_success(async_client: AsyncClient):
    """Test successful search request."""
    response = await async_client.post(
        "/api/v1/search",
        json={"query": "beverage", "top_k": 5}
    )

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) <= 5


@pytest.mark.asyncio
async def test_search_validation_error(async_client: AsyncClient):
    """Test validation error handling."""
    response = await async_client.post(
        "/api/v1/search",
        json={"query": "", "top_k": 0}
    )

    assert response.status_code == 422
```

**Pitfalls:**
- Don't use FastAPI's `TestClient` for async endpoints - it runs sync code and won't properly test async paths
- Always include the session-scoped `event_loop` fixture to avoid "Event loop is closed" errors
- Use `async with AsyncClient()` context manager to ensure proper cleanup

## Pattern 2: Mocking External Services (Kafka MSK and DynamoDB)

**When to Use:** Testing services that depend on Kafka for event streaming or DynamoDB for data storage. This pattern isolates unit tests from external infrastructure.

```python
# tests/conftest.py
from unittest.mock import AsyncMock, Mock

import pytest


@pytest.fixture
def mock_kafka_consumer():
    """Mock Kafka consumer for testing."""
    consumer = AsyncMock()
    consumer.start = AsyncMock()
    consumer.stop = AsyncMock()

    # Mock async iteration over messages
    consumer.__aiter__ = Mock(return_value=iter([]))

    return consumer


@pytest.fixture
def mock_kafka_producer():
    """Mock Kafka producer for testing."""
    producer = AsyncMock()
    producer.start = AsyncMock()
    producer.stop = AsyncMock()
    producer.send_and_wait = AsyncMock(return_value=Mock(offset=123))

    return producer


@pytest.fixture
def mock_dynamodb_client():
    """Mock DynamoDB client for testing."""
    client = Mock()
    client.get_item = Mock(return_value={
        "Item": {
            "id": {"S": "test-id"},
            "data": {"S": "test-data"}
        }
    })
    client.put_item = Mock(return_value={})
    client.query = Mock(return_value={
        "Items": [],
        "Count": 0
    })

    return client


# tests/unit/test_category_service.py
import pytest
from unittest.mock import Mock, patch

from src.services.category_service import CategoryService


class TestCategoryService:
    """Unit tests for CategoryService."""

    @pytest.fixture
    def service(self, test_settings, mock_kafka_consumer):
        """Create service with mocked dependencies."""
        return CategoryService(test_settings, mock_kafka_consumer)

    @pytest.mark.asyncio
    async def test_load_from_kafka(self, service, mock_kafka_consumer):
        """Test loading data from Kafka consumer."""
        # Setup mock to return test messages
        mock_messages = [
            Mock(value=b'{"categoryId": "cat1", "name": "Beverages"}'),
            Mock(value=b'{"categoryId": "cat2", "name": "Snacks"}')
        ]
        mock_kafka_consumer.__aiter__.return_value = iter(mock_messages)

        await service.load_data()

        assert len(service._data) == 2
        assert service._data[0]["categoryId"] == "cat1"
        mock_kafka_consumer.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_to_dynamodb(self, mock_dynamodb_client):
        """Test saving data to DynamoDB."""
        from src.repositories.category_repository import CategoryRepository

        repo = CategoryRepository(mock_dynamodb_client, table_name="test-table")

        await repo.save({
            "id": "cat1",
            "name": "Beverages",
            "tier": 1
        })

        mock_dynamodb_client.put_item.assert_called_once()
        call_args = mock_dynamodb_client.put_item.call_args
        assert call_args[1]["TableName"] == "test-table"
        assert "Item" in call_args[1]
```

**Pitfalls:**
- Use `AsyncMock()` for async methods, not regular `Mock()` - mixing them causes "object is not awaitable" errors
- When mocking Kafka consumers, must mock both `__aiter__` for iteration AND `start`/`stop` for lifecycle
- DynamoDB responses use nested structure (`{"Item": {"field": {"S": "value"}}}`) - match this in mocks
- Don't forget to call `assert_called_once()` to verify mocks were actually used

## Pattern 3: Factory Patterns with factory_boy

**When to Use:** Generating consistent test data for complex domain models. Factories make tests more readable and maintainable by centralizing data creation logic.

```python
# tests/factories.py
import factory
from factory import Faker, SubFactory, LazyAttribute

from src.models import Category, Product, Merchant


class CategoryFactory(factory.Factory):
    """Factory for Category test data."""

    class Meta:
        model = dict

    categoryId = Faker("uuid4")
    categoryName = Faker("word")
    tier = factory.Sequence(lambda n: n % 5 + 1)
    path = LazyAttribute(lambda obj: [obj.categoryName])
    parentId = None


class MerchantFactory(factory.Factory):
    """Factory for Merchant test data."""

    class Meta:
        model = dict

    merchantId = Faker("uuid4")
    merchantName = Faker("company")
    logo = Faker("image_url")
    isActive = True


class ProductFactory(factory.Factory):
    """Factory for Product test data."""

    class Meta:
        model = dict

    productId = Faker("uuid4")
    productName = Faker("word")
    category = SubFactory(CategoryFactory)
    merchant = SubFactory(MerchantFactory)
    price = Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    pointsMultiplier = 2.0


# tests/conftest.py
import pytest
from tests.factories import CategoryFactory, ProductFactory


@pytest.fixture
def sample_category():
    """Single category for testing."""
    return CategoryFactory()


@pytest.fixture
def sample_categories():
    """Multiple categories for testing."""
    return CategoryFactory.build_batch(5)


@pytest.fixture
def sample_product():
    """Product with nested category and merchant."""
    return ProductFactory()


# tests/unit/test_search_service.py
import pytest

from src.services.search_service import SearchService
from tests.factories import CategoryFactory


class TestSearchService:
    """Unit tests for SearchService."""

    @pytest.fixture
    def service(self):
        """Create search service instance."""
        return SearchService()

    def test_search_with_factory_data(self, service):
        """Test search using factory-generated data."""
        # Create specific test data
        categories = [
            CategoryFactory(categoryName="Beverages", tier=1),
            CategoryFactory(categoryName="Soft Drinks", tier=2, parentId="cat1"),
            CategoryFactory(categoryName="Snacks", tier=1),
        ]

        service.load_categories(categories)

        results = service.search("beverage", top_k=2)

        assert len(results) <= 2
        assert results[0]["categoryName"] == "Beverages"

    def test_search_with_batch_data(self, service):
        """Test search with batch-generated data."""
        # Generate 20 random categories
        categories = CategoryFactory.build_batch(20)

        service.load_categories(categories)

        results = service.search("test", top_k=5)

        assert len(results) <= 5
        assert all("categoryName" in r for r in results)

    def test_product_with_nested_data(self, sample_product):
        """Test product with nested category and merchant."""
        assert "productId" in sample_product
        assert "category" in sample_product
        assert "merchant" in sample_product
        assert sample_product["category"]["categoryName"]
        assert sample_product["merchant"]["merchantName"]
```

**Pitfalls:**
- Don't create factories that depend on database state - keep them pure and stateless
- Use `SubFactory` for nested relationships, not manual dictionary creation
- Use `LazyAttribute` when a field depends on other fields in the same factory
- Use `build()` for in-memory objects, `create()` only if using factory_boy with ORM

