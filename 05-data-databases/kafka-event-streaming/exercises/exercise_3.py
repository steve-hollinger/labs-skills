"""Exercise 3: Design an Event-Driven Notification System.

In this exercise, you will design and implement an event-driven
notification system that sends notifications based on various events.

Requirements:
1. Create event schemas for:
   - UserRegisteredEvent
   - OrderCompletedEvent
   - PaymentFailedEvent

2. Create a NotificationService that:
   - Consumes from multiple event topics
   - Routes events to appropriate handlers
   - Generates notifications based on event type
   - Produces notification events

3. Create notification types:
   - EmailNotification
   - SMSNotification
   - PushNotification

4. Implement notification routing logic:
   - UserRegistered -> Email welcome message
   - OrderCompleted -> Email + Push confirmation
   - PaymentFailed -> Email + SMS alert

Run with: python exercises/exercise_3.py
Test with: pytest tests/test_exercises.py -k exercise_3
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

# TODO: Implement the following


# ============================================================
# EVENT SCHEMAS
# ============================================================


class UserRegisteredEvent(BaseModel):
    """Event when a new user registers.

    TODO: Add fields:
    - event_id: str
    - event_type: str = "user.registered"
    - timestamp: datetime
    - user_id: str
    - email: str
    - name: str
    """

    pass


class OrderCompletedEvent(BaseModel):
    """Event when an order is completed.

    TODO: Add fields:
    - event_id: str
    - event_type: str = "order.completed"
    - timestamp: datetime
    - order_id: str
    - customer_id: str
    - customer_email: str
    - total_amount: float
    - items: list[dict]
    """

    pass


class PaymentFailedEvent(BaseModel):
    """Event when a payment fails.

    TODO: Add fields:
    - event_id: str
    - event_type: str = "payment.failed"
    - timestamp: datetime
    - order_id: str
    - customer_id: str
    - customer_email: str
    - customer_phone: str | None
    - amount: float
    - reason: str
    """

    pass


# ============================================================
# NOTIFICATION SCHEMAS
# ============================================================


class NotificationType(str, Enum):
    """Types of notifications."""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class Notification(BaseModel):
    """Base notification schema.

    TODO: Add fields:
    - notification_id: str
    - notification_type: NotificationType
    - recipient: str
    - subject: str
    - body: str
    - metadata: dict
    - created_at: datetime
    - source_event_id: str
    """

    pass


# ============================================================
# NOTIFICATION SERVICE
# ============================================================


class NotificationService:
    """Service that generates notifications from events.

    TODO: Implement methods:
    - __init__(self, input_topics, output_topic, group_id, bootstrap_servers)
    - run(self, duration)
    - process_event(self, event_data)
    - handle_user_registered(self, event)
    - handle_order_completed(self, event)
    - handle_payment_failed(self, event)
    - send_notification(self, notification)
    - close(self)
    """

    def __init__(
        self,
        input_topics: list[str],
        output_topic: str = "notifications",
        group_id: str = "notification-service",
        bootstrap_servers: str = "localhost:9092",
    ) -> None:
        """Initialize the notification service.

        TODO:
        1. Create Consumer subscribed to input_topics
        2. Create Producer for output_topic
        3. Store configuration
        4. Initialize notification count
        """
        pass

    def run(self, duration: float = 30.0) -> int:
        """Run the service for specified duration.

        TODO:
        1. Poll for messages
        2. Route to appropriate handler based on event_type
        3. Return total notifications sent
        """
        pass

    def process_event(self, event_data: dict[str, Any]) -> list[Notification]:
        """Process an event and generate notifications.

        TODO:
        1. Determine event type
        2. Call appropriate handler
        3. Return list of notifications generated
        """
        pass

    def handle_user_registered(
        self, event: UserRegisteredEvent
    ) -> list[Notification]:
        """Handle user registered event.

        TODO: Generate email welcome notification
        - Subject: "Welcome to Our Platform!"
        - Body: Include user's name
        """
        pass

    def handle_order_completed(
        self, event: OrderCompletedEvent
    ) -> list[Notification]:
        """Handle order completed event.

        TODO: Generate email AND push notifications
        - Email: Order confirmation with details
        - Push: Brief order confirmation
        """
        pass

    def handle_payment_failed(
        self, event: PaymentFailedEvent
    ) -> list[Notification]:
        """Handle payment failed event.

        TODO: Generate email AND SMS notifications
        - Email: Payment failure details with retry link
        - SMS: Brief alert (if phone available)
        """
        pass

    def send_notification(self, notification: Notification) -> None:
        """Produce notification to Kafka.

        TODO:
        1. Serialize notification
        2. Produce to output topic
        3. Use recipient as key
        """
        pass

    def close(self) -> None:
        """Close consumer and producer."""
        pass


def main() -> None:
    """Demonstrate the notification service."""
    print("Exercise 3: Event-Driven Notification System")
    print("=" * 50)

    # TODO: Implement the demonstration
    #
    # 1. Produce test events to appropriate topics:
    #    - UserRegisteredEvent to "user-events"
    #    - OrderCompletedEvent to "order-events"
    #    - PaymentFailedEvent to "payment-events"
    #
    # 2. Create NotificationService
    #
    # 3. Run service for a short duration
    #
    # 4. Consume from "notifications" topic and print results
    #
    # Expected output:
    # - 1 email notification for user registration
    # - 2 notifications (email + push) for order completion
    # - 2 notifications (email + sms) for payment failure

    print("\nNot implemented yet. See TODO comments.")


if __name__ == "__main__":
    main()
