"""Solution for Exercise 2: Test an S3 File Storage Service"""

import os
from dataclasses import dataclass

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws


# Set up credentials
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@dataclass
class FileMetadata:
    """File metadata."""

    key: str
    size: int
    content_type: str


class FileStorageService:
    """Service for S3 file operations."""

    def __init__(self, bucket_name: str) -> None:
        self.s3 = boto3.client("s3", region_name="us-east-1")
        self.bucket_name = bucket_name

    def upload(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload a file to S3."""
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return f"s3://{self.bucket_name}/{key}"

    def download(self, key: str) -> bytes | None:
        """Download a file from S3."""
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            return response["Body"].read()
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return None
            raise

    def delete(self, key: str) -> bool:
        """Delete a file from S3."""
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=key)
            self.s3.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    def list_files(self, prefix: str = "") -> list[FileMetadata]:
        """List files in the bucket with optional prefix."""
        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)

        if "Contents" not in response:
            return []

        result = []
        for obj in response["Contents"]:
            head = self.s3.head_object(Bucket=self.bucket_name, Key=obj["Key"])
            result.append(
                FileMetadata(
                    key=obj["Key"],
                    size=obj["Size"],
                    content_type=head.get("ContentType", "application/octet-stream"),
                )
            )

        return result

    def get_download_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a presigned download URL."""
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": key},
            ExpiresIn=expires_in,
        )

    def get_upload_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a presigned upload URL."""
        return self.s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": self.bucket_name, "Key": key},
            ExpiresIn=expires_in,
        )


# =============================================================================
# Fixtures and Tests (Solutions)
# =============================================================================


@pytest.fixture
def file_storage():
    """Create a mocked S3 bucket and FileStorageService."""
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-files")
        yield FileStorageService("test-files")


def test_upload_file(file_storage: FileStorageService) -> None:
    """Test uploading a file."""
    content = b"Hello, World!"
    uri = file_storage.upload("test/hello.txt", content, "text/plain")

    assert uri == "s3://test-files/test/hello.txt"

    # Verify file exists by downloading
    downloaded = file_storage.download("test/hello.txt")
    assert downloaded == content


def test_download_file(file_storage: FileStorageService) -> None:
    """Test downloading a file."""
    original_content = b"Test content for download"
    file_storage.upload("download-test.txt", original_content)

    downloaded = file_storage.download("download-test.txt")

    assert downloaded == original_content


def test_download_nonexistent_file(file_storage: FileStorageService) -> None:
    """Test downloading a file that doesn't exist."""
    result = file_storage.download("does-not-exist.txt")
    assert result is None


def test_delete_file(file_storage: FileStorageService) -> None:
    """Test deleting a file."""
    file_storage.upload("to-delete.txt", b"delete me")

    # Verify exists
    assert file_storage.download("to-delete.txt") is not None

    # Delete
    result = file_storage.delete("to-delete.txt")
    assert result is True

    # Verify gone
    assert file_storage.download("to-delete.txt") is None


def test_list_files(file_storage: FileStorageService) -> None:
    """Test listing files."""
    # Upload files with different prefixes
    file_storage.upload("images/photo1.jpg", b"photo1", "image/jpeg")
    file_storage.upload("images/photo2.jpg", b"photo2", "image/jpeg")
    file_storage.upload("documents/report.pdf", b"report", "application/pdf")
    file_storage.upload("README.txt", b"readme", "text/plain")

    # List all files
    all_files = file_storage.list_files()
    assert len(all_files) == 4

    # List with prefix
    images = file_storage.list_files("images/")
    assert len(images) == 2
    assert all(f.key.startswith("images/") for f in images)

    documents = file_storage.list_files("documents/")
    assert len(documents) == 1


def test_get_download_url(file_storage: FileStorageService) -> None:
    """Test generating presigned download URL."""
    file_storage.upload("url-test.txt", b"content")

    url = file_storage.get_download_url("url-test.txt")

    assert "test-files" in url
    assert "url-test.txt" in url


def test_upload_binary_file(file_storage: FileStorageService) -> None:
    """Test uploading binary data."""
    binary_data = bytes(range(256))  # All byte values 0-255
    file_storage.upload("binary.bin", binary_data)

    downloaded = file_storage.download("binary.bin")

    assert downloaded == binary_data
    assert len(downloaded) == 256


def test_file_metadata(file_storage: FileStorageService) -> None:
    """Test that file metadata is correct."""
    # Upload files with specific content types
    file_storage.upload("test.json", b'{"key": "value"}', "application/json")
    file_storage.upload("test.html", b"<html></html>", "text/html")

    files = file_storage.list_files()

    metadata_by_key = {f.key: f for f in files}

    assert metadata_by_key["test.json"].content_type == "application/json"
    assert metadata_by_key["test.json"].size == 16

    assert metadata_by_key["test.html"].content_type == "text/html"
    assert metadata_by_key["test.html"].size == 13


def test_list_empty_bucket(file_storage: FileStorageService) -> None:
    """Test listing files in empty bucket."""
    files = file_storage.list_files()
    assert files == []


def test_get_upload_url(file_storage: FileStorageService) -> None:
    """Test generating presigned upload URL."""
    url = file_storage.get_upload_url("future-upload.txt")

    assert "test-files" in url
    assert "future-upload.txt" in url


if __name__ == "__main__":
    import subprocess

    subprocess.run(["pytest", __file__, "-v"])
