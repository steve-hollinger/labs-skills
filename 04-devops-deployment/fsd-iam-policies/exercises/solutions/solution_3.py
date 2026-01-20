"""Solution 3: Multi-Service Policy"""

import yaml

POLICY = """
iam:
  policy_statements:
    # SQS consumer
    - sid: SQSConsumer
      effect: Allow
      actions:
        - sqs:ReceiveMessage
        - sqs:DeleteMessage
        - sqs:GetQueueAttributes
        - sqs:ChangeMessageVisibility
      resources:
        - arn:aws:sqs:us-east-1:111111111111:work-queue
        - arn:aws:sqs:us-east-1:111111111111:work-queue-dlq

    # DynamoDB writer
    - sid: DynamoDBWriter
      effect: Allow
      actions:
        - dynamodb:PutItem
        - dynamodb:UpdateItem
      resources:
        - arn:aws:dynamodb:us-east-1:111111111111:table/results

    # SNS publisher
    - sid: SNSPublisher
      effect: Allow
      actions:
        - sns:Publish
      resources:
        - arn:aws:sns:us-east-1:111111111111:notifications
"""

if __name__ == "__main__":
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

    # Check SQS includes DLQ
    all_resources = []
    for stmt in stmts:
        all_resources.extend(stmt.get('resources', []))
    resource_str = ' '.join(all_resources)
    assert 'dlq' in resource_str.lower(), "Should include DLQ queue"

    print("Solution 3: All tests passed!")
