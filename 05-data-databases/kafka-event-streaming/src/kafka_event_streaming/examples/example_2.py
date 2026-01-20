"""Example 2: Event Schemas and Serialization.

This example demonstrates how to use Pydantic models for defining
event schemas with validation and type-safe serialization.

Learning objectives:
- Define event schemas with Pydantic
- Serialize events for Kafka production
- Deserialize events with validation
- Handle schema evolution and versioning

Prerequisites:
- Kafka running on localhost:9092
- Start with: make infra-up (from repository root)
"""

from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from typing import Any

from confluent_kafka import Consumer, KafkaError, Producer
from pydantic import BaseModel, Field, ValidationError, field_validator


# ============================================================
# PART 1: Defining Event Schemas
# ============================================================


class EventType(str, Enum):
    """Event type enumeration."""

    ORDER_CREATED = "order.created"
    ORDER_UPDATED = "order.updated"
    ORDER_SHIPPED = "order.shipped"
    ORDER_DELIVERED = "order.delivered"
    ORDER_CANCELLED = "order.cancelled"


class Address(BaseModel):
    """Shipping address model."""

    street: str
    city: str
    state: str
    postal_code: str
    country: str = "US"


class OrderItem(BaseModel):
    """Order item model with validation."""

    product_id: str
    name: str
    quantity: int = Field(gt=0, description="Must be positive")
    unit_price: float = Field(gt=0, description="Must be positive")

    @property
    def total(self) -> float:
        """Calculate item total."""
        return self.quantity * self.unit_price


class OrderEvent(BaseModel):
    """Order event schema with comprehensive validation.

    This schema demonstrates:
    - Required and optional fields
    - Nested models (Address, OrderItem)
    - Custom validators
    - Computed fields
    - Type constraints
    """

    # Event metadata
    event_id: str = Field(default_factory=lambda: f"evt-{datetime.utcnow().timestamp()}")
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1

    # Order data
    order_id: str
    customer_id: str
    items: list[OrderItem] = Field(min_length=1)
    shipping_address: Address | None = None
    notes: str | None = None

    # Computed on validation
    total_amount: float = 0.0

    @field_validator("total_amount", mode="before")
    @classmethod
    def calculate_total(cls, v: float, info: Any) -> float:
        """Calculate total from items if not provided."""
        if v == 0 and info.data.get("items"):
            return sum(
                item.quantity * item.unit_price
                if isinstance(item, dict)
                else item.total
                for item in info.data["items"]
            )
        return v

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}


# ============================================================
# PART 2: Producing Typed Events
# ============================================================


def produce_typed_events() -> None:
    """Demonstrate producing events with schema validation."""
    print("\n" + "=" * 60)
    print("PART 1: Producing Typed Events")
    print("=" * 60)

    producer = Producer({"bootstrap.servers": "localhost:9092"})
    topic = "order-events"

    # Create valid events
    events = [
        OrderEvent(
            event_type=EventType.ORDER_CREATED,
            order_id="ord-001",
            customer_id="cust-123",
            items=[
                OrderItem(product_id="prod-1", name="Widget", quantity=2, unit_price=9.99),
                OrderItem(product_id="prod-2", name="Gadget", quantity=1, unit_price=24.99),
            ],
            shipping_address=Address(
                street="123 Main St",
                city="Springfield",
                state="IL",
                postal_code="62701",
            ),
        ),
        OrderEvent(
            event_type=EventType.ORDER_SHIPPED,
            order_id="ord-001",
            customer_id="cust-123",
            items=[
                OrderItem(product_id="prod-1", name="Widget", quantity=2, unit_price=9.99),
            ],
            notes="Shipped via FedEx",
        ),
    ]

    print(f"\nProducing {len(events)} events to topic: {topic}\n")

    for event in events:
        # Serialize using Pydantic's JSON serialization
        serialized = event.model_dump_json().encode("utf-8")

        print(f"  Event: {event.event_type.value}")
        print(f"    Order ID: {event.order_id}")
        print(f"    Total: ${event.total_amount:.2f}")
        print(f"    Serialized size: {len(serialized)} bytes")

        producer.produce(
            topic=topic,
            key=event.order_id.encode("utf-8"),
            value=serialized,
        )

    producer.flush(timeout=10)
    print("\n  All events produced successfully!")


# ============================================================
# PART 3: Consuming and Deserializing Events
# ============================================================


def consume_typed_events() -> None:
    """Demonstrate consuming events with schema validation."""
    print("\n" + "=" * 60)
    print("PART 2: Consuming Typed Events")
    print("=" * 60)

    consumer = Consumer({
        "bootstrap.servers": "localhost:9092",
        "group.id": "schema-consumer-group",
        "auto.offset.reset": "earliest",
    })
    topic = "order-events"

    consumer.subscribe([topic])
    print(f"\nConsuming events from topic: {topic}\n")

    message_count = 0
    max_messages = 5
    empty_polls = 0

    try:
        while message_count < max_messages and empty_polls < 5:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                empty_polls += 1
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    empty_polls += 1
                    continue
                raise Exception(msg.error())

            empty_polls = 0
            message_count += 1

            # Deserialize with Pydantic validation
            try:
                event = OrderEvent.model_validate_json(msg.value())

                print(f"  Event {message_count}: {event.event_type.value}")
                print(f"    Event ID: {event.event_id}")
                print(f"    Order: {event.order_id}")
                print(f"    Customer: {event.customer_id}")
                print(f"    Items: {len(event.items)}")
                print(f"    Total: ${event.total_amount:.2f}")
                if event.shipping_address:
                    print(f"    Ship to: {event.shipping_address.city}, {event.shipping_address.state}")
                print()

            except ValidationError as e:
                print(f"  [ERROR] Invalid event: {e}")

    finally:
        consumer.close()
        print(f"  Consumed {message_count} events")


# ============================================================
# PART 4: Schema Validation and Error Handling
# ============================================================


def demonstrate_validation() -> None:
    """Demonstrate schema validation and error handling."""
    print("\n" + "=" * 60)
    print("PART 3: Schema Validation")
    print("=" * 60)

    print("\n  Testing validation rules:\n")

    # Test 1: Missing required fields
    print("  Test 1: Missing required fields")
    try:
        OrderEvent(event_type=EventType.ORDER_CREATED)  # type: ignore
    except ValidationError as e:
        print(f"    [EXPECTED ERROR] {e.error_count()} validation errors")
        for error in e.errors()[:2]:
            print(f"      - {error['loc']}: {error['msg']}")

    # Test 2: Invalid quantity (must be > 0)
    print("\n  Test 2: Invalid quantity")
    try:
        OrderItem(product_id="p1", name="Test", quantity=0, unit_price=10.0)
    except ValidationError as e:
        print(f"    [EXPECTED ERROR] {e.errors()[0]['msg']}")

    # Test 3: Empty items list
    print("\n  Test 3: Empty items list")
    try:
        OrderEvent(
            event_type=EventType.ORDER_CREATED,
            order_id="ord-1",
            customer_id="cust-1",
            items=[],  # min_length=1 violated
        )
    except ValidationError as e:
        print(f"    [EXPECTED ERROR] {e.errors()[0]['msg']}")

    # Test 4: Valid event creation
    print("\n  Test 4: Valid event")
    event = OrderEvent(
        event_type=EventType.ORDER_CREATED,
        order_id="ord-valid",
        customer_id="cust-1",
        items=[OrderItem(product_id="p1", name="Test", quantity=1, unit_price=10.0)],
    )
    print(f"    [SUCCESS] Created event: {event.event_id}")
    print(f"    Total amount: ${event.total_amount:.2f}")


# ============================================================
# PART 5: Schema Evolution
# ============================================================


class OrderEventV2(OrderEvent):
    """Version 2 of OrderEvent with additional fields.

    Demonstrates backward-compatible schema evolution:
    - New optional fields don't break old consumers
    - Default values allow reading old events
    """

    version: int = 2
    priority: str = "normal"  # New field with default
    estimated_delivery: datetime | None = None  # New optional field
    tags: list[str] = Field(default_factory=list)  # New list field


def demonstrate_schema_evolution() -> None:
    """Demonstrate backward-compatible schema evolution."""
    print("\n" + "=" * 60)
    print("PART 4: Schema Evolution")
    print("=" * 60)

    # Old event (V1 format)
    old_event_json = json.dumps({
        "event_type": "order.created",
        "order_id": "ord-old",
        "customer_id": "cust-1",
        "items": [{"product_id": "p1", "name": "Test", "quantity": 1, "unit_price": 10.0}],
    })

    # New event (V2 format)
    new_event = OrderEventV2(
        event_type=EventType.ORDER_CREATED,
        order_id="ord-new",
        customer_id="cust-1",
        items=[OrderItem(product_id="p1", name="Test", quantity=1, unit_price=10.0)],
        priority="high",
        tags=["rush", "vip"],
    )

    print("\n  Reading old V1 event with V2 schema:")
    v2_from_v1 = OrderEventV2.model_validate_json(old_event_json)
    print(f"    Order: {v2_from_v1.order_id}")
    print(f"    Version: {v2_from_v1.version} (uses V2 default)")
    print(f"    Priority: {v2_from_v1.priority} (uses default)")
    print(f"    Tags: {v2_from_v1.tags} (uses default)")

    print("\n  Reading new V2 event with V1 schema:")
    v1_from_v2 = OrderEvent.model_validate_json(new_event.model_dump_json())
    print(f"    Order: {v1_from_v2.order_id}")
    print(f"    [OK] V1 consumer ignores unknown fields (priority, tags)")


def main() -> None:
    """Run all examples."""
    print("\n" + "#" * 60)
    print("# Example 2: Event Schemas and Serialization")
    print("#" * 60)

    try:
        produce_typed_events()
        consume_typed_events()
        demonstrate_validation()
        demonstrate_schema_evolution()

        print("\n" + "=" * 60)
        print("Example completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Example failed: {e}")
        print("\nMake sure Kafka is running:")
        print("  cd ../../.. && make infra-up")
        raise


if __name__ == "__main__":
    main()
