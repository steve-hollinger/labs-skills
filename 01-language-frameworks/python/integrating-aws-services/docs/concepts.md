# Core Concepts: AWS Service Clients

## What

boto3 is the AWS SDK for Python, providing interfaces to AWS services like DynamoDB, S3, and Secrets Manager. It offers two levels of abstraction:

- **Client**: Low-level interface mapping directly to AWS API operations. Requires manual data marshalling.
- **Resource**: High-level, object-oriented interface that automatically converts between Python types and AWS formats.

At Fetch, we primarily integrate with:
- **DynamoDB**: NoSQL database for user profiles, rewards transactions, and system state
- **S3**: Object storage for receipts, images, and data exports
- **Secrets Manager**: Secure storage for API keys, database credentials, and partner secrets

## Why

**Problem:** Direct AWS API calls are synchronous (blocking), lack error handling, and require repetitive boilerplate for retries and credential management.

**Solution:**
- boto3 provides Pythonic abstractions over AWS APIs with automatic credential discovery from IAM roles
- Retry logic with exponential backoff handles transient failures (throttling, network errors)
- aioboto3 enables async/await patterns for non-blocking operations in FastAPI services

**Fetch Context:**
- DynamoDB single-table design: All entities in one table using PK/SK composite keys (e.g., `USER#123`, `REWARD#456`)
- IAM permissions managed through FSD service definitions, not hardcoded credentials
- Retry strategies handle high-throughput scenarios during peak hours (receipt scanning surges)

## How

### boto3 Client Configuration

```python
import boto3

# Use resource for DynamoDB (automatic type conversion)
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("fetch-data")

# Use client for S3 (more control over operations)
s3_client = boto3.client("s3", region_name="us-east-1")
```

### Retry Logic

boto3 has built-in retry logic for throttling errors, but custom retries handle application-specific failures:

```python
from functools import wraps
import time
from botocore.exceptions import ClientError

def retry_with_backoff(max_attempts=3, base_delay=0.5):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except ClientError as e:
                    if e.response["Error"]["Code"] == "ProvisionedThroughputExceededException":
                        if attempt < max_attempts - 1:
                            time.sleep(base_delay * (2 ** attempt))
                            continue
                    raise
            return None
        return wrapper
    return decorator
```

### Resource vs Client

**Use Resource when:**
- Working with DynamoDB tables (simpler API, automatic marshalling)
- Performing CRUD operations on S3 objects
- You want object-oriented patterns

**Use Client when:**
- Need access to all AWS API operations (not all have resource equivalents)
- Generating presigned URLs
- Batch operations require fine-grained control

### Async with aioboto3

For FastAPI or async services, use aioboto3 to prevent blocking:

```python
import aioboto3

async def get_secret(secret_name: str) -> str:
    session = aioboto3.Session()
    async with session.client("secretsmanager") as secrets_client:
        response = await secrets_client.get_secret_value(SecretId=secret_name)
        return response["SecretString"]
```

## When to Use

**Use when:**
- Building Python services that need to persist data in DynamoDB
- Storing or retrieving files from S3 (receipts, exports)
- Accessing secrets during service initialization
- Integrating with any AWS service from Lambda or ECS containers

**Avoid when:**
- The AWS SDK for another language is more appropriate (e.g., Go services use AWS SDK for Go)
- You're in a frontend application (use presigned URLs or API Gateway instead)
- Local development requires mocking (use moto or LocalStack)

## Key Terminology

- **PK/SK**: Partition Key and Sort Key in DynamoDB single-table design
- **Resource vs Client**: High-level vs low-level boto3 interfaces
- **Throttling**: AWS rate-limiting that returns ProvisionedThroughputExceededException
- **IAM Role**: AWS identity with permissions, assigned to services via FSD
- **Presigned URL**: Time-limited URL granting temporary access to S3 objects
- **Exponential Backoff**: Retry strategy with increasing delays (0.5s, 1s, 2s, 4s...)
