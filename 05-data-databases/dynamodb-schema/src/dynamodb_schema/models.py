"""Pydantic models for DynamoDB entities.

These models provide type-safe representations of DynamoDB items with
automatic key generation for single-table design patterns.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def generate_id() -> str:
    """Generate a unique identifier."""
    return str(uuid4())


def current_timestamp() -> str:
    """Generate current UTC timestamp in ISO format."""
    return datetime.utcnow().isoformat() + "Z"


class BaseEntity(BaseModel):
    """Base class for all DynamoDB entities with common key patterns."""

    entity_type: str = Field(..., description="Type of entity (USER, ORDER, etc.)")
    created_at: str = Field(default_factory=current_timestamp)
    updated_at: str = Field(default_factory=current_timestamp)

    def get_pk(self) -> str:
        """Get the partition key for this entity."""
        raise NotImplementedError("Subclasses must implement get_pk()")

    def get_sk(self) -> str:
        """Get the sort key for this entity."""
        raise NotImplementedError("Subclasses must implement get_sk()")

    def to_dynamodb_item(self) -> dict[str, Any]:
        """Convert to DynamoDB item format with PK and SK."""
        item = self.model_dump()
        item["PK"] = self.get_pk()
        item["SK"] = self.get_sk()
        return item


class User(BaseEntity):
    """User entity for single-table design."""

    entity_type: str = "USER"
    user_id: str = Field(default_factory=generate_id)
    email: str
    name: str
    status: str = "active"

    def get_pk(self) -> str:
        """User partition key."""
        return f"USER#{self.user_id}"

    def get_sk(self) -> str:
        """User sort key (profile)."""
        return f"PROFILE#{self.user_id}"

    def get_gsi1_pk(self) -> str:
        """GSI1 partition key for email lookup."""
        return f"EMAIL#{self.email}"

    def get_gsi1_sk(self) -> str:
        """GSI1 sort key."""
        return f"USER#{self.user_id}"

    def to_dynamodb_item(self) -> dict[str, Any]:
        """Convert to DynamoDB item with GSI attributes."""
        item = super().to_dynamodb_item()
        item["GSI1PK"] = self.get_gsi1_pk()
        item["GSI1SK"] = self.get_gsi1_sk()
        return item


class Product(BaseEntity):
    """Product entity for e-commerce schema."""

    entity_type: str = "PRODUCT"
    product_id: str = Field(default_factory=generate_id)
    name: str
    description: str = ""
    price: Decimal
    category: str
    inventory_count: int = 0

    def get_pk(self) -> str:
        """Product partition key."""
        return f"PRODUCT#{self.product_id}"

    def get_sk(self) -> str:
        """Product sort key."""
        return f"PRODUCT#{self.product_id}"

    def get_gsi1_pk(self) -> str:
        """GSI1 for category queries."""
        return f"CATEGORY#{self.category}"

    def get_gsi1_sk(self) -> str:
        """GSI1 sort key for category queries."""
        return f"PRODUCT#{self.product_id}"

    def to_dynamodb_item(self) -> dict[str, Any]:
        """Convert to DynamoDB item with GSI attributes."""
        item = super().to_dynamodb_item()
        item["GSI1PK"] = self.get_gsi1_pk()
        item["GSI1SK"] = self.get_gsi1_sk()
        # Convert Decimal for DynamoDB
        item["price"] = str(self.price)
        return item


class OrderItem(BaseModel):
    """Line item within an order."""

    product_id: str
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class Order(BaseEntity):
    """Order entity for single-table design."""

    entity_type: str = "ORDER"
    order_id: str = Field(default_factory=generate_id)
    user_id: str
    items: list[OrderItem] = []
    total: Decimal
    status: str = "pending"
    shipping_address: str = ""

    def get_pk(self) -> str:
        """Order partition key - stored under user for adjacency pattern."""
        return f"USER#{self.user_id}"

    def get_sk(self) -> str:
        """Order sort key with date for range queries."""
        return f"ORDER#{self.created_at}#{self.order_id}"

    def get_order_pk(self) -> str:
        """Direct order lookup partition key."""
        return f"ORDER#{self.order_id}"

    def get_gsi1_pk(self) -> str:
        """GSI1 for status-based queries."""
        return f"STATUS#{self.status}"

    def get_gsi1_sk(self) -> str:
        """GSI1 sort key for date ordering within status."""
        return f"ORDER#{self.created_at}#{self.order_id}"

    def get_gsi2_pk(self) -> str:
        """GSI2 for direct order lookup."""
        return f"ORDER#{self.order_id}"

    def get_gsi2_sk(self) -> str:
        """GSI2 sort key."""
        return f"ORDER#{self.order_id}"

    def to_dynamodb_item(self) -> dict[str, Any]:
        """Convert to DynamoDB item with GSI attributes."""
        item = super().to_dynamodb_item()
        item["GSI1PK"] = self.get_gsi1_pk()
        item["GSI1SK"] = self.get_gsi1_sk()
        item["GSI2PK"] = self.get_gsi2_pk()
        item["GSI2SK"] = self.get_gsi2_sk()
        # Convert Decimal for DynamoDB
        item["total"] = str(self.total)
        # Serialize order items
        item["items"] = [
            {
                "product_id": oi.product_id,
                "product_name": oi.product_name,
                "quantity": oi.quantity,
                "unit_price": str(oi.unit_price),
                "subtotal": str(oi.subtotal),
            }
            for oi in self.items
        ]
        return item
