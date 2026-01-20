"""Example 3: Git-like Object Store

This example demonstrates implementing a Git-inspired object model
using content-addressed storage with blobs, trees, and commits.

Key concepts:
- Git object model (blob, tree, commit)
- Tree structures for directories
- Commit history and parent references
- Diff computation between commits
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

import boto3
from moto import mock_aws

from s3_content_addressed.hasher import compute_hash, short_hash
from s3_content_addressed.store import ContentAddressedStore


@dataclass
class Blob:
    """A blob represents file content (like Git blob)."""

    content: bytes
    hash: str = ""

    def __post_init__(self) -> None:
        if not self.hash:
            self.hash = compute_hash(self.content)


@dataclass
class TreeEntry:
    """Entry in a tree (file or subtree)."""

    name: str
    entry_type: str  # "blob" or "tree"
    hash: str


@dataclass
class Tree:
    """A tree represents a directory (like Git tree)."""

    entries: list[TreeEntry]
    hash: str = ""

    def __post_init__(self) -> None:
        if not self.hash:
            # Sort entries for deterministic hashing
            sorted_entries = sorted(self.entries, key=lambda e: e.name)
            data = json.dumps([asdict(e) for e in sorted_entries]).encode()
            self.hash = compute_hash(data)

    def to_bytes(self) -> bytes:
        sorted_entries = sorted(self.entries, key=lambda e: e.name)
        return json.dumps([asdict(e) for e in sorted_entries]).encode()

    @classmethod
    def from_bytes(cls, data: bytes) -> "Tree":
        entries_data = json.loads(data)
        entries = [TreeEntry(**e) for e in entries_data]
        return cls(entries=entries)


@dataclass
class Commit:
    """A commit represents a snapshot with history (like Git commit)."""

    tree_hash: str
    parent_hash: str | None
    message: str
    author: str
    timestamp: str
    hash: str = ""

    def __post_init__(self) -> None:
        if not self.hash:
            data = json.dumps({
                "tree": self.tree_hash,
                "parent": self.parent_hash,
                "message": self.message,
                "author": self.author,
                "timestamp": self.timestamp,
            }).encode()
            self.hash = compute_hash(data)

    def to_bytes(self) -> bytes:
        return json.dumps({
            "tree": self.tree_hash,
            "parent": self.parent_hash,
            "message": self.message,
            "author": self.author,
            "timestamp": self.timestamp,
        }).encode()

    @classmethod
    def from_bytes(cls, data: bytes) -> "Commit":
        commit_data = json.loads(data)
        return cls(**commit_data)


class GitLikeStore:
    """Git-like object store with blobs, trees, and commits."""

    def __init__(self, s3_client: Any, bucket: str):
        """Initialize Git-like store.

        Args:
            s3_client: Boto3 S3 client
            bucket: S3 bucket name
        """
        self.store = ContentAddressedStore(s3_client, bucket, prefix="git-objects")
        self.refs: dict[str, str] = {}  # ref name -> commit hash

    def store_blob(self, content: bytes) -> Blob:
        """Store a blob (file content).

        Args:
            content: File content

        Returns:
            Blob with computed hash
        """
        blob = Blob(content=content)
        self.store.store(content, metadata={"type": "blob"})
        return blob

    def store_tree(self, entries: list[TreeEntry]) -> Tree:
        """Store a tree (directory).

        Args:
            entries: List of tree entries

        Returns:
            Tree with computed hash
        """
        tree = Tree(entries=entries)
        self.store.store(tree.to_bytes(), metadata={"type": "tree"})
        return tree

    def store_commit(
        self,
        tree_hash: str,
        message: str,
        author: str,
        parent_hash: str | None = None,
    ) -> Commit:
        """Store a commit.

        Args:
            tree_hash: Hash of root tree
            message: Commit message
            author: Author name
            parent_hash: Parent commit hash (None for first commit)

        Returns:
            Commit with computed hash
        """
        commit = Commit(
            tree_hash=tree_hash,
            parent_hash=parent_hash,
            message=message,
            author=author,
            timestamp=datetime.utcnow().isoformat(),
        )
        self.store.store(commit.to_bytes(), metadata={"type": "commit"})
        return commit

    def get_blob(self, hash: str) -> bytes:
        """Get blob content by hash."""
        return self.store.get(hash)

    def get_tree(self, hash: str) -> Tree:
        """Get tree by hash."""
        data = self.store.get(hash)
        return Tree.from_bytes(data)

    def get_commit(self, hash: str) -> Commit:
        """Get commit by hash."""
        data = self.store.get(hash)
        return Commit.from_bytes(data)

    def update_ref(self, ref_name: str, commit_hash: str) -> None:
        """Update a reference (like branch) to point to a commit.

        Args:
            ref_name: Reference name (e.g., "main", "feature")
            commit_hash: Commit hash to point to
        """
        self.refs[ref_name] = commit_hash

    def get_ref(self, ref_name: str) -> str | None:
        """Get commit hash for a reference."""
        return self.refs.get(ref_name)

    def diff_trees(self, old_hash: str | None, new_hash: str) -> dict[str, list[str]]:
        """Compute diff between two trees.

        Args:
            old_hash: Old tree hash (None for first commit)
            new_hash: New tree hash

        Returns:
            Dict with added, modified, removed files
        """
        if old_hash is None:
            new_tree = self.get_tree(new_hash)
            return {
                "added": [e.name for e in new_tree.entries],
                "modified": [],
                "removed": [],
            }

        old_tree = self.get_tree(old_hash)
        new_tree = self.get_tree(new_hash)

        old_entries = {e.name: e.hash for e in old_tree.entries}
        new_entries = {e.name: e.hash for e in new_tree.entries}

        added = [n for n in new_entries if n not in old_entries]
        removed = [n for n in old_entries if n not in new_entries]
        modified = [
            n for n in new_entries
            if n in old_entries and new_entries[n] != old_entries[n]
        ]

        return {"added": added, "modified": modified, "removed": removed}

    def get_commit_history(self, commit_hash: str, limit: int = 10) -> list[Commit]:
        """Get commit history starting from a commit.

        Args:
            commit_hash: Starting commit hash
            limit: Maximum commits to return

        Returns:
            List of commits from newest to oldest
        """
        history = []
        current_hash: str | None = commit_hash

        while current_hash and len(history) < limit:
            commit = self.get_commit(current_hash)
            history.append(commit)
            current_hash = commit.parent_hash

        return history


def demonstrate_repository_workflow(store: GitLikeStore) -> None:
    """Demonstrate a Git-like repository workflow.

    Args:
        store: GitLikeStore instance
    """
    print("\n--- Initial Commit ---\n")

    # Create initial files
    readme_blob = store.store_blob(b"# My Project\n\nA demo project.")
    config_blob = store.store_blob(b'{"name": "demo", "version": "1.0.0"}')

    print(f"Created blobs:")
    print(f"  README.md: {short_hash(readme_blob.hash)}...")
    print(f"  config.json: {short_hash(config_blob.hash)}...")

    # Create root tree
    root_tree = store.store_tree([
        TreeEntry(name="README.md", entry_type="blob", hash=readme_blob.hash),
        TreeEntry(name="config.json", entry_type="blob", hash=config_blob.hash),
    ])
    print(f"Created tree: {short_hash(root_tree.hash)}...")

    # Create initial commit
    commit1 = store.store_commit(
        tree_hash=root_tree.hash,
        message="Initial commit",
        author="Alice",
    )
    print(f"Created commit: {short_hash(commit1.hash)}...")
    print(f"  Message: {commit1.message}")

    # Update main ref
    store.update_ref("main", commit1.hash)

    # Second commit - modify README
    print("\n--- Second Commit (modify README) ---\n")

    new_readme = store.store_blob(b"# My Project\n\nA demo project with updates!")
    print(f"New README blob: {short_hash(new_readme.hash)}...")

    # Same config, different readme
    root_tree2 = store.store_tree([
        TreeEntry(name="README.md", entry_type="blob", hash=new_readme.hash),
        TreeEntry(name="config.json", entry_type="blob", hash=config_blob.hash),
    ])
    print(f"New tree: {short_hash(root_tree2.hash)}...")

    commit2 = store.store_commit(
        tree_hash=root_tree2.hash,
        message="Update README",
        author="Alice",
        parent_hash=commit1.hash,
    )
    print(f"Created commit: {short_hash(commit2.hash)}...")
    store.update_ref("main", commit2.hash)

    # Third commit - add new file
    print("\n--- Third Commit (add app.py) ---\n")

    app_blob = store.store_blob(b'print("Hello, World!")')
    print(f"New app.py blob: {short_hash(app_blob.hash)}...")

    root_tree3 = store.store_tree([
        TreeEntry(name="README.md", entry_type="blob", hash=new_readme.hash),
        TreeEntry(name="config.json", entry_type="blob", hash=config_blob.hash),
        TreeEntry(name="app.py", entry_type="blob", hash=app_blob.hash),
    ])

    commit3 = store.store_commit(
        tree_hash=root_tree3.hash,
        message="Add application code",
        author="Bob",
        parent_hash=commit2.hash,
    )
    print(f"Created commit: {short_hash(commit3.hash)}...")
    store.update_ref("main", commit3.hash)

    # Show commit history
    print("\n--- Commit History ---\n")
    history = store.get_commit_history(commit3.hash)

    for commit in history:
        print(f"{short_hash(commit.hash)}... - {commit.message} ({commit.author})")

    # Show diffs
    print("\n--- Diffs Between Commits ---\n")

    diff1 = store.diff_trees(None, commit1.tree_hash)
    print(f"Commit 1 (initial):")
    print(f"  Added: {diff1['added']}")

    diff2 = store.diff_trees(commit1.tree_hash, commit2.tree_hash)
    print(f"Commit 2:")
    print(f"  Modified: {diff2['modified']}")

    diff3 = store.diff_trees(commit2.tree_hash, commit3.tree_hash)
    print(f"Commit 3:")
    print(f"  Added: {diff3['added']}")


def demonstrate_content_deduplication(store: GitLikeStore) -> None:
    """Demonstrate how Git-like store deduplicates content.

    Args:
        store: GitLikeStore instance
    """
    print("\n--- Content Deduplication Demo ---\n")

    # Create two branches with shared content
    print("Creating branch 'feature' from 'main'...")

    main_hash = store.get_ref("main")
    if main_hash:
        main_commit = store.get_commit(main_hash)
        main_tree = store.get_tree(main_commit.tree_hash)

        print(f"Main tree has {len(main_tree.entries)} entries")

        # Feature branch adds a file but keeps others
        new_file = store.store_blob(b"// Feature code")

        feature_tree = store.store_tree([
            *main_tree.entries,
            TreeEntry(name="feature.py", entry_type="blob", hash=new_file.hash),
        ])

        feature_commit = store.store_commit(
            tree_hash=feature_tree.hash,
            message="Add feature",
            author="Carol",
            parent_hash=main_hash,
        )
        store.update_ref("feature", feature_commit.hash)

        print(f"\nFeature branch:")
        print(f"  New tree: {short_hash(feature_tree.hash)}...")
        print(f"  Shared blobs with main: {len(main_tree.entries)}")
        print("  (Existing blobs are NOT duplicated - same hashes)")


@mock_aws
def main() -> None:
    """Run the Git-like object store example."""
    print("Example 3: Git-like Object Store")
    print("=" * 50)

    # Set up S3
    s3 = boto3.client("s3", region_name="us-east-1")
    bucket_name = "git-like-demo"
    s3.create_bucket(Bucket=bucket_name)

    # Create Git-like store
    store = GitLikeStore(s3, bucket_name)

    # Run demonstrations
    demonstrate_repository_workflow(store)
    demonstrate_content_deduplication(store)

    print("\n" + "=" * 50)
    print("Key Takeaways:")
    print("1. Blobs store file content, trees store directory structure")
    print("2. Commits link trees with history (parent commits)")
    print("3. Same content = same hash, enabling sharing across commits")
    print("4. Trees enable efficient directory-level comparisons")
    print("5. This is how Git achieves efficient version control!")
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
