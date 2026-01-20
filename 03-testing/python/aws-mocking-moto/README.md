# AWS Mocking with moto

Master AWS service mocking using moto for reliable, fast, and isolated tests. Learn to mock DynamoDB, S3, SQS, and other AWS services without hitting real infrastructure.

## Learning Objectives

After completing this skill, you will be able to:
- Mock AWS services using moto decorators and context managers
- Test DynamoDB operations (tables, items, queries)
- Test S3 operations (buckets, objects, uploads)
- Test SQS operations (queues, messages)
- Integrate moto with pytest fixtures
- Handle AWS credentials in test environments

## Prerequisites

- Python 3.11+
- UV package manager
- Basic pytest knowledge
- Familiarity with boto3 and AWS services

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Concepts

### Moto Decorator Pattern

The simplest way to mock AWS services:

```python
import boto3
from moto import mock_aws

@mock_aws
def test_s3_upload():
    # All boto3 calls are mocked within this function
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="test-bucket")
    s3.put_object(Bucket="test-bucket", Key="test.txt", Body=b"Hello")

    response = s3.get_object(Bucket="test-bucket", Key="test.txt")
    assert response["Body"].read() == b"Hello"
```

### Context Manager Pattern

For more control over mock scope:

```python
from moto import mock_aws

def test_dynamodb_with_context():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(
            TableName="users",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        # Table is available for testing
        table.put_item(Item={"id": "user1", "name": "Test User"})
```

### Pytest Fixture Integration

Create reusable mocked AWS resources:

```python
import pytest
from moto import mock_aws

@pytest.fixture
def aws_credentials():
    """Set up dummy AWS credentials for moto."""
    import os
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"

@pytest.fixture
def dynamodb_table(aws_credentials):
    """Create a mocked DynamoDB table."""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(...)
        yield table
```

## Examples

### Example 1: DynamoDB Mocking

Basic DynamoDB operations with moto.

```bash
make example-1
```

### Example 2: S3 Mocking

S3 bucket and object operations.

```bash
make example-2
```

### Example 3: SQS Mocking

SQS queue and message operations.

```bash
make example-3
```

### Example 4: Pytest Fixtures

Integrating moto with pytest fixtures.

```bash
make example-4
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Test a DynamoDB-backed user repository
2. **Exercise 2**: Test an S3 file storage service
3. **Exercise 3**: Test an SQS message processor

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Forgetting AWS Credentials

moto requires fake credentials to be set:

```python
# Set in conftest.py or fixture
import os
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
```

### Creating Clients Outside Mock Context

Clients created before mock_aws starts will hit real AWS:

```python
# WRONG - client created outside mock context
s3 = boto3.client("s3")

@mock_aws
def test_upload():
    s3.put_object(...)  # Hits real AWS!

# RIGHT - client created inside mock context
@mock_aws
def test_upload():
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.put_object(...)  # Mocked!
```

### Region Mismatch

Always specify region_name to avoid issues:

```python
# WRONG - may use unexpected region
dynamodb = boto3.resource("dynamodb")

# RIGHT - explicit region
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
```

## Further Reading

- [moto Documentation](https://docs.getmoto.org/)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- Related skills in this repository:
  - [pytest-markers](../pytest-markers/)
  - [pytest-asyncio](../pytest-asyncio/)
