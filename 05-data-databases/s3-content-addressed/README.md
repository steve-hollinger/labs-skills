# S3 Content-Addressed Storage

Master content-addressed storage patterns using S3, including hash-based object keys, deduplication strategies, and immutable data architectures.

## Learning Objectives

After completing this skill, you will be able to:
- Implement content-addressed storage (CAS) patterns with S3
- Generate and use hash-based object keys
- Build deduplication systems for large-scale data storage
- Implement Git-like object stores
- Apply CAS patterns to caching and artifact storage

## Prerequisites

- Python 3.11+
- UV package manager
- Basic understanding of hashing algorithms
- Familiarity with S3 operations
- AWS account (optional, for production testing)

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Concepts

### What is Content-Addressed Storage?

Content-addressed storage (CAS) is a method where data is stored and retrieved based on its content rather than its location. The key (address) is derived from the content itself, typically using a cryptographic hash.

```python
import hashlib

def content_address(data: bytes) -> str:
    """Generate content address (hash) for data."""
    return hashlib.sha256(data).hexdigest()

# Same content always produces same address
data = b"Hello, World!"
address = content_address(data)  # "dffd6021bb2bd5b0af676290809ec3a5..."

# Store in S3 using hash as key
s3.put_object(Bucket="my-bucket", Key=f"objects/{address}", Body=data)
```

### Benefits of CAS

| Benefit | Description |
|---------|-------------|
| Deduplication | Identical content stored only once |
| Integrity | Hash verifies data hasn't changed |
| Immutability | Content at address never changes |
| Caching | Safe to cache indefinitely |
| Distribution | Content can be verified from any source |

### Common Use Cases

- **Artifact storage**: Build outputs, Docker layers, npm packages
- **Backup systems**: Dedup across backups
- **Version control**: Git object model
- **CDN/Caching**: Cache by content hash
- **Document storage**: Dedup attachments and files

## Examples

### Example 1: Basic Content-Addressed Store

Demonstrates fundamental CAS operations with S3.

```bash
make example-1
```

### Example 2: Deduplication System

Building a deduplication layer for file storage.

```bash
make example-2
```

### Example 3: Git-like Object Store

Implementing a Git-inspired object model with blobs, trees, and commits.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Build a content-addressed file upload API
2. **Exercise 2**: Implement chunk-based deduplication
3. **Exercise 3**: Create a simple version control system

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Using MD5 for Security-Sensitive Applications

MD5 is fast but not cryptographically secure:

```python
# BAD: MD5 has known collisions
import hashlib
address = hashlib.md5(data).hexdigest()

# GOOD: Use SHA-256 for security
address = hashlib.sha256(data).hexdigest()
```

### Not Verifying Content on Read

Always verify content matches its address:

```python
# GOOD: Verify content integrity
def get_verified(bucket: str, key: str) -> bytes:
    expected_hash = key.split("/")[-1]  # Extract hash from key
    data = s3.get_object(Bucket=bucket, Key=key)["Body"].read()

    actual_hash = hashlib.sha256(data).hexdigest()
    if actual_hash != expected_hash:
        raise IntegrityError(f"Content mismatch: {actual_hash} != {expected_hash}")

    return data
```

### Forgetting Reference Counting for Garbage Collection

Content can be shared; don't delete without checking references:

```python
# Track references to content
metadata_table.update_item(
    Key={"content_hash": hash},
    UpdateExpression="ADD ref_count :one",
    ExpressionAttributeValues={":one": 1}
)
```

## Further Reading

- [Content-Addressable Storage](https://en.wikipedia.org/wiki/Content-addressable_storage)
- [Git Internals - Git Objects](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)
- Related skills in this repository:
  - [DynamoDB Schema Design](../dynamodb-schema/)
  - [S3 Operations](../s3-operations/)
