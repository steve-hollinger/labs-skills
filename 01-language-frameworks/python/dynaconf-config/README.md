# Dynaconf Config

Master configuration management with Dynaconf - a powerful, flexible configuration library for Python applications that supports multiple file formats, environment variables, and layered settings.

## Learning Objectives

After completing this skill, you will be able to:
- Configure applications using settings files (TOML, YAML, JSON, INI)
- Use environment variables with automatic type casting
- Implement multi-environment configurations (development, staging, production)
- Handle secrets securely with various backends
- Validate settings with custom validators
- Use settings in different application contexts

## Prerequisites

- Python 3.11+
- UV package manager
- Basic understanding of environment variables

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

### Settings Files

Dynaconf supports multiple configuration file formats with automatic detection.

```toml
# settings.toml
[default]
app_name = "MyApp"
debug = false
database_url = "postgresql://localhost/myapp"

[development]
debug = true
database_url = "postgresql://localhost/myapp_dev"

[production]
debug = false
```

```python
from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["settings.toml"],
    environments=True,
    env_switcher="APP_ENV",
)

print(settings.app_name)  # "MyApp"
print(settings.debug)     # True or False based on environment
```

### Environment Variables

Override any setting with environment variables using a configurable prefix.

```bash
export MYAPP_DEBUG=true
export MYAPP_DATABASE_URL="postgresql://prod-server/myapp"
```

```python
settings = Dynaconf(
    envvar_prefix="MYAPP",
    settings_files=["settings.toml"],
)
# Environment variables take precedence
```

### Secrets Management

Keep secrets separate from regular configuration.

```python
settings = Dynaconf(
    settings_files=["settings.toml", ".secrets.toml"],
)
```

## Examples

### Example 1: Basic Configuration

This example demonstrates loading settings from files and environment variables.

```bash
make example-1
```

### Example 2: Multi-Environment Setup

Working with development, staging, and production environments.

```bash
make example-2
```

### Example 3: Settings Validation

Implementing validators to ensure configuration correctness.

```bash
make example-3
```

### Example 4: Advanced Features

Dynamic settings, computed values, and programmatic configuration.

```bash
make example-4
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Basic App Configuration - Set up configuration for a web application
2. **Exercise 2**: Multi-Service Config - Configure multiple services with shared and unique settings
3. **Exercise 3**: Secrets and Validation - Implement secure configuration with validation

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Forgetting envvar_prefix

Without a prefix, Dynaconf won't pick up your environment variables:

```python
# Won't work with MYAPP_DEBUG
settings = Dynaconf(settings_files=["settings.toml"])

# Works with MYAPP_DEBUG
settings = Dynaconf(
    envvar_prefix="MYAPP",
    settings_files=["settings.toml"],
)
```

### Using Wrong Environment

Dynaconf defaults to `[development]` environment. Set the switcher to change:

```bash
export APP_ENV=production
```

### Not Loading Secrets File

Keep secrets in a separate file that's gitignored:

```python
settings = Dynaconf(
    settings_files=["settings.toml", ".secrets.toml"],
)
```

### Case Sensitivity

Dynaconf settings are case-insensitive by default:

```python
settings.DATABASE_URL == settings.database_url  # True
```

## Further Reading

- [Official Dynaconf Documentation](https://www.dynaconf.com/)
- [Dynaconf GitHub](https://github.com/dynaconf/dynaconf)
- Related skills in this repository:
  - [Pydantic v2](../pydantic-v2/) - For settings validation with Pydantic
  - [FastAPI Basics](../fastapi-basics/) - Using configuration in web apps
