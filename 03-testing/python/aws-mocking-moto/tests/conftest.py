"""Pytest configuration and fixtures for moto tests."""

import os
from typing import Any, Generator

import boto3
import pytest
from moto import mock_aws


@pytest.fixture(scope="session", autouse=True)
def aws_credentials() -> None:
    """Set up fake AWS credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def dynamodb_table() -> Generator[Any, None, None]:
    """Create a mocked DynamoDB table."""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        table = dynamodb.create_table(
            TableName="test-table",
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


@pytest.fixture
def s3_client() -> Generator[tuple[Any, str], None, None]:
    """Create a mocked S3 client with a bucket."""
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-bucket")
        yield s3, "test-bucket"


@pytest.fixture
def sqs_client() -> Generator[tuple[Any, str], None, None]:
    """Create a mocked SQS client with a queue."""
    with mock_aws():
        sqs = boto3.client("sqs", region_name="us-east-1")
        response = sqs.create_queue(QueueName="test-queue")
        queue_url = response["QueueUrl"]
        yield sqs, queue_url
