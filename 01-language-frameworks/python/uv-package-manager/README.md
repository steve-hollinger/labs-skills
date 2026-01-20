# UV Package Manager

Learn UV, the fast Python package and project manager written in Rust. UV provides a modern, performant alternative to pip, poetry, and pyenv combined into a single tool.

## Learning Objectives

After completing this skill, you will be able to:
- Initialize and manage Python projects with UV
- Handle dependencies and virtual environments efficiently
- Use lock files for reproducible builds
- Compare UV workflows to pip/poetry/pyenv
- Integrate UV into CI/CD pipelines

## Prerequisites

- Python 3.11+
- UV installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Basic Python development experience

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

### Project Initialization

UV can initialize new Python projects with a single command:

```bash
# Create a new project
uv init my-project

# Create a library project
uv init --lib my-library

# Create with specific Python version
uv init --python 3.12 my-project
```

### Dependency Management

Add and manage dependencies with simple commands:

```bash
# Add a production dependency
uv add requests

# Add a dev dependency
uv add --dev pytest

# Add with version constraint
uv add "fastapi>=0.100"

# Remove a dependency
uv remove requests
```

### Virtual Environments

UV manages virtual environments automatically:

```bash
# Create a venv (if not using uv sync)
uv venv

# Activate manually (optional)
source .venv/bin/activate

# Run commands in the venv
uv run python script.py
uv run pytest
```

## Examples

### Example 1: Basic Project Setup

Initialize a project and add dependencies.

```bash
make example-1
```

### Example 2: Lock Files and Reproducible Builds

Work with uv.lock for deterministic installs.

```bash
make example-2
```

### Example 3: Multi-Environment Management

Handle dev, test, and production environments.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Initialize a FastAPI project with UV
2. **Exercise 2**: Migrate a pip requirements.txt project to UV
3. **Exercise 3**: Set up a monorepo with multiple packages

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## UV vs Other Tools

| Feature | UV | pip | poetry | pyenv |
|---------|-----|-----|--------|-------|
| Speed | Very Fast | Slow | Medium | N/A |
| Lock files | Yes | No (pip-tools) | Yes | N/A |
| Virtual envs | Built-in | External | Built-in | No |
| Python versions | Built-in | No | No | Yes |
| Single binary | Yes | No | No | No |

## Common Mistakes

### Mistake 1: Forgetting to use `uv run`

When working with UV, run Python commands through UV to ensure the virtual environment is used:

```bash
# Wrong
python script.py

# Correct
uv run python script.py
```

### Mistake 2: Manually editing uv.lock

The lock file is auto-generated. Edit pyproject.toml instead:

```bash
# Wrong
vim uv.lock

# Correct
uv add package-name  # Updates both pyproject.toml and uv.lock
```

## Further Reading

- [UV Official Documentation](https://docs.astral.sh/uv/)
- [UV GitHub Repository](https://github.com/astral-sh/uv)
- Related skills in this repository:
  - [Ruff Linting](../../../09-code-quality/python/ruff-linting/)
  - [PyProject.toml Standards](../../python/pydantic-v2/)
