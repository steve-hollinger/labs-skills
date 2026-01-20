"""Exercise 1: Test a DynamoDB-backed User Repository

Your task is to implement tests for the UserRepository class using moto.
The repository provides CRUD operations for user records in DynamoDB.

Instructions:
1. Create a pytest fixture that provides a mocked DynamoDB table
2. Implement tests for all UserRepository methods
3. Test error cases (user not found, duplicate user)

Expected Tests:
- test_create_user: Create a new user and verify it's stored
- test_get_user: Retrieve a user by ID
- test_get_nonexistent_user: Should return None
- test_update_user: Update user fields
- test_delete_user: Delete a user
- test_list_users: Get all users

Hints:
- Use @mock_aws decorator or context manager
- Create the table in the fixture before yielding
- Remember to specify region_name

Run your tests with:
    pytest exercises/exercise_1.py -v
"""

from dataclasses import dataclass
from typing import Any

import boto3
import pytest  # noqa: F401
from moto import mock_aws  # noqa: F401


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
        except self.dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            return False

    def delete(self, user_id: str) -> bool:
        """Delete a user."""
        try:
            self.table.delete_item(
                Key={"pk": f"USER#{user_id}", "sk": "PROFILE"},
                ConditionExpression="attribute_exists(pk)",
            )
            return True
        except self.dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            return False

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
# TODO: Implement the fixture and tests below
# =============================================================================


@pytest.fixture
def user_repository():
    """Create a mocked DynamoDB table and UserRepository.

    TODO:
    1. Use mock_aws context manager
    2. Create DynamoDB resource
    3. Create a table with pk (HASH) and sk (RANGE) keys
    4. Create and yield UserRepository instance
    """
    pass


def test_create_user(user_repository) -> None:
    """Test creating a new user.

    TODO:
    1. Create a User instance
    2. Save it using the repository
    3. Verify it was stored correctly
    """
    pass


def test_get_user(user_repository) -> None:
    """Test retrieving a user by ID.

    TODO:
    1. Create and save a user
    2. Retrieve it using get()
    3. Verify all fields are correct
    """
    pass


def test_get_nonexistent_user(user_repository) -> None:
    """Test getting a user that doesn't exist.

    TODO: Verify that get() returns None for nonexistent user
    """
    pass


def test_update_user(user_repository) -> None:
    """Test updating user fields.

    TODO:
    1. Create a user
    2. Update some fields
    3. Verify the updates were applied
    """
    pass


def test_delete_user(user_repository) -> None:
    """Test deleting a user.

    TODO:
    1. Create a user
    2. Delete it
    3. Verify it's gone
    """
    pass


def test_list_users(user_repository) -> None:
    """Test listing all users.

    TODO:
    1. Create multiple users
    2. List all users
    3. Verify count and content
    """
    pass


def test_create_duplicate_user(user_repository) -> None:
    """Test that creating duplicate user fails.

    TODO:
    1. Create a user
    2. Try to create another user with same ID
    3. Verify it raises an exception
    """
    pass


if __name__ == "__main__":
    import subprocess

    subprocess.run(["pytest", __file__, "-v"])
