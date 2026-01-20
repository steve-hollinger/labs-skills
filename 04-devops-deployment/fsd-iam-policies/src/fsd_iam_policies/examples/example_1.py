"""Example 1: Basic DynamoDB read/write policy.

This example shows how to create a least-privilege IAM policy
for DynamoDB table access in FSD services.
"""

import yaml


DYNAMODB_POLICY = """
# FSD service with DynamoDB access
service:
  name: user-service
  platform: ecs

iam:
  policy_statements:
    # Read operations
    - sid: DynamoDBRead
      effect: Allow
      actions:
        - dynamodb:GetItem
        - dynamodb:BatchGetItem
        - dynamodb:Query
        - dynamodb:Scan
      resources:
        - arn:aws:dynamodb:${AWS_REGION}:${AWS_ACCOUNT}:table/users
        - arn:aws:dynamodb:${AWS_REGION}:${AWS_ACCOUNT}:table/users/index/*

    # Write operations
    - sid: DynamoDBWrite
      effect: Allow
      actions:
        - dynamodb:PutItem
        - dynamodb:UpdateItem
        - dynamodb:DeleteItem
        - dynamodb:BatchWriteItem
      resources:
        - arn:aws:dynamodb:${AWS_REGION}:${AWS_ACCOUNT}:table/users

    # Stream access (for CDC)
    - sid: DynamoDBStreams
      effect: Allow
      actions:
        - dynamodb:GetRecords
        - dynamodb:GetShardIterator
        - dynamodb:DescribeStream
        - dynamodb:ListStreams
      resources:
        - arn:aws:dynamodb:${AWS_REGION}:${AWS_ACCOUNT}:table/users/stream/*
"""


def main() -> None:
    """Demonstrate DynamoDB IAM policy patterns."""
    print("DynamoDB IAM Policy Example")
    print("=" * 60)

    # Parse and display the policy
    config = yaml.safe_load(DYNAMODB_POLICY)

    print(f"\nService: {config['service']['name']}")
    print(f"Platform: {config['service']['platform']}")

    print("\nPolicy Statements:")
    for stmt in config['iam']['policy_statements']:
        print(f"\n  {stmt['sid']}:")
        print(f"    Effect: {stmt['effect']}")
        print(f"    Actions: {len(stmt['actions'])} actions")
        for action in stmt['actions'][:3]:
            print(f"      - {action}")
        if len(stmt['actions']) > 3:
            print(f"      ... and {len(stmt['actions']) - 3} more")
        print(f"    Resources: {len(stmt['resources'])} resource(s)")

    print("\n" + "=" * 60)
    print("Best Practices Demonstrated:")
    print("1. Separate read and write permissions (different SIDs)")
    print("2. Specific resource ARNs (not * wildcards)")
    print("3. Index permissions included for Query operations")
    print("4. Stream access separated for CDC patterns")


if __name__ == "__main__":
    main()
