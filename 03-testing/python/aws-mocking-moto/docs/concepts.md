# Core Concepts

## Overview

moto is a library that allows you to mock AWS services in your tests. It intercepts boto3 calls and returns fake responses, enabling you to test AWS-dependent code without hitting real AWS infrastructure.

## Concept 1: The mock_aws Decorator

### What It Is

`@mock_aws` is a decorator that activates moto's mocking for all AWS services within the decorated function.

### Why It Matters

- Tests run fast (no network calls)
- Tests are isolated (no shared state)
- Tests are free (no AWS costs)
- Tests are reliable (no network failures)

### How It Works

```python
import boto3
from moto import mock_aws

@mock_aws
def test_create_bucket():
    # Everything inside is mocked
    s3 = boto3.client("s3", region_name="us-east-1")

    # This doesn't hit real AWS
    s3.create_bucket(Bucket="my-test-bucket")

    # Verify the bucket exists in the mock
    response = s3.list_buckets()
    bucket_names = [b["Name"] for b in response["Buckets"]]
    assert "my-test-bucket" in bucket_names
```

Under the hood, moto:
1. Patches boto3's transport layer
2. Routes requests to in-memory implementations
3. Maintains state within the mock context
4. Cleans up when the function returns

## Concept 2: Context Manager Pattern

### What It Is

Using `mock_aws()` as a context manager provides more control over when mocking starts and stops.

### Why It Matters

- Useful for pytest fixtures
- Allows setup before mock starts
- Enables multiple mock contexts in one test
- Better for async testing

### How It Works

```python
from moto import mock_aws
import boto3

def test_with_context_manager():
    # Code here hits real AWS (if credentials are set)

    with mock_aws():
        # Code here is mocked
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        table = dynamodb.create_table(
            TableName="users",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"}
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        table.put_item(Item={"id": "user1", "name": "Alice"})

        response = table.get_item(Key={"id": "user1"})
        assert response["Item"]["name"] == "Alice"

    # Code here hits real AWS again
```

## Concept 3: AWS Credentials in Tests

### What They Are

Even though moto doesn't make real AWS calls, boto3 requires credentials to be set.

### Why It Matters

- boto3 validates credentials exist
- Region affects resource behavior
- Missing credentials cause errors

### How It Works

```python
import os
import pytest
from moto import mock_aws

@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def dynamodb(aws_credentials):
    """DynamoDB resource fixture."""
    with mock_aws():
        yield boto3.resource("dynamodb", region_name="us-east-1")
```

Best practice: Set credentials in conftest.py so all tests have them.

## Concept 4: DynamoDB Mocking

### What It Is

moto provides complete DynamoDB mocking including tables, items, queries, and scans.

### Why It Matters

- DynamoDB is commonly used for serverless
- Real DynamoDB has latency and costs
- Testing CRUD operations is essential

### How It Works

```python
from moto import mock_aws
import boto3

@mock_aws
def test_dynamodb_operations():
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

    # Create table
    table = dynamodb.create_table(
        TableName="orders",
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    # Put item
    table.put_item(Item={
        "pk": "ORDER#123",
        "sk": "METADATA",
        "status": "pending",
        "total": 99.99,
    })

    # Query
    response = table.query(
        KeyConditionExpression="pk = :pk",
        ExpressionAttributeValues={":pk": "ORDER#123"}
    )

    assert len(response["Items"]) == 1
    assert response["Items"][0]["status"] == "pending"
```

## Concept 5: S3 Mocking

### What It Is

moto mocks S3 buckets, objects, and operations like upload, download, and list.

### Why It Matters

- S3 is ubiquitous for file storage
- Testing file operations locally
- Avoiding S3 costs in CI/CD

### How It Works

```python
from moto import mock_aws
import boto3

@mock_aws
def test_s3_operations():
    s3 = boto3.client("s3", region_name="us-east-1")

    # Create bucket
    s3.create_bucket(Bucket="my-bucket")

    # Upload object
    s3.put_object(
        Bucket="my-bucket",
        Key="data/file.txt",
        Body=b"Hello, World!",
        ContentType="text/plain",
    )

    # Download object
    response = s3.get_object(Bucket="my-bucket", Key="data/file.txt")
    content = response["Body"].read()
    assert content == b"Hello, World!"

    # List objects
    response = s3.list_objects_v2(Bucket="my-bucket", Prefix="data/")
    assert len(response["Contents"]) == 1
```

## Concept 6: SQS Mocking

### What It Is

moto mocks SQS queues, messages, and visibility handling.

### Why It Matters

- SQS is common for async processing
- Testing message flows
- Verifying queue behavior

### How It Works

```python
from moto import mock_aws
import boto3
import json

@mock_aws
def test_sqs_operations():
    sqs = boto3.client("sqs", region_name="us-east-1")

    # Create queue
    response = sqs.create_queue(QueueName="my-queue")
    queue_url = response["QueueUrl"]

    # Send message
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps({"event": "user_created", "user_id": "123"}),
    )

    # Receive message
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=0,
    )

    message = response["Messages"][0]
    body = json.loads(message["Body"])
    assert body["event"] == "user_created"

    # Delete message
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=message["ReceiptHandle"],
    )
```

## Summary

Key takeaways:

1. **mock_aws decorator** wraps functions to mock all AWS services
2. **Context manager** provides fixture-friendly mocking
3. **Credentials** must be set even for mocked tests
4. **DynamoDB mocking** supports tables, items, queries
5. **S3 mocking** supports buckets, objects, operations
6. **SQS mocking** supports queues, messages, visibility

Best practices:
- Always set fake credentials in conftest.py
- Create boto3 clients inside mock context
- Specify region_name explicitly
- Use fixtures for repeated setup
- Test both success and error paths
