# AWS Secrets Manager

Learn secure secrets management using AWS Secrets Manager with Python boto3. This skill covers storing, retrieving, and rotating secrets programmatically, including local development with LocalStack.

## Learning Objectives

After completing this skill, you will be able to:
- Store and retrieve secrets using AWS Secrets Manager
- Implement automatic secret rotation patterns
- Use boto3 for programmatic secret access
- Set up LocalStack for local development and testing
- Apply security best practices for secrets handling

## Prerequisites

- Python 3.11+
- UV package manager
- Basic AWS knowledge (helpful but not required)
- Docker (for LocalStack)

## Quick Start

```bash
# Install dependencies
make setup

# Start LocalStack for local development
make localstack-up

# Run examples
make examples

# Run tests
make test

# Stop LocalStack
make localstack-down
```

## Concepts

### What is AWS Secrets Manager?

AWS Secrets Manager is a service that helps protect secrets needed to access your applications, services, and IT resources. It enables you to:
- Store secrets securely with encryption at rest
- Rotate secrets automatically without code changes
- Control access using IAM policies
- Audit secret usage through CloudTrail

```python
import boto3

# Create a Secrets Manager client
client = boto3.client('secretsmanager')

# Store a secret
client.create_secret(
    Name='my-app/database',
    SecretString='{"username": "admin", "password": "secret123"}'
)

# Retrieve a secret
response = client.get_secret_value(SecretId='my-app/database')
secret = response['SecretString']
```

### Secret Rotation

Rotation keeps your secrets secure by periodically updating them:

```python
# Enable automatic rotation (30-day schedule)
client.rotate_secret(
    SecretId='my-app/database',
    RotationLambdaARN='arn:aws:lambda:us-east-1:123456789:function:rotate-secret',
    RotationRules={'AutomaticallyAfterDays': 30}
)
```

### LocalStack for Local Development

LocalStack provides a local AWS cloud stack for testing:

```python
# Connect to LocalStack
client = boto3.client(
    'secretsmanager',
    endpoint_url='http://localhost:4566',
    region_name='us-east-1',
    aws_access_key_id='test',
    aws_secret_access_key='test'
)
```

## Examples

### Example 1: Basic Secret Storage

Store and retrieve simple string secrets with proper error handling.

```bash
make example-1
```

### Example 2: JSON Secrets with Versioning

Work with structured secrets (JSON) and access specific versions.

```bash
make example-2
```

### Example 3: Secret Rotation Lambda

Implement a rotation function that follows AWS rotation protocol.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Create a configuration manager that loads database credentials from Secrets Manager
2. **Exercise 2**: Implement a caching layer for secrets with TTL expiration
3. **Exercise 3**: Build a secret rotation handler for API keys

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Hardcoding the Secret Name
Never hardcode secret names. Use environment variables or configuration:
```python
# Bad
secret = client.get_secret_value(SecretId='prod/database')

# Good
secret_name = os.environ['DATABASE_SECRET_NAME']
secret = client.get_secret_value(SecretId=secret_name)
```

### Not Handling Missing Secrets
Always handle cases where secrets don't exist:
```python
from botocore.exceptions import ClientError

try:
    response = client.get_secret_value(SecretId=secret_name)
except ClientError as e:
    if e.response['Error']['Code'] == 'ResourceNotFoundException':
        logger.error(f"Secret {secret_name} not found")
        raise
```

### Storing Secrets in Logs
Never log secret values:
```python
# Bad
logger.info(f"Retrieved password: {secret['password']}")

# Good
logger.info(f"Successfully retrieved secret: {secret_name}")
```

## Further Reading

- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
- [boto3 Secrets Manager Reference](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html)
- [LocalStack Documentation](https://docs.localstack.cloud/)
- Related skills in this repository:
  - [Token Masking](../token-masking/)
  - [API Key Auth](../api-key-auth/)
