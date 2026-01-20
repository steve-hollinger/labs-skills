"""Exercise 1: Design a Blog Platform Schema

Design a DynamoDB single-table schema for a blog platform with
the following entities: Users, Posts, and Comments.

Requirements:
1. Users have a unique ID, username, email, and bio
2. Posts belong to a user and have title, content, tags, and timestamps
3. Comments belong to posts and have author info and content

Access Patterns to Support:
- Get user by ID
- Get user by username (for login)
- Get all posts by a user
- Get a single post
- Get all comments on a post
- Get recent posts (across all users)

Instructions:
1. Define the key schema (PK and SK patterns)
2. Determine if/which GSIs are needed
3. Implement the item creation functions
4. Test your queries work correctly

Hints:
- Use entity prefixes (USER#, POST#, COMMENT#)
- Consider what data lives under what partition
- Think about sort key ordering for time-based queries
- GSIs can support username lookup and recent posts
"""

from decimal import Decimal
from typing import Any

import boto3
from moto import mock_aws


def create_blog_table() -> dict[str, Any]:
    """Create the blog platform table schema.

    TODO: Define the table with appropriate GSIs.

    Returns:
        Table creation parameters
    """
    # TODO: Implement table schema
    # Think about:
    # - What GSIs do you need?
    # - What attributes need to be defined?
    return {
        "TableName": "BlogPlatform",
        "KeySchema": [
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
            # TODO: Add GSI attributes
        ],
        # TODO: Add GlobalSecondaryIndexes
        "BillingMode": "PAY_PER_REQUEST",
    }


def create_user_item(
    user_id: str,
    username: str,
    email: str,
    bio: str = "",
) -> dict[str, Any]:
    """Create a user item.

    TODO: Implement with proper key structure and GSI attributes.

    Think about:
    - How to look up user by ID
    - How to look up user by username

    Args:
        user_id: Unique user identifier
        username: Unique username for login
        email: User email
        bio: User biography

    Returns:
        DynamoDB item dictionary
    """
    # TODO: Implement user item
    return {}


def create_post_item(
    post_id: str,
    author_id: str,
    title: str,
    content: str,
    tags: list[str],
    created_at: str,
) -> dict[str, Any]:
    """Create a blog post item.

    TODO: Implement with proper key structure.

    Think about:
    - Getting all posts by a user
    - Getting recent posts globally
    - Direct post lookup

    Args:
        post_id: Unique post identifier
        author_id: Author's user ID
        title: Post title
        content: Post content
        tags: List of tags
        created_at: Creation timestamp

    Returns:
        DynamoDB item dictionary
    """
    # TODO: Implement post item
    return {}


def create_comment_item(
    comment_id: str,
    post_id: str,
    author_id: str,
    author_name: str,
    content: str,
    created_at: str,
) -> dict[str, Any]:
    """Create a comment item.

    TODO: Implement with proper key structure.

    Think about:
    - Getting all comments on a post
    - Comments should be sorted by time

    Args:
        comment_id: Unique comment identifier
        post_id: Parent post ID
        author_id: Comment author's user ID
        author_name: Author's display name (denormalized)
        content: Comment content
        created_at: Creation timestamp

    Returns:
        DynamoDB item dictionary
    """
    # TODO: Implement comment item
    return {}


def get_user_posts(table: Any, user_id: str) -> list[dict[str, Any]]:
    """Get all posts by a user.

    TODO: Implement query.

    Args:
        table: DynamoDB table resource
        user_id: User ID to query

    Returns:
        List of post items
    """
    # TODO: Implement query
    return []


def get_post_comments(table: Any, post_id: str) -> list[dict[str, Any]]:
    """Get all comments on a post.

    TODO: Implement query.

    Args:
        table: DynamoDB table resource
        post_id: Post ID to query

    Returns:
        List of comment items
    """
    # TODO: Implement query
    return []


def get_recent_posts(table: Any, limit: int = 10) -> list[dict[str, Any]]:
    """Get recent posts across all users.

    TODO: Implement query using GSI.

    Args:
        table: DynamoDB table resource
        limit: Maximum posts to return

    Returns:
        List of recent posts
    """
    # TODO: Implement GSI query
    return []


@mock_aws
def exercise() -> None:
    """Test your blog schema implementation."""
    print("Exercise 1: Blog Platform Schema")
    print("=" * 50)

    # Create resources
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    client = boto3.client("dynamodb", region_name="us-east-1")

    # Create table
    schema = create_blog_table()
    client.create_table(**schema)
    table = dynamodb.Table("BlogPlatform")

    # TODO: Insert test data and verify queries work
    # 1. Create a few users
    # 2. Create posts for those users
    # 3. Create comments on posts
    # 4. Test each access pattern

    print("\nImplement the TODO sections and verify:")
    print("1. Can get user by ID")
    print("2. Can get user by username (via GSI)")
    print("3. Can get all posts by a user")
    print("4. Can get all comments on a post")
    print("5. Can get recent posts globally (via GSI)")


if __name__ == "__main__":
    exercise()
