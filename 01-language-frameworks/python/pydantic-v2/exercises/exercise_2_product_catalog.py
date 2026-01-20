"""Exercise 2: Build a Product Catalog

Create a product catalog system with nested models and validators.

Requirements:
1. Create a Category model:
   - id: positive integer
   - name: string, 1-50 characters
   - description: optional string

2. Create a Price model:
   - amount: Decimal, must be > 0
   - currency: string, exactly 3 uppercase letters (e.g., "USD", "EUR")
   - Add a field_serializer to format amount as string with 2 decimal places

3. Create a Product model:
   - id: positive integer
   - name: string, 1-200 characters
   - description: string, max 2000 characters
   - price: Price model (nested)
   - category: Category model (nested)
   - tags: list of strings, max 10 tags, each tag 1-30 characters
   - in_stock: boolean, default True
   - quantity: integer >= 0, default 0

4. Add validation:
   - If in_stock is True, quantity must be > 0
   - If in_stock is False, quantity must be 0
   (Use a model_validator for this)

5. Add a computed field 'is_available' that returns True if in_stock and quantity > 0

6. Create a Catalog model:
   - name: string
   - products: list of Product models
   - Add a computed field 'total_products' that returns the count
   - Add a computed field 'available_products' that returns count of available products

Expected behavior:
    product = Product(
        id=1,
        name="Laptop",
        description="A great laptop",
        price={"amount": "999.99", "currency": "USD"},
        category={"id": 1, "name": "Electronics"},
        tags=["tech", "computer"],
        in_stock=True,
        quantity=50
    )
    print(product.is_available)  # True

    # Should raise ValidationError:
    Product(..., in_stock=True, quantity=0)  # in_stock but no quantity
    Product(..., in_stock=False, quantity=10)  # not in_stock but has quantity

Hints:
- Use Decimal from decimal module for precise money handling
- Use @model_validator(mode='after') for cross-field validation
- Nested models can be created from dicts automatically
"""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class Category(BaseModel):
    """Category model - implement this!"""

    # TODO: Add fields
    pass


class Price(BaseModel):
    """Price model - implement this!"""

    # TODO: Add fields and serializer
    pass


class Product(BaseModel):
    """Product model - implement this!"""

    # TODO: Add fields, validators, and computed fields
    pass


class Catalog(BaseModel):
    """Catalog model - implement this!"""

    # TODO: Add fields and computed fields
    pass


def test_product_catalog() -> None:
    """Test your product catalog implementation."""
    # Test 1: Create a valid product
    # TODO: Implement tests

    print("\nAll tests passed!")


if __name__ == "__main__":
    test_product_catalog()
