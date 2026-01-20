"""Example 3: Cross-service permissions (SQS, SNS, Secrets Manager).

This example shows how to create IAM policies for services that
interact with multiple AWS services.
"""

import yaml


CROSS_SERVICE_POLICY = """
# FSD service with multiple AWS service integrations
service:
  name: notification-service
  platform: ecs

iam:
  policy_statements:
    # SQS - Receive and delete messages
    - sid: SQSConsumer
      effect: Allow
      actions:
        - sqs:ReceiveMessage
        - sqs:DeleteMessage
        - sqs:GetQueueAttributes
        - sqs:ChangeMessageVisibility
      resources:
        - arn:aws:sqs:${AWS_REGION}:${AWS_ACCOUNT}:notification-queue
        - arn:aws:sqs:${AWS_REGION}:${AWS_ACCOUNT}:notification-dlq

    # SNS - Publish notifications
    - sid: SNSPublish
      effect: Allow
      actions:
        - sns:Publish
      resources:
        - arn:aws:sns:${AWS_REGION}:${AWS_ACCOUNT}:user-notifications
        - arn:aws:sns:${AWS_REGION}:${AWS_ACCOUNT}:admin-alerts

    # Secrets Manager - Read secrets
    - sid: SecretsManagerRead
      effect: Allow
      actions:
        - secretsmanager:GetSecretValue
      resources:
        - arn:aws:secretsmanager:${AWS_REGION}:${AWS_ACCOUNT}:secret:notification-service/*
      conditions:
        StringEquals:
          secretsmanager:VersionStage: AWSCURRENT

    # KMS - Decrypt secrets
    - sid: KMSDecrypt
      effect: Allow
      actions:
        - kms:Decrypt
      resources:
        - arn:aws:kms:${AWS_REGION}:${AWS_ACCOUNT}:key/secrets-manager-key-id
      conditions:
        StringEquals:
          kms:ViaService: secretsmanager.${AWS_REGION}.amazonaws.com

    # CloudWatch Logs - Write logs
    - sid: CloudWatchLogs
      effect: Allow
      actions:
        - logs:CreateLogStream
        - logs:PutLogEvents
      resources:
        - arn:aws:logs:${AWS_REGION}:${AWS_ACCOUNT}:log-group:/ecs/notification-service:*
"""


def main() -> None:
    """Demonstrate cross-service IAM policy patterns."""
    print("Cross-Service IAM Policy Example")
    print("=" * 60)

    config = yaml.safe_load(CROSS_SERVICE_POLICY)

    print(f"\nService: {config['service']['name']}")

    # Group by AWS service
    services = {}
    for stmt in config['iam']['policy_statements']:
        # Extract AWS service from first action
        service = stmt['actions'][0].split(':')[0]
        if service not in services:
            services[service] = []
        services[service].append(stmt)

    print("\nPermissions by AWS Service:")
    for service, stmts in services.items():
        print(f"\n  {service.upper()}:")
        for stmt in stmts:
            print(f"    {stmt['sid']}")
            print(f"      Actions: {', '.join(stmt['actions'])}")
            if 'conditions' in stmt:
                print(f"      Conditions: {list(stmt['conditions'].keys())}")

    print("\n" + "=" * 60)
    print("Cross-Service Patterns Demonstrated:")
    print("1. SQS consumer with DLQ access")
    print("2. SNS publish to multiple topics")
    print("3. Secrets Manager with version constraints")
    print("4. KMS with ViaService condition (secrets only)")
    print("5. CloudWatch Logs for application logging")


if __name__ == "__main__":
    main()
