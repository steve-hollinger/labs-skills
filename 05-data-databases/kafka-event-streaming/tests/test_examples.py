"""Tests for Kafka Event Streaming examples.

These tests verify the schemas and utilities work correctly.
Integration tests require a running Kafka instance.
"""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from kafka_event_streaming.schemas import (
    BaseEvent,
    OrderEvent,
    OrderItem,
    OrderStatus,
    PaymentEvent,
    PaymentStatus,
    UserEvent,
    UserEventType,
    deserialize_event,
)


class TestBaseEvent:
    """Tests for BaseEvent schema."""

    def test_base_event_creation(self) -> None:
        """Test creating a base event."""
        event = BaseEvent(event_type="test.event")

        assert event.event_type == "test.event"
        assert event.event_id is not None
        assert event.timestamp is not None
        assert event.version == 1

    def test_base_event_serialization(self) -> None:
        """Test serializing base event to Kafka value."""
        event = BaseEvent(event_type="test.event")
        value = event.to_kafka_value()

        assert isinstance(value, bytes)
        assert b"test.event" in value

    def test_base_event_deserialization(self) -> None:
        """Test deserializing base event from Kafka value."""
        event = BaseEvent(event_type="test.event")
        value = event.to_kafka_value()

        restored = BaseEvent.from_kafka_value(value)

        assert restored.event_type == event.event_type
        assert restored.event_id == event.event_id


class TestOrderEvent:
    """Tests for OrderEvent schema."""

    def test_order_item_creation(self) -> None:
        """Test creating an order item."""
        item = OrderItem(
            product_id="prod-1",
            product_name="Widget",
            quantity=2,
            unit_price=9.99,
        )

        assert item.product_id == "prod-1"
        assert item.total_price == pytest.approx(19.98)

    def test_order_item_validation(self) -> None:
        """Test order item validation."""
        # Quantity must be positive
        with pytest.raises(ValidationError):
            OrderItem(
                product_id="prod-1",
                product_name="Widget",
                quantity=0,
                unit_price=9.99,
            )

        # Price must be positive
        with pytest.raises(ValidationError):
            OrderItem(
                product_id="prod-1",
                product_name="Widget",
                quantity=1,
                unit_price=-5.0,
            )

    def test_order_event_creation(self) -> None:
        """Test creating an order event."""
        event = OrderEvent(
            event_type="order.created",
            order_id="ord-123",
            customer_id="cust-456",
            status=OrderStatus.CREATED,
            items=[
                OrderItem(
                    product_id="prod-1",
                    product_name="Widget",
                    quantity=2,
                    unit_price=10.0,
                )
            ],
        )

        assert event.order_id == "ord-123"
        assert event.status == OrderStatus.CREATED
        assert len(event.items) == 1

    def test_order_event_type_validation(self) -> None:
        """Test order event type must start with 'order.'."""
        with pytest.raises(ValidationError):
            OrderEvent(
                event_type="invalid.type",
                order_id="ord-123",
                customer_id="cust-456",
                status=OrderStatus.CREATED,
                items=[],
            )

    def test_order_event_serialization(self) -> None:
        """Test order event serialization round-trip."""
        event = OrderEvent(
            event_type="order.created",
            order_id="ord-123",
            customer_id="cust-456",
            status=OrderStatus.CREATED,
            items=[
                OrderItem(
                    product_id="prod-1",
                    product_name="Widget",
                    quantity=2,
                    unit_price=10.0,
                )
            ],
        )

        json_str = event.model_dump_json()
        restored = OrderEvent.model_validate_json(json_str)

        assert restored.order_id == event.order_id
        assert restored.status == event.status


class TestUserEvent:
    """Tests for UserEvent schema."""

    def test_user_event_creation(self) -> None:
        """Test creating a user event."""
        event = UserEvent(
            event_type=UserEventType.CREATED,
            user_id="user-123",
            email="user@example.com",
        )

        assert event.user_id == "user-123"
        assert event.email == "user@example.com"

    def test_user_event_types(self) -> None:
        """Test different user event types."""
        for event_type in UserEventType:
            event = UserEvent(
                event_type=event_type,
                user_id="user-123",
            )
            assert event.event_type == event_type


class TestPaymentEvent:
    """Tests for PaymentEvent schema."""

    def test_payment_event_creation(self) -> None:
        """Test creating a payment event."""
        event = PaymentEvent(
            event_type="payment.completed",
            payment_id="pay-123",
            order_id="ord-456",
            amount=99.99,
            status=PaymentStatus.COMPLETED,
        )

        assert event.payment_id == "pay-123"
        assert event.amount == pytest.approx(99.99)
        assert event.status == PaymentStatus.COMPLETED

    def test_payment_event_amount_validation(self) -> None:
        """Test payment amount must be positive."""
        with pytest.raises(ValidationError):
            PaymentEvent(
                event_type="payment.completed",
                payment_id="pay-123",
                order_id="ord-456",
                amount=0,
                status=PaymentStatus.COMPLETED,
            )


class TestEventDeserialization:
    """Tests for event deserialization utility."""

    def test_deserialize_order_event(self) -> None:
        """Test deserializing order event."""
        event = OrderEvent(
            event_type="order.created",
            order_id="ord-123",
            customer_id="cust-456",
            status=OrderStatus.CREATED,
            items=[],
        )

        data = event.to_kafka_value()
        restored = deserialize_event(data)

        assert isinstance(restored, OrderEvent)
        assert restored.order_id == "ord-123"

    def test_deserialize_user_event(self) -> None:
        """Test deserializing user event."""
        event = UserEvent(
            event_type=UserEventType.LOGIN,
            user_id="user-123",
        )

        data = event.to_kafka_value()
        restored = deserialize_event(data)

        assert isinstance(restored, UserEvent)
        assert restored.user_id == "user-123"

    def test_deserialize_unknown_event(self) -> None:
        """Test deserializing unknown event type falls back to BaseEvent."""
        data = b'{"event_type": "unknown.event", "event_id": "123"}'
        event = deserialize_event(data)

        assert isinstance(event, BaseEvent)
        assert event.event_type == "unknown.event"


# ============================================================
# Integration Tests (require Kafka)
# ============================================================


@pytest.mark.integration
class TestKafkaIntegration:
    """Integration tests requiring Kafka."""

    def test_producer_consumer_roundtrip(self) -> None:
        """Test producing and consuming a message."""
        pytest.skip("Requires running Kafka instance")

    def test_consumer_group_assignment(self) -> None:
        """Test consumer group partition assignment."""
        pytest.skip("Requires running Kafka instance")
