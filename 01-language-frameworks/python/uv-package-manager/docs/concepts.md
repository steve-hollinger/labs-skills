# Core Concepts

## Overview

UV is a fast Python package and project manager written in Rust by Astral. It combines the functionality of pip, pip-tools, pyenv, virtualenv, and poetry into a single tool with exceptional performance.

## Concept 1: Project Structure

### What It Is

UV projects follow Python packaging standards with pyproject.toml as the central configuration file. UV adds a uv.lock file for reproducible installations.

### Why It Matters

- Standard pyproject.toml means compatibility with the Python ecosystem
- Lock files ensure every developer and CI system uses exact same versions
- No more "works on my machine" issues

### How It Works

```bash
# Initialize a new project
uv init my-project

# This creates:
# my-project/
# ├── pyproject.toml    # Project configuration
# ├── README.md         # Documentation
# ├── .python-version   # Python version pin
# └── src/
#     └── my_project/
#         └── __init__.py
```

```toml
# pyproject.toml structure
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = ["pytest", "ruff"]
```

## Concept 2: Dependency Resolution

### What It Is

UV uses a fast, correct dependency resolver that finds compatible versions of all packages and their transitive dependencies.

### Why It Matters

- Resolves conflicts that pip would fail on
- Much faster than pip (10-100x in benchmarks)
- Produces deterministic results via lock files

### How It Works

```bash
# Add a dependency (updates pyproject.toml and uv.lock)
uv add requests

# Add with version constraint
uv add "fastapi>=0.100,<1.0"

# Add development dependency
uv add --dev pytest pytest-cov

# View dependency tree
uv tree
```

The resolver:
1. Parses all requirements from pyproject.toml
2. Fetches metadata for all packages (in parallel)
3. Builds a dependency graph
4. Solves for compatible versions
5. Writes results to uv.lock

## Concept 3: Virtual Environments

### What It Is

UV automatically creates and manages virtual environments for project isolation.

### Why It Matters

- No need to manually create/activate venvs
- Each project has isolated dependencies
- Consistent environment across team members

### How It Works

```bash
# UV creates .venv automatically on first sync
uv sync

# Run commands in the venv without activation
uv run python script.py
uv run pytest

# Or activate manually if preferred
source .venv/bin/activate
python script.py
```

UV stores venvs in `.venv` by default, following modern conventions.

## Concept 4: Lock Files

### What It Is

The uv.lock file records exact versions of all dependencies (direct and transitive) for reproducible installs.

### Why It Matters

- Same versions installed everywhere (dev, CI, production)
- Security: pinned versions prevent supply chain attacks
- Auditability: clear record of what's installed

### How It Works

```bash
# Install from lock file (fast, no resolution needed)
uv sync

# Update lock file when pyproject.toml changes
uv lock

# Update a specific package
uv lock --upgrade-package requests

# Update all packages to latest compatible versions
uv lock --upgrade
```

The lock file format:
```toml
# uv.lock (auto-generated, do not edit)
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
```

## Concept 5: Python Version Management

### What It Is

UV can download, install, and manage multiple Python versions without requiring pyenv or similar tools.

### Why It Matters

- Single tool for entire Python workflow
- Easy testing across Python versions
- Consistent version management across team

### How It Works

```bash
# Install a Python version
uv python install 3.12

# List available versions
uv python list

# Pin project to specific version
uv python pin 3.11

# Run with different version
uv run --python 3.12 python script.py
```

## Summary

Key takeaways from UV concepts:

1. **Single Tool**: UV replaces pip, poetry, pyenv, and virtualenv
2. **Speed**: Written in Rust, parallel operations, global cache
3. **Reproducibility**: Lock files ensure consistent installs
4. **Standards**: Uses pyproject.toml (PEP 621)
5. **Simplicity**: `uv add`, `uv sync`, `uv run` cover most workflows
