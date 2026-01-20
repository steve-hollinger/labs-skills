"""Example 1: Basic Single-Table Design

This example demonstrates the fundamental single-table design pattern
with users and their orders stored in a single DynamoDB table.

Key concepts:
- Entity type prefixes for partition keys
- Composite sort keys for range queries
- Adjacency list pattern for relationships
"""

from decimal import Decimal
from typing import Any

import boto3
from moto import mock_aws


def create_single_table_schema() -> dict[str, Any]:
    """Define the schema for a single-table design.

    Returns:
        Table creation parameters
    """
    return {
        "TableName": "UserOrders",
        "KeySchema": [
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
    }


def create_user_item(user_id: str, name: str, email: str) -> dict[str, Any]:
    """Create a user item for DynamoDB.

    Args:
        user_id: Unique user identifier
        name: User's full name
        email: User's email address

    Returns:
        DynamoDB item dictionary
    """
    return {
        "PK": f"USER#{user_id}",
        "SK": f"PROFILE#{user_id}",
        "entity_type": "USER",
        "user_id": user_id,
        "name": name,
        "email": email,
        "created_at": "2024-01-15T10:00:00Z",
    }


def create_order_item(
    user_id: str,
    order_id: str,
    total: Decimal,
    status: str = "pending",
    created_at: str = "2024-01-15T10:00:00Z",
) -> dict[str, Any]:
    """Create an order item under a user's partition.

    The order is stored under the user's partition key to enable
    efficient queries for "get all orders for user".

    Args:
        user_id: Owner's user ID
        order_id: Unique order identifier
        total: Order total amount
        status: Order status
        created_at: Order creation timestamp

    Returns:
        DynamoDB item dictionary
    """
    return {
        "PK": f"USER#{user_id}",
        "SK": f"ORDER#{created_at}#{order_id}",
        "entity_type": "ORDER",
        "user_id": user_id,
        "order_id": order_id,
        "total": total,
        "status": status,
        "created_at": created_at,
    }


def demonstrate_single_table_queries(table: Any) -> None:
    """Demonstrate various query patterns on the single table.

    Args:
        table: DynamoDB table resource
    """
    print("\n--- Query Patterns ---\n")

    # Pattern 1: Get user profile
    print("1. Get User Profile:")
    response = table.get_item(
        Key={"PK": "USER#user-001", "SK": "PROFILE#user-001"}
    )
    if "Item" in response:
        user = response["Item"]
        print(f"   Name: {user['name']}, Email: {user['email']}")

    # Pattern 2: Get all orders for a user
    print("\n2. Get All Orders for User:")
    response = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :sk_prefix)",
        ExpressionAttributeValues={
            ":pk": "USER#user-001",
            ":sk_prefix": "ORDER#",
        },
    )
    for order in response.get("Items", []):
        print(f"   Order {order['order_id']}: ${order['total']} ({order['status']})")

    # Pattern 3: Get user profile AND orders in one query
    print("\n3. Get User Profile and Orders (Single Query):")
    response = table.query(
        KeyConditionExpression="PK = :pk",
        ExpressionAttributeValues={":pk": "USER#user-001"},
    )
    for item in response.get("Items", []):
        if item["entity_type"] == "USER":
            print(f"   User: {item['name']}")
        else:
            print(f"   Order: {item['order_id']} - ${item['total']}")

    # Pattern 4: Get recent orders (sorted by date, newest first)
    print("\n4. Get Recent Orders (Newest First):")
    response = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :sk_prefix)",
        ExpressionAttributeValues={
            ":pk": "USER#user-001",
            ":sk_prefix": "ORDER#",
        },
        ScanIndexForward=False,  # Descending order
        Limit=3,
    )
    for order in response.get("Items", []):
        print(f"   {order['created_at']}: Order {order['order_id']}")


@mock_aws
def main() -> None:
    """Run the basic single-table design example."""
    print("Example 1: Basic Single-Table Design")
    print("=" * 50)

    # Create DynamoDB resources
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    client = boto3.client("dynamodb", region_name="us-east-1")

    # Create the table
    print("\n--- Creating Table ---\n")
    schema = create_single_table_schema()
    client.create_table(**schema)

    table = dynamodb.Table("UserOrders")

    # Insert sample data
    print("--- Inserting Sample Data ---\n")

    # Create users
    users = [
        create_user_item("user-001", "Alice Smith", "alice@example.com"),
        create_user_item("user-002", "Bob Jones", "bob@example.com"),
    ]

    # Create orders for users
    orders = [
        create_order_item("user-001", "order-001", Decimal("99.99"), "delivered", "2024-01-10T10:00:00Z"),
        create_order_item("user-001", "order-002", Decimal("149.99"), "shipped", "2024-01-12T14:30:00Z"),
        create_order_item("user-001", "order-003", Decimal("29.99"), "pending", "2024-01-15T09:00:00Z"),
        create_order_item("user-002", "order-004", Decimal("199.99"), "pending", "2024-01-14T11:00:00Z"),
    ]

    # Batch write all items
    with table.batch_writer() as batch:
        for user in users:
            batch.put_item(Item=user)
            print(f"Inserted user: {user['name']}")
        for order in orders:
            batch.put_item(Item=order)
            print(f"Inserted order: {order['order_id']} for user {order['user_id']}")

    # Demonstrate query patterns
    demonstrate_single_table_queries(table)

    print("\n" + "=" * 50)
    print("Key Takeaways:")
    print("1. Users and orders share the same table")
    print("2. Entity type prefixes (USER#, ORDER#) distinguish items")
    print("3. Sort key includes timestamp for chronological ordering")
    print("4. Single query can retrieve user + all their orders")
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
