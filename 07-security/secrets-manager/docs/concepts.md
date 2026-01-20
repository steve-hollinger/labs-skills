# Core Concepts

## Overview

AWS Secrets Manager provides secure, centralized storage for sensitive configuration data. This document covers the core concepts you need to understand for effective secrets management.

## Concept 1: Secret Storage and Encryption

### What It Is

AWS Secrets Manager stores secrets as encrypted key-value pairs. Each secret can contain up to 64KB of data and is encrypted using AWS KMS (Key Management Service).

### Why It Matters

- **Security**: Secrets are encrypted at rest and in transit
- **Centralization**: Single source of truth for sensitive data
- **Access Control**: Fine-grained IAM policies control who can access secrets
- **Audit Trail**: CloudTrail logs all secret access

### How It Works

Secrets are stored with metadata:
- **Name**: Unique identifier (e.g., `prod/myapp/database`)
- **Value**: The secret data (string or binary)
- **Description**: Human-readable description
- **Tags**: Key-value pairs for organization
- **KMS Key**: The encryption key used

```python
import boto3
import json

client = boto3.client('secretsmanager')

# Create a secret
response = client.create_secret(
    Name='prod/myapp/database',
    Description='Production database credentials',
    SecretString=json.dumps({
        'host': 'db.example.com',
        'port': 5432,
        'username': 'app_user',
        'password': 'super-secret-password'
    }),
    Tags=[
        {'Key': 'Environment', 'Value': 'production'},
        {'Key': 'Application', 'Value': 'myapp'}
    ]
)

print(f"Created secret: {response['ARN']}")
```

## Concept 2: Secret Versioning

### What It Is

Secrets Manager maintains version history for each secret. Every update creates a new version, allowing rollback and audit capabilities.

### Why It Matters

- **Rollback**: Recover from bad updates
- **Audit**: Track when secrets changed
- **Rotation**: Support zero-downtime rotation with staging labels

### How It Works

Versions are identified by:
- **VersionId**: Unique UUID for each version
- **VersionStage**: Labels like `AWSCURRENT`, `AWSPREVIOUS`, `AWSPENDING`

```python
# Get current version
current = client.get_secret_value(
    SecretId='prod/myapp/database',
    VersionStage='AWSCURRENT'
)

# Get previous version
previous = client.get_secret_value(
    SecretId='prod/myapp/database',
    VersionStage='AWSPREVIOUS'
)

# List all versions
versions = client.list_secret_version_ids(
    SecretId='prod/myapp/database'
)

for version in versions['Versions']:
    print(f"Version: {version['VersionId']}")
    print(f"Stages: {version.get('VersionStages', [])}")
    print(f"Created: {version['CreatedDate']}")
```

## Concept 3: Secret Rotation

### What It Is

Automatic secret rotation updates credentials on a schedule without requiring application changes. AWS uses a Lambda function to perform the rotation.

### Why It Matters

- **Security**: Regular rotation limits exposure from compromised credentials
- **Compliance**: Meet regulatory requirements for credential rotation
- **Automation**: No manual intervention required

### How It Works

Rotation follows a 4-step protocol:

1. **createSecret**: Create new version with `AWSPENDING` stage
2. **setSecret**: Update the resource (database, API, etc.) with new credentials
3. **testSecret**: Verify the new credentials work
4. **finishSecret**: Move `AWSCURRENT` to new version, `AWSPREVIOUS` to old

```python
def lambda_handler(event, context):
    """Rotation Lambda handler."""
    arn = event['SecretId']
    token = event['ClientRequestToken']
    step = event['Step']

    client = boto3.client('secretsmanager')

    if step == 'createSecret':
        # Generate new password
        new_password = generate_secure_password()
        client.put_secret_value(
            SecretId=arn,
            ClientRequestToken=token,
            SecretString=json.dumps({'password': new_password}),
            VersionStages=['AWSPENDING']
        )

    elif step == 'setSecret':
        # Update the database password
        pending = client.get_secret_value(
            SecretId=arn,
            VersionStage='AWSPENDING'
        )
        update_database_password(json.loads(pending['SecretString']))

    elif step == 'testSecret':
        # Verify new password works
        pending = client.get_secret_value(
            SecretId=arn,
            VersionStage='AWSPENDING'
        )
        test_database_connection(json.loads(pending['SecretString']))

    elif step == 'finishSecret':
        # Move staging labels
        metadata = client.describe_secret(SecretId=arn)
        current_version = None
        for version, stages in metadata['VersionIdsToStages'].items():
            if 'AWSCURRENT' in stages:
                current_version = version
                break

        client.update_secret_version_stage(
            SecretId=arn,
            VersionStage='AWSCURRENT',
            MoveToVersionId=token,
            RemoveFromVersionId=current_version
        )
```

## Concept 4: LocalStack for Development

### What It Is

LocalStack provides a local AWS cloud stack, allowing you to develop and test AWS integrations without a real AWS account.

### Why It Matters

- **Cost**: No AWS charges during development
- **Speed**: Faster iteration without network latency
- **Isolation**: Test environment doesn't affect production
- **CI/CD**: Run tests in pipelines without AWS credentials

### How It Works

LocalStack runs as a Docker container and exposes AWS-compatible APIs on port 4566.

```python
import boto3

def get_client(use_localstack: bool = False):
    """Create Secrets Manager client."""
    if use_localstack:
        return boto3.client(
            'secretsmanager',
            endpoint_url='http://localhost:4566',
            region_name='us-east-1',
            aws_access_key_id='test',
            aws_secret_access_key='test'
        )
    return boto3.client('secretsmanager')

# Usage
client = get_client(use_localstack=True)

# Works exactly like real AWS
client.create_secret(Name='test/secret', SecretString='my-secret')
response = client.get_secret_value(SecretId='test/secret')
print(response['SecretString'])  # 'my-secret'
```

## Summary

Key takeaways:

1. **Use Secrets Manager** instead of hardcoded credentials or config files
2. **Enable versioning** for audit trails and rollback capability
3. **Implement rotation** for critical secrets (databases, API keys)
4. **Use LocalStack** for development and testing
5. **Never log secret values** - only log secret names and operations
