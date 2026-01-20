"""Example 1: Basic Models

This example demonstrates defining Pydantic models with various field types,
constraints, and default values.
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl, ValidationError


class UserRole(str, Enum):
    """User roles in the system."""

    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class User(BaseModel):
    """A user model with various field types and constraints."""

    # Required fields
    username: str = Field(min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(description="User's email address")

    # Optional field with default
    role: UserRole = Field(default=UserRole.USER, description="User's role")

    # Numeric constraints
    age: Optional[int] = Field(default=None, ge=0, le=150, description="User's age")

    # Boolean with default
    is_active: bool = Field(default=True, description="Whether user is active")

    # Date field
    birth_date: Optional[date] = Field(default=None, description="Date of birth")


class Product(BaseModel):
    """A product model with numeric and string constraints."""

    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    price: float = Field(gt=0, description="Price must be positive")
    quantity: int = Field(ge=0, default=0)
    sku: str = Field(pattern=r"^[A-Z]{3}-\d{4}$", description="SKU like ABC-1234")
    tags: list[str] = Field(default_factory=list, max_length=10)


class BlogPost(BaseModel):
    """A blog post with various field types."""

    title: str = Field(min_length=1, max_length=200)
    content: str
    author: str
    published_at: Optional[datetime] = None
    url: Optional[HttpUrl] = None
    views: int = Field(default=0, ge=0)


def main() -> None:
    """Run the basic models example."""
    print("Example 1: Basic Pydantic Models")
    print("=" * 50)

    # Creating a valid user
    print("\n1. Creating a valid user:")
    user = User(
        username="alice_smith",
        email="alice@example.com",
        age=28,
        birth_date=date(1996, 5, 15),
    )
    print(f"   User: {user}")
    print(f"   Username: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Role: {user.role}")
    print(f"   Age: {user.age}")

    # Type coercion - string to int
    print("\n2. Type coercion (string '30' to int 30):")
    user2 = User(username="bob", email="bob@example.com", age="30")  # type: ignore[arg-type]
    print(f"   Age type: {type(user2.age).__name__}, value: {user2.age}")

    # Creating a product
    print("\n3. Creating a product with constraints:")
    product = Product(
        name="Wireless Mouse",
        description="Ergonomic wireless mouse",
        price=29.99,
        quantity=100,
        sku="MOU-1234",
        tags=["electronics", "accessories"],
    )
    print(f"   Product: {product.name}")
    print(f"   SKU: {product.sku}")
    print(f"   Price: ${product.price}")

    # Validation error examples
    print("\n4. Validation errors:")

    # Invalid email
    try:
        User(username="charlie", email="not-an-email")
    except ValidationError as e:
        print(f"   Invalid email error: {e.errors()[0]['msg']}")

    # Username too short
    try:
        User(username="ab", email="valid@example.com")
    except ValidationError as e:
        print(f"   Short username error: {e.errors()[0]['msg']}")

    # Invalid SKU pattern
    try:
        Product(name="Test", price=10.0, sku="invalid-sku")
    except ValidationError as e:
        print(f"   Invalid SKU error: {e.errors()[0]['msg']}")

    # Negative price
    try:
        Product(name="Test", price=-5.0, sku="ABC-1234")
    except ValidationError as e:
        print(f"   Negative price error: {e.errors()[0]['msg']}")

    # Creating a blog post
    print("\n5. Blog post with optional URL:")
    post = BlogPost(
        title="Getting Started with Pydantic",
        content="Pydantic makes data validation easy...",
        author="Alice",
        url="https://blog.example.com/pydantic-intro",
    )
    print(f"   Title: {post.title}")
    print(f"   URL: {post.url}")

    # Accessing model metadata
    print("\n6. Model metadata:")
    print(f"   User fields: {list(User.model_fields.keys())}")
    print(f"   User JSON schema keys: {list(User.model_json_schema().keys())}")

    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
