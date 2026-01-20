---
name: storing-content-addressed-s3
description: Content-addressed storage patterns using S3, including hash-based keys, deduplication, and immutable data architectures. Use when writing or improving tests.
---

# S3 Content Addressed

## Quick Start
```python
import hashlib
from typing import BinaryIO

def store_content(s3_client, bucket: str, data: bytes) -> str:
    """Store content and return its address (hash)."""
    content_hash = hashlib.sha256(data).hexdigest()
    key = f"objects/{content_hash}"

    # Check if already exists (dedup)
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return content_hash  # Already stored
    except s3_client.exceptions.ClientError:
        pass  # Not found, proceed to store

    # ... see docs/patterns.md for more
```


## Key Points
- Content Addressing
- Deduplication
- Immutability

## Common Mistakes
1. **Using weak hashes for security** - Use SHA-256 for content addressing
2. **Not verifying on read** - Always verify hash after retrieval
3. **Deleting shared content** - Implement reference counting

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples