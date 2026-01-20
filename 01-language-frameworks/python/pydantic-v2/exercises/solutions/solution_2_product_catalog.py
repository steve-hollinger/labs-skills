"""Solution for Exercise 2: Build a Product Catalog

This is the reference solution for the product catalog exercise.
"""

from decimal import Decimal
from typing import Optional

from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)


class Category(BaseModel):
    """Category model for organizing products."""

    id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=50)
    description: Optional[str] = None


class Price(BaseModel):
    """Price model with currency support."""

    amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Ensure currency is uppercase."""
        if not v.isupper() or not v.isalpha():
            raise ValueError("Currency must be 3 uppercase letters (e.g., USD, EUR)")
        return v

    @field_serializer("amount")
    def serialize_amount(self, value: Decimal) -> str:
        """Format amount as string with 2 decimal places."""
        return f"{value:.2f}"


class Product(BaseModel):
    """Product model with validation and computed fields."""

    id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(max_length=2000)
    price: Price
    category: Category
    tags: list[str] = Field(default_factory=list, max_length=10)
    in_stock: bool = True
    quantity: int = Field(ge=0, default=0)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate individual tag lengths."""
        for tag in v:
            if len(tag) < 1 or len(tag) > 30:
                raise ValueError(f"Tag '{tag}' must be 1-30 characters")
        return v

    @model_validator(mode="after")
    def validate_stock_quantity(self) -> "Product":
        """Ensure stock status matches quantity."""
        if self.in_stock and self.quantity <= 0:
            raise ValueError("in_stock is True but quantity is 0 or less")
        if not self.in_stock and self.quantity > 0:
            raise ValueError("in_stock is False but quantity is greater than 0")
        return self

    @computed_field
    @property
    def is_available(self) -> bool:
        """Check if product is available for purchase."""
        return self.in_stock and self.quantity > 0


class Catalog(BaseModel):
    """Catalog containing multiple products."""

    name: str
    products: list[Product] = Field(default_factory=list)

    @computed_field
    @property
    def total_products(self) -> int:
        """Get total number of products in catalog."""
        return len(self.products)

    @computed_field
    @property
    def available_products(self) -> int:
        """Get count of available products."""
        return sum(1 for p in self.products if p.is_available)


def test_product_catalog() -> None:
    """Test the product catalog implementation."""
    print("Testing Product Catalog implementation...")

    # Test 1: Create a valid category
    category = Category(id=1, name="Electronics", description="Electronic devices")
    assert category.id == 1
    print("  Test 1 passed: Category created successfully")

    # Test 2: Create a valid price
    price = Price(amount=Decimal("999.99"), currency="USD")
    assert price.amount == Decimal("999.99")
    print("  Test 2 passed: Price created successfully")

    # Test 3: Price serialization
    price_dict = price.model_dump()
    assert price_dict["amount"] == "999.99"
    print("  Test 3 passed: Price amount serialized to 2 decimal places")

    # Test 4: Currency validation
    try:
        Price(amount=Decimal("10.00"), currency="usd")  # lowercase
        raise AssertionError("Should have rejected lowercase currency")
    except ValidationError:
        print("  Test 4 passed: Lowercase currency rejected")

    # Test 5: Create valid product
    product = Product(
        id=1,
        name="Laptop",
        description="A great laptop for developers",
        price=Price(amount=Decimal("999.99"), currency="USD"),
        category=category,
        tags=["tech", "computer"],
        in_stock=True,
        quantity=50,
    )
    assert product.is_available
    print("  Test 5 passed: Valid product created, is_available=True")

    # Test 6: Product from dict (nested models)
    product_dict = {
        "id": 2,
        "name": "Mouse",
        "description": "Wireless mouse",
        "price": {"amount": "29.99", "currency": "USD"},
        "category": {"id": 2, "name": "Accessories"},
        "tags": ["peripheral"],
        "in_stock": True,
        "quantity": 100,
    }
    product2 = Product.model_validate(product_dict)
    assert product2.price.amount == Decimal("29.99")
    print("  Test 6 passed: Product created from dict with nested models")

    # Test 7: Stock/quantity validation - in_stock but no quantity
    try:
        Product(
            id=3,
            name="Test",
            description="Test",
            price=Price(amount=Decimal("10"), currency="USD"),
            category=category,
            in_stock=True,
            quantity=0,
        )
        raise AssertionError("Should have rejected in_stock=True with quantity=0")
    except ValidationError as e:
        assert "in_stock is True but quantity is 0" in str(e)
        print("  Test 7 passed: in_stock=True with quantity=0 rejected")

    # Test 8: Stock/quantity validation - not in_stock but has quantity
    try:
        Product(
            id=4,
            name="Test",
            description="Test",
            price=Price(amount=Decimal("10"), currency="USD"),
            category=category,
            in_stock=False,
            quantity=10,
        )
        raise AssertionError("Should have rejected in_stock=False with quantity>0")
    except ValidationError as e:
        assert "in_stock is False but quantity is greater" in str(e)
        print("  Test 8 passed: in_stock=False with quantity>0 rejected")

    # Test 9: Out of stock product
    out_of_stock = Product(
        id=5,
        name="Out of Stock Item",
        description="Currently unavailable",
        price=Price(amount=Decimal("50"), currency="USD"),
        category=category,
        in_stock=False,
        quantity=0,
    )
    assert not out_of_stock.is_available
    print("  Test 9 passed: Out of stock product has is_available=False")

    # Test 10: Catalog with computed fields
    catalog = Catalog(
        name="Tech Store",
        products=[product, product2, out_of_stock],
    )
    assert catalog.total_products == 3
    assert catalog.available_products == 2
    print("  Test 10 passed: Catalog computed fields work correctly")

    # Test 11: Tag validation
    try:
        Product(
            id=6,
            name="Bad Tags",
            description="Product with bad tags",
            price=Price(amount=Decimal("10"), currency="USD"),
            category=category,
            tags=["valid", "this-tag-is-way-too-long-and-exceeds-thirty-characters"],
            in_stock=True,
            quantity=1,
        )
        raise AssertionError("Should have rejected long tag")
    except ValidationError:
        print("  Test 11 passed: Long tag rejected")

    # Test 12: Serialization
    catalog_json = catalog.model_dump_json()
    assert "Tech Store" in catalog_json
    print("  Test 12 passed: Catalog serializes to JSON")

    print("\nAll tests passed!")


if __name__ == "__main__":
    test_product_catalog()
