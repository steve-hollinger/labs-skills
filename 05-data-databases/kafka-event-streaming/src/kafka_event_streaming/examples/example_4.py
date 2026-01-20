"""Example 4: Event-Driven Order Processing System.

This example demonstrates a complete event-driven system with multiple
services communicating via Kafka. It implements the Saga pattern for
distributed transactions.

Learning objectives:
- Design event-driven microservices
- Implement the Saga pattern with choreography
- Handle failures and compensating transactions
- Build resilient event-driven systems

Prerequisites:
- Kafka running on localhost:9092
- Start with: make infra-up (from repository root)
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from confluent_kafka import Consumer, KafkaError, Producer
from pydantic import BaseModel, Field


# ============================================================
# EVENT SCHEMAS
# ============================================================


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAYMENT_PROCESSING = "payment_processing"
    PAID = "paid"
    INVENTORY_RESERVED = "inventory_reserved"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"
    FAILED = "failed"


class BaseEvent(BaseModel):
    """Base event with common fields."""

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: str = ""  # Links related events

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# Order Events
class OrderCreatedEvent(BaseEvent):
    event_type: str = "order.created"
    order_id: str
    customer_id: str
    items: list[dict[str, Any]]
    total_amount: float


class OrderStatusChangedEvent(BaseEvent):
    event_type: str = "order.status_changed"
    order_id: str
    old_status: OrderStatus
    new_status: OrderStatus
    reason: str = ""


# Payment Events
class PaymentRequestedEvent(BaseEvent):
    event_type: str = "payment.requested"
    order_id: str
    customer_id: str
    amount: float


class PaymentCompletedEvent(BaseEvent):
    event_type: str = "payment.completed"
    order_id: str
    payment_id: str
    amount: float


class PaymentFailedEvent(BaseEvent):
    event_type: str = "payment.failed"
    order_id: str
    reason: str


# Inventory Events
class InventoryReservationRequestedEvent(BaseEvent):
    event_type: str = "inventory.reservation_requested"
    order_id: str
    items: list[dict[str, Any]]


class InventoryReservedEvent(BaseEvent):
    event_type: str = "inventory.reserved"
    order_id: str
    reservation_id: str


class InventoryReservationFailedEvent(BaseEvent):
    event_type: str = "inventory.reservation_failed"
    order_id: str
    reason: str


# ============================================================
# SERVICES
# ============================================================


@dataclass
class ServiceStats:
    """Track service statistics."""

    name: str
    events_processed: int = 0
    events_published: int = 0
    errors: int = 0


class BaseService:
    """Base class for event-driven services."""

    def __init__(
        self,
        name: str,
        input_topics: list[str],
        output_topics: list[str],
        group_id: str,
    ):
        self.name = name
        self.stats = ServiceStats(name=name)
        self.input_topics = input_topics
        self.output_topics = output_topics
        self.running = False

        self.consumer = Consumer({
            "bootstrap.servers": "localhost:9092",
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        })
        self.producer = Producer({"bootstrap.servers": "localhost:9092"})

    def publish(self, topic: str, event: BaseEvent) -> None:
        """Publish an event to a topic."""
        self.producer.produce(
            topic=topic,
            key=event.correlation_id.encode("utf-8"),
            value=event.model_dump_json().encode("utf-8"),
        )
        self.producer.poll(0)
        self.stats.events_published += 1
        print(f"    [{self.name}] Published: {event.event_type}")

    def process_event(self, event_data: dict[str, Any]) -> None:
        """Process an event. Override in subclasses."""
        raise NotImplementedError

    def run(self, duration: float = 10.0) -> None:
        """Run the service for a specified duration."""
        self.consumer.subscribe(self.input_topics)
        self.running = True
        start_time = time.time()

        try:
            while self.running and (time.time() - start_time) < duration:
                msg = self.consumer.poll(timeout=0.5)

                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    self.stats.errors += 1
                    continue

                try:
                    event_data = json.loads(msg.value().decode("utf-8"))
                    self.process_event(event_data)
                    self.consumer.commit(asynchronous=False)
                    self.stats.events_processed += 1
                except Exception as e:
                    print(f"    [{self.name}] Error: {e}")
                    self.stats.errors += 1

        finally:
            self.producer.flush()
            self.consumer.close()

    def stop(self) -> None:
        """Stop the service."""
        self.running = False


class OrderService(BaseService):
    """Manages orders and orchestrates the order saga."""

    def __init__(self) -> None:
        super().__init__(
            name="OrderService",
            input_topics=["payment-events", "inventory-events"],
            output_topics=["order-events"],
            group_id="order-service",
        )
        self.orders: dict[str, dict[str, Any]] = {}

    def create_order(
        self,
        customer_id: str,
        items: list[dict[str, Any]],
        total_amount: float,
    ) -> str:
        """Create a new order and start the saga."""
        order_id = f"ord-{uuid4().hex[:8]}"
        correlation_id = f"saga-{uuid4().hex[:8]}"

        self.orders[order_id] = {
            "status": OrderStatus.PENDING,
            "customer_id": customer_id,
            "items": items,
            "total_amount": total_amount,
            "correlation_id": correlation_id,
        }

        # Publish order created event
        event = OrderCreatedEvent(
            correlation_id=correlation_id,
            order_id=order_id,
            customer_id=customer_id,
            items=items,
            total_amount=total_amount,
        )
        self.publish("order-events", event)

        print(f"    [{self.name}] Created order: {order_id}")
        return order_id

    def process_event(self, event_data: dict[str, Any]) -> None:
        """Process payment and inventory events."""
        event_type = event_data.get("event_type", "")
        order_id = event_data.get("order_id", "")

        if order_id not in self.orders:
            return

        order = self.orders[order_id]
        old_status = order["status"]

        if event_type == "payment.completed":
            order["status"] = OrderStatus.PAID
            print(f"    [{self.name}] Order {order_id}: Payment completed")

            # Request inventory reservation
            inv_event = InventoryReservationRequestedEvent(
                correlation_id=order["correlation_id"],
                order_id=order_id,
                items=order["items"],
            )
            self.publish("inventory-events", inv_event)

        elif event_type == "payment.failed":
            order["status"] = OrderStatus.FAILED
            print(f"    [{self.name}] Order {order_id}: Payment failed - {event_data.get('reason')}")

        elif event_type == "inventory.reserved":
            order["status"] = OrderStatus.INVENTORY_RESERVED
            print(f"    [{self.name}] Order {order_id}: Inventory reserved")

        elif event_type == "inventory.reservation_failed":
            order["status"] = OrderStatus.FAILED
            print(f"    [{self.name}] Order {order_id}: Inventory failed - {event_data.get('reason')}")

            # Compensate: Refund payment
            print(f"    [{self.name}] Order {order_id}: Initiating refund (compensation)")

        # Publish status change
        if old_status != order["status"]:
            status_event = OrderStatusChangedEvent(
                correlation_id=order["correlation_id"],
                order_id=order_id,
                old_status=old_status,
                new_status=order["status"],
            )
            self.publish("order-events", status_event)


class PaymentService(BaseService):
    """Processes payments for orders."""

    def __init__(self, failure_rate: float = 0.0):
        super().__init__(
            name="PaymentService",
            input_topics=["order-events"],
            output_topics=["payment-events"],
            group_id="payment-service",
        )
        self.failure_rate = failure_rate
        self.processed_orders: set[str] = set()

    def process_event(self, event_data: dict[str, Any]) -> None:
        """Process order created events."""
        event_type = event_data.get("event_type", "")

        if event_type != "order.created":
            return

        order_id = event_data["order_id"]

        # Idempotency check
        if order_id in self.processed_orders:
            return
        self.processed_orders.add(order_id)

        correlation_id = event_data.get("correlation_id", "")
        amount = event_data["total_amount"]

        print(f"    [{self.name}] Processing payment for order {order_id}: ${amount:.2f}")

        # Simulate processing time
        time.sleep(0.1)

        # Simulate occasional failures
        import random

        if random.random() < self.failure_rate:
            event = PaymentFailedEvent(
                correlation_id=correlation_id,
                order_id=order_id,
                reason="Insufficient funds",
            )
        else:
            event = PaymentCompletedEvent(
                correlation_id=correlation_id,
                order_id=order_id,
                payment_id=f"pay-{uuid4().hex[:8]}",
                amount=amount,
            )

        self.publish("payment-events", event)


class InventoryService(BaseService):
    """Manages inventory reservations."""

    def __init__(self, failure_rate: float = 0.0):
        super().__init__(
            name="InventoryService",
            input_topics=["inventory-events"],
            output_topics=["inventory-events"],
            group_id="inventory-service",
        )
        self.failure_rate = failure_rate
        self.inventory: dict[str, int] = {
            "prod-001": 100,
            "prod-002": 50,
            "prod-003": 25,
        }
        self.reservations: dict[str, list[dict[str, Any]]] = {}

    def process_event(self, event_data: dict[str, Any]) -> None:
        """Process inventory reservation requests."""
        event_type = event_data.get("event_type", "")

        if event_type != "inventory.reservation_requested":
            return

        order_id = event_data["order_id"]
        correlation_id = event_data.get("correlation_id", "")
        items = event_data["items"]

        print(f"    [{self.name}] Reserving inventory for order {order_id}")

        # Check availability
        can_reserve = True
        for item in items:
            product_id = item["product_id"]
            quantity = item["quantity"]
            available = self.inventory.get(product_id, 0)

            if available < quantity:
                can_reserve = False
                break

        # Simulate occasional failures
        import random

        if random.random() < self.failure_rate:
            can_reserve = False

        if can_reserve:
            # Reserve inventory
            for item in items:
                product_id = item["product_id"]
                quantity = item["quantity"]
                self.inventory[product_id] -= quantity

            reservation_id = f"res-{uuid4().hex[:8]}"
            self.reservations[reservation_id] = items

            event = InventoryReservedEvent(
                correlation_id=correlation_id,
                order_id=order_id,
                reservation_id=reservation_id,
            )
        else:
            event = InventoryReservationFailedEvent(
                correlation_id=correlation_id,
                order_id=order_id,
                reason="Insufficient inventory",
            )

        self.publish("inventory-events", event)


# ============================================================
# DEMONSTRATION
# ============================================================


def run_event_driven_demo() -> None:
    """Run the complete event-driven order processing demo."""
    print("\n" + "=" * 60)
    print("Event-Driven Order Processing System")
    print("=" * 60)

    print("\n  Architecture:")
    print("  +------------+     +----------------+     +-----------------+")
    print("  |   Order    | --> |    Payment     | --> |    Inventory    |")
    print("  |  Service   | <-- |    Service     | <-- |    Service      |")
    print("  +------------+     +----------------+     +-----------------+")
    print("       |                    |                      |")
    print("       v                    v                      v")
    print("  [order-events]    [payment-events]      [inventory-events]")

    # Create services
    order_service = OrderService()
    payment_service = PaymentService(failure_rate=0.0)  # No failures for demo
    inventory_service = InventoryService(failure_rate=0.0)

    # Start services in threads
    threads = [
        threading.Thread(target=payment_service.run, args=(8.0,), name="PaymentService"),
        threading.Thread(target=inventory_service.run, args=(8.0,), name="InventoryService"),
        threading.Thread(target=order_service.run, args=(8.0,), name="OrderService"),
    ]

    print("\n  Starting services...")
    for t in threads:
        t.start()
        time.sleep(0.5)  # Stagger starts

    # Create orders
    print("\n  Creating orders...")
    time.sleep(1)  # Let services initialize

    orders = [
        {
            "customer_id": "cust-001",
            "items": [
                {"product_id": "prod-001", "name": "Widget", "quantity": 2, "price": 9.99},
                {"product_id": "prod-002", "name": "Gadget", "quantity": 1, "price": 24.99},
            ],
            "total_amount": 44.97,
        },
        {
            "customer_id": "cust-002",
            "items": [
                {"product_id": "prod-003", "name": "Gizmo", "quantity": 3, "price": 15.00},
            ],
            "total_amount": 45.00,
        },
    ]

    order_ids = []
    for order_data in orders:
        order_id = order_service.create_order(
            customer_id=order_data["customer_id"],
            items=order_data["items"],
            total_amount=order_data["total_amount"],
        )
        order_ids.append(order_id)
        time.sleep(0.5)

    # Wait for processing
    print("\n  Processing orders...")
    for t in threads:
        t.join()

    # Print results
    print("\n  Final Order States:")
    for order_id in order_ids:
        if order_id in order_service.orders:
            order = order_service.orders[order_id]
            print(f"    {order_id}: {order['status'].value}")

    print("\n  Service Statistics:")
    for service in [order_service, payment_service, inventory_service]:
        print(f"    {service.name}:")
        print(f"      Events processed: {service.stats.events_processed}")
        print(f"      Events published: {service.stats.events_published}")
        print(f"      Errors: {service.stats.errors}")


def main() -> None:
    """Run all examples."""
    print("\n" + "#" * 60)
    print("# Example 4: Event-Driven Order Processing")
    print("#" * 60)

    try:
        run_event_driven_demo()

        print("\n" + "=" * 60)
        print("Example completed successfully!")
        print("=" * 60)

        print("\n  Key Takeaways:")
        print("  - Services communicate only through events")
        print("  - Each service handles its own domain")
        print("  - Saga pattern coordinates distributed transactions")
        print("  - Compensation handles failures gracefully")

    except Exception as e:
        print(f"\n[ERROR] Example failed: {e}")
        print("\nMake sure Kafka is running:")
        print("  cd ../../.. && make infra-up")
        raise


if __name__ == "__main__":
    main()
