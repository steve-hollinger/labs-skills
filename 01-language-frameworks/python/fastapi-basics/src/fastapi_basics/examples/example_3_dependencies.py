"""Example 3: Dependency Injection

This example demonstrates FastAPI's dependency injection system
for database connections, authentication, and shared resources.
"""

from datetime import datetime
from typing import Annotated, Generator

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from fastapi.security import APIKeyHeader
from fastapi.testclient import TestClient
from pydantic import BaseModel


# =============================================================================
# Simulated Database
# =============================================================================


class FakeDatabase:
    """Simulated database connection."""

    def __init__(self):
        self.connected = False
        self._data = {
            "users": {
                1: {"id": 1, "username": "alice", "email": "alice@example.com"},
                2: {"id": 2, "username": "bob", "email": "bob@example.com"},
            },
            "items": {
                1: {"id": 1, "name": "Widget", "owner_id": 1},
                2: {"id": 2, "name": "Gadget", "owner_id": 2},
            },
        }

    def connect(self):
        self.connected = True
        return self

    def close(self):
        self.connected = False

    def get_user(self, user_id: int):
        return self._data["users"].get(user_id)

    def get_items(self, owner_id: int | None = None, skip: int = 0, limit: int = 10):
        items = list(self._data["items"].values())
        if owner_id:
            items = [i for i in items if i["owner_id"] == owner_id]
        return items[skip : skip + limit]


# =============================================================================
# Models
# =============================================================================


class User(BaseModel):
    id: int
    username: str
    email: str


class Item(BaseModel):
    id: int
    name: str
    owner_id: int


class Pagination(BaseModel):
    skip: int = 0
    limit: int = 10


# =============================================================================
# Dependencies
# =============================================================================


def get_database() -> Generator[FakeDatabase, None, None]:
    """Database dependency with cleanup.

    This is a generator dependency that:
    1. Creates and connects to the database
    2. Yields it for use in the route handler
    3. Closes the connection after the request completes
    """
    db = FakeDatabase()
    db.connect()
    try:
        yield db
    finally:
        db.close()


def get_pagination(
    skip: int = Query(0, ge=0, description="Items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max items to return"),
) -> Pagination:
    """Pagination dependency.

    Extracts and validates pagination parameters from query string.
    """
    return Pagination(skip=skip, limit=limit)


# API Key authentication
API_KEY = "secret-api-key-12345"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str | None = Depends(api_key_header)) -> str:
    """Verify API key from header.

    Raises HTTPException if key is missing or invalid.
    """
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    return api_key


def get_current_user(
    db: FakeDatabase = Depends(get_database),
    user_id: int = Header(..., alias="X-User-ID"),
) -> User:
    """Get current user from header.

    Demonstrates dependency that depends on another dependency (db).
    """
    user_data = db.get_user(user_id)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User {user_id} not found",
        )
    return User(**user_data)


# Class-based dependency
class CommonQueryParams:
    """Class-based dependency for common query parameters.

    Using a class allows for more complex initialization and state.
    """

    def __init__(
        self,
        q: str | None = Query(None, description="Search query"),
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
    ):
        self.q = q
        self.skip = skip
        self.limit = limit


# Request context dependency
class RequestContext:
    """Holds request context information."""

    def __init__(self):
        self.request_time = datetime.now()
        self.request_id = f"req-{datetime.now().timestamp()}"


def get_request_context() -> RequestContext:
    """Create request context for logging/tracing."""
    return RequestContext()


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="Dependency Injection Example",
    description="Demonstrates FastAPI dependency injection patterns",
    version="1.0.0",
)

# Type aliases for cleaner signatures
DatabaseDep = Annotated[FakeDatabase, Depends(get_database)]
PaginationDep = Annotated[Pagination, Depends(get_pagination)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
ApiKeyDep = Annotated[str, Depends(verify_api_key)]
CommonParamsDep = Annotated[CommonQueryParams, Depends()]
ContextDep = Annotated[RequestContext, Depends(get_request_context)]


@app.get("/items/", response_model=list[Item])
def list_items(
    db: DatabaseDep,
    pagination: PaginationDep,
    context: ContextDep,
):
    """List items with pagination.

    Uses:
    - Database dependency (with automatic cleanup)
    - Pagination dependency
    - Request context
    """
    items = db.get_items(skip=pagination.skip, limit=pagination.limit)
    print(f"[{context.request_id}] Listed {len(items)} items")
    return items


@app.get("/items/search/")
def search_items(
    db: DatabaseDep,
    params: CommonParamsDep,
):
    """Search items using class-based dependency."""
    items = db.get_items(skip=params.skip, limit=params.limit)
    if params.q:
        items = [i for i in items if params.q.lower() in i["name"].lower()]
    return {"query": params.q, "items": items}


@app.get("/users/me", response_model=User)
def get_me(current_user: CurrentUserDep):
    """Get current user.

    Requires X-User-ID header.
    """
    return current_user


@app.get("/users/me/items", response_model=list[Item])
def get_my_items(
    db: DatabaseDep,
    current_user: CurrentUserDep,
    pagination: PaginationDep,
):
    """Get current user's items.

    Demonstrates chained dependencies:
    - current_user depends on db
    - This endpoint uses both
    """
    items = db.get_items(
        owner_id=current_user.id,
        skip=pagination.skip,
        limit=pagination.limit,
    )
    return items


@app.get("/protected/")
def protected_endpoint(api_key: ApiKeyDep):
    """Protected endpoint requiring API key.

    Send X-API-Key header with value: secret-api-key-12345
    """
    return {"message": "Access granted", "api_key_prefix": api_key[:10] + "..."}


@app.get("/admin/users/", response_model=list[User])
def admin_list_users(
    db: DatabaseDep,
    api_key: ApiKeyDep,  # Requires API key
    pagination: PaginationDep,
):
    """Admin endpoint to list users.

    Requires both API key and database access.
    """
    users = list(db._data["users"].values())
    return users[pagination.skip : pagination.skip + pagination.limit]


def demonstrate_dependencies():
    """Demonstrate dependency injection."""
    print("Example 3: Dependency Injection")
    print("=" * 50)

    client = TestClient(app)

    # 1. Basic dependency (database + pagination)
    print("\n1. GET /items/ - Database and pagination dependencies:")
    response = client.get("/items/?skip=0&limit=5")
    print(f"   Status: {response.status_code}")
    print(f"   Items: {response.json()}")

    # 2. Class-based dependency
    print("\n2. GET /items/search/ - Class-based dependency:")
    response = client.get("/items/search/?q=widget&limit=5")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # 3. User dependency (from header)
    print("\n3. GET /users/me - User from header dependency:")
    response = client.get("/users/me", headers={"X-User-ID": "1"})
    print(f"   Status: {response.status_code}")
    print(f"   User: {response.json()}")

    # 4. Missing user header
    print("\n4. GET /users/me - Missing user header:")
    response = client.get("/users/me")
    print(f"   Status: {response.status_code}")
    print(f"   Error: {response.json()}")

    # 5. Chained dependencies (user's items)
    print("\n5. GET /users/me/items - Chained dependencies:")
    response = client.get("/users/me/items", headers={"X-User-ID": "1"})
    print(f"   Status: {response.status_code}")
    print(f"   User 1's items: {response.json()}")

    # 6. API key authentication
    print("\n6. GET /protected/ - With valid API key:")
    response = client.get("/protected/", headers={"X-API-Key": API_KEY})
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # 7. Missing API key
    print("\n7. GET /protected/ - Missing API key:")
    response = client.get("/protected/")
    print(f"   Status: {response.status_code}")
    print(f"   Error: {response.json()}")

    # 8. Invalid API key
    print("\n8. GET /protected/ - Invalid API key:")
    response = client.get("/protected/", headers={"X-API-Key": "wrong-key"})
    print(f"   Status: {response.status_code}")
    print(f"   Error: {response.json()}")

    # 9. Combined dependencies
    print("\n9. GET /admin/users/ - Multiple dependencies:")
    response = client.get(
        "/admin/users/?limit=5", headers={"X-API-Key": API_KEY}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Users: {response.json()}")

    # 10. Summary
    print("\n10. Dependency Features Demonstrated:")
    print("    - Generator dependencies (database with cleanup)")
    print("    - Simple function dependencies (pagination)")
    print("    - Class-based dependencies (CommonQueryParams)")
    print("    - Security dependencies (API key, user auth)")
    print("    - Chained dependencies (user depends on db)")
    print("    - Type aliases with Annotated")

    print("\nExample completed successfully!")


def main():
    """Run the example demonstration."""
    demonstrate_dependencies()


if __name__ == "__main__":
    main()
