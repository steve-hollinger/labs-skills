"""Event schemas for Kafka messages."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class BaseEvent(BaseModel):
    """Base class for all events.

    Provides common fields and serialization logic for Kafka events.
    All events should inherit from this class.

    Example:
        >>> class MyEvent(BaseEvent):
        ...     event_type: str = "my.event"
        ...     data: dict
    """

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}

    def to_kafka_value(self) -> bytes:
        """Serialize for Kafka production."""
        return self.model_dump_json().encode("utf-8")

    @classmethod
    def from_kafka_value(cls, data: bytes) -> BaseEvent:
        """Deserialize from Kafka consumption."""
        return cls.model_validate_json(data)


class OrderStatus(str, Enum):
    """Order status enumeration."""

    CREATED = "created"
    CONFIRMED = "confirmed"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItem(BaseModel):
    """Item within an order."""

    product_id: str
    product_name: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)

    @property
    def total_price(self) -> float:
        """Calculate total price for this item."""
        return self.quantity * self.unit_price


class OrderEvent(BaseEvent):
    """Event for order-related actions.

    Example:
        >>> event = OrderEvent(
        ...     event_type="order.created",
        ...     order_id="ord-123",
        ...     customer_id="cust-456",
        ...     status=OrderStatus.CREATED,
        ...     items=[OrderItem(
        ...         product_id="prod-1",
        ...         product_name="Widget",
        ...         quantity=2,
        ...         unit_price=9.99
        ...     )]
        ... )
    """

    event_type: str = Field(..., pattern=r"^order\.")
    order_id: str
    customer_id: str
    status: OrderStatus
    items: list[OrderItem] = Field(default_factory=list)
    total_amount: float = Field(default=0.0, ge=0)
    shipping_address: str | None = None
    notes: str | None = None

    @field_validator("total_amount", mode="before")
    @classmethod
    def calculate_total(cls, v: float, info: Any) -> float:
        """Calculate total from items if not provided."""
        if v == 0 and "items" in info.data:
            items = info.data["items"]
            if items:
                return sum(
                    item.total_price if isinstance(item, OrderItem) else item["quantity"] * item["unit_price"]
                    for item in items
                )
        return v


class UserEventType(str, Enum):
    """User event types."""

    CREATED = "user.created"
    UPDATED = "user.updated"
    DELETED = "user.deleted"
    LOGIN = "user.login"
    LOGOUT = "user.logout"
    PASSWORD_CHANGED = "user.password_changed"


class UserEvent(BaseEvent):
    """Event for user-related actions.

    Example:
        >>> event = UserEvent(
        ...     event_type=UserEventType.CREATED,
        ...     user_id="user-123",
        ...     email="user@example.com"
        ... )
    """

    event_type: UserEventType
    user_id: str
    email: str | None = None
    username: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    changes: dict[str, Any] = Field(default_factory=dict)


class PaymentStatus(str, Enum):
    """Payment status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentEvent(BaseEvent):
    """Event for payment-related actions.

    Example:
        >>> event = PaymentEvent(
        ...     event_type="payment.completed",
        ...     payment_id="pay-123",
        ...     order_id="ord-456",
        ...     amount=99.99,
        ...     currency="USD",
        ...     status=PaymentStatus.COMPLETED
        ... )
    """

    event_type: str = Field(..., pattern=r"^payment\.")
    payment_id: str
    order_id: str
    amount: float = Field(gt=0)
    currency: str = "USD"
    status: PaymentStatus
    payment_method: str | None = None
    transaction_id: str | None = None
    error_message: str | None = None


class InventoryEvent(BaseEvent):
    """Event for inventory-related actions.

    Example:
        >>> event = InventoryEvent(
        ...     event_type="inventory.reserved",
        ...     product_id="prod-123",
        ...     quantity_change=-5,
        ...     order_id="ord-456"
        ... )
    """

    event_type: str = Field(..., pattern=r"^inventory\.")
    product_id: str
    warehouse_id: str | None = None
    quantity_change: int
    current_quantity: int | None = None
    order_id: str | None = None
    reason: str | None = None


# Event type registry for deserialization
EVENT_TYPES: dict[str, type[BaseEvent]] = {
    "order": OrderEvent,
    "user": UserEvent,
    "payment": PaymentEvent,
    "inventory": InventoryEvent,
}


def deserialize_event(data: bytes) -> BaseEvent:
    """Deserialize an event based on its type.

    Args:
        data: Raw event bytes.

    Returns:
        Appropriate event instance.

    Example:
        >>> data = b'{"event_type": "order.created", "order_id": "123", ...}'
        >>> event = deserialize_event(data)
        >>> isinstance(event, OrderEvent)
        True
    """
    import json

    parsed = json.loads(data)
    event_type = parsed.get("event_type", "")

    # Get event class from prefix
    prefix = event_type.split(".")[0] if "." in event_type else event_type
    event_class = EVENT_TYPES.get(prefix, BaseEvent)

    return event_class.model_validate(parsed)
