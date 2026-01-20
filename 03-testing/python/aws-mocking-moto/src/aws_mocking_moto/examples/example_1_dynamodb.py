"""Example 1: DynamoDB Mocking with moto

This example demonstrates how to mock DynamoDB operations using moto,
including table creation, CRUD operations, and queries.
"""

import os


def setup_aws_credentials() -> None:
    """Set up fake AWS credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


def main() -> None:
    """Demonstrate DynamoDB mocking with moto."""
    print("Example 1: DynamoDB Mocking with moto")
    print("=" * 50)
    print()

    # Show decorator pattern
    print("1. Decorator Pattern")
    print("-" * 40)
    print("""
    import boto3
    from moto import mock_aws

    @mock_aws
    def test_create_table():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        table = dynamodb.create_table(
            TableName="users",
            KeySchema=[
                {"AttributeName": "pk", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "pk", "AttributeType": "S"},
                {"AttributeName": "sk", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        # Table is created in mock, not real AWS
        assert table.table_status == "ACTIVE"
    """)

    # Show CRUD operations
    print("2. CRUD Operations")
    print("-" * 40)
    print("""
    @mock_aws
    def test_crud_operations():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = create_users_table(dynamodb)  # Helper function

        # CREATE - Put Item
        table.put_item(Item={
            "pk": "USER#123",
            "sk": "PROFILE",
            "name": "Alice",
            "email": "alice@example.com",
        })

        # READ - Get Item
        response = table.get_item(Key={"pk": "USER#123", "sk": "PROFILE"})
        item = response["Item"]
        assert item["name"] == "Alice"

        # UPDATE - Update Item
        table.update_item(
            Key={"pk": "USER#123", "sk": "PROFILE"},
            UpdateExpression="SET #n = :name",
            ExpressionAttributeNames={"#n": "name"},
            ExpressionAttributeValues={":name": "Alice Smith"},
        )

        # DELETE - Delete Item
        table.delete_item(Key={"pk": "USER#123", "sk": "PROFILE"})
    """)

    # Show query operations
    print("3. Query Operations")
    print("-" * 40)
    print("""
    @mock_aws
    def test_query_items():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = create_orders_table(dynamodb)

        # Insert multiple items
        orders = [
            {"pk": "USER#123", "sk": "ORDER#001", "total": 50.00},
            {"pk": "USER#123", "sk": "ORDER#002", "total": 75.00},
            {"pk": "USER#123", "sk": "ORDER#003", "total": 100.00},
        ]
        for order in orders:
            table.put_item(Item=order)

        # Query by partition key
        response = table.query(
            KeyConditionExpression="pk = :pk",
            ExpressionAttributeValues={":pk": "USER#123"},
        )

        assert len(response["Items"]) == 3

        # Query with filter
        response = table.query(
            KeyConditionExpression="pk = :pk",
            FilterExpression="total > :min_total",
            ExpressionAttributeValues={
                ":pk": "USER#123",
                ":min_total": 60.00,
            },
        )

        assert len(response["Items"]) == 2
    """)

    # Show context manager
    print("4. Context Manager Pattern")
    print("-" * 40)
    print("""
    from moto import mock_aws

    def test_with_context_manager():
        with mock_aws():
            dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

            table = dynamodb.create_table(
                TableName="test-table",
                KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
                BillingMode="PAY_PER_REQUEST",
            )

            # Use the table within the context
            table.put_item(Item={"id": "1", "data": "test"})

        # Outside the context, mocking stops
    """)

    # Run actual demo
    print("5. Live Demo")
    print("-" * 40)

    setup_aws_credentials()

    import boto3
    from moto import mock_aws

    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        # Create table
        table = dynamodb.create_table(
            TableName="demo-users",
            KeySchema=[
                {"AttributeName": "pk", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "pk", "AttributeType": "S"},
                {"AttributeName": "sk", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        print(f"Created table: {table.table_name}")
        print(f"Table status: {table.table_status}")

        # Insert items
        users = [
            {"pk": "USER#1", "sk": "PROFILE", "name": "Alice", "email": "alice@example.com"},
            {"pk": "USER#2", "sk": "PROFILE", "name": "Bob", "email": "bob@example.com"},
            {"pk": "USER#1", "sk": "ORDER#001", "total": 99.99},
        ]

        for user in users:
            table.put_item(Item=user)
            print(f"Inserted: {user['pk']} / {user['sk']}")

        # Query
        response = table.query(
            KeyConditionExpression="pk = :pk",
            ExpressionAttributeValues={":pk": "USER#1"},
        )
        print(f"\nQuery results for USER#1: {len(response['Items'])} items")
        for item in response["Items"]:
            print(f"  - {item}")

    print()
    print("Run the tests with:")
    print("  pytest tests/test_dynamodb.py -v")
    print()
    print("Example completed!")


if __name__ == "__main__":
    main()
