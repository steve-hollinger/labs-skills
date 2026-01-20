"""Tests demonstrating DynamoDB mocking with moto."""

from decimal import Decimal
from typing import Any

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws


# =============================================================================
# Basic CRUD Operations
# =============================================================================


def test_put_and_get_item(dynamodb_table: Any) -> None:
    """Test basic put and get item operations."""
    dynamodb_table.put_item(
        Item={
            "pk": "USER#123",
            "sk": "PROFILE",
            "name": "Alice",
            "email": "alice@example.com",
        }
    )

    response = dynamodb_table.get_item(Key={"pk": "USER#123", "sk": "PROFILE"})

    assert "Item" in response
    assert response["Item"]["name"] == "Alice"
    assert response["Item"]["email"] == "alice@example.com"


def test_update_item(dynamodb_table: Any) -> None:
    """Test update item operation."""
    # Create item
    dynamodb_table.put_item(
        Item={"pk": "USER#123", "sk": "PROFILE", "name": "Alice", "age": 25}
    )

    # Update item
    dynamodb_table.update_item(
        Key={"pk": "USER#123", "sk": "PROFILE"},
        UpdateExpression="SET #n = :name, age = :age",
        ExpressionAttributeNames={"#n": "name"},
        ExpressionAttributeValues={":name": "Alice Smith", ":age": 26},
    )

    # Verify update
    response = dynamodb_table.get_item(Key={"pk": "USER#123", "sk": "PROFILE"})
    assert response["Item"]["name"] == "Alice Smith"
    assert response["Item"]["age"] == 26


def test_delete_item(dynamodb_table: Any) -> None:
    """Test delete item operation."""
    # Create item
    dynamodb_table.put_item(Item={"pk": "USER#123", "sk": "PROFILE", "name": "Alice"})

    # Delete item
    dynamodb_table.delete_item(Key={"pk": "USER#123", "sk": "PROFILE"})

    # Verify deletion
    response = dynamodb_table.get_item(Key={"pk": "USER#123", "sk": "PROFILE"})
    assert "Item" not in response


def test_get_nonexistent_item(dynamodb_table: Any) -> None:
    """Test getting an item that doesn't exist."""
    response = dynamodb_table.get_item(Key={"pk": "NONEXISTENT", "sk": "PROFILE"})
    assert "Item" not in response


# =============================================================================
# Query Operations
# =============================================================================


def test_query_by_partition_key(dynamodb_table: Any) -> None:
    """Test query operation by partition key."""
    # Insert multiple items
    items = [
        {"pk": "USER#123", "sk": "PROFILE", "name": "Alice"},
        {"pk": "USER#123", "sk": "ORDER#001", "total": Decimal("99.99")},
        {"pk": "USER#123", "sk": "ORDER#002", "total": Decimal("149.99")},
        {"pk": "USER#456", "sk": "PROFILE", "name": "Bob"},
    ]

    for item in items:
        dynamodb_table.put_item(Item=item)

    # Query by partition key
    response = dynamodb_table.query(
        KeyConditionExpression="pk = :pk",
        ExpressionAttributeValues={":pk": "USER#123"},
    )

    assert len(response["Items"]) == 3


def test_query_with_sort_key_condition(dynamodb_table: Any) -> None:
    """Test query with sort key condition."""
    # Insert items
    items = [
        {"pk": "USER#123", "sk": "ORDER#001", "status": "shipped"},
        {"pk": "USER#123", "sk": "ORDER#002", "status": "pending"},
        {"pk": "USER#123", "sk": "PROFILE", "name": "Alice"},
    ]

    for item in items:
        dynamodb_table.put_item(Item=item)

    # Query orders only (sk begins with ORDER#)
    response = dynamodb_table.query(
        KeyConditionExpression="pk = :pk AND begins_with(sk, :prefix)",
        ExpressionAttributeValues={":pk": "USER#123", ":prefix": "ORDER#"},
    )

    assert len(response["Items"]) == 2
    assert all(item["sk"].startswith("ORDER#") for item in response["Items"])


def test_query_with_filter(dynamodb_table: Any) -> None:
    """Test query with filter expression."""
    # Insert items
    items = [
        {"pk": "USER#123", "sk": "ORDER#001", "total": Decimal("50.00")},
        {"pk": "USER#123", "sk": "ORDER#002", "total": Decimal("150.00")},
        {"pk": "USER#123", "sk": "ORDER#003", "total": Decimal("200.00")},
    ]

    for item in items:
        dynamodb_table.put_item(Item=item)

    # Query with filter on total
    response = dynamodb_table.query(
        KeyConditionExpression="pk = :pk",
        FilterExpression="total > :min_total",
        ExpressionAttributeValues={":pk": "USER#123", ":min_total": Decimal("100.00")},
    )

    assert len(response["Items"]) == 2


# =============================================================================
# Scan Operations
# =============================================================================


def test_scan_table(dynamodb_table: Any) -> None:
    """Test scan operation."""
    # Insert items
    for i in range(5):
        dynamodb_table.put_item(Item={"pk": f"USER#{i}", "sk": "PROFILE", "index": i})

    # Scan all items
    response = dynamodb_table.scan()

    assert len(response["Items"]) == 5


def test_scan_with_filter(dynamodb_table: Any) -> None:
    """Test scan with filter expression."""
    # Insert items
    items = [
        {"pk": "USER#1", "sk": "PROFILE", "status": "active"},
        {"pk": "USER#2", "sk": "PROFILE", "status": "inactive"},
        {"pk": "USER#3", "sk": "PROFILE", "status": "active"},
    ]

    for item in items:
        dynamodb_table.put_item(Item=item)

    # Scan with filter
    response = dynamodb_table.scan(
        FilterExpression="#s = :status",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":status": "active"},
    )

    assert len(response["Items"]) == 2


# =============================================================================
# Batch Operations
# =============================================================================


def test_batch_write(dynamodb_table: Any) -> None:
    """Test batch write operation."""
    # Batch write items
    with dynamodb_table.batch_writer() as batch:
        for i in range(25):
            batch.put_item(Item={"pk": f"ITEM#{i}", "sk": "DATA", "value": i})

    # Verify all items were written
    response = dynamodb_table.scan()
    assert len(response["Items"]) == 25


# =============================================================================
# Error Handling
# =============================================================================


@mock_aws
def test_table_not_found_error() -> None:
    """Test error when accessing nonexistent table."""
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table("nonexistent-table")

    with pytest.raises(ClientError) as exc_info:
        table.get_item(Key={"pk": "test", "sk": "test"})

    assert exc_info.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_validation_error() -> None:
    """Test validation error for missing key."""
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

    dynamodb.create_table(
        TableName="test",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    table = dynamodb.Table("test")

    # Missing required key attribute
    with pytest.raises(ClientError) as exc_info:
        table.put_item(Item={"not_id": "value"})

    assert exc_info.value.response["Error"]["Code"] == "ValidationException"


# =============================================================================
# Conditional Operations
# =============================================================================


def test_conditional_put(dynamodb_table: Any) -> None:
    """Test conditional put operation."""
    # First put succeeds
    dynamodb_table.put_item(
        Item={"pk": "USER#123", "sk": "PROFILE", "name": "Alice"},
        ConditionExpression="attribute_not_exists(pk)",
    )

    # Second put fails due to condition
    with pytest.raises(ClientError) as exc_info:
        dynamodb_table.put_item(
            Item={"pk": "USER#123", "sk": "PROFILE", "name": "Bob"},
            ConditionExpression="attribute_not_exists(pk)",
        )

    assert exc_info.value.response["Error"]["Code"] == "ConditionalCheckFailedException"


def test_conditional_update(dynamodb_table: Any) -> None:
    """Test conditional update operation."""
    # Create item
    dynamodb_table.put_item(
        Item={"pk": "USER#123", "sk": "PROFILE", "version": 1, "name": "Alice"}
    )

    # Update with version check
    dynamodb_table.update_item(
        Key={"pk": "USER#123", "sk": "PROFILE"},
        UpdateExpression="SET #n = :name, version = :new_version",
        ConditionExpression="version = :current_version",
        ExpressionAttributeNames={"#n": "name"},
        ExpressionAttributeValues={
            ":name": "Alice Smith",
            ":new_version": 2,
            ":current_version": 1,
        },
    )

    # Verify update
    response = dynamodb_table.get_item(Key={"pk": "USER#123", "sk": "PROFILE"})
    assert response["Item"]["version"] == 2
