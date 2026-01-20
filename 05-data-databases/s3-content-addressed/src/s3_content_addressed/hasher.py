"""Hashing utilities for content-addressed storage.

Provides functions for computing and verifying content hashes.
"""

import hashlib
from typing import BinaryIO


def compute_hash(data: bytes, algorithm: str = "sha256") -> str:
    """Compute content hash using specified algorithm.

    Args:
        data: Content to hash
        algorithm: Hash algorithm (sha256, sha1, blake2b)

    Returns:
        Hexadecimal hash string

    Example:
        >>> compute_hash(b"Hello, World!")
        'dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f'
    """
    hasher = hashlib.new(algorithm)
    hasher.update(data)
    return hasher.hexdigest()


def compute_hash_streaming(
    stream: BinaryIO,
    algorithm: str = "sha256",
    chunk_size: int = 8192,
) -> str:
    """Compute hash of large file without loading into memory.

    Args:
        stream: File-like object to hash
        algorithm: Hash algorithm
        chunk_size: Size of chunks to read

    Returns:
        Hexadecimal hash string

    Example:
        >>> with open("large_file.bin", "rb") as f:
        ...     file_hash = compute_hash_streaming(f)
    """
    hasher = hashlib.new(algorithm)
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        hasher.update(chunk)
    return hasher.hexdigest()


def verify_hash(data: bytes, expected_hash: str, algorithm: str = "sha256") -> bool:
    """Verify that data matches expected hash.

    Args:
        data: Content to verify
        expected_hash: Expected hash value
        algorithm: Hash algorithm

    Returns:
        True if hash matches, False otherwise

    Example:
        >>> data = b"Hello, World!"
        >>> hash_val = compute_hash(data)
        >>> verify_hash(data, hash_val)
        True
    """
    actual_hash = compute_hash(data, algorithm)
    return actual_hash == expected_hash


def hash_with_prefix(data: bytes, prefix: str, algorithm: str = "sha256") -> str:
    """Compute hash with type prefix (Git-style).

    Git prepends "blob {size}\0" before hashing.

    Args:
        data: Content to hash
        prefix: Type prefix (e.g., "blob", "tree", "commit")
        algorithm: Hash algorithm

    Returns:
        Hexadecimal hash string

    Example:
        >>> hash_with_prefix(b"content", "blob")
        # Returns hash of "blob 7\0content"
    """
    header = f"{prefix} {len(data)}\0".encode()
    hasher = hashlib.new(algorithm)
    hasher.update(header)
    hasher.update(data)
    return hasher.hexdigest()


def short_hash(full_hash: str, length: int = 8) -> str:
    """Get shortened hash for display.

    Args:
        full_hash: Full hash string
        length: Number of characters to return

    Returns:
        Shortened hash

    Example:
        >>> short_hash("dffd6021bb2bd5b0af676290809ec3a5...")
        'dffd6021'
    """
    return full_hash[:length]
