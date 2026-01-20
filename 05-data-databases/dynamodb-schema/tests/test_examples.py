"""Tests for DynamoDB Schema Design examples."""

from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock

import boto3
import pytest
from moto import mock_aws

from dynamodb_schema.examples.example_1 import (
    create_order_item,
    create_single_table_schema,
    create_user_item,
)
from dynamodb_schema.examples.example_2 import (
    create_ecommerce_table_with_gsis,
    create_order_with_gsi,
    create_product_with_gsi,
)
from dynamodb_schema.examples.example_3 import EcommerceStore
from dynamodb_schema.models import Order, OrderItem, Product, User
from dynamodb_schema.schema import DynamoDBSchema, create_composite_key, create_gsi_key


class TestExample1SingleTable:
    """Tests for Example 1: Basic Single-Table Design."""

    def test_create_user_item(self) -> None:
        """Test user item creation with proper key structure."""
        user = create_user_item("user-123", "Test User", "test@example.com")

        assert user["PK"] == "USER#user-123"
        assert user["SK"] == "PROFILE#user-123"
        assert user["entity_type"] == "USER"
        assert user["name"] == "Test User"
        assert user["email"] == "test@example.com"

    def test_create_order_item(self) -> None:
        """Test order item creation with composite sort key."""
        order = create_order_item(
            user_id="user-123",
            order_id="order-456",
            total=Decimal("99.99"),
            status="pending",
            created_at="2024-01-15T10:00:00Z",
        )

        assert order["PK"] == "USER#user-123"
        assert order["SK"] == "ORDER#2024-01-15T10:00:00Z#order-456"
        assert order["entity_type"] == "ORDER"
        assert order["total"] == Decimal("99.99")
        assert order["status"] == "pending"

    def test_orders_sort_by_date(self) -> None:
        """Test that orders sort correctly by date in sort key."""
        order1 = create_order_item("user-1", "o1", Decimal("10"), created_at="2024-01-10T10:00:00Z")
        order2 = create_order_item("user-1", "o2", Decimal("20"), created_at="2024-01-15T10:00:00Z")
        order3 = create_order_item("user-1", "o3", Decimal("30"), created_at="2024-01-12T10:00:00Z")

        # Sort keys should maintain date order
        sorted_orders = sorted([order1, order2, order3], key=lambda x: x["SK"])

        assert sorted_orders[0]["order_id"] == "o1"  # Jan 10
        assert sorted_orders[1]["order_id"] == "o3"  # Jan 12
        assert sorted_orders[2]["order_id"] == "o2"  # Jan 15

    @mock_aws
    def test_single_table_query(self) -> None:
        """Test querying single table for user and orders."""
        # Setup
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        client = boto3.client("dynamodb", region_name="us-east-1")

        schema = create_single_table_schema()
        client.create_table(**schema)
        table = dynamodb.Table("UserOrders")

        # Insert data
        user = create_user_item("user-001", "Alice", "alice@example.com")
        order1 = create_order_item("user-001", "order-001", Decimal("50"), created_at="2024-01-10T10:00:00Z")
        order2 = create_order_item("user-001", "order-002", Decimal("75"), created_at="2024-01-15T10:00:00Z")

        table.put_item(Item=user)
        table.put_item(Item=order1)
        table.put_item(Item=order2)

        # Query all items for user
        response = table.query(
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={":pk": "USER#user-001"},
        )

        items = response["Items"]
        assert len(items) == 3  # 1 user + 2 orders

        # Query only orders
        response = table.query(
            KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
            ExpressionAttributeValues={
                ":pk": "USER#user-001",
                ":sk": "ORDER#",
            },
        )

        orders = response["Items"]
        assert len(orders) == 2


class TestExample2GSI:
    """Tests for Example 2: GSI Access Patterns."""

    def test_create_order_with_gsi(self) -> None:
        """Test order creation includes GSI attributes."""
        order = create_order_with_gsi(
            user_id="user-123",
            order_id="order-456",
            total=Decimal("99.99"),
            status="pending",
            created_at="2024-01-15T10:00:00Z",
        )

        assert order["GSI1PK"] == "STATUS#pending"
        assert "GSI1SK" in order
        assert order["user_id"] == "user-123"

    def test_create_product_with_category_gsi(self) -> None:
        """Test product creation with category GSI."""
        product = create_product_with_gsi(
            product_id="prod-001",
            name="Test Product",
            category="Electronics",
            price=Decimal("29.99"),
        )

        assert product["GSI1PK"] == "CATEGORY#Electronics"
        assert product["GSI1SK"] == "PRODUCT#Test Product"
        assert "GSI2PK" not in product  # Not featured

    def test_sparse_index_featured_product(self) -> None:
        """Test sparse index only includes featured products."""
        regular = create_product_with_gsi("p1", "Regular", "Cat", Decimal("10"))
        featured = create_product_with_gsi("p2", "Featured", "Cat", Decimal("20"), featured=True)

        assert "GSI2PK" not in regular
        assert featured["GSI2PK"] == "FEATURED"
        assert featured["GSI2SK"] == "PRODUCT#Featured"

    @mock_aws
    def test_gsi_query(self) -> None:
        """Test querying GSI for orders by status."""
        # Setup
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        client = boto3.client("dynamodb", region_name="us-east-1")

        schema = create_ecommerce_table_with_gsis()
        client.create_table(**schema)
        table = dynamodb.Table("EcommerceData")

        # Insert orders with different statuses
        pending = create_order_with_gsi("u1", "o1", Decimal("10"), "pending", "2024-01-15T10:00:00Z")
        shipped = create_order_with_gsi("u1", "o2", Decimal("20"), "shipped", "2024-01-14T10:00:00Z")
        pending2 = create_order_with_gsi("u2", "o3", Decimal("30"), "pending", "2024-01-15T11:00:00Z")

        table.put_item(Item=pending)
        table.put_item(Item=shipped)
        table.put_item(Item=pending2)

        # Query GSI1 for pending orders
        response = table.query(
            IndexName="GSI1",
            KeyConditionExpression="GSI1PK = :pk",
            ExpressionAttributeValues={":pk": "STATUS#pending"},
        )

        pending_orders = response["Items"]
        assert len(pending_orders) == 2
        assert all(o["status"] == "pending" for o in pending_orders)


class TestExample3EcommerceStore:
    """Tests for Example 3: E-commerce Schema."""

    @mock_aws
    def test_create_and_query_customer_orders(self) -> None:
        """Test creating orders and querying by customer."""
        # Setup
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        client = boto3.client("dynamodb", region_name="us-east-1")

        from dynamodb_schema.examples.example_3 import create_complete_ecommerce_schema

        schema = create_complete_ecommerce_schema()
        client.create_table(**schema)
        table = dynamodb.Table("EcommerceComplete")

        store = EcommerceStore(table)

        # Create customer and orders
        store.create_customer("cust-001", "Alice", "alice@test.com", "123 Main St")
        store.create_order("cust-001", [
            {"product_id": "p1", "quantity": 1, "unit_price": Decimal("10")},
        ])
        store.create_order("cust-001", [
            {"product_id": "p2", "quantity": 2, "unit_price": Decimal("20")},
        ])

        # Query orders
        orders = store.get_customer_orders("cust-001")
        assert len(orders) == 2

    @mock_aws
    def test_low_stock_sparse_index(self) -> None:
        """Test low stock items appear in sparse index."""
        # Setup
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        client = boto3.client("dynamodb", region_name="us-east-1")

        from dynamodb_schema.examples.example_3 import create_complete_ecommerce_schema

        schema = create_complete_ecommerce_schema()
        client.create_table(**schema)
        table = dynamodb.Table("EcommerceComplete")

        store = EcommerceStore(table)

        # Set inventory with some low stock
        store.set_inventory("prod-001", "wh-east", 100)  # OK
        store.set_inventory("prod-002", "wh-east", 5)  # Low (< 10)
        store.set_inventory("prod-003", "wh-west", 3)  # Low (< 10)

        # Query low stock
        low_stock = store.get_low_stock_items()
        assert len(low_stock) == 2

        product_ids = {item["product_id"] for item in low_stock}
        assert "prod-002" in product_ids
        assert "prod-003" in product_ids
        assert "prod-001" not in product_ids


class TestModels:
    """Tests for Pydantic models."""

    def test_user_model_keys(self) -> None:
        """Test User model generates correct keys."""
        user = User(
            user_id="test-123",
            email="test@example.com",
            name="Test User",
        )

        assert user.get_pk() == "USER#test-123"
        assert user.get_sk() == "PROFILE#test-123"
        assert user.get_gsi1_pk() == "EMAIL#test@example.com"

    def test_order_model_keys(self) -> None:
        """Test Order model generates correct keys."""
        order = Order(
            order_id="order-456",
            user_id="user-123",
            total=Decimal("99.99"),
            status="pending",
        )

        assert order.get_pk() == "USER#user-123"
        assert order.get_sk().startswith("ORDER#")
        assert order.get_gsi1_pk() == "STATUS#pending"

    def test_product_model_to_dynamodb(self) -> None:
        """Test Product serialization to DynamoDB format."""
        product = Product(
            product_id="prod-001",
            name="Test Product",
            price=Decimal("29.99"),
            category="Electronics",
        )

        item = product.to_dynamodb_item()

        assert item["PK"] == "PRODUCT#prod-001"
        assert item["GSI1PK"] == "CATEGORY#Electronics"
        assert item["price"] == "29.99"  # Decimal converted to string


class TestSchemaUtilities:
    """Tests for schema utility functions."""

    def test_create_composite_key(self) -> None:
        """Test composite key creation."""
        key = create_composite_key("USER", "123")
        assert key == "USER#123"

        key = create_composite_key("ORDER", "2024-01-15", "456")
        assert key == "ORDER#2024-01-15#456"

    def test_create_composite_key_custom_separator(self) -> None:
        """Test composite key with custom separator."""
        key = create_composite_key("USER", "123", separator="|")
        assert key == "USER|123"

    def test_create_gsi_key(self) -> None:
        """Test GSI key attribute creation."""
        name, value = create_gsi_key("STATUS", "pending", gsi_number=1, key_type="PK")
        assert name == "GSI1PK"
        assert value == "STATUS#pending"

        name, value = create_gsi_key("ORDER", "2024-01-15", gsi_number=2, key_type="SK")
        assert name == "GSI2SK"
        assert value == "ORDER#2024-01-15"

    @mock_aws
    def test_dynamodb_schema_class(self) -> None:
        """Test DynamoDBSchema utility class."""
        schema = DynamoDBSchema(
            table_name="TestTable",
            region="us-east-1",
        )

        # Create table
        schema.create_table()

        # Put and get item
        item = {"PK": "TEST#1", "SK": "TEST#1", "data": "test"}
        schema.put_item(item)

        retrieved = schema.get_item("TEST#1", "TEST#1")
        assert retrieved is not None
        assert retrieved["data"] == "test"

        # Query
        results = schema.query("TEST#1")
        assert len(results) == 1


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_order_items(self) -> None:
        """Test order with no items."""
        order = Order(
            order_id="order-001",
            user_id="user-001",
            total=Decimal("0"),
            items=[],
        )

        item = order.to_dynamodb_item()
        assert item["items"] == []
        assert item["total"] == "0"

    def test_special_characters_in_keys(self) -> None:
        """Test handling of special characters in entity IDs."""
        # UUIDs and other special chars should work
        user = create_user_item(
            "550e8400-e29b-41d4-a716-446655440000",
            "Test User",
            "test+label@example.com",
        )

        assert "550e8400" in user["PK"]
        assert user["email"] == "test+label@example.com"

    @pytest.mark.slow
    @mock_aws
    def test_batch_write_many_items(self) -> None:
        """Test batch writing many items."""
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        client = boto3.client("dynamodb", region_name="us-east-1")

        schema = create_single_table_schema()
        client.create_table(**schema)
        table = dynamodb.Table("UserOrders")

        # Create 100 items
        items = [
            create_user_item(f"user-{i:03d}", f"User {i}", f"user{i}@test.com")
            for i in range(100)
        ]

        # Batch write
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)

        # Verify count (scan for test purposes only)
        response = table.scan(Select="COUNT")
        assert response["Count"] == 100
