"""Tests demonstrating S3 mocking with moto."""

from typing import Any

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws


# =============================================================================
# Basic Object Operations
# =============================================================================


def test_put_and_get_object(s3_client: tuple[Any, str]) -> None:
    """Test basic put and get object operations."""
    s3, bucket = s3_client

    s3.put_object(
        Bucket=bucket,
        Key="test/file.txt",
        Body=b"Hello, World!",
        ContentType="text/plain",
    )

    response = s3.get_object(Bucket=bucket, Key="test/file.txt")

    assert response["Body"].read() == b"Hello, World!"
    assert response["ContentType"] == "text/plain"


def test_put_large_object(s3_client: tuple[Any, str]) -> None:
    """Test uploading larger objects."""
    s3, bucket = s3_client

    # Create 1MB of data
    large_data = b"x" * (1024 * 1024)

    s3.put_object(Bucket=bucket, Key="large/file.bin", Body=large_data)

    response = s3.get_object(Bucket=bucket, Key="large/file.bin")
    assert len(response["Body"].read()) == 1024 * 1024


def test_delete_object(s3_client: tuple[Any, str]) -> None:
    """Test delete object operation."""
    s3, bucket = s3_client

    # Put object
    s3.put_object(Bucket=bucket, Key="to-delete.txt", Body=b"temp data")

    # Verify exists
    response = s3.list_objects_v2(Bucket=bucket)
    assert len(response.get("Contents", [])) == 1

    # Delete object
    s3.delete_object(Bucket=bucket, Key="to-delete.txt")

    # Verify deleted
    response = s3.list_objects_v2(Bucket=bucket)
    assert "Contents" not in response or len(response["Contents"]) == 0


# =============================================================================
# Listing Objects
# =============================================================================


def test_list_objects(s3_client: tuple[Any, str]) -> None:
    """Test listing objects."""
    s3, bucket = s3_client

    # Upload multiple objects
    for i in range(5):
        s3.put_object(Bucket=bucket, Key=f"file{i}.txt", Body=f"content {i}".encode())

    # List all objects
    response = s3.list_objects_v2(Bucket=bucket)

    assert len(response["Contents"]) == 5


def test_list_objects_with_prefix(s3_client: tuple[Any, str]) -> None:
    """Test listing objects with prefix filter."""
    s3, bucket = s3_client

    # Upload objects with different prefixes
    objects = [
        "images/photo1.jpg",
        "images/photo2.jpg",
        "documents/report.pdf",
        "documents/notes.txt",
        "README.md",
    ]

    for key in objects:
        s3.put_object(Bucket=bucket, Key=key, Body=b"content")

    # List only images
    response = s3.list_objects_v2(Bucket=bucket, Prefix="images/")
    assert len(response["Contents"]) == 2

    # List only documents
    response = s3.list_objects_v2(Bucket=bucket, Prefix="documents/")
    assert len(response["Contents"]) == 2


def test_list_objects_with_delimiter(s3_client: tuple[Any, str]) -> None:
    """Test listing with delimiter for folder-like behavior."""
    s3, bucket = s3_client

    # Upload objects simulating folders
    objects = [
        "folder1/file1.txt",
        "folder1/file2.txt",
        "folder2/file1.txt",
        "root.txt",
    ]

    for key in objects:
        s3.put_object(Bucket=bucket, Key=key, Body=b"content")

    # List with delimiter to get "folders"
    response = s3.list_objects_v2(Bucket=bucket, Delimiter="/")

    # Should have one root object and two "folders"
    assert len(response.get("Contents", [])) == 1  # root.txt
    assert len(response.get("CommonPrefixes", [])) == 2  # folder1/, folder2/


# =============================================================================
# Copy Operations
# =============================================================================


def test_copy_object(s3_client: tuple[Any, str]) -> None:
    """Test copying objects."""
    s3, bucket = s3_client

    # Put original
    s3.put_object(Bucket=bucket, Key="original.txt", Body=b"original content")

    # Copy to new location
    s3.copy_object(
        Bucket=bucket,
        Key="copy.txt",
        CopySource={"Bucket": bucket, "Key": "original.txt"},
    )

    # Verify both exist
    response = s3.list_objects_v2(Bucket=bucket)
    keys = [obj["Key"] for obj in response["Contents"]]
    assert "original.txt" in keys
    assert "copy.txt" in keys

    # Verify content is same
    original = s3.get_object(Bucket=bucket, Key="original.txt")["Body"].read()
    copy = s3.get_object(Bucket=bucket, Key="copy.txt")["Body"].read()
    assert original == copy


@mock_aws
def test_copy_across_buckets() -> None:
    """Test copying objects between buckets."""
    s3 = boto3.client("s3", region_name="us-east-1")

    # Create buckets
    s3.create_bucket(Bucket="source-bucket")
    s3.create_bucket(Bucket="dest-bucket")

    # Put in source
    s3.put_object(Bucket="source-bucket", Key="file.txt", Body=b"data")

    # Copy to destination
    s3.copy_object(
        Bucket="dest-bucket",
        Key="file.txt",
        CopySource={"Bucket": "source-bucket", "Key": "file.txt"},
    )

    # Verify in destination
    response = s3.get_object(Bucket="dest-bucket", Key="file.txt")
    assert response["Body"].read() == b"data"


# =============================================================================
# Error Handling
# =============================================================================


def test_get_nonexistent_object(s3_client: tuple[Any, str]) -> None:
    """Test error when getting nonexistent object."""
    s3, bucket = s3_client

    with pytest.raises(ClientError) as exc_info:
        s3.get_object(Bucket=bucket, Key="does-not-exist.txt")

    assert exc_info.value.response["Error"]["Code"] == "NoSuchKey"


@mock_aws
def test_put_to_nonexistent_bucket() -> None:
    """Test error when putting to nonexistent bucket."""
    s3 = boto3.client("s3", region_name="us-east-1")

    with pytest.raises(ClientError) as exc_info:
        s3.put_object(Bucket="nonexistent-bucket", Key="file.txt", Body=b"data")

    assert exc_info.value.response["Error"]["Code"] == "NoSuchBucket"


# =============================================================================
# Metadata and Tags
# =============================================================================


def test_object_metadata(s3_client: tuple[Any, str]) -> None:
    """Test object metadata."""
    s3, bucket = s3_client

    s3.put_object(
        Bucket=bucket,
        Key="with-metadata.txt",
        Body=b"content",
        Metadata={"author": "Alice", "version": "1.0"},
    )

    response = s3.head_object(Bucket=bucket, Key="with-metadata.txt")

    assert response["Metadata"]["author"] == "Alice"
    assert response["Metadata"]["version"] == "1.0"


def test_object_tags(s3_client: tuple[Any, str]) -> None:
    """Test object tagging."""
    s3, bucket = s3_client

    # Put object
    s3.put_object(Bucket=bucket, Key="tagged.txt", Body=b"content")

    # Add tags
    s3.put_object_tagging(
        Bucket=bucket,
        Key="tagged.txt",
        Tagging={
            "TagSet": [
                {"Key": "environment", "Value": "test"},
                {"Key": "project", "Value": "demo"},
            ]
        },
    )

    # Get tags
    response = s3.get_object_tagging(Bucket=bucket, Key="tagged.txt")
    tags = {tag["Key"]: tag["Value"] for tag in response["TagSet"]}

    assert tags["environment"] == "test"
    assert tags["project"] == "demo"


# =============================================================================
# Presigned URLs
# =============================================================================


def test_generate_presigned_url(s3_client: tuple[Any, str]) -> None:
    """Test generating presigned URLs."""
    s3, bucket = s3_client

    s3.put_object(Bucket=bucket, Key="file.txt", Body=b"content")

    # Generate download URL
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": "file.txt"},
        ExpiresIn=3600,
    )

    assert bucket in url
    assert "file.txt" in url


def test_generate_presigned_upload_url(s3_client: tuple[Any, str]) -> None:
    """Test generating presigned upload URLs."""
    s3, bucket = s3_client

    # Generate upload URL
    url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": bucket, "Key": "upload.txt"},
        ExpiresIn=3600,
    )

    assert bucket in url
    assert "upload.txt" in url


# =============================================================================
# Bucket Operations
# =============================================================================


@mock_aws
def test_list_buckets() -> None:
    """Test listing buckets."""
    s3 = boto3.client("s3", region_name="us-east-1")

    # Create buckets
    s3.create_bucket(Bucket="bucket-1")
    s3.create_bucket(Bucket="bucket-2")
    s3.create_bucket(Bucket="bucket-3")

    # List buckets
    response = s3.list_buckets()
    bucket_names = [b["Name"] for b in response["Buckets"]]

    assert "bucket-1" in bucket_names
    assert "bucket-2" in bucket_names
    assert "bucket-3" in bucket_names


@mock_aws
def test_delete_bucket() -> None:
    """Test deleting a bucket."""
    s3 = boto3.client("s3", region_name="us-east-1")

    # Create and delete bucket
    s3.create_bucket(Bucket="to-delete")
    s3.delete_bucket(Bucket="to-delete")

    # Verify deleted
    response = s3.list_buckets()
    bucket_names = [b["Name"] for b in response["Buckets"]]
    assert "to-delete" not in bucket_names


@mock_aws
def test_delete_nonempty_bucket_fails() -> None:
    """Test that deleting a non-empty bucket fails."""
    s3 = boto3.client("s3", region_name="us-east-1")

    s3.create_bucket(Bucket="nonempty")
    s3.put_object(Bucket="nonempty", Key="file.txt", Body=b"content")

    with pytest.raises(ClientError) as exc_info:
        s3.delete_bucket(Bucket="nonempty")

    assert exc_info.value.response["Error"]["Code"] == "BucketNotEmpty"
