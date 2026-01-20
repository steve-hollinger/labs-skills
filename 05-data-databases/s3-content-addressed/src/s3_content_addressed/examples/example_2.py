"""Example 2: Deduplication System

This example demonstrates building a file deduplication system using
content-addressed storage with chunk-based deduplication.

Key concepts:
- Chunking large files for finer-grained dedup
- Computing deduplication ratios
- Manifest-based file reconstruction
- Cross-file deduplication
"""

import json
import random
from typing import Any

import boto3
from moto import mock_aws

from s3_content_addressed.hasher import compute_hash, short_hash
from s3_content_addressed.store import ChunkedStore, ContentAddressedStore


class FileDeduplicator:
    """File storage with deduplication tracking."""

    def __init__(self, chunked_store: ChunkedStore, metadata_store: Any):
        """Initialize deduplicator.

        Args:
            chunked_store: Store for chunked content
            metadata_store: Store for file metadata
        """
        self.store = chunked_store
        self.metadata = metadata_store
        self.stats = {
            "total_files": 0,
            "total_bytes_input": 0,
            "total_bytes_stored": 0,
            "total_chunks": 0,
            "unique_chunks": 0,
        }

    def store_file(self, filename: str, data: bytes) -> dict[str, Any]:
        """Store a file with deduplication.

        Args:
            filename: Original filename
            data: File content

        Returns:
            Storage result with dedup stats
        """
        # Store chunked
        result = self.store.store_chunked(data)

        # Calculate stats
        input_size = len(data)
        new_data_size = result["new_chunks"] * (
            self.store.chunk_size
            if result["new_chunks"] > 0
            else 0
        )
        # Approximate: last chunk may be smaller
        if result["new_chunks"] > 0:
            chunks = result["chunks"]
            new_data_size = sum(
                c["size"] for i, c in enumerate(chunks)
                if i < result["new_chunks"]
            )

        # Update global stats
        self.stats["total_files"] += 1
        self.stats["total_bytes_input"] += input_size
        self.stats["total_bytes_stored"] += new_data_size
        self.stats["total_chunks"] += result["chunk_count"]
        self.stats["unique_chunks"] += result["new_chunks"]

        # Store file metadata
        file_info = {
            "filename": filename,
            "manifest_hash": result["manifest_hash"],
            "size_bytes": input_size,
            "chunk_count": result["chunk_count"],
            "new_chunks": result["new_chunks"],
            "deduped_chunks": result["deduped_chunks"],
            "dedup_ratio": result["deduped_chunks"] / result["chunk_count"]
            if result["chunk_count"] > 0
            else 0,
        }

        return file_info

    def retrieve_file(self, manifest_hash: str) -> bytes:
        """Retrieve a file by its manifest hash.

        Args:
            manifest_hash: Hash of the file manifest

        Returns:
            Original file content
        """
        return self.store.retrieve_chunked(manifest_hash)

    def get_global_stats(self) -> dict[str, Any]:
        """Get global deduplication statistics.

        Returns:
            Dictionary with dedup stats
        """
        if self.stats["total_bytes_input"] > 0:
            overall_ratio = 1 - (
                self.stats["total_bytes_stored"] / self.stats["total_bytes_input"]
            )
        else:
            overall_ratio = 0

        return {
            **self.stats,
            "overall_dedup_ratio": overall_ratio,
            "space_saved_bytes": (
                self.stats["total_bytes_input"] - self.stats["total_bytes_stored"]
            ),
        }


def create_test_files() -> dict[str, bytes]:
    """Create test files with varying similarity for dedup testing.

    Returns:
        Dictionary of filename -> content
    """
    # Base content that will be shared
    base_header = b"=" * 1000 + b"\nHeader content that appears in all files\n" + b"=" * 1000
    base_footer = b"\n" + b"-" * 1000 + b"\nCommon footer content\n" + b"-" * 1000

    files = {}

    # File 1: Base template
    files["template.txt"] = base_header + b"\nTemplate specific content\n" + base_footer

    # File 2: Uses same header/footer (should dedup those chunks)
    files["document1.txt"] = (
        base_header +
        b"\nDocument 1 unique content: " + b"A" * 500 +
        base_footer
    )

    # File 3: Similar to document1 (high dedup expected)
    files["document2.txt"] = (
        base_header +
        b"\nDocument 2 unique content: " + b"B" * 500 +
        base_footer
    )

    # File 4: Completely different (no dedup expected)
    files["unique.txt"] = b"Completely unique content " * 100

    # File 5: Exact duplicate of document1 (100% dedup)
    files["document1_copy.txt"] = files["document1.txt"]

    return files


def demonstrate_file_deduplication(deduplicator: FileDeduplicator) -> None:
    """Demonstrate file deduplication in action.

    Args:
        deduplicator: FileDeduplicator instance
    """
    print("\n--- Storing Files with Deduplication ---\n")

    files = create_test_files()
    stored_files = []

    for filename, content in files.items():
        result = deduplicator.store_file(filename, content)
        stored_files.append(result)

        dedup_pct = result["dedup_ratio"] * 100
        print(f"{filename}:")
        print(f"  Size: {result['size_bytes']:,} bytes")
        print(f"  Chunks: {result['chunk_count']} ({result['deduped_chunks']} deduped)")
        print(f"  Dedup Ratio: {dedup_pct:.1f}%")
        print()

    # Global stats
    print("--- Global Deduplication Statistics ---\n")
    stats = deduplicator.get_global_stats()

    print(f"Total files processed: {stats['total_files']}")
    print(f"Total input data: {stats['total_bytes_input']:,} bytes")
    print(f"Actual data stored: {stats['total_bytes_stored']:,} bytes")
    print(f"Space saved: {stats['space_saved_bytes']:,} bytes")
    print(f"Overall dedup ratio: {stats['overall_dedup_ratio'] * 100:.1f}%")
    print(f"Total chunks: {stats['total_chunks']} ({stats['unique_chunks']} unique)")


def demonstrate_incremental_backup(deduplicator: FileDeduplicator) -> None:
    """Demonstrate incremental backup scenario.

    Args:
        deduplicator: FileDeduplicator instance
    """
    print("\n--- Incremental Backup Simulation ---\n")

    # Simulate a large database backup
    print("Creating 'backup' data (simulated database dump)...")
    base_data = b"Database records: " + bytes(random.getrandbits(8) for _ in range(50000))

    # Full backup
    print("\nDay 1: Full backup")
    result1 = deduplicator.store_file("backup_day1.db", base_data)
    print(f"  Stored: {result1['size_bytes']:,} bytes")
    print(f"  New chunks: {result1['new_chunks']}")

    # Day 2: Small change (should have high dedup)
    print("\nDay 2: Small change (10% modified)")
    modified_data = base_data[:45000] + b"MODIFIED" * 625  # ~10% change
    result2 = deduplicator.store_file("backup_day2.db", modified_data)
    print(f"  Stored: {result2['size_bytes']:,} bytes")
    print(f"  New chunks: {result2['new_chunks']}")
    print(f"  Deduped chunks: {result2['deduped_chunks']} ({result2['dedup_ratio']*100:.1f}%)")

    # Day 3: Another small change
    print("\nDay 3: Another small change")
    modified_data2 = modified_data[:40000] + b"DAY3CHANGE" * 500 + modified_data[45000:]
    result3 = deduplicator.store_file("backup_day3.db", modified_data2)
    print(f"  Stored: {result3['size_bytes']:,} bytes")
    print(f"  New chunks: {result3['new_chunks']}")
    print(f"  Deduped chunks: {result3['deduped_chunks']} ({result3['dedup_ratio']*100:.1f}%)")


@mock_aws
def main() -> None:
    """Run the deduplication system example."""
    print("Example 2: Deduplication System")
    print("=" * 50)

    # Set up S3
    s3 = boto3.client("s3", region_name="us-east-1")
    bucket_name = "dedup-demo"
    s3.create_bucket(Bucket=bucket_name)

    # Create stores
    chunked_store = ChunkedStore(s3, bucket_name, chunk_size=1024)  # 1KB chunks for demo
    deduplicator = FileDeduplicator(chunked_store, None)

    # Run demonstrations
    demonstrate_file_deduplication(deduplicator)
    demonstrate_incremental_backup(deduplicator)

    # Final stats
    print("\n" + "=" * 50)
    print("Final Global Statistics:")
    stats = deduplicator.get_global_stats()
    print(f"  Space efficiency: {(1 - stats['overall_dedup_ratio']) * 100:.1f}% of original")

    print("\n" + "=" * 50)
    print("Key Takeaways:")
    print("1. Chunking enables dedup across file boundaries")
    print("2. Similar files share common chunks")
    print("3. Incremental backups benefit greatly from dedup")
    print("4. Exact duplicates achieve 100% dedup")
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
