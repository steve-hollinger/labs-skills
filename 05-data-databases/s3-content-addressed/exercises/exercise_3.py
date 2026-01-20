"""Exercise 3: Create a Simple Version Control System

Build a minimal version control system inspired by Git using
content-addressed storage for blobs, trees, and commits.

Requirements:
1. Store file content as blobs
2. Store directory structure as trees
3. Create commits with parent references
4. Support branches (refs)
5. Compute diffs between commits

Instructions:
1. Implement Blob, Tree, and Commit classes
2. Implement the VersionControlStore class
3. Support commit history traversal
4. Implement tree diffing

Hints:
- Blobs are just raw file content
- Trees contain entries pointing to blobs or other trees
- Commits point to a root tree and optionally a parent commit
- Branches are just named references to commits
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any

import boto3
from moto import mock_aws

from s3_content_addressed.hasher import compute_hash


@dataclass
class TreeEntry:
    """Entry in a tree (file or directory)."""

    name: str
    entry_type: str  # "blob" or "tree"
    hash: str


@dataclass
class CommitInfo:
    """Information about a commit."""

    tree_hash: str
    parent_hash: str | None
    message: str
    author: str
    timestamp: str
    hash: str


class VersionControlStore:
    """Simple Git-like version control store."""

    def __init__(self, s3_client: Any, bucket: str):
        """Initialize version control store.

        Args:
            s3_client: Boto3 S3 client
            bucket: S3 bucket name
        """
        self.s3 = s3_client
        self.bucket = bucket
        self.refs: dict[str, str] = {}  # branch name -> commit hash

    def store_blob(self, content: bytes) -> str:
        """Store a blob (file content).

        TODO: Implement blob storage.

        Args:
            content: File content

        Returns:
            Blob hash
        """
        # TODO: Implement
        pass

    def get_blob(self, blob_hash: str) -> bytes:
        """Retrieve a blob by hash.

        TODO: Implement blob retrieval.

        Args:
            blob_hash: Hash of blob

        Returns:
            Blob content
        """
        # TODO: Implement
        pass

    def store_tree(self, entries: list[TreeEntry]) -> str:
        """Store a tree (directory structure).

        TODO: Implement tree storage.

        Remember to sort entries for deterministic hashing!

        Args:
            entries: List of tree entries

        Returns:
            Tree hash
        """
        # TODO: Implement
        pass

    def get_tree(self, tree_hash: str) -> list[TreeEntry]:
        """Retrieve a tree by hash.

        TODO: Implement tree retrieval.

        Args:
            tree_hash: Hash of tree

        Returns:
            List of tree entries
        """
        # TODO: Implement
        pass

    def create_commit(
        self,
        tree_hash: str,
        message: str,
        author: str,
        parent_hash: str | None = None,
    ) -> CommitInfo:
        """Create and store a commit.

        TODO: Implement commit creation.

        Args:
            tree_hash: Hash of root tree
            message: Commit message
            author: Author name
            parent_hash: Parent commit hash (None for first commit)

        Returns:
            CommitInfo with hash
        """
        # TODO: Implement
        pass

    def get_commit(self, commit_hash: str) -> CommitInfo:
        """Retrieve a commit by hash.

        TODO: Implement commit retrieval.

        Args:
            commit_hash: Hash of commit

        Returns:
            CommitInfo
        """
        # TODO: Implement
        pass

    def update_branch(self, branch_name: str, commit_hash: str) -> None:
        """Update a branch to point to a commit.

        TODO: Implement branch update.

        Args:
            branch_name: Branch name (e.g., "main")
            commit_hash: Commit hash to point to
        """
        # TODO: Implement
        pass

    def get_branch(self, branch_name: str) -> str | None:
        """Get the commit hash for a branch.

        TODO: Implement branch lookup.

        Args:
            branch_name: Branch name

        Returns:
            Commit hash or None if branch doesn't exist
        """
        # TODO: Implement
        pass

    def get_history(self, commit_hash: str, limit: int = 10) -> list[CommitInfo]:
        """Get commit history starting from a commit.

        TODO: Implement history traversal.

        Args:
            commit_hash: Starting commit
            limit: Maximum commits to return

        Returns:
            List of commits, newest first
        """
        # TODO: Implement
        pass

    def diff_trees(
        self,
        old_tree_hash: str | None,
        new_tree_hash: str,
    ) -> dict[str, list[str]]:
        """Compute diff between two trees.

        TODO: Implement tree diff.

        Args:
            old_tree_hash: Old tree hash (None for initial commit)
            new_tree_hash: New tree hash

        Returns:
            Dict with "added", "modified", "removed" lists
        """
        # TODO: Implement
        pass

    def diff_commits(self, old_hash: str | None, new_hash: str) -> dict[str, list[str]]:
        """Compute diff between two commits.

        TODO: Implement commit diff (wrapper around tree diff).

        Args:
            old_hash: Old commit hash (None for initial)
            new_hash: New commit hash

        Returns:
            Dict with "added", "modified", "removed" lists
        """
        # TODO: Implement
        pass


def create_project_snapshot(
    vcs: VersionControlStore,
    files: dict[str, bytes],
) -> str:
    """Create a tree from a flat file dictionary.

    Helper function to create a tree from files.

    Args:
        vcs: VersionControlStore instance
        files: Dict of path -> content

    Returns:
        Root tree hash
    """
    entries = []
    for path, content in sorted(files.items()):
        blob_hash = vcs.store_blob(content)
        entries.append(TreeEntry(name=path, entry_type="blob", hash=blob_hash))

    return vcs.store_tree(entries)


@mock_aws
def exercise() -> None:
    """Test your version control system."""
    print("Exercise 3: Simple Version Control System")
    print("=" * 50)

    # Set up S3
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="vcs")

    # Create VCS
    vcs = VersionControlStore(s3, "vcs")

    # TODO: Test your implementation
    # 1. Create initial commit with some files
    # 2. Create second commit modifying a file
    # 3. Create third commit adding a file
    # 4. View commit history
    # 5. Compute diff between commits

    print("\nImplement the TODO sections and verify:")
    print("1. Blobs store file content correctly")
    print("2. Trees store directory structure")
    print("3. Commits link trees with history")
    print("4. Branches point to commits")
    print("5. History traversal works")
    print("6. Diffs show changes between commits")


if __name__ == "__main__":
    exercise()
