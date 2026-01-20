"""Example 3: Serialization and Parsing

This example demonstrates converting models to dict/JSON,
custom serializers, and parsing from various data sources.
"""

import json
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
)


class OrderStatus(str, Enum):
    """Order status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"


class Money(BaseModel):
    """Money model with custom serialization."""

    amount: Decimal
    currency: str = "USD"

    @field_serializer("amount")
    def serialize_amount(self, value: Decimal) -> str:
        """Serialize Decimal to string with 2 decimal places."""
        return f"{value:.2f}"


class OrderItem(BaseModel):
    """Order item with computed total."""

    product_name: str
    quantity: int = Field(gt=0)
    unit_price: Money

    @computed_field
    @property
    def total(self) -> Money:
        """Calculate total for this item."""
        return Money(
            amount=self.unit_price.amount * self.quantity,
            currency=self.unit_price.currency,
        )


class Order(BaseModel):
    """Order model demonstrating serialization options."""

    model_config = ConfigDict(
        # Allow creating from ORM objects
        from_attributes=True,
        # Validate on assignment
        validate_assignment=True,
    )

    id: UUID = Field(default_factory=uuid4)
    customer_email: str
    items: list[OrderItem]
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = None

    # Field excluded from serialization
    internal_reference: str = Field(default="", exclude=True)

    @computed_field
    @property
    def item_count(self) -> int:
        """Total number of items in order."""
        return sum(item.quantity for item in self.items)

    @computed_field
    @property
    def order_total(self) -> Money:
        """Calculate order total."""
        if not self.items:
            return Money(amount=Decimal("0"))
        total = sum(item.total.amount for item in self.items)
        return Money(amount=total, currency=self.items[0].unit_price.currency)

    @field_serializer("created_at")
    def serialize_datetime(self, dt: datetime) -> str:
        """Serialize datetime to ISO format."""
        return dt.isoformat()

    @field_serializer("id")
    def serialize_uuid(self, value: UUID) -> str:
        """Serialize UUID to string."""
        return str(value)


class UserProfile(BaseModel):
    """User profile with alias support for API compatibility."""

    model_config = ConfigDict(
        populate_by_name=True,  # Allow both alias and field name
    )

    user_id: int = Field(alias="userId")
    user_name: str = Field(alias="userName")
    email_address: str = Field(alias="emailAddress")
    is_verified: bool = Field(default=False, alias="isVerified")

    @field_serializer("user_name")
    def serialize_username(self, value: str) -> str:
        """Always serialize username as lowercase."""
        return value.lower()


class SensitiveData(BaseModel):
    """Model demonstrating selective serialization."""

    username: str
    password: str = Field(exclude=True)  # Never serialize
    api_key: str = Field(repr=False)  # Don't show in repr
    email: str


def main() -> None:
    """Run the serialization example."""
    print("Example 3: Serialization and Parsing")
    print("=" * 50)

    # Create an order
    print("\n1. Creating an order with nested items:")
    order = Order(
        customer_email="customer@example.com",
        items=[
            OrderItem(
                product_name="Laptop",
                quantity=1,
                unit_price=Money(amount=Decimal("999.99")),
            ),
            OrderItem(
                product_name="Mouse",
                quantity=2,
                unit_price=Money(amount=Decimal("29.99")),
            ),
        ],
        notes="Gift wrap please",
        internal_reference="INT-12345",
    )
    print(f"   Order ID: {order.id}")
    print(f"   Item count: {order.item_count}")
    print(f"   Order total: ${order.order_total.amount}")

    # Convert to dict
    print("\n2. Converting to dictionary (model_dump):")
    order_dict = order.model_dump()
    print(f"   Keys: {list(order_dict.keys())}")
    print(f"   'internal_reference' excluded: {'internal_reference' not in order_dict}")

    # Convert to JSON
    print("\n3. Converting to JSON (model_dump_json):")
    order_json = order.model_dump_json(indent=2)
    print(f"   JSON preview:\n{order_json[:200]}...")

    # Selective serialization
    print("\n4. Selective serialization:")
    print(f"   Include only status: {order.model_dump(include={'status'})}")
    print(f"   Exclude items: {list(order.model_dump(exclude={'items'}).keys())}")
    print(f"   Exclude unset: {order.model_dump(exclude_unset=True).keys()}")

    # Serialization modes
    print("\n5. Serialization modes:")
    print(f"   mode='json': {order.model_dump(mode='json')['created_at']}")
    print(f"   mode='python': {type(order.model_dump(mode='python')['created_at'])}")

    # Parsing from dict
    print("\n6. Parsing from dictionary:")
    data = {
        "customer_email": "new@example.com",
        "items": [{"product_name": "Keyboard", "quantity": 1, "unit_price": {"amount": "79.99"}}],
    }
    parsed_order = Order.model_validate(data)
    print(f"   Parsed order total: ${parsed_order.order_total.amount}")

    # Parsing from JSON
    print("\n7. Parsing from JSON:")
    json_data = '{"customer_email": "json@example.com", "items": []}'
    order_from_json = Order.model_validate_json(json_data)
    print(f"   Parsed from JSON: {order_from_json.customer_email}")

    # Alias support
    print("\n8. Alias support (camelCase <-> snake_case):")
    # Create from camelCase (e.g., from JavaScript frontend)
    profile = UserProfile.model_validate(
        {"userId": 123, "userName": "Alice", "emailAddress": "alice@example.com"}
    )
    print(f"   Created from camelCase: {profile.user_name}")

    # Serialize to camelCase
    print(f"   Serialized with aliases: {profile.model_dump(by_alias=True)}")
    # Serialize to snake_case
    print(f"   Serialized without aliases: {profile.model_dump(by_alias=False)}")

    # Sensitive data handling
    print("\n9. Sensitive data exclusion:")
    sensitive = SensitiveData(
        username="alice", password="secret123", api_key="key-abc-123", email="alice@example.com"
    )
    print(f"   repr (api_key hidden): {sensitive}")
    print(f"   dict (password excluded): {sensitive.model_dump()}")

    # Round-trip serialization
    print("\n10. Round-trip serialization:")
    original = order.model_dump()
    recreated = Order.model_validate(original)
    print(f"   Original total: ${order.order_total.amount}")
    print(f"   Recreated total: ${recreated.order_total.amount}")
    print(f"   Totals match: {order.order_total.amount == recreated.order_total.amount}")

    # Copy with modifications
    print("\n11. Creating modified copies:")
    updated_order = order.model_copy(update={"status": OrderStatus.SHIPPED})
    print(f"   Original status: {order.status}")
    print(f"   Updated status: {updated_order.status}")

    # Deep copy for nested modifications
    deep_copy = order.model_copy(deep=True)
    print(f"   Deep copy created: {deep_copy.id == order.id}")

    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
