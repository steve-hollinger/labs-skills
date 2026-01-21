---
name: configuring-with-dynaconf
description: Configuration management using Dynaconf, a powerful and flexible library for managing application settings in Python. Use when writing or improving tests.
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


## Key Points
- Settings Files
- Environments
- Environment Variables

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples