"""Solution for Exercise 1: Test a DynamoDB-backed User Repository"""

import os
from dataclasses import dataclass
from typing import Any

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws


# Set up credentials
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@dataclass
class User:
    """User model."""

    user_id: str
    name: str
    email: str
    status: str = "active"


class UserRepository:
    """Repository for user CRUD operations."""

    def __init__(self, table_name: str) -> None:
        self.dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        self.table = self.dynamodb.Table(table_name)

    def create(self, user: User) -> None:
        """Create a new user."""
        self.table.put_item(
            Item={
                "pk": f"USER#{user.user_id}",
                "sk": "PROFILE",
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "status": user.status,
            },
            ConditionExpression="attribute_not_exists(pk)",
        )

    def get(self, user_id: str) -> User | None:
        """Get a user by ID."""
        response = self.table.get_item(Key={"pk": f"USER#{user_id}", "sk": "PROFILE"})

        if "Item" not in response:
            return None

        item = response["Item"]
        return User(
            user_id=item["user_id"],
            name=item["name"],
            email=item["email"],
            status=item.get("status", "active"),
        )

    def update(self, user_id: str, **updates: Any) -> bool:
        """Update user fields."""
        if not updates:
            return False

        update_expr = "SET " + ", ".join(f"#{k} = :{k}" for k in updates)
        attr_names = {f"#{k}": k for k in updates}
        attr_values = {f":{k}": v for k, v in updates.items()}

        try:
            self.table.update_item(
                Key={"pk": f"USER#{user_id}", "sk": "PROFILE"},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=attr_names,
                ExpressionAttributeValues=attr_values,
                ConditionExpression="attribute_exists(pk)",
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return False
            raise

    def delete(self, user_id: str) -> bool:
        """Delete a user."""
        try:
            self.table.delete_item(
                Key={"pk": f"USER#{user_id}", "sk": "PROFILE"},
                ConditionExpression="attribute_exists(pk)",
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return False
            raise

    def list_all(self) -> list[User]:
        """List all users."""
        response = self.table.scan(
            FilterExpression="begins_with(pk, :prefix)",
            ExpressionAttributeValues={":prefix": "USER#"},
        )

        return [
            User(
                user_id=item["user_id"],
                name=item["name"],
                email=item["email"],
                status=item.get("status", "active"),
            )
            for item in response["Items"]
        ]


# =============================================================================
# Fixtures and Tests (Solutions)
# =============================================================================


@pytest.fixture
def user_repository():
    """Create a mocked DynamoDB table and UserRepository."""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        dynamodb.create_table(
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

        yield UserRepository("users")


def test_create_user(user_repository: UserRepository) -> None:
    """Test creating a new user."""
    user = User(user_id="123", name="Alice", email="alice@example.com")
    user_repository.create(user)

    # Verify by getting the user
    retrieved = user_repository.get("123")
    assert retrieved is not None
    assert retrieved.user_id == "123"
    assert retrieved.name == "Alice"
    assert retrieved.email == "alice@example.com"


def test_get_user(user_repository: UserRepository) -> None:
    """Test retrieving a user by ID."""
    user = User(user_id="456", name="Bob", email="bob@example.com", status="pending")
    user_repository.create(user)

    retrieved = user_repository.get("456")

    assert retrieved is not None
    assert retrieved.user_id == "456"
    assert retrieved.name == "Bob"
    assert retrieved.email == "bob@example.com"
    assert retrieved.status == "pending"


def test_get_nonexistent_user(user_repository: UserRepository) -> None:
    """Test getting a user that doesn't exist."""
    result = user_repository.get("nonexistent")
    assert result is None


def test_update_user(user_repository: UserRepository) -> None:
    """Test updating user fields."""
    user = User(user_id="789", name="Charlie", email="charlie@example.com")
    user_repository.create(user)

    # Update user
    result = user_repository.update("789", name="Charlie Brown", status="inactive")
    assert result is True

    # Verify updates
    updated = user_repository.get("789")
    assert updated is not None
    assert updated.name == "Charlie Brown"
    assert updated.status == "inactive"
    assert updated.email == "charlie@example.com"  # Unchanged


def test_delete_user(user_repository: UserRepository) -> None:
    """Test deleting a user."""
    user = User(user_id="delete-me", name="Test", email="test@example.com")
    user_repository.create(user)

    # Verify exists
    assert user_repository.get("delete-me") is not None

    # Delete
    result = user_repository.delete("delete-me")
    assert result is True

    # Verify gone
    assert user_repository.get("delete-me") is None


def test_list_users(user_repository: UserRepository) -> None:
    """Test listing all users."""
    users = [
        User(user_id="1", name="Alice", email="alice@example.com"),
        User(user_id="2", name="Bob", email="bob@example.com"),
        User(user_id="3", name="Charlie", email="charlie@example.com"),
    ]

    for user in users:
        user_repository.create(user)

    all_users = user_repository.list_all()

    assert len(all_users) == 3
    names = {u.name for u in all_users}
    assert names == {"Alice", "Bob", "Charlie"}


def test_create_duplicate_user(user_repository: UserRepository) -> None:
    """Test that creating duplicate user fails."""
    user = User(user_id="unique", name="Original", email="original@example.com")
    user_repository.create(user)

    # Try to create duplicate
    duplicate = User(user_id="unique", name="Duplicate", email="duplicate@example.com")

    with pytest.raises(ClientError) as exc_info:
        user_repository.create(duplicate)

    assert exc_info.value.response["Error"]["Code"] == "ConditionalCheckFailedException"


def test_update_nonexistent_user(user_repository: UserRepository) -> None:
    """Test updating a user that doesn't exist."""
    result = user_repository.update("nonexistent", name="New Name")
    assert result is False


def test_delete_nonexistent_user(user_repository: UserRepository) -> None:
    """Test deleting a user that doesn't exist."""
    result = user_repository.delete("nonexistent")
    assert result is False


if __name__ == "__main__":
    import subprocess

    subprocess.run(["pytest", __file__, "-v"])
