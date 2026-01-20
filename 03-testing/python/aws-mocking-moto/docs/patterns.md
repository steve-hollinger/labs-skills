# Common Patterns

## Overview

This document covers common patterns and best practices for testing AWS code with moto.

## Pattern 1: Pytest Fixture for DynamoDB Table

### When to Use

When multiple tests need the same DynamoDB table structure.

### Implementation

```python
import pytest
import boto3
from moto import mock_aws

@pytest.fixture
def dynamodb_table():
    """Provide a mocked DynamoDB table."""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        table = dynamodb.create_table(
            TableName="users",
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

        yield table


def test_create_user(dynamodb_table):
    dynamodb_table.put_item(Item={"pk": "USER#1", "sk": "PROFILE", "name": "Alice"})

    response = dynamodb_table.get_item(Key={"pk": "USER#1", "sk": "PROFILE"})
    assert response["Item"]["name"] == "Alice"
```

### Pitfalls to Avoid

- Don't create the table outside the mock context
- Remember the table is fresh for each test (fixture scope="function")

## Pattern 2: Pre-populated Test Data

### When to Use

When tests need existing data to work with.

### Implementation

```python
import pytest
import boto3
from moto import mock_aws

@pytest.fixture
def populated_s3_bucket():
    """S3 bucket with pre-loaded test files."""
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-bucket")

        # Pre-populate with test data
        test_files = {
            "config/settings.json": b'{"version": "1.0"}',
            "data/users.csv": b"id,name\n1,Alice\n2,Bob",
            "images/logo.png": b"fake-image-data",
        }

        for key, body in test_files.items():
            s3.put_object(Bucket="test-bucket", Key=key, Body=body)

        yield s3, "test-bucket"


def test_list_config_files(populated_s3_bucket):
    s3, bucket = populated_s3_bucket

    response = s3.list_objects_v2(Bucket=bucket, Prefix="config/")
    keys = [obj["Key"] for obj in response["Contents"]]

    assert "config/settings.json" in keys
```

### Pitfalls to Avoid

- Keep pre-populated data minimal
- Document what data is provided

## Pattern 3: Testing Repository Pattern

### When to Use

When testing classes that encapsulate AWS operations.

### Implementation

```python
import boto3
from moto import mock_aws
from dataclasses import dataclass

@dataclass
class User:
    user_id: str
    name: str
    email: str

class UserRepository:
    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        self.table = self.dynamodb.Table(table_name)

    def save(self, user: User) -> None:
        self.table.put_item(Item={
            "pk": f"USER#{user.user_id}",
            "sk": "PROFILE",
            "name": user.name,
            "email": user.email,
        })

    def get(self, user_id: str) -> User | None:
        response = self.table.get_item(
            Key={"pk": f"USER#{user_id}", "sk": "PROFILE"}
        )
        if "Item" not in response:
            return None
        item = response["Item"]
        return User(
            user_id=user_id,
            name=item["name"],
            email=item["email"],
        )


# Tests
@pytest.fixture
def user_repository():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName="users",
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

        yield UserRepository("users")


def test_save_and_get_user(user_repository):
    user = User(user_id="123", name="Alice", email="alice@example.com")
    user_repository.save(user)

    loaded = user_repository.get("123")
    assert loaded is not None
    assert loaded.name == "Alice"
    assert loaded.email == "alice@example.com"


def test_get_nonexistent_user(user_repository):
    result = user_repository.get("nonexistent")
    assert result is None
```

### Pitfalls to Avoid

- Create the repository after creating the table
- Ensure the table name matches

## Pattern 4: Testing Error Handling

### When to Use

When testing how code handles AWS errors.

### Implementation

```python
import pytest
import boto3
from botocore.exceptions import ClientError
from moto import mock_aws

@mock_aws
def test_get_nonexistent_object():
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="test-bucket")

    with pytest.raises(ClientError) as exc_info:
        s3.get_object(Bucket="test-bucket", Key="does-not-exist")

    error = exc_info.value.response["Error"]
    assert error["Code"] == "NoSuchKey"


@mock_aws
def test_put_to_nonexistent_bucket():
    s3 = boto3.client("s3", region_name="us-east-1")

    with pytest.raises(ClientError) as exc_info:
        s3.put_object(
            Bucket="nonexistent-bucket",
            Key="test.txt",
            Body=b"data"
        )

    error = exc_info.value.response["Error"]
    assert error["Code"] == "NoSuchBucket"
```

### Pitfalls to Avoid

- Test specific error codes, not just that an exception was raised
- moto implements most AWS error responses

## Pattern 5: SQS Message Processing

### When to Use

When testing code that processes messages from SQS.

### Implementation

```python
import json
import boto3
from moto import mock_aws

def process_messages(queue_url: str, handler) -> int:
    """Process messages from SQS queue."""
    sqs = boto3.client("sqs", region_name="us-east-1")
    processed = 0

    while True:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=0,
        )

        if "Messages" not in response:
            break

        for message in response["Messages"]:
            handler(json.loads(message["Body"]))
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message["ReceiptHandle"],
            )
            processed += 1

    return processed


@pytest.fixture
def sqs_queue():
    with mock_aws():
        sqs = boto3.client("sqs", region_name="us-east-1")
        response = sqs.create_queue(QueueName="test-queue")
        yield sqs, response["QueueUrl"]


def test_process_messages(sqs_queue):
    sqs, queue_url = sqs_queue
    processed_events = []

    # Send test messages
    for i in range(3):
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps({"event_id": i}),
        )

    # Process messages
    count = process_messages(
        queue_url,
        lambda msg: processed_events.append(msg["event_id"])
    )

    assert count == 3
    assert sorted(processed_events) == [0, 1, 2]
```

### Pitfalls to Avoid

- Don't forget to delete messages after processing
- Use WaitTimeSeconds=0 in tests for speed

## Pattern 6: Testing File Uploads

### When to Use

When testing code that uploads files to S3.

### Implementation

```python
import io
import boto3
from moto import mock_aws

class FileStorage:
    def __init__(self, bucket_name: str):
        self.s3 = boto3.client("s3", region_name="us-east-1")
        self.bucket_name = bucket_name

    def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return f"s3://{self.bucket_name}/{key}"

    def download(self, key: str) -> bytes:
        response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
        return response["Body"].read()


@pytest.fixture
def file_storage():
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="uploads")
        yield FileStorage("uploads")


def test_upload_and_download(file_storage):
    content = b"Hello, World!"
    uri = file_storage.upload("test/hello.txt", content, "text/plain")

    assert uri == "s3://uploads/test/hello.txt"

    downloaded = file_storage.download("test/hello.txt")
    assert downloaded == content


def test_upload_binary_file(file_storage):
    binary_data = bytes(range(256))
    file_storage.upload("binary/data.bin", binary_data)

    downloaded = file_storage.download("binary/data.bin")
    assert downloaded == binary_data
```

### Pitfalls to Avoid

- Remember to create the bucket first
- Test with both text and binary data

## Anti-Patterns

### Anti-Pattern 1: Client Created Outside Mock

```python
# BAD - client created before mock starts
s3 = boto3.client("s3")

@mock_aws
def test_upload():
    s3.put_object(Bucket="bucket", Key="key", Body=b"data")  # HITS REAL AWS!

# GOOD - client created inside mock
@mock_aws
def test_upload():
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="bucket")
    s3.put_object(Bucket="bucket", Key="key", Body=b"data")
```

### Anti-Pattern 2: Missing Region

```python
# BAD - no region specified
dynamodb = boto3.resource("dynamodb")  # Uses AWS_DEFAULT_REGION or fails

# GOOD - explicit region
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
```

### Anti-Pattern 3: Forgetting to Create Resources

```python
# BAD - assumes table exists
@mock_aws
def test_put_item():
    table = boto3.resource("dynamodb").Table("users")
    table.put_item(Item={"id": "1"})  # ResourceNotFoundException!

# GOOD - create table first
@mock_aws
def test_put_item():
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    dynamodb.create_table(...)
    table = dynamodb.Table("users")
    table.put_item(Item={"id": "1"})
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Simple one-off test | @mock_aws decorator |
| Shared table structure | Pytest fixture |
| Testing service class | Repository pattern fixture |
| Testing errors | ClientError assertions |
| Message processing | SQS fixture with queue_url |
| File operations | FileStorage class fixture |
| Multiple services | Combined fixtures |
