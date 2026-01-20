"""Example 2: Lock Files and Reproducible Builds

This example demonstrates how UV's lock files ensure consistent,
reproducible builds across different environments.
"""

from pathlib import Path


def demonstrate_lock_file_structure() -> None:
    """Show the structure of a uv.lock file."""
    print("\n" + "=" * 60)
    print("STEP 1: Understanding uv.lock Structure")
    print("=" * 60)

    example_lock = '''
# uv.lock - Auto-generated, DO NOT EDIT MANUALLY
version = 1
requires-python = ">=3.11"

[[package]]
name = "certifi"
version = "2024.2.2"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "...", hash = "sha256:..." }
wheels = [
    { url = "...", hash = "sha256:..." },
]

[[package]]
name = "requests"
version = "2.31.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "certifi" },
    { name = "charset-normalizer" },
    { name = "idna" },
    { name = "urllib3" },
]
sdist = { url = "...", hash = "sha256:..." }
wheels = [
    { url = "...", hash = "sha256:..." },
]
'''

    print("""
The uv.lock file records exact versions of ALL dependencies:

Key properties:
- Contains direct AND transitive dependencies
- Includes cryptographic hashes for integrity
- Records the source (registry URL)
- Specifies compatible wheels and source distributions
""")
    print("Example uv.lock structure:")
    print(example_lock)


def demonstrate_lock_commands() -> None:
    """Show lock-related UV commands."""
    print("\n" + "=" * 60)
    print("STEP 2: Lock File Commands")
    print("=" * 60)

    print("""
UV provides several commands for managing lock files:

Creating/Updating lock file:
    uv lock                    # Generate uv.lock from pyproject.toml

Installing from lock file:
    uv sync                    # Install exact versions from lock

Updating specific packages:
    uv lock --upgrade-package requests   # Update only requests
    uv lock --upgrade-package "requests>=2.32"

Updating all packages:
    uv lock --upgrade          # Update all to latest compatible

Viewing locked versions:
    uv tree                    # Show dependency tree with versions
""")


def demonstrate_reproducibility() -> None:
    """Explain why lock files matter for reproducibility."""
    print("\n" + "=" * 60)
    print("STEP 3: Why Lock Files Matter")
    print("=" * 60)

    print("""
Without lock files (pip workflow):
    1. Developer A installs requests (gets 2.31.0)
    2. Developer B installs later (gets 2.32.0 - new release)
    3. CI installs even later (gets 2.32.1)
    4. Bug appears in production that can't be reproduced locally

With lock files (UV workflow):
    1. Developer A adds requests, commits uv.lock
    2. Developer B runs uv sync (gets exact 2.31.0)
    3. CI runs uv sync (gets exact 2.31.0)
    4. Everyone has identical environments

Benefits:
    - "Works on my machine" becomes "works everywhere"
    - Security: known, audited versions
    - Debugging: exact reproduction of issues
    - Compliance: clear dependency inventory
""")


def demonstrate_ci_workflow() -> None:
    """Show CI workflow with lock files."""
    print("\n" + "=" * 60)
    print("STEP 4: CI/CD Integration")
    print("=" * 60)

    ci_example = '''
# .github/workflows/test.yml
name: Test

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Install UV (official action)
      - uses: astral-sh/setup-uv@v4

      # Cache UV's package cache
      - uses: actions/cache@v4
        with:
          path: ~/.cache/uv
          key: uv-${{ hashFiles('uv.lock') }}

      # Install from lock file (fast, deterministic)
      - name: Install dependencies
        run: uv sync --all-extras

      # Run tests in UV environment
      - name: Run tests
        run: uv run pytest

      # Linting
      - name: Lint
        run: |
          uv run ruff check .
          uv run mypy src/
'''

    print("GitHub Actions example with UV:")
    print(ci_example)


def demonstrate_update_workflow() -> None:
    """Show how to update dependencies safely."""
    print("\n" + "=" * 60)
    print("STEP 5: Safe Dependency Updates")
    print("=" * 60)

    print("""
Recommended workflow for updating dependencies:

1. Create a branch for updates:
    git checkout -b update-dependencies

2. Update all packages:
    uv lock --upgrade

3. Review changes:
    git diff uv.lock        # See what changed

4. Run tests:
    uv sync
    uv run pytest

5. Update individual packages (if full update fails):
    uv lock --upgrade-package problematic-package

6. Commit and create PR:
    git add uv.lock
    git commit -m "chore: update dependencies"
    git push

Automation tip:
    Use Dependabot or Renovate for automated dependency updates
    with pull requests.
""")


def demonstrate_comparison() -> None:
    """Compare lock file approaches."""
    print("\n" + "=" * 60)
    print("Comparison: UV vs Other Lock File Approaches")
    print("=" * 60)

    print("""
| Aspect            | UV (uv.lock)     | Poetry        | pip-tools       |
|-------------------|------------------|---------------|-----------------|
| Format            | TOML             | TOML          | requirements.txt|
| Speed             | Very fast        | Medium        | Slow            |
| Hashes            | Yes              | Yes           | Optional        |
| Cross-platform    | Yes              | Partial       | Manual          |
| Integrated        | Yes              | Yes           | Separate tool   |

UV's advantages:
- Fastest resolution by far (Rust-based)
- Single tool (no pip-compile step)
- Modern TOML format
- Built-in hash verification
""")


def main() -> None:
    """Run the lock files example."""
    print("Example 2: Lock Files and Reproducible Builds")
    print("=" * 60)

    print("""
This example explores UV's lock file system for ensuring
reproducible builds across development, CI, and production.

Lock files are essential for:
- Consistent environments across team members
- Reproducible CI/CD pipelines
- Security auditing of dependencies
- Debugging production issues locally
""")

    demonstrate_lock_file_structure()
    demonstrate_lock_commands()
    demonstrate_reproducibility()
    demonstrate_ci_workflow()
    demonstrate_update_workflow()
    demonstrate_comparison()

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Look at uv.lock in this project's root directory")
    print("  2. Try 'uv tree' to see the dependency tree")
    print("  3. Run 'make example-3' to learn about multi-environment setups")


if __name__ == "__main__":
    main()
