"""Exercise 1: Create a DynamoDB Read-Only Policy

Your task: Create an FSD IAM policy that allows a service to read
from a DynamoDB table but NOT write to it.

Requirements:
1. Allow GetItem, Query, Scan, BatchGetItem
2. Include permissions for GSI indexes
3. Use the table name 'products' in account 123456789012, region us-west-2
"""

# TODO: Fill in the policy YAML
POLICY = """
# Your policy here
iam:
  policy_statements:
    - sid: # TODO
      effect: # TODO
      actions:
        # TODO: Add read actions
      resources:
        # TODO: Add table and index ARNs
"""

# Test your policy
if __name__ == "__main__":
    import yaml

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

    print("Policy looks good!")
