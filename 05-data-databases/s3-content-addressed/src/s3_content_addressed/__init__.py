"""S3 Content-Addressed Storage - Labs Skills.

This module provides utilities and examples for content-addressed storage
patterns using S3, including hash-based keys, deduplication, and
immutable data architectures.
"""

from s3_content_addressed.hasher import (
    compute_hash,
    compute_hash_streaming,
    verify_hash,
)
from s3_content_addressed.store import (
    ContentAddressedStore,
    IntegrityError,
    StoreResult,
)

__all__ = [
    "ContentAddressedStore",
    "IntegrityError",
    "StoreResult",
    "compute_hash",
    "compute_hash_streaming",
    "verify_hash",
]
