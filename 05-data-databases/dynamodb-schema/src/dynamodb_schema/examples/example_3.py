"""Example 3: E-commerce Schema Design

This example demonstrates a complete e-commerce schema design
supporting complex access patterns across customers, products,
orders, and inventory.

Key concepts:
- Multi-entity single-table design
- Transaction support across entities
- Inventory management patterns
- Real-world access patterns
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

import boto3
from moto import mock_aws


@dataclass
class AccessPattern:
    """Defines an access pattern with its key design."""

    name: str
    description: str
    pk_pattern: str
    sk_pattern: str
    index: str | None = None


# Define all access patterns upfront - this is the key to good schema design!
ACCESS_PATTERNS = [
    AccessPattern(
        name="GetCustomer",
        description="Get customer profile by ID",
        pk_pattern="CUSTOMER#{customer_id}",
        sk_pattern="PROFILE#{customer_id}",
    ),
    AccessPattern(
        name="GetCustomerOrders",
        description="Get all orders for a customer",
        pk_pattern="CUSTOMER#{customer_id}",
        sk_pattern="ORDER#{date}#{order_id}",
    ),
    AccessPattern(
        name="GetOrder",
        description="Get order by ID (direct lookup)",
        pk_pattern="ORDER#{order_id}",
        sk_pattern="ORDER#{order_id}",
        index="GSI1",
    ),
    AccessPattern(
        name="GetOrdersByStatus",
        description="Get orders by status for fulfillment",
        pk_pattern="STATUS#{status}",
        sk_pattern="ORDER#{date}#{order_id}",
        index="GSI2",
    ),
    AccessPattern(
        name="GetProduct",
        description="Get product by ID",
        pk_pattern="PRODUCT#{product_id}",
        sk_pattern="PRODUCT#{product_id}",
    ),
    AccessPattern(
        name="GetProductsByCategory",
        description="Browse products by category",
        pk_pattern="CATEGORY#{category}",
        sk_pattern="PRODUCT#{product_id}",
        index="GSI1",
    ),
    AccessPattern(
        name="GetInventory",
        description="Get inventory for a product",
        pk_pattern="PRODUCT#{product_id}",
        sk_pattern="INVENTORY#{warehouse_id}",
    ),
    AccessPattern(
        name="GetLowStockItems",
        description="Get items below reorder threshold",
        pk_pattern="LOWSTOCK",
        sk_pattern="PRODUCT#{product_id}#{warehouse_id}",
        index="GSI2",
    ),
]


def create_complete_ecommerce_schema() -> dict[str, Any]:
    """Create the complete e-commerce table schema.

    Returns:
        Table creation parameters
    """
    return {
        "TableName": "EcommerceComplete",
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


class EcommerceStore:
    """E-commerce store with DynamoDB single-table design."""

    def __init__(self, table: Any) -> None:
        """Initialize the store with a DynamoDB table.

        Args:
            table: DynamoDB table resource
        """
        self.table = table

    def create_customer(
        self,
        customer_id: str,
        name: str,
        email: str,
        address: str,
    ) -> dict[str, Any]:
        """Create a customer profile.

        Args:
            customer_id: Unique customer ID
            name: Customer name
            email: Customer email
            address: Shipping address

        Returns:
            Created customer item
        """
        item = {
            "PK": f"CUSTOMER#{customer_id}",
            "SK": f"PROFILE#{customer_id}",
            "entity_type": "CUSTOMER",
            "customer_id": customer_id,
            "name": name,
            "email": email,
            "address": address,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        self.table.put_item(Item=item)
        return item

    def create_product(
        self,
        product_id: str,
        name: str,
        category: str,
        price: Decimal,
        description: str = "",
    ) -> dict[str, Any]:
        """Create a product.

        Args:
            product_id: Unique product ID
            name: Product name
            category: Product category
            price: Product price
            description: Product description

        Returns:
            Created product item
        """
        item = {
            "PK": f"PRODUCT#{product_id}",
            "SK": f"PRODUCT#{product_id}",
            # GSI1 for category browsing
            "GSI1PK": f"CATEGORY#{category}",
            "GSI1SK": f"PRODUCT#{product_id}",
            "entity_type": "PRODUCT",
            "product_id": product_id,
            "name": name,
            "category": category,
            "price": price,
            "description": description,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        self.table.put_item(Item=item)
        return item

    def set_inventory(
        self,
        product_id: str,
        warehouse_id: str,
        quantity: int,
        reorder_threshold: int = 10,
    ) -> dict[str, Any]:
        """Set inventory level for a product at a warehouse.

        Args:
            product_id: Product ID
            warehouse_id: Warehouse ID
            quantity: Current quantity
            reorder_threshold: Threshold for low stock alert

        Returns:
            Created inventory item
        """
        is_low_stock = quantity < reorder_threshold

        item: dict[str, Any] = {
            "PK": f"PRODUCT#{product_id}",
            "SK": f"INVENTORY#{warehouse_id}",
            "entity_type": "INVENTORY",
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "quantity": quantity,
            "reorder_threshold": reorder_threshold,
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }

        # Sparse index: Only low stock items appear in GSI2
        if is_low_stock:
            item["GSI2PK"] = "LOWSTOCK"
            item["GSI2SK"] = f"PRODUCT#{product_id}#{warehouse_id}"

        self.table.put_item(Item=item)
        return item

    def create_order(
        self,
        customer_id: str,
        items: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Create an order with items.

        Uses transaction to ensure atomicity of order creation.

        Args:
            customer_id: Customer placing the order
            items: List of {product_id, quantity, unit_price}

        Returns:
            Created order item
        """
        order_id = str(uuid4())[:8]
        timestamp = datetime.utcnow().isoformat() + "Z"
        total = sum(
            Decimal(str(item["unit_price"])) * item["quantity"]
            for item in items
        )

        order_item = {
            "PK": f"CUSTOMER#{customer_id}",
            "SK": f"ORDER#{timestamp}#{order_id}",
            # GSI1 for direct order lookup
            "GSI1PK": f"ORDER#{order_id}",
            "GSI1SK": f"ORDER#{order_id}",
            # GSI2 for status-based queries
            "GSI2PK": "STATUS#pending",
            "GSI2SK": f"ORDER#{timestamp}#{order_id}",
            "entity_type": "ORDER",
            "order_id": order_id,
            "customer_id": customer_id,
            "items": items,
            "total": total,
            "status": "pending",
            "created_at": timestamp,
        }

        self.table.put_item(Item=order_item)
        return order_item

    def update_order_status(
        self,
        customer_id: str,
        order_sk: str,
        new_status: str,
    ) -> None:
        """Update order status.

        Args:
            customer_id: Customer ID
            order_sk: Full sort key of the order
            new_status: New status value
        """
        timestamp = datetime.utcnow().isoformat() + "Z"

        self.table.update_item(
            Key={
                "PK": f"CUSTOMER#{customer_id}",
                "SK": order_sk,
            },
            UpdateExpression="SET #status = :status, GSI2PK = :gsi2pk, updated_at = :updated",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":status": new_status,
                ":gsi2pk": f"STATUS#{new_status}",
                ":updated": timestamp,
            },
        )

    def get_customer_orders(
        self,
        customer_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Get recent orders for a customer.

        Args:
            customer_id: Customer ID
            limit: Maximum orders to return

        Returns:
            List of orders
        """
        response = self.table.query(
            KeyConditionExpression="PK = :pk AND begins_with(SK, :sk_prefix)",
            ExpressionAttributeValues={
                ":pk": f"CUSTOMER#{customer_id}",
                ":sk_prefix": "ORDER#",
            },
            ScanIndexForward=False,  # Newest first
            Limit=limit,
        )
        return response.get("Items", [])

    def get_orders_by_status(self, status: str) -> list[dict[str, Any]]:
        """Get orders by status for fulfillment.

        Args:
            status: Order status to filter

        Returns:
            List of orders with that status
        """
        response = self.table.query(
            IndexName="GSI2",
            KeyConditionExpression="GSI2PK = :pk",
            ExpressionAttributeValues={":pk": f"STATUS#{status}"},
        )
        return response.get("Items", [])

    def get_products_by_category(self, category: str) -> list[dict[str, Any]]:
        """Get products in a category.

        Args:
            category: Product category

        Returns:
            List of products
        """
        response = self.table.query(
            IndexName="GSI1",
            KeyConditionExpression="GSI1PK = :pk",
            ExpressionAttributeValues={":pk": f"CATEGORY#{category}"},
        )
        return response.get("Items", [])

    def get_low_stock_items(self) -> list[dict[str, Any]]:
        """Get all inventory items below reorder threshold.

        Returns:
            List of low stock inventory items
        """
        response = self.table.query(
            IndexName="GSI2",
            KeyConditionExpression="GSI2PK = :pk",
            ExpressionAttributeValues={":pk": "LOWSTOCK"},
        )
        return response.get("Items", [])

    def get_product_inventory(self, product_id: str) -> list[dict[str, Any]]:
        """Get inventory levels across all warehouses for a product.

        Args:
            product_id: Product ID

        Returns:
            List of inventory items
        """
        response = self.table.query(
            KeyConditionExpression="PK = :pk AND begins_with(SK, :sk_prefix)",
            ExpressionAttributeValues={
                ":pk": f"PRODUCT#{product_id}",
                ":sk_prefix": "INVENTORY#",
            },
        )
        return response.get("Items", [])


def print_access_patterns() -> None:
    """Print all defined access patterns."""
    print("\n--- Defined Access Patterns ---\n")
    for ap in ACCESS_PATTERNS:
        index_info = f" (via {ap.index})" if ap.index else ""
        print(f"  {ap.name}{index_info}")
        print(f"    {ap.description}")
        print(f"    PK: {ap.pk_pattern}")
        print(f"    SK: {ap.sk_pattern}")
        print()


@mock_aws
def main() -> None:
    """Run the e-commerce schema example."""
    print("Example 3: E-commerce Schema Design")
    print("=" * 50)

    # Print access patterns first - always design around these!
    print_access_patterns()

    # Create DynamoDB resources
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    client = boto3.client("dynamodb", region_name="us-east-1")

    # Create table
    print("--- Creating Table ---\n")
    schema = create_complete_ecommerce_schema()
    client.create_table(**schema)

    table = dynamodb.Table("EcommerceComplete")
    store = EcommerceStore(table)

    # Seed data
    print("--- Seeding Data ---\n")

    # Customers
    store.create_customer("cust-001", "Alice Smith", "alice@example.com", "123 Main St")
    store.create_customer("cust-002", "Bob Jones", "bob@example.com", "456 Oak Ave")
    print("Created 2 customers")

    # Products
    store.create_product("prod-001", "Laptop Pro", "Electronics", Decimal("999.99"))
    store.create_product("prod-002", "Wireless Mouse", "Electronics", Decimal("29.99"))
    store.create_product("prod-003", "Python Book", "Books", Decimal("49.99"))
    store.create_product("prod-004", "Coffee Mug", "Home", Decimal("14.99"))
    print("Created 4 products")

    # Inventory (some low stock)
    store.set_inventory("prod-001", "warehouse-east", 50)
    store.set_inventory("prod-001", "warehouse-west", 5, reorder_threshold=10)  # Low stock!
    store.set_inventory("prod-002", "warehouse-east", 200)
    store.set_inventory("prod-003", "warehouse-east", 8, reorder_threshold=10)  # Low stock!
    store.set_inventory("prod-004", "warehouse-east", 100)
    print("Set inventory levels (2 items are low stock)")

    # Orders
    order1 = store.create_order("cust-001", [
        {"product_id": "prod-001", "quantity": 1, "unit_price": Decimal("999.99")},
        {"product_id": "prod-002", "quantity": 2, "unit_price": Decimal("29.99")},
    ])
    order2 = store.create_order("cust-001", [
        {"product_id": "prod-003", "quantity": 1, "unit_price": Decimal("49.99")},
    ])
    order3 = store.create_order("cust-002", [
        {"product_id": "prod-004", "quantity": 3, "unit_price": Decimal("14.99")},
    ])
    print("Created 3 orders")

    # Update one order status
    store.update_order_status("cust-001", order1["SK"], "shipped")
    print("Updated order1 to 'shipped'")

    # Demonstrate access patterns
    print("\n--- Access Pattern Demonstrations ---\n")

    # Get customer orders
    print("1. GetCustomerOrders (cust-001):")
    orders = store.get_customer_orders("cust-001")
    for order in orders:
        print(f"   Order {order['order_id']}: ${order['total']} [{order['status']}]")

    # Get orders by status
    print("\n2. GetOrdersByStatus ('pending'):")
    pending = store.get_orders_by_status("pending")
    for order in pending:
        print(f"   Order {order['order_id']}: Customer {order['customer_id']}")

    # Get products by category
    print("\n3. GetProductsByCategory ('Electronics'):")
    electronics = store.get_products_by_category("Electronics")
    for product in electronics:
        print(f"   {product['name']}: ${product['price']}")

    # Get low stock items
    print("\n4. GetLowStockItems (sparse index):")
    low_stock = store.get_low_stock_items()
    for item in low_stock:
        print(f"   Product {item['product_id']} at {item['warehouse_id']}: {item['quantity']} units")

    # Get product inventory across warehouses
    print("\n5. GetInventory ('prod-001' across warehouses):")
    inventory = store.get_product_inventory("prod-001")
    for inv in inventory:
        low = " (LOW)" if inv["quantity"] < inv["reorder_threshold"] else ""
        print(f"   {inv['warehouse_id']}: {inv['quantity']} units{low}")

    print("\n" + "=" * 50)
    print("Key Takeaways:")
    print("1. Define ALL access patterns before designing schema")
    print("2. Use entity prefixes to colocate related data")
    print("3. GSIs enable alternative access patterns")
    print("4. Sparse indexes efficiently filter subsets (low stock)")
    print("5. Single table enables transactions across entities")
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
