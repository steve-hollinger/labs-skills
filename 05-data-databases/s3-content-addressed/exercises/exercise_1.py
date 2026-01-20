"""Exercise 1: Build a Content-Addressed File Upload API

Create a file upload service that uses content-addressed storage
to provide deduplication and integrity verification.

Requirements:
1. Upload files and return their content hash
2. Download files by hash with verification
3. Get file metadata (size, upload time)
4. Check if file already exists before upload
5. List all stored files

Instructions:
1. Implement the FileUploadService class
2. Use ContentAddressedStore for storage
3. Store metadata (filename, upload time) separately
4. Implement deduplication detection

Hints:
- Store content in S3 using hash as key
- Store metadata in a separate structure (or S3 object metadata)
- Check existence before upload to save bandwidth
- Return dedup status to client
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, BinaryIO

import boto3
from moto import mock_aws

from s3_content_addressed.store import ContentAddressedStore


@dataclass
class UploadResult:
    """Result of a file upload."""

    content_hash: str
    filename: str
    size_bytes: int
    was_deduplicated: bool
    upload_time: str


@dataclass
class FileMetadata:
    """Metadata about an uploaded file."""

    content_hash: str
    filename: str
    size_bytes: int
    upload_time: str
    content_type: str


class FileUploadService:
    """File upload service with content-addressed storage."""

    def __init__(self, s3_client: Any, bucket: str):
        """Initialize upload service.

        Args:
            s3_client: Boto3 S3 client
            bucket: S3 bucket name
        """
        self.store = ContentAddressedStore(s3_client, bucket)
        self.metadata: dict[str, FileMetadata] = {}

    def upload_file(
        self,
        filename: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> UploadResult:
        """Upload a file.

        TODO: Implement file upload with deduplication.

        Steps:
        1. Check if content already exists (by computing hash)
        2. Store content if new
        3. Store/update metadata
        4. Return upload result with dedup status

        Args:
            filename: Original filename
            data: File content
            content_type: MIME type

        Returns:
            UploadResult with hash and dedup info
        """
        # TODO: Implement
        pass

    def download_file(self, content_hash: str) -> tuple[bytes, FileMetadata]:
        """Download a file by its content hash.

        TODO: Implement file download with verification.

        Args:
            content_hash: Hash of content to download

        Returns:
            Tuple of (content, metadata)

        Raises:
            ValueError: If file not found
        """
        # TODO: Implement
        pass

    def file_exists(self, content_hash: str) -> bool:
        """Check if a file exists.

        TODO: Implement existence check.

        Args:
            content_hash: Hash to check

        Returns:
            True if file exists
        """
        # TODO: Implement
        pass

    def get_metadata(self, content_hash: str) -> FileMetadata | None:
        """Get file metadata.

        TODO: Implement metadata retrieval.

        Args:
            content_hash: Hash of file

        Returns:
            FileMetadata or None if not found
        """
        # TODO: Implement
        pass

    def list_files(self) -> list[FileMetadata]:
        """List all uploaded files.

        TODO: Implement file listing.

        Returns:
            List of file metadata
        """
        # TODO: Implement
        pass

    def delete_file(self, content_hash: str) -> bool:
        """Delete a file.

        TODO: Implement file deletion.

        Note: In a real system, you'd need reference counting
        if the same content can be uploaded with different filenames.

        Args:
            content_hash: Hash of file to delete

        Returns:
            True if deleted, False if not found
        """
        # TODO: Implement
        pass


@mock_aws
def exercise() -> None:
    """Test your file upload service."""
    print("Exercise 1: Content-Addressed File Upload API")
    print("=" * 50)

    # Set up S3
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="uploads")

    # Create service
    service = FileUploadService(s3, "uploads")

    # TODO: Test your implementation
    # 1. Upload a file
    # 2. Upload the same file with different name (should dedup)
    # 3. Download and verify
    # 4. List all files
    # 5. Delete a file

    print("\nImplement the TODO sections and verify:")
    print("1. Files are uploaded with content hash as key")
    print("2. Duplicate content is detected (dedup)")
    print("3. Downloads are verified")
    print("4. Metadata is stored and retrievable")
    print("5. Files can be listed and deleted")


if __name__ == "__main__":
    exercise()
