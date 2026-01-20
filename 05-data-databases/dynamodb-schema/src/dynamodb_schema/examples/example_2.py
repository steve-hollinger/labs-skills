"""Example 2: Complex Access Patterns with GSIs

This example demonstrates how to use Global Secondary Indexes (GSIs)
to support multiple access patterns beyond the primary key.

Key concepts:
- GSI design for alternative access patterns
- GSI overloading (multiple patterns on one GSI)
- Sparse indexes for filtered access
- Query efficiency considerations
"""

from decimal import Decimal
from typing import Any

import boto3
from moto import mock_aws


def create_ecommerce_table_with_gsis() -> dict[str, Any]:
    """Create table schema with multiple GSIs for diverse access patterns.

    GSI1: Orders by status (for fulfillment dashboard)
    GSI2: Products by category (for catalog browsing)

    Returns:
        Table creation parameters
    """
    return {
        "TableName": "EcommerceData",
        "KeySchema": [
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
            {"AttributeName": "GSI1PK", "AttributeType": "S"},
            {"AttributeName": "GSI1SK", "AttributeType": "S"},
            {"AttributeName": "GSI2PK", "AttributeType": "S"},
            {"AttributeName": "GSI2SK", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "GSI1",
                "KeySchema": [
                    {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                    {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "GSI2",
                "KeySchema": [
                    {"AttributeName": "GSI2PK", "KeyType": "HASH"},
                    {"AttributeName": "GSI2SK", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST",
    }


def create_order_with_gsi(
    user_id: str,
    order_id: str,
    total: Decimal,
    status: str,
    created_at: str,
) -> dict[str, Any]:
    """Create an order item with GSI attributes for status queries.

    Args:
        user_id: Owner's user ID
        order_id: Unique order identifier
        total: Order total
        status: Order status (pending, processing, shipped, delivered)
        created_at: Creation timestamp

    Returns:
        DynamoDB item with GSI keys
    """
    return {
        # Primary key: Store under user for user-centric queries
        "PK": f"USER#{user_id}",
        "SK": f"ORDER#{created_at}#{order_id}",
        # GSI1: Query orders by status
        "GSI1PK": f"STATUS#{status}",
        "GSI1SK": f"ORDER#{created_at}#{order_id}",
        # Item data
        "entity_type": "ORDER",
        "user_id": user_id,
        "order_id": order_id,
        "total": total,
        "status": status,
        "created_at": created_at,
    }


def create_product_with_gsi(
    product_id: str,
    name: str,
    category: str,
    price: Decimal,
    featured: bool = False,
) -> dict[str, Any]:
    """Create a product item with GSI attributes for category browsing.

    Args:
        product_id: Unique product identifier
        name: Product name
        category: Product category
        price: Product price
        featured: Whether product is featured (sparse index)

    Returns:
        DynamoDB item with GSI keys
    """
    item: dict[str, Any] = {
        # Primary key: Direct product lookup
        "PK": f"PRODUCT#{product_id}",
        "SK": f"PRODUCT#{product_id}",
        # GSI1: Query products by category
        "GSI1PK": f"CATEGORY#{category}",
        "GSI1SK": f"PRODUCT#{name}",  # Sort alphabetically within category
        # Item data
        "entity_type": "PRODUCT",
        "product_id": product_id,
        "name": name,
        "category": category,
        "price": price,
        "featured": featured,
    }

    # GSI2: Sparse index - only featured products
    # Items without GSI2PK won't appear in GSI2
    if featured:
        item["GSI2PK"] = "FEATURED"
        item["GSI2SK"] = f"PRODUCT#{name}"

    return item


def demonstrate_gsi_queries(table: Any) -> None:
    """Demonstrate GSI query patterns.

    Args:
        table: DynamoDB table resource
    """
    print("\n--- GSI Query Patterns ---\n")

    # GSI1 Pattern 1: Get all pending orders (fulfillment dashboard)
    print("1. GSI1: Get All Pending Orders:")
    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression="GSI1PK = :pk",
        ExpressionAttributeValues={":pk": "STATUS#pending"},
    )
    for order in response.get("Items", []):
        print(f"   Order {order['order_id']}: ${order['total']} - User: {order['user_id']}")

    # GSI1 Pattern 2: Get products in Electronics category
    print("\n2. GSI1: Get Products in Electronics Category:")
    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression="GSI1PK = :pk",
        ExpressionAttributeValues={":pk": "CATEGORY#Electronics"},
    )
    for product in response.get("Items", []):
        print(f"   {product['name']}: ${product['price']}")

    # GSI2 Pattern: Get featured products (sparse index)
    print("\n3. GSI2: Get Featured Products (Sparse Index):")
    response = table.query(
        IndexName="GSI2",
        KeyConditionExpression="GSI2PK = :pk",
        ExpressionAttributeValues={":pk": "FEATURED"},
    )
    for product in response.get("Items", []):
        print(f"   {product['name']}: ${product['price']} (featured)")

    # Compare: Total products vs featured products
    print("\n4. Sparse Index Comparison:")
    all_products = table.query(
        KeyConditionExpression="begins_with(PK, :pk_prefix)",
        ExpressionAttributeValues={":pk_prefix": "PRODUCT#"},
    )
    # Note: This scan is for demonstration - in production, track counts separately
    print(f"   Total products in table: ~4 (demo data)")
    print(f"   Products in GSI2 (featured): {len(response.get('Items', []))}")


def demonstrate_gsi_overloading(table: Any) -> None:
    """Show how one GSI can serve multiple access patterns.

    Args:
        table: DynamoDB table resource
    """
    print("\n--- GSI Overloading Demo ---\n")
    print("GSI1 serves multiple patterns with different prefixes:")
    print("- STATUS#pending -> Orders by status")
    print("- CATEGORY#Electronics -> Products by category")
    print("\nBoth use GSI1 but with different partition key prefixes!")

    # Orders by status
    print("\n1. Orders (STATUS# prefix):")
    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression="GSI1PK = :pk",
        ExpressionAttributeValues={":pk": "STATUS#shipped"},
    )
    for item in response.get("Items", []):
        print(f"   Order: {item['order_id']}")

    # Products by category
    print("\n2. Products (CATEGORY# prefix):")
    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression="GSI1PK = :pk",
        ExpressionAttributeValues={":pk": "CATEGORY#Books"},
    )
    for item in response.get("Items", []):
        print(f"   Product: {item['name']}")


@mock_aws
def main() -> None:
    """Run the GSI access patterns example."""
    print("Example 2: Complex Access Patterns with GSIs")
    print("=" * 50)

    # Create DynamoDB resources
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    client = boto3.client("dynamodb", region_name="us-east-1")

    # Create table with GSIs
    print("\n--- Creating Table with GSIs ---\n")
    schema = create_ecommerce_table_with_gsis()
    client.create_table(**schema)
    print("Created table with GSI1 (status/category) and GSI2 (featured products)")

    table = dynamodb.Table("EcommerceData")

    # Insert sample data
    print("\n--- Inserting Sample Data ---\n")

    # Products
    products = [
        create_product_with_gsi("prod-001", "Laptop Pro", "Electronics", Decimal("999.99"), featured=True),
        create_product_with_gsi("prod-002", "Wireless Mouse", "Electronics", Decimal("29.99")),
        create_product_with_gsi("prod-003", "Python Cookbook", "Books", Decimal("49.99"), featured=True),
        create_product_with_gsi("prod-004", "USB Cable", "Electronics", Decimal("9.99")),
    ]

    # Orders with various statuses
    orders = [
        create_order_with_gsi("user-001", "order-001", Decimal("999.99"), "pending", "2024-01-15T10:00:00Z"),
        create_order_with_gsi("user-001", "order-002", Decimal("29.99"), "shipped", "2024-01-14T09:00:00Z"),
        create_order_with_gsi("user-002", "order-003", Decimal("49.99"), "pending", "2024-01-15T11:00:00Z"),
        create_order_with_gsi("user-002", "order-004", Decimal("9.99"), "delivered", "2024-01-10T08:00:00Z"),
    ]

    # Batch write
    with table.batch_writer() as batch:
        for product in products:
            batch.put_item(Item=product)
            featured_tag = " (featured)" if product.get("featured") else ""
            print(f"Inserted product: {product['name']}{featured_tag}")

        for order in orders:
            batch.put_item(Item=order)
            print(f"Inserted order: {order['order_id']} [{order['status']}]")

    # Demonstrate GSI queries
    demonstrate_gsi_queries(table)

    # Demonstrate GSI overloading
    demonstrate_gsi_overloading(table)

    print("\n" + "=" * 50)
    print("Key Takeaways:")
    print("1. GSIs enable queries on non-primary-key attributes")
    print("2. GSI overloading: One GSI serves multiple patterns with prefixes")
    print("3. Sparse indexes: Only items with GSI attributes appear in index")
    print("4. Consider GSI write costs - each GSI doubles write operations")
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
