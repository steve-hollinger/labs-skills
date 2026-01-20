"""Example 2: Real-Time Aggregations

This example demonstrates building real-time aggregations from DynamoDB
Stream events, such as counters, running totals, and statistics.

Key concepts:
- Atomic counter updates
- Handling all event types for accurate aggregations
- Computing deltas from MODIFY events
- Maintaining aggregate consistency
"""

from decimal import Decimal
from typing import Any

import boto3
from moto import mock_aws

from dynamodb_streams_cdc.processor import StreamRecord


class OrderAggregator:
    """Maintains real-time order aggregations from stream events."""

    def __init__(self, aggregates_table: Any):
        """Initialize aggregator.

        Args:
            aggregates_table: DynamoDB table for storing aggregates
        """
        self.table = aggregates_table

    def process_record(self, record: StreamRecord) -> None:
        """Process a stream record and update aggregations.

        Args:
            record: Parsed stream record
        """
        # Only process ORDER entities
        if record.get_entity_type() != "ORDER":
            return

        if record.event_name == "INSERT":
            self._handle_new_order(record)
        elif record.event_name == "MODIFY":
            self._handle_order_update(record)
        elif record.event_name == "REMOVE":
            self._handle_order_deletion(record)

    def _handle_new_order(self, record: StreamRecord) -> None:
        """Handle new order - increment counters and totals."""
        if not record.new_image:
            return

        # Extract user from PK (e.g., "USER#user-123")
        pk = record.keys.get("PK", "")
        user_id = pk.split("#")[1] if "#" in pk else pk

        total = record.new_image.get("total", Decimal("0"))
        status = record.new_image.get("status", "unknown")

        print(f"  New order: user={user_id}, total=${total}, status={status}")

        # Update user aggregates
        self._update_user_aggregates(user_id, order_count_delta=1, total_delta=total)

        # Update status aggregates
        self._update_status_count(status, delta=1)

        # Update daily aggregates
        created_at = record.new_image.get("created_at", "")
        if created_at:
            date = str(created_at)[:10]  # "2024-01-15"
            self._update_daily_aggregates(date, order_count_delta=1, total_delta=total)

    def _handle_order_update(self, record: StreamRecord) -> None:
        """Handle order modification - compute and apply deltas."""
        old = record.old_image or {}
        new = record.new_image or {}

        changes = record.get_changes()

        # Check for status change
        if "status" in changes:
            old_status, new_status = changes["status"]
            print(f"  Order status: {old_status} -> {new_status}")
            self._update_status_count(str(old_status), delta=-1)
            self._update_status_count(str(new_status), delta=1)

        # Check for total change
        if "total" in changes:
            old_total = Decimal(str(changes["total"][0] or 0))
            new_total = Decimal(str(changes["total"][1] or 0))
            delta = new_total - old_total

            pk = record.keys.get("PK", "")
            user_id = pk.split("#")[1] if "#" in pk else pk

            print(f"  Order total changed: ${old_total} -> ${new_total} (delta: ${delta})")
            self._update_user_aggregates(user_id, order_count_delta=0, total_delta=delta)

    def _handle_order_deletion(self, record: StreamRecord) -> None:
        """Handle order deletion - decrement counters and totals."""
        if not record.old_image:
            return

        pk = record.keys.get("PK", "")
        user_id = pk.split("#")[1] if "#" in pk else pk

        total = record.old_image.get("total", Decimal("0"))
        status = record.old_image.get("status", "unknown")

        print(f"  Order deleted: user={user_id}, total=${total}, status={status}")

        # Update user aggregates (negative delta)
        self._update_user_aggregates(user_id, order_count_delta=-1, total_delta=-total)

        # Update status aggregates
        self._update_status_count(str(status), delta=-1)

    def _update_user_aggregates(
        self, user_id: str, order_count_delta: int, total_delta: Decimal
    ) -> None:
        """Update user-level aggregates atomically."""
        self.table.update_item(
            Key={"PK": f"USER#{user_id}", "SK": "AGGREGATES"},
            UpdateExpression="""
                SET order_count = if_not_exists(order_count, :zero) + :count_delta,
                    total_spent = if_not_exists(total_spent, :zero) + :total_delta,
                    updated_at = :now
            """,
            ExpressionAttributeValues={
                ":zero": Decimal("0"),
                ":count_delta": order_count_delta,
                ":total_delta": total_delta,
                ":now": "2024-01-16T12:00:00Z",  # Would use actual timestamp
            },
        )

    def _update_status_count(self, status: str, delta: int) -> None:
        """Update status-level counts."""
        self.table.update_item(
            Key={"PK": "AGGREGATES", "SK": f"STATUS#{status}"},
            UpdateExpression="""
                SET order_count = if_not_exists(order_count, :zero) + :delta
            """,
            ExpressionAttributeValues={
                ":zero": 0,
                ":delta": delta,
            },
        )

    def _update_daily_aggregates(
        self, date: str, order_count_delta: int, total_delta: Decimal
    ) -> None:
        """Update daily aggregates."""
        self.table.update_item(
            Key={"PK": "DAILY", "SK": f"DATE#{date}"},
            UpdateExpression="""
                SET order_count = if_not_exists(order_count, :zero) + :count_delta,
                    revenue = if_not_exists(revenue, :zero_dec) + :total_delta
            """,
            ExpressionAttributeValues={
                ":zero": 0,
                ":zero_dec": Decimal("0"),
                ":count_delta": order_count_delta,
                ":total_delta": total_delta,
            },
        )

    def get_user_aggregates(self, user_id: str) -> dict[str, Any] | None:
        """Get aggregates for a user."""
        response = self.table.get_item(
            Key={"PK": f"USER#{user_id}", "SK": "AGGREGATES"}
        )
        return response.get("Item")

    def get_status_counts(self) -> dict[str, int]:
        """Get counts by order status."""
        response = self.table.query(
            KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
            ExpressionAttributeValues={
                ":pk": "AGGREGATES",
                ":sk": "STATUS#",
            },
        )
        return {
            item["SK"].replace("STATUS#", ""): int(item["order_count"])
            for item in response.get("Items", [])
        }


def create_sample_order_events() -> list[dict[str, Any]]:
    """Create sample order stream events."""
    return [
        # New order from user-001
        {
            "eventID": "evt-001",
            "eventName": "INSERT",
            "dynamodb": {
                "Keys": {
                    "PK": {"S": "USER#user-001"},
                    "SK": {"S": "ORDER#2024-01-15#order-001"},
                },
                "NewImage": {
                    "PK": {"S": "USER#user-001"},
                    "SK": {"S": "ORDER#2024-01-15#order-001"},
                    "order_id": {"S": "order-001"},
                    "total": {"N": "99.99"},
                    "status": {"S": "pending"},
                    "created_at": {"S": "2024-01-15T10:00:00Z"},
                },
                "SequenceNumber": "1",
            },
        },
        # Another order from user-001
        {
            "eventID": "evt-002",
            "eventName": "INSERT",
            "dynamodb": {
                "Keys": {
                    "PK": {"S": "USER#user-001"},
                    "SK": {"S": "ORDER#2024-01-15#order-002"},
                },
                "NewImage": {
                    "PK": {"S": "USER#user-001"},
                    "SK": {"S": "ORDER#2024-01-15#order-002"},
                    "order_id": {"S": "order-002"},
                    "total": {"N": "149.99"},
                    "status": {"S": "pending"},
                    "created_at": {"S": "2024-01-15T14:00:00Z"},
                },
                "SequenceNumber": "2",
            },
        },
        # Order status changed to shipped
        {
            "eventID": "evt-003",
            "eventName": "MODIFY",
            "dynamodb": {
                "Keys": {
                    "PK": {"S": "USER#user-001"},
                    "SK": {"S": "ORDER#2024-01-15#order-001"},
                },
                "OldImage": {
                    "PK": {"S": "USER#user-001"},
                    "SK": {"S": "ORDER#2024-01-15#order-001"},
                    "order_id": {"S": "order-001"},
                    "total": {"N": "99.99"},
                    "status": {"S": "pending"},
                },
                "NewImage": {
                    "PK": {"S": "USER#user-001"},
                    "SK": {"S": "ORDER#2024-01-15#order-001"},
                    "order_id": {"S": "order-001"},
                    "total": {"N": "99.99"},
                    "status": {"S": "shipped"},
                },
                "SequenceNumber": "3",
            },
        },
        # Order from different user
        {
            "eventID": "evt-004",
            "eventName": "INSERT",
            "dynamodb": {
                "Keys": {
                    "PK": {"S": "USER#user-002"},
                    "SK": {"S": "ORDER#2024-01-15#order-003"},
                },
                "NewImage": {
                    "PK": {"S": "USER#user-002"},
                    "SK": {"S": "ORDER#2024-01-15#order-003"},
                    "order_id": {"S": "order-003"},
                    "total": {"N": "49.99"},
                    "status": {"S": "pending"},
                    "created_at": {"S": "2024-01-15T16:00:00Z"},
                },
                "SequenceNumber": "4",
            },
        },
    ]


@mock_aws
def main() -> None:
    """Run the aggregation example."""
    print("Example 2: Real-Time Aggregations")
    print("=" * 50)

    # Create DynamoDB table for aggregates
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    client = boto3.client("dynamodb", region_name="us-east-1")

    client.create_table(
        TableName="OrderAggregates",
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    table = dynamodb.Table("OrderAggregates")
    aggregator = OrderAggregator(table)

    # Process stream events
    print("\n--- Processing Order Stream Events ---\n")

    events = create_sample_order_events()
    for raw_record in events:
        record = StreamRecord.from_raw(raw_record)
        print(f"Processing: {record.event_name} - {record.keys.get('SK')}")
        aggregator.process_record(record)

    # Check aggregates
    print("\n--- Aggregation Results ---\n")

    # User aggregates
    print("User Aggregates:")
    for user_id in ["user-001", "user-002"]:
        agg = aggregator.get_user_aggregates(user_id)
        if agg:
            print(f"  {user_id}:")
            print(f"    Order Count: {agg.get('order_count')}")
            print(f"    Total Spent: ${agg.get('total_spent')}")

    # Status counts
    print("\nStatus Counts:")
    status_counts = aggregator.get_status_counts()
    for status, count in status_counts.items():
        print(f"  {status}: {count}")

    print("\n" + "=" * 50)
    print("Key Takeaways:")
    print("1. Use atomic updates (ADD, SET with if_not_exists)")
    print("2. Handle all event types for accurate counts")
    print("3. Compute deltas from MODIFY events")
    print("4. Update multiple aggregation dimensions")
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
