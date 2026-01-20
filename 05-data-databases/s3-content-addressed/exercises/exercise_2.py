"""Exercise 2: Implement Chunk-Based Deduplication

Build a chunk-based deduplication system that can efficiently
store large files and detect shared chunks across files.

Requirements:
1. Split files into fixed-size chunks
2. Store each chunk with content-addressed key
3. Create manifests that reference chunks
4. Track deduplication statistics
5. Reassemble files from manifests

Bonus: Implement content-defined chunking (CDC) for better dedup

Instructions:
1. Implement the ChunkDeduplicator class
2. Handle chunk boundaries correctly
3. Track new vs deduplicated chunks
4. Implement file reconstruction

Hints:
- Fixed-size chunks are simpler but less effective
- Last chunk may be smaller than chunk_size
- Store manifest as JSON with chunk list
- Consider parallel chunk uploads for performance
"""

import json
from dataclasses import dataclass
from typing import Any

import boto3
from moto import mock_aws

from s3_content_addressed.hasher import compute_hash


@dataclass
class ChunkInfo:
    """Information about a stored chunk."""

    hash: str
    offset: int
    size: int


@dataclass
class FileManifest:
    """Manifest describing a chunked file."""

    chunks: list[ChunkInfo]
    total_size: int
    filename: str
    chunk_size: int


@dataclass
class DedupStats:
    """Deduplication statistics."""

    total_chunks: int
    new_chunks: int
    deduped_chunks: int
    total_bytes: int
    new_bytes: int

    @property
    def dedup_ratio(self) -> float:
        """Calculate deduplication ratio (0-1)."""
        if self.total_chunks == 0:
            return 0.0
        return self.deduped_chunks / self.total_chunks

    @property
    def space_saved(self) -> int:
        """Calculate bytes saved by deduplication."""
        return self.total_bytes - self.new_bytes


class ChunkDeduplicator:
    """Chunk-based file deduplication system."""

    def __init__(self, s3_client: Any, bucket: str, chunk_size: int = 64 * 1024):
        """Initialize deduplicator.

        Args:
            s3_client: Boto3 S3 client
            bucket: S3 bucket name
            chunk_size: Size of chunks in bytes (default 64KB)
        """
        self.s3 = s3_client
        self.bucket = bucket
        self.chunk_size = chunk_size

    def store_file(self, filename: str, data: bytes) -> tuple[str, DedupStats]:
        """Store a file with chunk deduplication.

        TODO: Implement chunked storage.

        Steps:
        1. Split data into chunks
        2. For each chunk, compute hash and check if exists
        3. Store new chunks
        4. Create and store manifest
        5. Return manifest hash and stats

        Args:
            filename: Original filename
            data: File content

        Returns:
            Tuple of (manifest_hash, dedup_stats)
        """
        # TODO: Implement
        pass

    def retrieve_file(self, manifest_hash: str) -> tuple[bytes, str]:
        """Retrieve a file from its manifest.

        TODO: Implement file reconstruction.

        Steps:
        1. Get manifest by hash
        2. Retrieve each chunk
        3. Reassemble in order
        4. Verify total size

        Args:
            manifest_hash: Hash of the manifest

        Returns:
            Tuple of (file_content, filename)
        """
        # TODO: Implement
        pass

    def _split_into_chunks(self, data: bytes) -> list[bytes]:
        """Split data into chunks.

        TODO: Implement chunking.

        Args:
            data: Data to split

        Returns:
            List of chunk bytes
        """
        # TODO: Implement
        pass

    def _store_chunk(self, chunk: bytes) -> tuple[str, bool]:
        """Store a chunk, returning hash and whether it was new.

        TODO: Implement chunk storage with dedup detection.

        Args:
            chunk: Chunk data

        Returns:
            Tuple of (chunk_hash, was_new)
        """
        # TODO: Implement
        pass

    def _get_chunk(self, chunk_hash: str) -> bytes:
        """Retrieve a chunk by hash.

        TODO: Implement chunk retrieval.

        Args:
            chunk_hash: Hash of chunk

        Returns:
            Chunk data
        """
        # TODO: Implement
        pass

    def _store_manifest(self, manifest: FileManifest) -> str:
        """Store a manifest and return its hash.

        TODO: Implement manifest storage.

        Args:
            manifest: File manifest

        Returns:
            Manifest hash
        """
        # TODO: Implement
        pass

    def _get_manifest(self, manifest_hash: str) -> FileManifest:
        """Retrieve a manifest by hash.

        TODO: Implement manifest retrieval.

        Args:
            manifest_hash: Hash of manifest

        Returns:
            FileManifest
        """
        # TODO: Implement
        pass


def create_test_files() -> dict[str, bytes]:
    """Create test files with varying similarity."""
    # Common header/footer for dedup
    header = b"=== COMMON HEADER ===" * 100
    footer = b"=== COMMON FOOTER ===" * 100

    return {
        "file1.txt": header + b"File 1 unique content" * 50 + footer,
        "file2.txt": header + b"File 2 unique content" * 50 + footer,
        "file3.txt": b"Completely unique content" * 200,
        "file1_copy.txt": header + b"File 1 unique content" * 50 + footer,  # Exact copy
    }


@mock_aws
def exercise() -> None:
    """Test your chunk deduplicator."""
    print("Exercise 2: Chunk-Based Deduplication")
    print("=" * 50)

    # Set up S3
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="chunks")

    # Create deduplicator
    deduplicator = ChunkDeduplicator(s3, "chunks", chunk_size=1024)

    # TODO: Test your implementation
    # 1. Store test files
    # 2. Track dedup stats for each
    # 3. Verify file2 has some dedup (shared chunks with file1)
    # 4. Verify file1_copy has 100% dedup
    # 5. Retrieve and verify files

    print("\nImplement the TODO sections and verify:")
    print("1. Files are split into chunks correctly")
    print("2. Duplicate chunks are detected")
    print("3. Manifests correctly describe files")
    print("4. Files can be reconstructed from manifests")
    print("5. Dedup stats are accurate")


if __name__ == "__main__":
    exercise()
