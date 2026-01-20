"""Exercise 3: Create a Multi-Service Policy

Your task: Create an FSD IAM policy for a worker service that:
1. Consumes messages from an SQS queue
2. Writes results to a DynamoDB table
3. Publishes notifications to an SNS topic

Requirements:
- SQS: queue name 'work-queue', include DLQ
- DynamoDB: table name 'results'
- SNS: topic name 'notifications'
- All in us-east-1, account 111111111111
"""

# TODO: Fill in the policy YAML
POLICY = """
iam:
  policy_statements:
    # SQS consumer
    - sid: # TODO
      # TODO

    # DynamoDB writer
    - sid: # TODO
      # TODO

    # SNS publisher
    - sid: # TODO
      # TODO
"""

if __name__ == "__main__":
    import yaml

    config = yaml.safe_load(POLICY)
    stmts = config['iam']['policy_statements']

    # Should have 3 statements
    assert len(stmts) >= 3, "Should have at least 3 statements"

    # Check for each service
    all_actions = []
    for stmt in stmts:
        all_actions.extend(stmt.get('actions', []))

    action_str = ' '.join(all_actions)
    assert 'sqs' in action_str.lower(), "Should have SQS actions"
    assert 'dynamodb' in action_str.lower(), "Should have DynamoDB actions"
    assert 'sns' in action_str.lower(), "Should have SNS actions"

    print("Multi-service policy looks good!")
