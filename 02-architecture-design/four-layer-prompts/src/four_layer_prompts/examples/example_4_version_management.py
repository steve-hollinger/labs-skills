"""Example 4: Prompt Version Management.

This example demonstrates managing prompt versions for reproducibility,
A/B testing, and tracking changes over time.

Run with: make example-4
Or: uv run python -m four_layer_prompts.examples.example_4_version_management
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from four_layer_prompts.layers import PromptLayers
from four_layer_prompts.templates import LayerTemplate


@dataclass
class PromptVersion:
    """A versioned prompt configuration.

    Attributes:
        version: Semantic version string.
        layers: The prompt layer templates.
        description: Human-readable description of this version.
        created_at: Timestamp of version creation.
        metadata: Additional metadata (author, tags, etc).
    """

    version: str
    layers: PromptLayers
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def content_hash(self) -> str:
        """Generate a hash of the prompt content.

        Returns:
            Short hash string identifying this prompt content.
        """
        content = (
            f"{self.layers.system}"
            f"{self.layers.context}"
            f"{self.layers.instruction}"
            f"{self.layers.constraint}"
        )
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def render(self, variables: dict[str, Any] | None = None) -> str:
        """Render the prompt with optional variables.

        Args:
            variables: Variables to substitute in templates.

        Returns:
            Rendered prompt string.
        """
        vars_dict = variables or {}

        # Apply variable substitution to each layer
        system = LayerTemplate(self.layers.system).render(**vars_dict)
        context = LayerTemplate(self.layers.context).render(**vars_dict)
        instruction = LayerTemplate(self.layers.instruction).render(**vars_dict)
        constraint = LayerTemplate(self.layers.constraint).render(**vars_dict)

        return PromptLayers(
            system=system,
            context=context,
            instruction=instruction,
            constraint=constraint,
        ).compose()


class VersionManager:
    """Manages multiple prompt versions."""

    def __init__(self) -> None:
        """Initialize empty version manager."""
        self._versions: dict[str, PromptVersion] = {}
        self._active: str | None = None
        self._history: list[tuple[datetime, str, str]] = []  # timestamp, version, action

    def register(self, version: PromptVersion) -> None:
        """Register a new prompt version.

        Args:
            version: The version to register.
        """
        self._versions[version.version] = version
        self._history.append((datetime.now(), version.version, "registered"))

    def set_active(self, version: str) -> None:
        """Set the active prompt version.

        Args:
            version: Version string to activate.

        Raises:
            KeyError: If version not found.
        """
        if version not in self._versions:
            raise KeyError(f"Version {version} not found")

        previous = self._active
        self._active = version
        self._history.append((datetime.now(), version, f"activated (was: {previous})"))

    def get_active(self) -> PromptVersion:
        """Get the currently active version.

        Returns:
            The active PromptVersion.

        Raises:
            ValueError: If no version is active.
        """
        if not self._active:
            raise ValueError("No active version set")
        return self._versions[self._active]

    def get_version(self, version: str) -> PromptVersion:
        """Get a specific version.

        Args:
            version: Version string to retrieve.

        Returns:
            The requested PromptVersion.
        """
        return self._versions[version]

    def list_versions(self) -> list[str]:
        """List all registered versions.

        Returns:
            List of version strings.
        """
        return list(self._versions.keys())

    def compare_versions(self, v1: str, v2: str) -> dict[str, dict[str, str]]:
        """Compare two versions.

        Args:
            v1: First version string.
            v2: Second version string.

        Returns:
            Dictionary showing differences per layer.
        """
        version1 = self._versions[v1]
        version2 = self._versions[v2]

        result = {}
        for layer in ["system", "context", "instruction", "constraint"]:
            l1 = getattr(version1.layers, layer)
            l2 = getattr(version2.layers, layer)

            if l1 != l2:
                result[layer] = {v1: l1, v2: l2}

        return result

    def get_history(self) -> list[tuple[datetime, str, str]]:
        """Get version change history.

        Returns:
            List of (timestamp, version, action) tuples.
        """
        return self._history.copy()


def example_basic_versioning() -> None:
    """Demonstrate basic version management."""
    print("=== Basic Versioning ===\n")

    manager = VersionManager()

    # Version 1.0.0 - Initial version
    v1 = PromptVersion(
        version="1.0.0",
        layers=PromptLayers(
            system="You are a helpful assistant.",
            context="User query: $query",
            instruction="Answer the question.",
            constraint="Be concise.",
        ),
        description="Initial release",
        metadata={"author": "team-a"},
    )

    # Version 1.1.0 - Improved instructions
    v1_1 = PromptVersion(
        version="1.1.0",
        layers=PromptLayers(
            system="You are a helpful assistant.",
            context="User query: $query",
            instruction="Answer the question thoroughly but stay on topic.",
            constraint="Be concise. Maximum 100 words.",
        ),
        description="Improved instruction clarity and added word limit",
        metadata={"author": "team-a"},
    )

    # Version 2.0.0 - Major update
    v2 = PromptVersion(
        version="2.0.0",
        layers=PromptLayers(
            system="You are an expert assistant with deep knowledge across domains.",
            context="User query: $query\nUser expertise level: $level",
            instruction="Provide a comprehensive answer tailored to the user's expertise level.",
            constraint="Format response with headers. Adjust complexity based on expertise level.",
        ),
        description="Major update with user expertise adaptation",
        metadata={"author": "team-b", "breaking_change": True},
    )

    # Register versions
    manager.register(v1)
    manager.register(v1_1)
    manager.register(v2)

    print("Registered versions:")
    for ver in manager.list_versions():
        v = manager.get_version(ver)
        print(f"  {ver}: {v.description} (hash: {v.content_hash})")

    # Set active version
    manager.set_active("1.1.0")
    print(f"\nActive version: {manager.get_active().version}")

    # Render with variables
    prompt = manager.get_active().render({"query": "What is Python?"})
    print(f"\nRendered prompt:\n{prompt}")


def example_version_comparison() -> None:
    """Demonstrate comparing versions."""
    print("\n=== Version Comparison ===\n")

    manager = VersionManager()

    v1 = PromptVersion(
        version="1.0.0",
        layers=PromptLayers(
            system="You are a code reviewer.",
            context="Code: $code",
            instruction="Review the code.",
            constraint="List issues.",
        ),
    )

    v2 = PromptVersion(
        version="2.0.0",
        layers=PromptLayers(
            system="You are a senior code reviewer focused on security and performance.",
            context="Code: $code\nLanguage: $language",
            instruction="Review the code for security vulnerabilities and performance issues.",
            constraint="List issues with severity ratings.",
        ),
    )

    manager.register(v1)
    manager.register(v2)

    differences = manager.compare_versions("1.0.0", "2.0.0")

    print("Differences between 1.0.0 and 2.0.0:")
    for layer, changes in differences.items():
        print(f"\n{layer.upper()}:")
        print(f"  1.0.0: {changes['1.0.0'][:50]}...")
        print(f"  2.0.0: {changes['2.0.0'][:50]}...")


def example_ab_testing() -> None:
    """Demonstrate A/B testing setup."""
    print("\n=== A/B Testing Setup ===\n")

    import random

    manager = VersionManager()

    # Control prompt (A)
    control = PromptVersion(
        version="control",
        layers=PromptLayers(
            system="You are a helpful assistant.",
            instruction="Answer the question.",
            constraint="Be helpful.",
        ),
        metadata={"experiment": "response_quality", "variant": "A"},
    )

    # Treatment prompt (B)
    treatment = PromptVersion(
        version="treatment",
        layers=PromptLayers(
            system="You are an expert assistant who provides detailed, accurate answers.",
            instruction="Answer the question with supporting reasoning.",
            constraint="Include confidence level. Cite sources if possible.",
        ),
        metadata={"experiment": "response_quality", "variant": "B"},
    )

    manager.register(control)
    manager.register(treatment)

    # Simulate A/B assignment
    def get_prompt_for_user(user_id: str) -> PromptVersion:
        """Deterministically assign user to variant."""
        hash_val = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        if hash_val % 2 == 0:
            return manager.get_version("control")
        return manager.get_version("treatment")

    # Simulate users
    users = ["user_001", "user_002", "user_003", "user_004", "user_005"]

    print("A/B Test Assignments:")
    for user in users:
        version = get_prompt_for_user(user)
        print(f"  {user} -> {version.version} (variant {version.metadata['variant']})")


def example_version_history() -> None:
    """Demonstrate version history tracking."""
    print("\n=== Version History ===\n")

    manager = VersionManager()

    # Simulate version lifecycle
    versions = [
        PromptVersion("1.0.0", PromptLayers(system="v1"), description="Initial"),
        PromptVersion("1.0.1", PromptLayers(system="v1 patch"), description="Bug fix"),
        PromptVersion("1.1.0", PromptLayers(system="v1.1"), description="Feature update"),
        PromptVersion("2.0.0", PromptLayers(system="v2"), description="Major release"),
    ]

    for v in versions:
        manager.register(v)

    manager.set_active("1.0.0")
    manager.set_active("1.0.1")  # Hotfix
    manager.set_active("1.1.0")  # Feature release
    manager.set_active("2.0.0")  # Major upgrade

    print("Version History:")
    for timestamp, version, action in manager.get_history():
        print(f"  [{timestamp.strftime('%H:%M:%S')}] {version}: {action}")


def example_rollback_pattern() -> None:
    """Demonstrate rollback pattern."""
    print("\n=== Rollback Pattern ===\n")

    class RollbackManager(VersionManager):
        """Version manager with rollback support."""

        def __init__(self) -> None:
            super().__init__()
            self._active_history: list[str] = []

        def set_active(self, version: str) -> None:
            if self._active:
                self._active_history.append(self._active)
            super().set_active(version)

        def rollback(self) -> str | None:
            """Rollback to previous version.

            Returns:
                Previous version string, or None if no history.
            """
            if not self._active_history:
                return None

            previous = self._active_history.pop()
            self._active = previous
            self._history.append((datetime.now(), previous, "rollback"))
            return previous

    manager = RollbackManager()

    manager.register(PromptVersion("1.0.0", PromptLayers(system="Stable")))
    manager.register(PromptVersion("2.0.0", PromptLayers(system="New but buggy")))

    manager.set_active("1.0.0")
    print(f"Active: {manager._active}")

    manager.set_active("2.0.0")
    print(f"Active: {manager._active} (deployed new version)")

    # Simulate issue detected - rollback!
    print("Issue detected! Rolling back...")
    previous = manager.rollback()
    print(f"Active: {manager._active} (rolled back from 2.0.0)")


def main() -> None:
    """Run all version management examples."""
    example_basic_versioning()
    example_version_comparison()
    example_ab_testing()
    example_version_history()
    example_rollback_pattern()
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
