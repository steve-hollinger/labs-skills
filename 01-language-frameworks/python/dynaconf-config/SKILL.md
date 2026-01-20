---
name: configuring-with-dynaconf
description: This skill teaches configuration management using Dynaconf, a powerful and flexible library for managing application settings in Python. Use when writing or improving tests.
---

# Dynaconf Config

## Quick Start
```python
from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["settings.toml", ".secrets.toml"],
    envvar_prefix="MYAPP",
    environments=True,
    env_switcher="MYAPP_ENV",
)
```

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run basic configuration example
make example-2  # Run multi-environment example
make example-3  # Run validation example
make example-4  # Run advanced features example
```

## Key Points
- Settings Files
- Environments
- Environment Variables

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples