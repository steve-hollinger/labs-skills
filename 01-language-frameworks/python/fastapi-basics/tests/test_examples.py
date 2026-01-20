"""Tests for FastAPI Basics examples."""

import pytest
from fastapi.testclient import TestClient


class TestExample1BasicRoutes:
    """Tests for Example 1: Basic Routes."""

    def test_root_endpoint(self) -> None:
        """Test root endpoint returns welcome message."""
        from fastapi_basics.examples.example_1_basic_routes import app

        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_path_parameter(self) -> None:
        """Test path parameter validation."""
        from fastapi_basics.examples.example_1_basic_routes import app

        client = TestClient(app)

        # Valid integer
        response = client.get("/items/42")
        assert response.status_code == 200
        assert response.json()["item_id"] == 42

        # Invalid (non-integer)
        response = client.get("/items/invalid")
        assert response.status_code == 422

    def test_query_parameters(self) -> None:
        """Test query parameter handling."""
        from fastapi_basics.examples.example_1_basic_routes import app

        client = TestClient(app)

        # With parameters
        response = client.get("/items/?skip=5&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert data["skip"] == 5
        assert data["limit"] == 3

        # Defaults
        response = client.get("/items/")
        assert response.status_code == 200
        data = response.json()
        assert data["skip"] == 0
        assert data["limit"] == 10

    def test_query_parameter_validation(self) -> None:
        """Test query parameter validation."""
        from fastapi_basics.examples.example_1_basic_routes import app

        client = TestClient(app)

        # Limit too high
        response = client.get("/items/?limit=200")
        assert response.status_code == 422

        # Negative skip
        response = client.get("/items/?skip=-1")
        assert response.status_code == 422

    def test_health_endpoint(self) -> None:
        """Test health check endpoint."""
        from fastapi_basics.examples.example_1_basic_routes import app

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestExample2Models:
    """Tests for Example 2: Request/Response Models."""

    def test_list_items(self) -> None:
        """Test listing items with pagination."""
        from fastapi_basics.examples.example_2_models import app

        client = TestClient(app)
        response = client.get("/items/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data

    def test_create_item(self) -> None:
        """Test creating an item."""
        from fastapi_basics.examples.example_2_models import app, fake_items_db, next_id

        client = TestClient(app)

        response = client.post(
            "/items/",
            json={
                "name": "Test Item",
                "price": 19.99,
                "quantity": 10,
                "tags": ["test"],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Item"
        assert data["status"] == "draft"
        assert "in_stock" in data  # Computed field

    def test_create_item_validation(self) -> None:
        """Test item creation validation."""
        from fastapi_basics.examples.example_2_models import app

        client = TestClient(app)

        # Missing required field
        response = client.post("/items/", json={"description": "No name"})
        assert response.status_code == 422

        # Negative price
        response = client.post("/items/", json={"name": "Test", "price": -10})
        assert response.status_code == 422

    def test_get_item(self) -> None:
        """Test getting a single item."""
        from fastapi_basics.examples.example_2_models import app

        client = TestClient(app)

        response = client.get("/items/1")
        assert response.status_code == 200
        assert response.json()["id"] == 1

    def test_get_item_not_found(self) -> None:
        """Test 404 for non-existent item."""
        from fastapi_basics.examples.example_2_models import app

        client = TestClient(app)

        response = client.get("/items/999")
        assert response.status_code == 404

    def test_partial_update(self) -> None:
        """Test partial update with PATCH."""
        from fastapi_basics.examples.example_2_models import app

        client = TestClient(app)

        # Only update status
        response = client.patch("/items/1", json={"status": "active"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"


class TestExample3Dependencies:
    """Tests for Example 3: Dependency Injection."""

    def test_list_items_with_pagination(self) -> None:
        """Test items endpoint with pagination dependency."""
        from fastapi_basics.examples.example_3_dependencies import app

        client = TestClient(app)

        response = client.get("/items/?skip=0&limit=5")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_protected_endpoint_without_key(self) -> None:
        """Test protected endpoint without API key."""
        from fastapi_basics.examples.example_3_dependencies import app

        client = TestClient(app)

        response = client.get("/protected/")
        assert response.status_code == 401

    def test_protected_endpoint_with_valid_key(self) -> None:
        """Test protected endpoint with valid API key."""
        from fastapi_basics.examples.example_3_dependencies import app, API_KEY

        client = TestClient(app)

        response = client.get("/protected/", headers={"X-API-Key": API_KEY})
        assert response.status_code == 200
        assert "message" in response.json()

    def test_protected_endpoint_with_invalid_key(self) -> None:
        """Test protected endpoint with invalid API key."""
        from fastapi_basics.examples.example_3_dependencies import app

        client = TestClient(app)

        response = client.get("/protected/", headers={"X-API-Key": "wrong-key"})
        assert response.status_code == 403

    def test_user_dependency(self) -> None:
        """Test user dependency from header."""
        from fastapi_basics.examples.example_3_dependencies import app

        client = TestClient(app)

        response = client.get("/users/me", headers={"X-User-ID": "1"})
        assert response.status_code == 200
        assert response.json()["id"] == 1

    def test_user_dependency_missing_header(self) -> None:
        """Test user dependency with missing header."""
        from fastapi_basics.examples.example_3_dependencies import app

        client = TestClient(app)

        response = client.get("/users/me")
        assert response.status_code == 422  # Missing required header


class TestExample4AsyncMiddleware:
    """Tests for Example 4: Async and Middleware."""

    def test_middleware_headers(self) -> None:
        """Test custom middleware headers are added."""
        from fastapi_basics.examples.example_4_async_middleware import app

        client = TestClient(app)

        response = client.get("/health")
        assert response.status_code == 200
        assert "X-Process-Time" in response.headers
        assert "X-Request-ID" in response.headers

    def test_async_endpoint(self) -> None:
        """Test async endpoint returns data."""
        from fastapi_basics.examples.example_4_async_middleware import app

        client = TestClient(app)

        response = client.get("/async/users")
        assert response.status_code == 200
        data = response.json()
        assert "source" in data
        assert "data" in data
        assert "duration_ms" in data

    def test_dashboard_parallel(self) -> None:
        """Test dashboard parallel endpoint."""
        from fastapi_basics.examples.example_4_async_middleware import app

        client = TestClient(app)

        response = client.get("/async/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "orders" in data
        assert "stats" in data

    def test_custom_error_handler(self) -> None:
        """Test custom error handler."""
        from fastapi_basics.examples.example_4_async_middleware import app

        client = TestClient(app)

        response = client.get("/error/custom")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "timestamp" in data

    def test_general_error_handler(self) -> None:
        """Test general error handler."""
        from fastapi_basics.examples.example_4_async_middleware import app

        client = TestClient(app)

        response = client.get("/error/unhandled")
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Internal server error"

    def test_cors_headers(self) -> None:
        """Test CORS headers on preflight request."""
        from fastapi_basics.examples.example_4_async_middleware import app

        client = TestClient(app)

        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert "access-control-allow-origin" in response.headers
