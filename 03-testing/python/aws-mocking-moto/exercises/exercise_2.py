"""Exercise 2: Test an S3 File Storage Service

Your task is to implement tests for the FileStorageService class using moto.
The service handles file uploads, downloads, and metadata management.

Instructions:
1. Create a pytest fixture that provides a mocked S3 bucket
2. Implement tests for all FileStorageService methods
3. Test error handling (file not found, etc.)

Expected Tests:
- test_upload_file: Upload a file and verify it exists
- test_download_file: Download a file and verify content
- test_download_nonexistent_file: Should return None
- test_delete_file: Delete a file
- test_list_files: List files with optional prefix
- test_get_file_url: Generate a presigned URL

Hints:
- Use @mock_aws decorator or context manager
- Create the bucket in the fixture
- Test with both text and binary data

Run your tests with:
    pytest exercises/exercise_2.py -v
"""

from dataclasses import dataclass

import boto3
import pytest  # noqa: F401
from botocore.exceptions import ClientError
from moto import mock_aws  # noqa: F401


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
        """Upload a file to S3.

        Returns the S3 URI of the uploaded file.
        """
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return f"s3://{self.bucket_name}/{key}"

    def download(self, key: str) -> bytes | None:
        """Download a file from S3.

        Returns the file content or None if not found.
        """
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            return response["Body"].read()
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return None
            raise

    def delete(self, key: str) -> bool:
        """Delete a file from S3.

        Returns True if deleted, False if not found.
        """
        try:
            # Check if exists first
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
            # Get content type from head object
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
# TODO: Implement the fixture and tests below
# =============================================================================


@pytest.fixture
def file_storage():
    """Create a mocked S3 bucket and FileStorageService.

    TODO:
    1. Use mock_aws context manager
    2. Create S3 client
    3. Create a bucket
    4. Yield FileStorageService instance
    """
    pass


def test_upload_file(file_storage) -> None:
    """Test uploading a file.

    TODO:
    1. Upload a text file
    2. Verify it exists in the bucket
    3. Verify the returned URI is correct
    """
    pass


def test_download_file(file_storage) -> None:
    """Test downloading a file.

    TODO:
    1. Upload a file with known content
    2. Download it
    3. Verify the content matches
    """
    pass


def test_download_nonexistent_file(file_storage) -> None:
    """Test downloading a file that doesn't exist.

    TODO: Verify that download() returns None for nonexistent file
    """
    pass


def test_delete_file(file_storage) -> None:
    """Test deleting a file.

    TODO:
    1. Upload a file
    2. Delete it
    3. Verify it's gone
    """
    pass


def test_list_files(file_storage) -> None:
    """Test listing files.

    TODO:
    1. Upload multiple files with different prefixes
    2. List all files
    3. List files with prefix filter
    """
    pass


def test_get_download_url(file_storage) -> None:
    """Test generating presigned download URL.

    TODO:
    1. Upload a file
    2. Generate download URL
    3. Verify URL contains bucket and key
    """
    pass


def test_upload_binary_file(file_storage) -> None:
    """Test uploading binary data.

    TODO:
    1. Upload binary data (e.g., bytes(range(256)))
    2. Download and verify content matches
    """
    pass


def test_file_metadata(file_storage) -> None:
    """Test that file metadata is correct.

    TODO:
    1. Upload files with specific content types
    2. List files
    3. Verify metadata (size, content_type) is correct
    """
    pass


if __name__ == "__main__":
    import subprocess

    subprocess.run(["pytest", __file__, "-v"])
