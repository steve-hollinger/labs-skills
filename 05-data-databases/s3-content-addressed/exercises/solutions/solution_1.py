"""Solution for Exercise 1: Content-Addressed File Upload API"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import boto3
from moto import mock_aws

from s3_content_addressed.store import ContentAddressedStore


@dataclass
class UploadResult:
    content_hash: str
    filename: str
    size_bytes: int
    was_deduplicated: bool
    upload_time: str


@dataclass
class FileMetadata:
    content_hash: str
    filename: str
    size_bytes: int
    upload_time: str
    content_type: str


class FileUploadService:
    """File upload service with content-addressed storage."""

    def __init__(self, s3_client: Any, bucket: str):
        self.store = ContentAddressedStore(s3_client, bucket)
        self.metadata: dict[str, FileMetadata] = {}

    def upload_file(
        self,
        filename: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> UploadResult:
        """Upload a file with deduplication."""
        upload_time = datetime.utcnow().isoformat() + "Z"

        # Store content
        result = self.store.store(data)

        # Store/update metadata
        self.metadata[result.content_hash] = FileMetadata(
            content_hash=result.content_hash,
            filename=filename,
            size_bytes=len(data),
            upload_time=upload_time,
            content_type=content_type,
        )

        return UploadResult(
            content_hash=result.content_hash,
            filename=filename,
            size_bytes=len(data),
            was_deduplicated=result.was_deduplicated,
            upload_time=upload_time,
        )

    def download_file(self, content_hash: str) -> tuple[bytes, FileMetadata]:
        """Download a file by its content hash."""
        if content_hash not in self.metadata:
            raise ValueError(f"File not found: {content_hash}")

        content = self.store.get(content_hash, verify=True)
        return content, self.metadata[content_hash]

    def file_exists(self, content_hash: str) -> bool:
        """Check if a file exists."""
        return self.store.exists(content_hash)

    def get_metadata(self, content_hash: str) -> FileMetadata | None:
        """Get file metadata."""
        return self.metadata.get(content_hash)

    def list_files(self) -> list[FileMetadata]:
        """List all uploaded files."""
        return list(self.metadata.values())

    def delete_file(self, content_hash: str) -> bool:
        """Delete a file."""
        if content_hash not in self.metadata:
            return False

        self.store.delete(content_hash)
        del self.metadata[content_hash]
        return True


@mock_aws
def solution() -> None:
    """Demonstrate the file upload service solution."""
    print("Solution 1: Content-Addressed File Upload API")
    print("=" * 50)

    # Set up S3
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="uploads")

    # Create service
    service = FileUploadService(s3, "uploads")

    # Upload first file
    print("\n--- Uploading Files ---\n")

    result1 = service.upload_file(
        "document.txt",
        b"Hello, this is my document content!",
        "text/plain"
    )
    print(f"Upload 1: {result1.filename}")
    print(f"  Hash: {result1.content_hash[:16]}...")
    print(f"  Deduplicated: {result1.was_deduplicated}")

    # Upload same content with different name
    result2 = service.upload_file(
        "document_copy.txt",
        b"Hello, this is my document content!",
        "text/plain"
    )
    print(f"\nUpload 2: {result2.filename}")
    print(f"  Hash: {result2.content_hash[:16]}... (same!)")
    print(f"  Deduplicated: {result2.was_deduplicated}")

    # Upload different content
    result3 = service.upload_file(
        "other.txt",
        b"Different content here",
        "text/plain"
    )
    print(f"\nUpload 3: {result3.filename}")
    print(f"  Hash: {result3.content_hash[:16]}... (different)")
    print(f"  Deduplicated: {result3.was_deduplicated}")

    # Download and verify
    print("\n--- Downloading Files ---\n")

    content, metadata = service.download_file(result1.content_hash)
    print(f"Downloaded: {metadata.filename}")
    print(f"  Content: '{content.decode()}'")
    print(f"  Size: {metadata.size_bytes} bytes")

    # List all files
    print("\n--- All Files ---\n")

    for meta in service.list_files():
        print(f"  {meta.filename}: {meta.content_hash[:16]}...")

    # Delete a file
    print("\n--- Deleting File ---\n")

    deleted = service.delete_file(result3.content_hash)
    print(f"Deleted other.txt: {deleted}")
    print(f"Files remaining: {len(service.list_files())}")

    print("\n" + "=" * 50)
    print("Solution completed successfully!")


if __name__ == "__main__":
    solution()
