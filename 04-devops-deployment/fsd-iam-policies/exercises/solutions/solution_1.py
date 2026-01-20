"""Solution 1: DynamoDB Read-Only Policy"""

import yaml

POLICY = """
iam:
  policy_statements:
    - sid: DynamoDBReadOnly
      effect: Allow
      actions:
        - dynamodb:GetItem
        - dynamodb:BatchGetItem
        - dynamodb:Query
        - dynamodb:Scan
      resources:
        - arn:aws:dynamodb:us-west-2:123456789012:table/products
        - arn:aws:dynamodb:us-west-2:123456789012:table/products/index/*
"""

if __name__ == "__main__":
    config = yaml.safe_load(POLICY)
    stmt = config['iam']['policy_statements'][0]

    # Verify it's read-only
    write_actions = ['PutItem', 'UpdateItem', 'DeleteItem', 'BatchWriteItem']
    for action in stmt.get('actions', []):
        for write_action in write_actions:
            assert write_action not in action, f"Policy should not include {write_action}"

    # Verify required read actions
    read_actions = ['GetItem', 'Query', 'Scan']
    action_str = ' '.join(stmt.get('actions', []))
    for read_action in read_actions:
        assert read_action in action_str, f"Policy should include {read_action}"

    # Verify index access
    resources = stmt.get('resources', [])
    assert any('index' in r for r in resources), "Policy should include index permissions"

    print("Solution 1: All tests passed!")
