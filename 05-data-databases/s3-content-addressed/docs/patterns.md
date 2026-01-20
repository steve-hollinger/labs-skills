# Common Patterns

## Overview

This document covers common patterns for content-addressed storage systems, including deduplication strategies, versioning, and caching.

## Pattern 1: Tree-Based Structures (Git-like)

### When to Use

Use tree structures when you need:
- Hierarchical data (directories, namespaces)
- Versioned snapshots of structures
- Efficient diff computation

### Implementation

```python
import hashlib
import json
from typing import Any


class TreeStore:
    """Git-like tree storage with blobs and trees."""

    def __init__(self, s3_client, bucket: str):
        self.s3 = s3_client
        self.bucket = bucket

    def store_blob(self, data: bytes) -> str:
        """Store a blob (file content)."""
        content_hash = hashlib.sha256(data).hexdigest()
        self.s3.put_object(
            Bucket=self.bucket,
            Key=f"objects/{content_hash}",
            Body=data,
            Metadata={"type": "blob"}
        )
        return content_hash

    def store_tree(self, entries: list[dict[str, str]]) -> str:
        """Store a tree (directory).

        entries: [{"name": "file.txt", "type": "blob", "hash": "abc..."}]
        """
        # Sort for deterministic hashing
        sorted_entries = sorted(entries, key=lambda e: e["name"])
        tree_data = json.dumps(sorted_entries).encode()

        content_hash = hashlib.sha256(tree_data).hexdigest()
        self.s3.put_object(
            Bucket=self.bucket,
            Key=f"objects/{content_hash}",
            Body=tree_data,
            Metadata={"type": "tree"}
        )
        return content_hash

    def store_commit(self, tree_hash: str, parent_hash: str | None, message: str) -> str:
        """Store a commit pointing to a tree."""
        commit = {
            "tree": tree_hash,
            "parent": parent_hash,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        commit_data = json.dumps(commit).encode()

        content_hash = hashlib.sha256(commit_data).hexdigest()
        self.s3.put_object(
            Bucket=self.bucket,
            Key=f"objects/{content_hash}",
            Body=commit_data,
            Metadata={"type": "commit"}
        )
        return content_hash
```

### Example

```python
# Store a project snapshot
store = TreeStore(s3, "my-bucket")

# Store files (blobs)
readme_hash = store.store_blob(b"# My Project\n\nWelcome!")
config_hash = store.store_blob(b'{"version": "1.0.0"}')

# Store directory structure (tree)
root_tree = store.store_tree([
    {"name": "README.md", "type": "blob", "hash": readme_hash},
    {"name": "config.json", "type": "blob", "hash": config_hash},
])

# Create commit
commit_hash = store.store_commit(root_tree, None, "Initial commit")
```

### Pitfalls to Avoid

- Forgetting to sort tree entries (non-deterministic hashing)
- Not storing object type metadata
- Creating cycles in commit history

## Pattern 2: Content-Addressed Caching

### When to Use

Use for caching when:
- Cache key derivable from inputs
- Content immutable for given inputs
- Want to share cache across environments

### Implementation

```python
class ContentCache:
    """Cache using content-addressed keys."""

    def __init__(self, s3_client, bucket: str, prefix: str = "cache"):
        self.s3 = s3_client
        self.bucket = bucket
        self.prefix = prefix

    def cache_key(self, *inputs: str) -> str:
        """Generate cache key from inputs."""
        combined = "|".join(inputs)
        return hashlib.sha256(combined.encode()).hexdigest()

    def get(self, *inputs: str) -> bytes | None:
        """Get cached content by inputs."""
        key = f"{self.prefix}/{self.cache_key(*inputs)}"
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()
        except self.s3.exceptions.NoSuchKey:
            return None

    def put(self, content: bytes, *inputs: str) -> str:
        """Cache content with key derived from inputs."""
        cache_hash = self.cache_key(*inputs)
        key = f"{self.prefix}/{cache_hash}"

        self.s3.put_object(Bucket=self.bucket, Key=key, Body=content)
        return cache_hash

    def get_or_compute(
        self,
        compute_fn: Callable[[], bytes],
        *inputs: str
    ) -> bytes:
        """Get from cache or compute and cache."""
        cached = self.get(*inputs)
        if cached is not None:
            return cached

        result = compute_fn()
        self.put(result, *inputs)
        return result
```

### Example

```python
cache = ContentCache(s3, "build-cache")

# Cache build artifacts by source hash
source_hash = compute_hash(source_code)
build_config = "release-linux-x64"

artifact = cache.get_or_compute(
    lambda: expensive_build(source_code),
    source_hash,
    build_config
)
```

### Pitfalls to Avoid

- Including non-deterministic inputs in cache key (timestamps)
- Not invalidating when inputs change semantically
- Cache poisoning (validate content on retrieval)

## Pattern 3: Chunk-Based Deduplication

### When to Use

Use chunk-based dedup when:
- Files are large
- Files have similar sections
- Files are updated incrementally

### Implementation

```python
class ChunkDeduplicator:
    """Chunk-based deduplication with content-defined chunking."""

    def __init__(self, s3_client, bucket: str, target_chunk_size: int = 64 * 1024):
        self.s3 = s3_client
        self.bucket = bucket
        self.target_size = target_chunk_size

    def store_file(self, data: bytes) -> dict[str, Any]:
        """Store file with chunk deduplication."""
        chunks = self._chunk_data(data)
        chunk_refs = []
        new_chunks = 0
        deduped_chunks = 0

        for chunk in chunks:
            chunk_hash = hashlib.sha256(chunk).hexdigest()
            key = f"chunks/{chunk_hash}"

            # Check if chunk exists
            if not self._exists(key):
                self.s3.put_object(Bucket=self.bucket, Key=key, Body=chunk)
                new_chunks += 1
            else:
                deduped_chunks += 1

            chunk_refs.append({
                "hash": chunk_hash,
                "size": len(chunk)
            })

        return {
            "chunks": chunk_refs,
            "total_size": len(data),
            "new_chunks": new_chunks,
            "deduped_chunks": deduped_chunks,
            "dedup_ratio": deduped_chunks / len(chunks) if chunks else 0
        }

    def _chunk_data(self, data: bytes) -> list[bytes]:
        """Split data into chunks using fixed-size chunking.

        For production, consider content-defined chunking (CDC)
        using rolling hash (Rabin fingerprint) for better dedup.
        """
        chunks = []
        for i in range(0, len(data), self.target_size):
            chunks.append(data[i:i + self.target_size])
        return chunks

    def _exists(self, key: str) -> bool:
        try:
            self.s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except:
            return False
```

### Example

```python
deduper = ChunkDeduplicator(s3, "backup-bucket")

# Store first backup
result1 = deduper.store_file(full_backup_1)
print(f"Backup 1: {result1['new_chunks']} new, {result1['deduped_chunks']} deduped")

# Store second backup (mostly same data)
result2 = deduper.store_file(full_backup_2)
print(f"Backup 2: {result2['new_chunks']} new, {result2['deduped_chunks']} deduped")
# Most chunks already exist -> high dedup ratio
```

### Pitfalls to Avoid

- Fixed-size chunks have poor dedup when insertions shift boundaries
- Consider content-defined chunking (CDC) for better results
- Track chunk references for garbage collection

## Pattern 4: Manifest-Based File Sets

### When to Use

Use manifests when:
- Managing collections of files
- Need atomic updates to file sets
- Want to track versions of collections

### Implementation

```python
@dataclass
class FileManifest:
    """Manifest describing a set of files."""

    files: dict[str, str]  # path -> content_hash
    created_at: str
    metadata: dict[str, Any]

    def to_bytes(self) -> bytes:
        return json.dumps(asdict(self), sort_keys=True).encode()

    @classmethod
    def from_bytes(cls, data: bytes) -> "FileManifest":
        return cls(**json.loads(data))


class ManifestStore:
    """Store file sets as content-addressed manifests."""

    def __init__(self, content_store: ContentStore):
        self.store = content_store

    def create_manifest(
        self,
        files: dict[str, bytes],
        metadata: dict[str, Any] | None = None
    ) -> str:
        """Store files and create manifest."""
        file_hashes = {}

        for path, content in files.items():
            content_hash = self.store.store(content)
            file_hashes[path] = content_hash

        manifest = FileManifest(
            files=file_hashes,
            created_at=datetime.utcnow().isoformat(),
            metadata=metadata or {}
        )

        manifest_hash = self.store.store(manifest.to_bytes())
        return manifest_hash

    def get_manifest(self, manifest_hash: str) -> FileManifest:
        """Retrieve manifest by hash."""
        data = self.store.get(manifest_hash)
        return FileManifest.from_bytes(data)

    def diff_manifests(
        self,
        old_hash: str,
        new_hash: str
    ) -> dict[str, list[str]]:
        """Compare two manifests."""
        old = self.get_manifest(old_hash)
        new = self.get_manifest(new_hash)

        added = [p for p in new.files if p not in old.files]
        removed = [p for p in old.files if p not in new.files]
        modified = [
            p for p in new.files
            if p in old.files and new.files[p] != old.files[p]
        ]

        return {"added": added, "removed": removed, "modified": modified}
```

### Example

```python
manifest_store = ManifestStore(content_store)

# Create v1
v1_hash = manifest_store.create_manifest({
    "index.html": b"<html>v1</html>",
    "style.css": b"body { color: black; }",
})

# Create v2 (modified style, added script)
v2_hash = manifest_store.create_manifest({
    "index.html": b"<html>v1</html>",  # Same content, deduped
    "style.css": b"body { color: blue; }",  # Modified
    "app.js": b"console.log('hello')",  # Added
})

# Compare versions
diff = manifest_store.diff_manifests(v1_hash, v2_hash)
print(diff)  # {"added": ["app.js"], "removed": [], "modified": ["style.css"]}
```

### Pitfalls to Avoid

- Not sorting manifest contents (non-deterministic hash)
- Storing manifests without content type
- Forgetting to handle file deletions

## Anti-Patterns

### Anti-Pattern 1: Mutable Content

Allowing content at an address to change.

```python
# BAD: Updating content at same key
def update_document(doc_id: str, new_content: bytes) -> None:
    s3.put_object(Bucket=bucket, Key=f"docs/{doc_id}", Body=new_content)
    # Same key, different content - breaks CAS guarantees!
```

### Better Approach

```python
# GOOD: Create new version with new hash
def update_document(doc_id: str, new_content: bytes) -> str:
    content_hash = store_content(new_content)
    # Update metadata to point to new version
    update_doc_metadata(doc_id, current_hash=content_hash)
    return content_hash
```

### Anti-Pattern 2: Not Verifying on Read

Trusting storage without verification.

```python
# BAD: Assuming content matches hash
def get_content(hash: str) -> bytes:
    return s3.get_object(Bucket=bucket, Key=f"objects/{hash}")["Body"].read()
```

### Better Approach

```python
# GOOD: Always verify
def get_content(expected_hash: str) -> bytes:
    data = s3.get_object(Bucket=bucket, Key=f"objects/{expected_hash}")["Body"].read()
    actual_hash = hashlib.sha256(data).hexdigest()
    if actual_hash != expected_hash:
        raise IntegrityError(f"Hash mismatch: {actual_hash} != {expected_hash}")
    return data
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| File versioning | Tree-Based Structures |
| Build artifacts | Content-Addressed Caching |
| Large file backups | Chunk-Based Deduplication |
| Asset deployment | Manifest-Based File Sets |
| Docker layers | Chunk + Manifest combo |
| Git-like VCS | Tree + Commit structures |
