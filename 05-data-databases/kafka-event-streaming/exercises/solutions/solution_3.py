"""Solution 3: Event-Driven Notification System.

This is the solution for Exercise 3: Design an Event-Driven Notification System.
"""

from __future__ import annotations

import json
import threading
import time
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from confluent_kafka import Consumer, KafkaError, Producer
from pydantic import BaseModel, Field


# ============================================================
# EVENT SCHEMAS
# ============================================================


class UserRegisteredEvent(BaseModel):
    """Event when a new user registers."""

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str = "user.registered"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: str
    email: str
    name: str

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class OrderCompletedEvent(BaseModel):
    """Event when an order is completed."""

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str = "order.completed"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    order_id: str
    customer_id: str
    customer_email: str
    total_amount: float
    items: list[dict[str, Any]]

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class PaymentFailedEvent(BaseModel):
    """Event when a payment fails."""

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str = "payment.failed"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    order_id: str
    customer_id: str
    customer_email: str
    customer_phone: str | None = None
    amount: float
    reason: str

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ============================================================
# NOTIFICATION SCHEMAS
# ============================================================


class NotificationType(str, Enum):
    """Types of notifications."""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class Notification(BaseModel):
    """Notification schema."""

    notification_id: str = Field(default_factory=lambda: str(uuid4()))
    notification_type: NotificationType
    recipient: str
    subject: str
    body: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source_event_id: str

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ============================================================
# NOTIFICATION SERVICE
# ============================================================


class NotificationService:
    """Service that generates notifications from events."""

    def __init__(
        self,
        input_topics: list[str],
        output_topic: str = "notifications",
        group_id: str = "notification-service",
        bootstrap_servers: str = "localhost:9092",
    ) -> None:
        """Initialize the notification service."""
        self.input_topics = input_topics
        self.output_topic = output_topic
        self.notification_count = 0
        self.running = False

        self.consumer = Consumer({
            "bootstrap.servers": bootstrap_servers,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        })
        self.consumer.subscribe(input_topics)

        self.producer = Producer({
            "bootstrap.servers": bootstrap_servers,
        })

    def run(self, duration: float = 30.0) -> int:
        """Run the service for specified duration."""
        self.running = True
        start_time = time.time()
        empty_polls = 0

        try:
            while self.running and (time.time() - start_time) < duration:
                msg = self.consumer.poll(timeout=0.5)

                if msg is None:
                    empty_polls += 1
                    if empty_polls >= 10:
                        break
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        empty_polls += 1
                        continue
                    print(f"  [ERROR] {msg.error()}")
                    continue

                empty_polls = 0

                try:
                    event_data = json.loads(msg.value().decode("utf-8"))
                    notifications = self.process_event(event_data)

                    for notification in notifications:
                        self.send_notification(notification)

                    self.consumer.commit(asynchronous=False)

                except Exception as e:
                    print(f"  [ERROR] Processing failed: {e}")

        finally:
            self.producer.flush()

        return self.notification_count

    def process_event(self, event_data: dict[str, Any]) -> list[Notification]:
        """Process an event and generate notifications."""
        event_type = event_data.get("event_type", "")

        if event_type == "user.registered":
            event = UserRegisteredEvent.model_validate(event_data)
            return self.handle_user_registered(event)

        elif event_type == "order.completed":
            event = OrderCompletedEvent.model_validate(event_data)
            return self.handle_order_completed(event)

        elif event_type == "payment.failed":
            event = PaymentFailedEvent.model_validate(event_data)
            return self.handle_payment_failed(event)

        return []

    def handle_user_registered(
        self, event: UserRegisteredEvent
    ) -> list[Notification]:
        """Handle user registered event."""
        return [
            Notification(
                notification_type=NotificationType.EMAIL,
                recipient=event.email,
                subject="Welcome to Our Platform!",
                body=f"Hi {event.name},\n\nWelcome! We're excited to have you on board.\n\nBest regards,\nThe Team",
                metadata={"user_id": event.user_id},
                source_event_id=event.event_id,
            )
        ]

    def handle_order_completed(
        self, event: OrderCompletedEvent
    ) -> list[Notification]:
        """Handle order completed event."""
        items_text = "\n".join(
            f"  - {item.get('name', 'Item')}: ${item.get('price', 0):.2f}"
            for item in event.items
        )

        return [
            # Email notification
            Notification(
                notification_type=NotificationType.EMAIL,
                recipient=event.customer_email,
                subject=f"Order Confirmed: {event.order_id}",
                body=f"Your order has been confirmed!\n\nOrder ID: {event.order_id}\nTotal: ${event.total_amount:.2f}\n\nItems:\n{items_text}\n\nThank you for your purchase!",
                metadata={"order_id": event.order_id},
                source_event_id=event.event_id,
            ),
            # Push notification
            Notification(
                notification_type=NotificationType.PUSH,
                recipient=event.customer_id,
                subject="Order Confirmed",
                body=f"Your order {event.order_id} for ${event.total_amount:.2f} has been confirmed!",
                metadata={"order_id": event.order_id},
                source_event_id=event.event_id,
            ),
        ]

    def handle_payment_failed(
        self, event: PaymentFailedEvent
    ) -> list[Notification]:
        """Handle payment failed event."""
        notifications = [
            # Email notification
            Notification(
                notification_type=NotificationType.EMAIL,
                recipient=event.customer_email,
                subject=f"Payment Failed for Order {event.order_id}",
                body=f"Unfortunately, your payment of ${event.amount:.2f} could not be processed.\n\nReason: {event.reason}\n\nPlease try again or use a different payment method.\n\nRetry: https://example.com/orders/{event.order_id}/pay",
                metadata={"order_id": event.order_id},
                source_event_id=event.event_id,
            ),
        ]

        # SMS notification if phone available
        if event.customer_phone:
            notifications.append(
                Notification(
                    notification_type=NotificationType.SMS,
                    recipient=event.customer_phone,
                    subject="Payment Failed",
                    body=f"Payment of ${event.amount:.2f} failed for order {event.order_id}. Please retry.",
                    metadata={"order_id": event.order_id},
                    source_event_id=event.event_id,
                )
            )

        return notifications

    def send_notification(self, notification: Notification) -> None:
        """Produce notification to Kafka."""
        self.producer.produce(
            topic=self.output_topic,
            key=notification.recipient.encode("utf-8"),
            value=notification.model_dump_json().encode("utf-8"),
        )
        self.producer.poll(0)
        self.notification_count += 1
        print(f"  [{notification.notification_type.value.upper()}] -> {notification.recipient}: {notification.subject}")

    def close(self) -> None:
        """Close consumer and producer."""
        self.producer.flush()
        self.consumer.close()


def produce_test_events() -> None:
    """Produce test events to appropriate topics."""
    producer = Producer({"bootstrap.servers": "localhost:9092"})

    # User registered event
    user_event = UserRegisteredEvent(
        user_id="user-001",
        email="john@example.com",
        name="John Doe",
    )
    producer.produce(
        topic="user-events",
        key=user_event.user_id.encode("utf-8"),
        value=user_event.model_dump_json().encode("utf-8"),
    )
    print("  Produced: UserRegisteredEvent")

    # Order completed event
    order_event = OrderCompletedEvent(
        order_id="ord-001",
        customer_id="user-001",
        customer_email="john@example.com",
        total_amount=149.97,
        items=[
            {"name": "Widget", "price": 49.99},
            {"name": "Gadget", "price": 99.98},
        ],
    )
    producer.produce(
        topic="order-events",
        key=order_event.order_id.encode("utf-8"),
        value=order_event.model_dump_json().encode("utf-8"),
    )
    print("  Produced: OrderCompletedEvent")

    # Payment failed event
    payment_event = PaymentFailedEvent(
        order_id="ord-002",
        customer_id="user-002",
        customer_email="jane@example.com",
        customer_phone="+1234567890",
        amount=75.00,
        reason="Card declined",
    )
    producer.produce(
        topic="payment-events",
        key=payment_event.order_id.encode("utf-8"),
        value=payment_event.model_dump_json().encode("utf-8"),
    )
    print("  Produced: PaymentFailedEvent")

    producer.flush(timeout=10)


def main() -> None:
    """Demonstrate the notification service."""
    print("Solution 3: Event-Driven Notification System")
    print("=" * 50)

    # Produce test events
    print("\n  Producing test events...")
    produce_test_events()

    # Create and run notification service
    print("\n  Starting notification service...")
    service = NotificationService(
        input_topics=["user-events", "order-events", "payment-events"],
        output_topic="notifications",
        group_id=f"notification-service-{time.time()}",  # Unique for demo
    )

    try:
        time.sleep(1)  # Let events propagate
        notification_count = service.run(duration=10.0)

        print(f"\n  Summary: Generated {notification_count} notifications")
        print("    - 1 email (welcome)")
        print("    - 1 email + 1 push (order confirmation)")
        print("    - 1 email + 1 sms (payment failure)")

    finally:
        service.close()


if __name__ == "__main__":
    main()
