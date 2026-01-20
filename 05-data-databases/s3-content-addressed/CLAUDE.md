# CLAUDE.md - S3 Content-Addressed Storage

This skill teaches content-addressed storage patterns using S3, including hash-based keys, deduplication, and immutable data architectures.

## Key Concepts

- **Content Addressing**: Deriving storage keys from content hashes
- **Deduplication**: Storing identical content only once
- **Immutability**: Content at an address never changes
- **Integrity Verification**: Hash validates data correctness
- **Reference Counting**: Tracking usage for garbage collection
- **Chunking**: Breaking large files into addressable pieces

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Basic content-addressed store
make example-2  # Deduplication system
make example-3  # Git-like object store
make test       # Run pytest with mocked S3
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
s3-content-addressed/
├── src/s3_content_addressed/
│   ├── __init__.py
│   ├── store.py           # Content-addressed store
│   ├── hasher.py          # Hashing utilities
│   ├── dedup.py           # Deduplication logic
│   └── examples/
│       ├── example_1.py   # Basic CAS
│       ├── example_2.py   # Deduplication
│       └── example_3.py   # Git-like store
├── exercises/
│   ├── exercise_1.py      # File upload API
│   ├── exercise_2.py      # Chunk dedup
│   ├── exercise_3.py      # Version control
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic Content Store
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

    s3_client.put_object(Bucket=bucket, Key=key, Body=data)
    return content_hash
```

### Pattern 2: Verified Retrieval
```python
def get_content(s3_client, bucket: str, content_hash: str) -> bytes:
    """Retrieve and verify content by hash."""
    key = f"objects/{content_hash}"
    response = s3_client.get_object(Bucket=bucket, Key=key)
    data = response["Body"].read()

    # Verify integrity
    actual_hash = hashlib.sha256(data).hexdigest()
    if actual_hash != content_hash:
        raise ValueError(f"Integrity check failed")

    return data
```

### Pattern 3: Chunked Storage
```python
def store_chunked(s3_client, bucket: str, stream: BinaryIO, chunk_size: int = 1024*1024) -> list[str]:
    """Store large file in content-addressed chunks."""
    chunk_hashes = []

    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        chunk_hash = store_content(s3_client, bucket, chunk)
        chunk_hashes.append(chunk_hash)

    return chunk_hashes
```

## Common Mistakes

1. **Using weak hashes for security**
   - Why it happens: MD5 is faster
   - How to fix: Use SHA-256 for content addressing

2. **Not verifying on read**
   - Why it happens: Assuming storage is trustworthy
   - How to fix: Always verify hash after retrieval

3. **Deleting shared content**
   - Why it happens: Not tracking references
   - How to fix: Implement reference counting

4. **Re-uploading existing content**
   - Why it happens: Not checking existence
   - How to fix: HEAD request before PUT

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make example-1` for the basic CAS pattern.

### "What hash algorithm should I use?"
Recommend SHA-256 for most cases. SHA-1 for Git compatibility. Never MD5 for new systems.

### "How do I handle large files?"
Use chunked storage (Example 2) to break files into pieces and enable dedup across file boundaries.

### "How do I delete content?"
Implement reference counting. Only delete when ref count reaches zero.

## Testing Notes

- Tests use moto library to mock S3
- Run specific tests: `pytest -k "test_content"`
- Use pytest.mark.integration for tests needing real S3
- Test both upload and verified download

## Dependencies

Key dependencies in pyproject.toml:
- boto3: AWS SDK for S3 operations
- moto: Mock AWS services for testing
- pydantic: Data validation
