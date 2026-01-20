"""Example 2: Request/Response Models

This example demonstrates using Pydantic models for
request validation and response serialization.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field, EmailStr, computed_field


# Enums for type safety
class ItemStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


# Request Models (what the client sends)
class ItemCreate(BaseModel):
    """Model for creating a new item."""

    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    description: str | None = Field(None, max_length=1000)
    price: float = Field(..., gt=0, description="Price in USD")
    quantity: int = Field(default=0, ge=0)
    tags: list[str] = Field(default_factory=list, max_length=10)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Widget",
                    "description": "A useful widget",
                    "price": 9.99,
                    "quantity": 100,
                    "tags": ["tool", "useful"],
                }
            ]
        }
    }


class ItemUpdate(BaseModel):
    """Model for updating an existing item (all fields optional)."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    price: float | None = Field(None, gt=0)
    quantity: int | None = Field(None, ge=0)
    status: ItemStatus | None = None
    tags: list[str] | None = Field(None, max_length=10)


class UserCreate(BaseModel):
    """Model for creating a new user."""

    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.USER


# Response Models (what the API returns)
class ItemResponse(BaseModel):
    """Model for item responses."""

    id: int
    name: str
    description: str | None
    price: float
    quantity: int
    status: ItemStatus
    tags: list[str]
    created_at: datetime
    updated_at: datetime | None

    @computed_field
    @property
    def in_stock(self) -> bool:
        """Computed field showing if item is in stock."""
        return self.quantity > 0

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    """Model for user responses (excludes sensitive data)."""

    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    created_at: datetime

    # Note: password is not included in response

    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""

    items: list[ItemResponse]
    total: int
    page: int
    page_size: int
    pages: int


# Simulated database
fake_items_db: dict[int, dict] = {
    1: {
        "id": 1,
        "name": "Widget",
        "description": "A useful widget",
        "price": 9.99,
        "quantity": 100,
        "status": ItemStatus.ACTIVE,
        "tags": ["tool", "useful"],
        "created_at": datetime(2024, 1, 1, 12, 0, 0),
        "updated_at": None,
    },
    2: {
        "id": 2,
        "name": "Gadget",
        "description": "A cool gadget",
        "price": 19.99,
        "quantity": 0,
        "status": ItemStatus.ACTIVE,
        "tags": ["electronics"],
        "created_at": datetime(2024, 1, 2, 10, 0, 0),
        "updated_at": datetime(2024, 1, 5, 14, 30, 0),
    },
}
next_id = 3


# Create FastAPI app
app = FastAPI(
    title="Request/Response Models Example",
    description="Demonstrates Pydantic models for request validation and response serialization",
    version="1.0.0",
)


@app.get("/items/", response_model=PaginatedResponse)
def list_items(page: int = 1, page_size: int = 10):
    """List all items with pagination."""
    items = list(fake_items_db.values())
    total = len(items)
    pages = (total + page_size - 1) // page_size

    start = (page - 1) * page_size
    end = start + page_size
    page_items = items[start:end]

    return {
        "items": page_items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@app.post("/items/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate):
    """Create a new item.

    The request body is automatically validated against ItemCreate model.
    """
    global next_id

    new_item = {
        "id": next_id,
        **item.model_dump(),
        "status": ItemStatus.DRAFT,
        "created_at": datetime.now(),
        "updated_at": None,
    }
    fake_items_db[next_id] = new_item
    next_id += 1

    return new_item


@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    """Get a specific item by ID."""
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return fake_items_db[item_id]


@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemCreate):
    """Fully update an item (all fields required)."""
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

    existing = fake_items_db[item_id]
    updated = {
        **existing,
        **item.model_dump(),
        "updated_at": datetime.now(),
    }
    fake_items_db[item_id] = updated
    return updated


@app.patch("/items/{item_id}", response_model=ItemResponse)
def partial_update_item(item_id: int, item: ItemUpdate):
    """Partially update an item (only provided fields)."""
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

    existing = fake_items_db[item_id]
    # Only update fields that were explicitly provided
    update_data = item.model_dump(exclude_unset=True)

    updated = {
        **existing,
        **update_data,
        "updated_at": datetime.now(),
    }
    fake_items_db[item_id] = updated
    return updated


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    """Delete an item."""
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    del fake_items_db[item_id]


def demonstrate_models():
    """Demonstrate request/response models."""
    print("Example 2: Request/Response Models")
    print("=" * 50)

    client = TestClient(app)

    # 1. List items
    print("\n1. GET /items/ - List items:")
    response = client.get("/items/")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Total items: {data['total']}")
    print(f"   First item has 'in_stock': {data['items'][0].get('in_stock')}")

    # 2. Create item with valid data
    print("\n2. POST /items/ - Create item with valid data:")
    new_item = {
        "name": "New Product",
        "description": "A brand new product",
        "price": 29.99,
        "quantity": 50,
        "tags": ["new", "featured"],
    }
    response = client.post("/items/", json=new_item)
    print(f"   Status: {response.status_code}")
    created = response.json()
    print(f"   Created ID: {created['id']}")
    print(f"   Status: {created['status']}")  # Automatically set to 'draft'
    print(f"   In stock: {created['in_stock']}")  # Computed field

    # 3. Create item with invalid data
    print("\n3. POST /items/ - Invalid data (negative price):")
    invalid_item = {"name": "Bad Item", "price": -10}
    response = client.post("/items/", json=invalid_item)
    print(f"   Status: {response.status_code}")
    print(f"   Error: {response.json()['detail'][0]['msg']}")

    # 4. Create item with missing required field
    print("\n4. POST /items/ - Missing required field:")
    incomplete_item = {"description": "No name"}
    response = client.post("/items/", json=incomplete_item)
    print(f"   Status: {response.status_code}")
    errors = response.json()["detail"]
    print(f"   Missing fields: {[e['loc'][-1] for e in errors]}")

    # 5. Get single item
    print("\n5. GET /items/1 - Get item with computed field:")
    response = client.get("/items/1")
    item = response.json()
    print(f"   Name: {item['name']}")
    print(f"   Quantity: {item['quantity']}")
    print(f"   In stock (computed): {item['in_stock']}")

    # 6. Partial update (PATCH)
    print("\n6. PATCH /items/1 - Partial update:")
    response = client.patch("/items/1", json={"quantity": 200, "status": "active"})
    updated = response.json()
    print(f"   New quantity: {updated['quantity']}")
    print(f"   New status: {updated['status']}")
    print(f"   Name unchanged: {updated['name']}")

    # 7. Full update (PUT)
    print("\n7. PUT /items/2 - Full update:")
    full_update = {
        "name": "Updated Gadget",
        "description": "An updated gadget",
        "price": 24.99,
        "quantity": 75,
        "tags": ["updated"],
    }
    response = client.put("/items/2", json=full_update)
    updated = response.json()
    print(f"   Updated name: {updated['name']}")
    print(f"   Updated at: {updated['updated_at']}")

    # 8. Delete item
    print("\n8. DELETE /items/3 - Delete item:")
    response = client.delete("/items/3")
    print(f"   Status: {response.status_code}")

    # 9. Get deleted item (404)
    print("\n9. GET /items/3 - Get deleted item:")
    response = client.get("/items/3")
    print(f"   Status: {response.status_code}")
    print(f"   Detail: {response.json()['detail']}")

    # 10. Validation summary
    print("\n10. Model Features Demonstrated:")
    print("    - Request body validation (ItemCreate, ItemUpdate)")
    print("    - Response model filtering (ItemResponse)")
    print("    - Computed fields (in_stock)")
    print("    - Enum fields (status, role)")
    print("    - Partial updates with exclude_unset")
    print("    - Pagination wrapper (PaginatedResponse)")

    print("\nExample completed successfully!")


def main():
    """Run the example demonstration."""
    demonstrate_models()


if __name__ == "__main__":
    main()
