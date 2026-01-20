"""Example 4: Pytest Fixtures with moto

This example demonstrates how to integrate moto with pytest fixtures
for clean, reusable test setup.
"""

import os


def setup_aws_credentials() -> None:
    """Set up fake AWS credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


def main() -> None:
    """Demonstrate pytest fixtures with moto."""
    print("Example 4: Pytest Fixtures with moto")
    print("=" * 50)
    print()

    # Show credentials fixture
    print("1. AWS Credentials Fixture")
    print("-" * 40)
    print("""
    # conftest.py
    import os
    import pytest

    @pytest.fixture(scope="session")
    def aws_credentials():
        \"\"\"Set up fake AWS credentials for moto.\"\"\"
        os.environ["AWS_ACCESS_KEY_ID"] = "testing"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
        os.environ["AWS_SECURITY_TOKEN"] = "testing"
        os.environ["AWS_SESSION_TOKEN"] = "testing"
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    """)

    # Show DynamoDB fixture
    print("2. DynamoDB Table Fixture")
    print("-" * 40)
    print("""
    import pytest
    import boto3
    from moto import mock_aws

    @pytest.fixture
    def dynamodb_table(aws_credentials):
        \"\"\"Create a mocked DynamoDB table.\"\"\"
        with mock_aws():
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

            yield table


    def test_create_user(dynamodb_table):
        dynamodb_table.put_item(Item={
            "pk": "USER#123",
            "sk": "PROFILE",
            "name": "Alice",
        })

        response = dynamodb_table.get_item(
            Key={"pk": "USER#123", "sk": "PROFILE"}
        )
        assert response["Item"]["name"] == "Alice"
    """)

    # Show S3 fixture
    print("3. S3 Bucket Fixture")
    print("-" * 40)
    print("""
    @pytest.fixture
    def s3_bucket(aws_credentials):
        \"\"\"Create a mocked S3 bucket.\"\"\"
        with mock_aws():
            s3 = boto3.client("s3", region_name="us-east-1")
            s3.create_bucket(Bucket="test-bucket")
            yield s3, "test-bucket"


    def test_upload_file(s3_bucket):
        s3, bucket_name = s3_bucket

        s3.put_object(
            Bucket=bucket_name,
            Key="test.txt",
            Body=b"Hello, World!",
        )

        response = s3.get_object(Bucket=bucket_name, Key="test.txt")
        assert response["Body"].read() == b"Hello, World!"
    """)

    # Show pre-populated fixture
    print("4. Pre-populated Fixture")
    print("-" * 40)
    print("""
    @pytest.fixture
    def populated_dynamodb(dynamodb_table):
        \"\"\"DynamoDB table with test data.\"\"\"
        # Add test users
        users = [
            {"pk": "USER#1", "sk": "PROFILE", "name": "Alice", "email": "alice@example.com"},
            {"pk": "USER#2", "sk": "PROFILE", "name": "Bob", "email": "bob@example.com"},
            {"pk": "USER#1", "sk": "ORDER#001", "total": 99.99, "status": "shipped"},
            {"pk": "USER#1", "sk": "ORDER#002", "total": 149.99, "status": "pending"},
        ]

        for user in users:
            dynamodb_table.put_item(Item=user)

        return dynamodb_table


    def test_query_user_orders(populated_dynamodb):
        response = populated_dynamodb.query(
            KeyConditionExpression="pk = :pk AND begins_with(sk, :prefix)",
            ExpressionAttributeValues={
                ":pk": "USER#1",
                ":prefix": "ORDER#",
            },
        )

        assert len(response["Items"]) == 2
    """)

    # Show combined fixtures
    print("5. Combined Service Fixtures")
    print("-" * 40)
    print("""
    @pytest.fixture
    def aws_services(aws_credentials):
        \"\"\"Fixture providing multiple AWS services.\"\"\"
        with mock_aws():
            s3 = boto3.client("s3", region_name="us-east-1")
            dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
            sqs = boto3.client("sqs", region_name="us-east-1")

            # Set up resources
            s3.create_bucket(Bucket="uploads")

            table = dynamodb.create_table(
                TableName="data",
                KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
                BillingMode="PAY_PER_REQUEST",
            )

            queue_url = sqs.create_queue(QueueName="events")["QueueUrl"]

            yield {
                "s3": s3,
                "bucket": "uploads",
                "dynamodb": table,
                "sqs": sqs,
                "queue_url": queue_url,
            }


    def test_upload_and_record(aws_services):
        # Upload to S3
        aws_services["s3"].put_object(
            Bucket=aws_services["bucket"],
            Key="file.txt",
            Body=b"data",
        )

        # Record in DynamoDB
        aws_services["dynamodb"].put_item(Item={
            "id": "file-001",
            "s3_key": "file.txt",
        })

        # Send notification
        aws_services["sqs"].send_message(
            QueueUrl=aws_services["queue_url"],
            MessageBody='{"file_id": "file-001"}',
        )
    """)

    # Show repository pattern
    print("6. Repository Pattern Fixture")
    print("-" * 40)
    print("""
    from dataclasses import dataclass

    @dataclass
    class User:
        user_id: str
        name: str
        email: str

    class UserRepository:
        def __init__(self, table):
            self.table = table

        def save(self, user: User) -> None:
            self.table.put_item(Item={
                "pk": f"USER#{user.user_id}",
                "sk": "PROFILE",
                "name": user.name,
                "email": user.email,
            })

        def get(self, user_id: str) -> User | None:
            response = self.table.get_item(
                Key={"pk": f"USER#{user_id}", "sk": "PROFILE"}
            )
            if "Item" not in response:
                return None
            item = response["Item"]
            return User(
                user_id=user_id,
                name=item["name"],
                email=item["email"],
            )


    @pytest.fixture
    def user_repository(dynamodb_table):
        return UserRepository(dynamodb_table)


    def test_save_and_get_user(user_repository):
        user = User(user_id="123", name="Alice", email="alice@example.com")
        user_repository.save(user)

        loaded = user_repository.get("123")
        assert loaded is not None
        assert loaded.name == "Alice"
    """)

    # Run actual demo
    print("7. Live Demo")
    print("-" * 40)

    setup_aws_credentials()

    import boto3
    from moto import mock_aws
    from dataclasses import dataclass

    @dataclass
    class Product:
        product_id: str
        name: str
        price: float

    class ProductRepository:
        def __init__(self, table_name: str) -> None:
            self.dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
            self.table = self.dynamodb.Table(table_name)

        def save(self, product: Product) -> None:
            self.table.put_item(Item={
                "pk": f"PRODUCT#{product.product_id}",
                "sk": "INFO",
                "name": product.name,
                "price": str(product.price),  # DynamoDB doesn't support float
            })

        def get(self, product_id: str) -> Product | None:
            response = self.table.get_item(
                Key={"pk": f"PRODUCT#{product_id}", "sk": "INFO"}
            )
            if "Item" not in response:
                return None
            item = response["Item"]
            return Product(
                product_id=product_id,
                name=item["name"],
                price=float(item["price"]),
            )

        def list_all(self) -> list[Product]:
            response = self.table.scan(
                FilterExpression="begins_with(pk, :prefix)",
                ExpressionAttributeValues={":prefix": "PRODUCT#"},
            )
            return [
                Product(
                    product_id=item["pk"].replace("PRODUCT#", ""),
                    name=item["name"],
                    price=float(item["price"]),
                )
                for item in response["Items"]
            ]

    with mock_aws():
        # Create table (simulating fixture)
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName="products",
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
        print("Created DynamoDB table: products")

        # Use repository
        repo = ProductRepository("products")

        # Save products
        products = [
            Product("001", "Widget", 9.99),
            Product("002", "Gadget", 19.99),
            Product("003", "Gizmo", 29.99),
        ]

        for product in products:
            repo.save(product)
            print(f"Saved: {product.name} (${product.price})")

        # Get single product
        print("\nRetrieving product 002:")
        p = repo.get("002")
        if p:
            print(f"  {p.name}: ${p.price}")

        # List all products
        print("\nAll products:")
        for p in repo.list_all():
            print(f"  - {p.product_id}: {p.name} (${p.price})")

    print()
    print("Run the tests with:")
    print("  pytest tests/test_fixtures.py -v")
    print()
    print("Example completed!")


if __name__ == "__main__":
    main()
