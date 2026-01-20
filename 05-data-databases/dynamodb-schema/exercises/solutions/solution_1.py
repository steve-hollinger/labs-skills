"""Solution for Exercise 1: Blog Platform Schema

This solution demonstrates a complete single-table design for a blog platform
with users, posts, and comments.
"""

from typing import Any

import boto3
from moto import mock_aws


def create_blog_table() -> dict[str, Any]:
    """Create the blog platform table schema with GSIs.

    GSI1: Username lookup and recent posts
    """
    return {
        "TableName": "BlogPlatform",
        "KeySchema": [
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
            {"AttributeName": "GSI1PK", "AttributeType": "S"},
            {"AttributeName": "GSI1SK", "AttributeType": "S"},
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
        ],
        "BillingMode": "PAY_PER_REQUEST",
    }


def create_user_item(
    user_id: str,
    username: str,
    email: str,
    bio: str = "",
) -> dict[str, Any]:
    """Create a user item with username lookup GSI.

    Key Design:
    - PK: USER#{user_id} - Direct lookup by ID
    - SK: PROFILE#{user_id}
    - GSI1PK: USERNAME#{username} - Lookup by username
    - GSI1SK: USER#{user_id}
    """
    return {
        "PK": f"USER#{user_id}",
        "SK": f"PROFILE#{user_id}",
        "GSI1PK": f"USERNAME#{username}",
        "GSI1SK": f"USER#{user_id}",
        "entity_type": "USER",
        "user_id": user_id,
        "username": username,
        "email": email,
        "bio": bio,
    }


def create_post_item(
    post_id: str,
    author_id: str,
    title: str,
    content: str,
    tags: list[str],
    created_at: str,
) -> dict[str, Any]:
    """Create a blog post item.

    Key Design:
    - PK: USER#{author_id} - Store under author for "get user's posts"
    - SK: POST#{created_at}#{post_id} - Sorted by date
    - GSI1PK: POSTS - All posts for "recent posts" query
    - GSI1SK: POST#{created_at}#{post_id} - Sorted by date globally
    """
    return {
        "PK": f"USER#{author_id}",
        "SK": f"POST#{created_at}#{post_id}",
        "GSI1PK": "POSTS",  # All posts in one GSI partition
        "GSI1SK": f"POST#{created_at}#{post_id}",
        "entity_type": "POST",
        "post_id": post_id,
        "author_id": author_id,
        "title": title,
        "content": content,
        "tags": tags,
        "created_at": created_at,
    }


def create_comment_item(
    comment_id: str,
    post_id: str,
    author_id: str,
    author_name: str,
    content: str,
    created_at: str,
) -> dict[str, Any]:
    """Create a comment item under a post.

    Key Design:
    - PK: POST#{post_id} - Store under post for "get post comments"
    - SK: COMMENT#{created_at}#{comment_id} - Sorted by time
    """
    return {
        "PK": f"POST#{post_id}",
        "SK": f"COMMENT#{created_at}#{comment_id}",
        "entity_type": "COMMENT",
        "comment_id": comment_id,
        "post_id": post_id,
        "author_id": author_id,
        "author_name": author_name,  # Denormalized for display
        "content": content,
        "created_at": created_at,
    }


def get_user_by_id(table: Any, user_id: str) -> dict[str, Any] | None:
    """Get user by ID (direct lookup)."""
    response = table.get_item(
        Key={"PK": f"USER#{user_id}", "SK": f"PROFILE#{user_id}"}
    )
    return response.get("Item")


def get_user_by_username(table: Any, username: str) -> dict[str, Any] | None:
    """Get user by username (GSI query)."""
    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression="GSI1PK = :pk",
        ExpressionAttributeValues={":pk": f"USERNAME#{username}"},
        Limit=1,
    )
    items = response.get("Items", [])
    return items[0] if items else None


def get_user_posts(table: Any, user_id: str) -> list[dict[str, Any]]:
    """Get all posts by a user, newest first."""
    response = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :sk_prefix)",
        ExpressionAttributeValues={
            ":pk": f"USER#{user_id}",
            ":sk_prefix": "POST#",
        },
        ScanIndexForward=False,  # Newest first
    )
    return response.get("Items", [])


def get_post_comments(table: Any, post_id: str) -> list[dict[str, Any]]:
    """Get all comments on a post, oldest first."""
    response = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :sk_prefix)",
        ExpressionAttributeValues={
            ":pk": f"POST#{post_id}",
            ":sk_prefix": "COMMENT#",
        },
        ScanIndexForward=True,  # Oldest first (chronological)
    )
    return response.get("Items", [])


def get_recent_posts(table: Any, limit: int = 10) -> list[dict[str, Any]]:
    """Get recent posts across all users."""
    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression="GSI1PK = :pk",
        ExpressionAttributeValues={":pk": "POSTS"},
        ScanIndexForward=False,  # Newest first
        Limit=limit,
    )
    return response.get("Items", [])


@mock_aws
def solution() -> None:
    """Demonstrate the complete blog schema solution."""
    print("Solution 1: Blog Platform Schema")
    print("=" * 50)

    # Create resources
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    client = boto3.client("dynamodb", region_name="us-east-1")

    # Create table
    schema = create_blog_table()
    client.create_table(**schema)
    table = dynamodb.Table("BlogPlatform")

    # Create test data
    print("\n--- Creating Test Data ---\n")

    # Users
    users = [
        create_user_item("user-001", "alice", "alice@example.com", "Python developer"),
        create_user_item("user-002", "bob", "bob@example.com", "Tech blogger"),
    ]

    # Posts
    posts = [
        create_post_item(
            "post-001", "user-001", "Getting Started with DynamoDB",
            "DynamoDB is a fully managed NoSQL database...",
            ["dynamodb", "aws", "nosql"],
            "2024-01-15T10:00:00Z"
        ),
        create_post_item(
            "post-002", "user-001", "Single Table Design Patterns",
            "Single table design is a powerful pattern...",
            ["dynamodb", "patterns"],
            "2024-01-16T14:00:00Z"
        ),
        create_post_item(
            "post-003", "user-002", "Python Best Practices",
            "Here are my favorite Python tips...",
            ["python", "tips"],
            "2024-01-17T09:00:00Z"
        ),
    ]

    # Comments
    comments = [
        create_comment_item(
            "comment-001", "post-001", "user-002", "bob",
            "Great introduction!", "2024-01-15T12:00:00Z"
        ),
        create_comment_item(
            "comment-002", "post-001", "user-001", "alice",
            "Thanks Bob!", "2024-01-15T13:00:00Z"
        ),
    ]

    # Insert all data
    with table.batch_writer() as batch:
        for user in users:
            batch.put_item(Item=user)
        for post in posts:
            batch.put_item(Item=post)
        for comment in comments:
            batch.put_item(Item=comment)

    print("Inserted 2 users, 3 posts, 2 comments")

    # Demonstrate access patterns
    print("\n--- Access Pattern Demonstrations ---\n")

    # 1. Get user by ID
    print("1. Get user by ID ('user-001'):")
    user = get_user_by_id(table, "user-001")
    if user:
        print(f"   Found: {user['username']} - {user['email']}")

    # 2. Get user by username
    print("\n2. Get user by username ('bob'):")
    user = get_user_by_username(table, "bob")
    if user:
        print(f"   Found: {user['user_id']} - {user['bio']}")

    # 3. Get all posts by user
    print("\n3. Get all posts by user 'alice':")
    user_posts = get_user_posts(table, "user-001")
    for post in user_posts:
        print(f"   - {post['title']} ({post['created_at']})")

    # 4. Get comments on post
    print("\n4. Get comments on post-001:")
    post_comments = get_post_comments(table, "post-001")
    for comment in post_comments:
        print(f"   - {comment['author_name']}: {comment['content']}")

    # 5. Get recent posts globally
    print("\n5. Get recent posts (all users):")
    recent = get_recent_posts(table, limit=5)
    for post in recent:
        print(f"   - {post['title']} by {post['author_id']}")

    print("\n" + "=" * 50)
    print("Schema Design Summary:")
    print("- Users: PK=USER#{id}, SK=PROFILE#{id}")
    print("- Posts: PK=USER#{author}, SK=POST#{date}#{id}")
    print("- Comments: PK=POST#{id}, SK=COMMENT#{date}#{id}")
    print("- GSI1: Username lookup + Recent posts")
    print("\nSolution completed successfully!")


if __name__ == "__main__":
    solution()
