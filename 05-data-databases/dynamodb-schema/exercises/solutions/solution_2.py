"""Solution for Exercise 2: Extended Blog Schema with GSIs

This solution demonstrates advanced GSI patterns including:
- Tag-based queries with many-to-many relationship
- Trending posts with numeric sorting
- Email domain search with inverted strings
"""

from typing import Any

import boto3
from moto import mock_aws


def create_extended_blog_table() -> dict[str, Any]:
    """Create blog table with advanced GSIs."""
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
            {"AttributeName": "GSI2PK", "AttributeType": "S"},
            {"AttributeName": "GSI2SK", "AttributeType": "S"},
            {"AttributeName": "GSI3PK", "AttributeType": "S"},
            {"AttributeName": "GSI3SK", "AttributeType": "S"},
            {"AttributeName": "GSI4PK", "AttributeType": "S"},
            {"AttributeName": "GSI4SK", "AttributeType": "S"},
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
            {
                "IndexName": "GSI3",
                "KeySchema": [
                    {"AttributeName": "GSI3PK", "KeyType": "HASH"},
                    {"AttributeName": "GSI3SK", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "GSI4",
                "KeySchema": [
                    {"AttributeName": "GSI4PK", "KeyType": "HASH"},
                    {"AttributeName": "GSI4SK", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST",
    }


def format_view_count_for_sort(view_count: int) -> str:
    """Format view count as zero-padded string for lexicographic sorting.

    DynamoDB sorts strings lexicographically, so we need to zero-pad
    numbers to get correct numeric ordering.

    Examples:
        42 -> "00000000042"
        1000 -> "00000001000"
    """
    return f"{view_count:011d}"


def invert_string(s: str) -> str:
    """Invert a string for suffix-based queries.

    By inverting strings, we can use begins_with for suffix matching.
    Example: "user@company.com" -> "moc.ynapmoc@resu"
    """
    return s[::-1]


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

    Returns multiple items:
    1. Main post item (with trending GSI)
    2. One tag-post mapping item per tag
    """
    items = []

    # Main post item
    main_post = {
        "PK": f"USER#{author_id}",
        "SK": f"POST#{created_at}#{post_id}",
        # GSI1: Recent posts
        "GSI1PK": "POSTS",
        "GSI1SK": f"POST#{created_at}#{post_id}",
        # GSI3: Trending by view count
        "GSI3PK": "TRENDING",
        "GSI3SK": f"VIEWS#{format_view_count_for_sort(view_count)}#{post_id}",
        # Data
        "entity_type": "POST",
        "post_id": post_id,
        "author_id": author_id,
        "title": title,
        "content": content,
        "tags": tags,
        "created_at": created_at,
        "view_count": view_count,
    }
    items.append(main_post)

    # Tag index items (one per tag)
    # This enables "get posts by tag" queries
    for tag in tags:
        tag_item = {
            "PK": f"TAG#{tag.lower()}",
            "SK": f"POST#{created_at}#{post_id}",
            # GSI2: Alternative tag lookup (could group by popularity)
            "GSI2PK": f"TAG#{tag.lower()}",
            "GSI2SK": f"POST#{created_at}#{post_id}",
            # Data (denormalized for display without fetching main post)
            "entity_type": "TAG_POST",
            "tag": tag.lower(),
            "post_id": post_id,
            "author_id": author_id,
            "title": title,
            "created_at": created_at,
        }
        items.append(tag_item)

    return items


def create_user_with_email_index(
    user_id: str,
    username: str,
    email: str,
    bio: str = "",
) -> dict[str, Any]:
    """Create user with email domain index using inverted email."""
    inverted_email = invert_string(email.lower())

    return {
        "PK": f"USER#{user_id}",
        "SK": f"PROFILE#{user_id}",
        # GSI1: Username lookup
        "GSI1PK": f"USERNAME#{username}",
        "GSI1SK": f"USER#{user_id}",
        # GSI4: Email domain lookup (inverted)
        "GSI4PK": "EMAIL",
        "GSI4SK": f"EMAIL#{inverted_email}",
        # Data
        "entity_type": "USER",
        "user_id": user_id,
        "username": username,
        "email": email,
        "email_inverted": inverted_email,
        "bio": bio,
    }


def update_view_count(
    table: Any,
    post_pk: str,
    post_sk: str,
    new_view_count: int,
    post_id: str,
) -> None:
    """Update post view count and GSI3 sort key for trending."""
    table.update_item(
        Key={"PK": post_pk, "SK": post_sk},
        UpdateExpression="SET view_count = :vc, GSI3SK = :gsi3sk",
        ExpressionAttributeValues={
            ":vc": new_view_count,
            ":gsi3sk": f"VIEWS#{format_view_count_for_sort(new_view_count)}#{post_id}",
        },
    )


def get_posts_by_tag(table: Any, tag: str, limit: int = 20) -> list[dict[str, Any]]:
    """Get posts with a specific tag, newest first."""
    response = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :sk_prefix)",
        ExpressionAttributeValues={
            ":pk": f"TAG#{tag.lower()}",
            ":sk_prefix": "POST#",
        },
        ScanIndexForward=False,  # Newest first
        Limit=limit,
    )
    return response.get("Items", [])


def get_trending_posts(table: Any, limit: int = 10) -> list[dict[str, Any]]:
    """Get posts sorted by view count (highest first)."""
    response = table.query(
        IndexName="GSI3",
        KeyConditionExpression="GSI3PK = :pk",
        ExpressionAttributeValues={":pk": "TRENDING"},
        ScanIndexForward=False,  # Highest views first (descending)
        Limit=limit,
    )
    return response.get("Items", [])


def get_users_by_email_domain(table: Any, domain: str) -> list[dict[str, Any]]:
    """Get users by email domain using inverted email pattern.

    To find all users @company.com:
    1. Invert domain: "company.com" -> "moc.ynapmoc"
    2. Query GSI4 with begins_with on inverted email
    """
    inverted_domain = invert_string(domain.lower())

    response = table.query(
        IndexName="GSI4",
        KeyConditionExpression="GSI4PK = :pk AND begins_with(GSI4SK, :sk_prefix)",
        ExpressionAttributeValues={
            ":pk": "EMAIL",
            ":sk_prefix": f"EMAIL#{inverted_domain}",
        },
    )
    return response.get("Items", [])


@mock_aws
def solution() -> None:
    """Demonstrate the extended blog schema solution."""
    print("Solution 2: Extended Blog Schema with GSIs")
    print("=" * 50)

    # Create resources
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    client = boto3.client("dynamodb", region_name="us-east-1")

    # Create table
    schema = create_extended_blog_table()
    client.create_table(**schema)
    table = dynamodb.Table("BlogPlatformExtended")

    # Create test data
    print("\n--- Creating Test Data ---\n")

    # Users with different email domains
    users = [
        create_user_with_email_index("u1", "alice", "alice@company.com", "Engineer"),
        create_user_with_email_index("u2", "bob", "bob@company.com", "Designer"),
        create_user_with_email_index("u3", "carol", "carol@gmail.com", "Writer"),
    ]

    # Posts with tags and view counts
    post_batches = [
        create_post_with_tags(
            "p1", "u1", "DynamoDB Basics", "Content...",
            ["dynamodb", "aws", "tutorial"],
            "2024-01-10T10:00:00Z", view_count=1500
        ),
        create_post_with_tags(
            "p2", "u1", "Advanced GSI Patterns", "Content...",
            ["dynamodb", "aws", "advanced"],
            "2024-01-15T10:00:00Z", view_count=3200
        ),
        create_post_with_tags(
            "p3", "u2", "Python Tips", "Content...",
            ["python", "tutorial"],
            "2024-01-12T10:00:00Z", view_count=800
        ),
        create_post_with_tags(
            "p4", "u3", "AWS Tutorial", "Content...",
            ["aws", "tutorial"],
            "2024-01-14T10:00:00Z", view_count=2100
        ),
    ]

    # Insert all data
    with table.batch_writer() as batch:
        for user in users:
            batch.put_item(Item=user)
        for posts in post_batches:
            for item in posts:
                batch.put_item(Item=item)

    print("Inserted 3 users and 4 posts with tags")

    # Demonstrate access patterns
    print("\n--- Access Pattern Demonstrations ---\n")

    # 1. Posts by tag
    print("1. Get posts with 'aws' tag:")
    aws_posts = get_posts_by_tag(table, "aws")
    for post in aws_posts:
        print(f"   - {post['title']}")

    print("\n2. Get posts with 'tutorial' tag:")
    tutorial_posts = get_posts_by_tag(table, "tutorial")
    for post in tutorial_posts:
        print(f"   - {post['title']}")

    # 2. Trending posts
    print("\n3. Get trending posts (by view count):")
    trending = get_trending_posts(table, limit=5)
    for post in trending:
        print(f"   - {post['title']}: {post['view_count']} views")

    # 3. Update view count and check trending again
    print("\n4. After updating 'Python Tips' to 5000 views:")
    update_view_count(
        table,
        "USER#u2",
        "POST#2024-01-12T10:00:00Z#p3",
        5000,
        "p3"
    )
    trending = get_trending_posts(table, limit=5)
    for post in trending:
        print(f"   - {post['title']}: {post['view_count']} views")

    # 4. Users by email domain
    print("\n5. Get users @company.com:")
    company_users = get_users_by_email_domain(table, "company.com")
    for user in company_users:
        print(f"   - {user['username']} ({user['email']})")

    print("\n6. Get users @gmail.com:")
    gmail_users = get_users_by_email_domain(table, "gmail.com")
    for user in gmail_users:
        print(f"   - {user['username']} ({user['email']})")

    print("\n" + "=" * 50)
    print("Key Techniques:")
    print("1. Tag items: Separate items for many-to-many tag relationships")
    print("2. View count: Zero-padded for lexicographic sorting")
    print("3. Email domain: Inverted strings enable suffix queries")
    print("\nSolution completed successfully!")


if __name__ == "__main__":
    solution()
