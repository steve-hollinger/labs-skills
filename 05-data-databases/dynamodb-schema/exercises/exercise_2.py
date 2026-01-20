"""Exercise 2: Add GSIs for Tag-Based Queries and Recent Posts

Extend the blog platform schema to support additional access patterns
using Global Secondary Indexes.

Requirements:
1. Query posts by tag
2. Get trending posts (by view count)
3. Search users by email domain (for admin)

New Access Patterns:
- Get all posts with a specific tag
- Get most viewed posts (trending)
- Find users by email domain (e.g., "@company.com")

Instructions:
1. Design GSI key patterns for each access pattern
2. Modify item creation to include GSI attributes
3. Implement query functions
4. Consider write amplification costs

Hints:
- Tags are many-to-many: one post has many tags, one tag has many posts
- For tags, you might need to create separate items per tag
- Trending posts need numeric sort, but SK must be string
- Email domain can use begins_with with inverted email
"""

from decimal import Decimal
from typing import Any

import boto3
from moto import mock_aws


def create_extended_blog_table() -> dict[str, Any]:
    """Create blog table with additional GSIs.

    TODO: Add GSIs for:
    - GSI2: Posts by tag
    - GSI3: Posts by view count (trending)
    - GSI4: Users by email domain

    Returns:
        Table creation parameters
    """
    return {
        "TableName": "BlogPlatformExtended",
        "KeySchema": [
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
            {"AttributeName": "GSI1PK", "AttributeType": "S"},
            {"AttributeName": "GSI1SK", "AttributeType": "S"},
            # TODO: Add more GSI attributes
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
            # TODO: Add GSI2, GSI3, GSI4
        ],
        "BillingMode": "PAY_PER_REQUEST",
    }


def create_post_with_tags(
    post_id: str,
    author_id: str,
    title: str,
    content: str,
    tags: list[str],
    created_at: str,
    view_count: int = 0,
) -> list[dict[str, Any]]:
    """Create a post with tag index items.

    For tag-based queries, we need to create additional items
    that map tags to posts.

    TODO: Return list of items to insert:
    - Main post item
    - One TAG# item per tag for the tag GSI

    Args:
        post_id: Unique post identifier
        author_id: Author's user ID
        title: Post title
        content: Post content
        tags: List of tags
        created_at: Creation timestamp
        view_count: Number of views

    Returns:
        List of DynamoDB items to insert
    """
    items = []

    # TODO: Create main post item
    # Include GSI3 attributes for trending query
    # Hint: For numeric sorting in string SK, zero-pad the number
    # e.g., view_count=42 -> GSI3SK="VIEWS#00000042#post-123"
    main_post = {}
    items.append(main_post)

    # TODO: Create tag index items
    # One item per tag for querying posts by tag
    # Think about:
    # - PK: TAG#{tag_name}
    # - SK: POST#{created_at}#{post_id}
    for tag in tags:
        tag_item = {}
        items.append(tag_item)

    return items


def create_user_with_email_index(
    user_id: str,
    username: str,
    email: str,
    bio: str = "",
) -> dict[str, Any]:
    """Create user with email domain index.

    For querying users by email domain, we can use begins_with
    on a reversed/inverted email address.

    TODO: Implement with GSI for email domain queries.

    Hint: Invert email "user@company.com" -> "moc.ynapmoc@resu"
    Then query begins_with "moc.ynapmoc" finds all @company.com users

    Args:
        user_id: User ID
        username: Username
        email: Email address
        bio: Bio text

    Returns:
        User item with email domain GSI
    """
    # TODO: Implement
    # Include GSI4PK and GSI4SK for email domain queries
    return {}


def update_view_count(
    table: Any,
    post_pk: str,
    post_sk: str,
    new_view_count: int,
) -> None:
    """Update post view count and GSI3 sort key.

    When view count changes, we need to update the GSI3SK
    so trending queries reflect the new count.

    TODO: Implement update that changes both view_count and GSI3SK

    Args:
        table: DynamoDB table
        post_pk: Post partition key
        post_sk: Post sort key
        new_view_count: New view count
    """
    # TODO: Implement update
    # Update both view_count attribute and GSI3SK
    pass


def get_posts_by_tag(table: Any, tag: str, limit: int = 20) -> list[dict[str, Any]]:
    """Get posts with a specific tag.

    TODO: Query the tag GSI.

    Args:
        table: DynamoDB table
        tag: Tag to search for
        limit: Maximum posts to return

    Returns:
        List of posts with this tag
    """
    # TODO: Implement GSI query
    return []


def get_trending_posts(table: Any, limit: int = 10) -> list[dict[str, Any]]:
    """Get posts sorted by view count (descending).

    TODO: Query the trending GSI.

    Args:
        table: DynamoDB table
        limit: Maximum posts to return

    Returns:
        List of trending posts
    """
    # TODO: Implement GSI query
    # Remember: ScanIndexForward=False for descending order
    return []


def get_users_by_email_domain(
    table: Any,
    domain: str,
) -> list[dict[str, Any]]:
    """Get users by email domain.

    TODO: Query using inverted email pattern.

    Args:
        table: DynamoDB table
        domain: Email domain (e.g., "company.com")

    Returns:
        List of users with this email domain
    """
    # TODO: Implement
    # Invert the domain and use begins_with
    return []


@mock_aws
def exercise() -> None:
    """Test your extended blog schema."""
    print("Exercise 2: Extended Blog Schema with GSIs")
    print("=" * 50)

    # Create resources
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    client = boto3.client("dynamodb", region_name="us-east-1")

    # Create table
    schema = create_extended_blog_table()
    client.create_table(**schema)
    table = dynamodb.Table("BlogPlatformExtended")

    # TODO: Test your implementation
    # 1. Create posts with various tags
    # 2. Test get_posts_by_tag
    # 3. Update view counts
    # 4. Test get_trending_posts
    # 5. Create users with different email domains
    # 6. Test get_users_by_email_domain

    print("\nImplement the TODO sections and verify:")
    print("1. Posts by tag query works")
    print("2. Trending posts returns highest view counts first")
    print("3. Email domain search finds correct users")
    print("4. View count updates reflect in trending order")


if __name__ == "__main__":
    exercise()
