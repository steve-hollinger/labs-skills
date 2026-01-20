# Core Concepts

## Overview

Dynaconf is a layered configuration system for Python that supports multiple file formats, environment variables, and runtime settings. It provides a clean separation between code and configuration while supporting complex deployment scenarios.

## Concept 1: Settings Instance

### What It Is

The `Dynaconf` class is the central interface for accessing configuration. It loads settings from multiple sources and provides attribute-style access to values.

### Why It Matters

- Centralizes all configuration in one object
- Provides type casting and validation
- Supports multiple file formats
- Enables environment-based configuration

### How It Works

```python
from dynaconf import Dynaconf

# Create settings instance
settings = Dynaconf(
    # List of configuration files to load (in order)
    settings_files=["settings.toml", "settings.yaml", ".secrets.toml"],

    # Prefix for environment variables (MYAPP_DEBUG=true)
    envvar_prefix="MYAPP",

    # Enable environment sections ([development], [production])
    environments=True,

    # Environment variable to switch environments
    env_switcher="MYAPP_ENV",

    # Default environment
    env="development",
)

# Access settings
print(settings.DEBUG)           # Boolean
print(settings.DATABASE_URL)    # String
print(settings.PORT)            # Integer (auto-converted from TOML)
```

## Concept 2: Configuration Sources and Precedence

### What It Is

Dynaconf loads configuration from multiple sources with a clear precedence order. Later sources override earlier ones.

### Why It Matters

- Allows sensible defaults with environment overrides
- Supports 12-factor app methodology
- Enables different configurations per environment
- Keeps secrets separate from version control

### How It Works

Precedence order (highest to lowest):
1. **Runtime settings** (`settings.set("key", value)`)
2. **Environment variables** (`MYAPP_DEBUG=true`)
3. **Secrets files** (`.secrets.toml`)
4. **Settings files** (`settings.toml`)
5. **Default values**

```python
# settings.toml
[default]
debug = false
port = 8000

# .secrets.toml (gitignored)
[default]
api_key = "secret-key-here"

# Environment variable
# export MYAPP_DEBUG=true

# Result: debug=true (from env var), port=8000 (from file), api_key="secret..."
```

## Concept 3: Environments

### What It Is

Dynaconf supports environment-based configuration sections that automatically switch based on an environment variable.

### Why It Matters

- Same codebase, different configurations
- No code changes needed for deployment
- Clear separation of environment concerns
- Inheritance from default section

### How It Works

```toml
# settings.toml

# Base settings inherited by all environments
[default]
app_name = "MyApp"
debug = false
database.host = "localhost"
database.port = 5432

# Development overrides
[development]
debug = true
database.name = "myapp_dev"

# Production overrides
[production]
debug = false
database.host = "prod-db.example.com"
database.name = "myapp_prod"
```

```python
from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["settings.toml"],
    environments=True,
    env_switcher="APP_ENV",
)

# With APP_ENV=development
# settings.debug -> True
# settings.database.host -> "localhost" (inherited from default)
# settings.database.name -> "myapp_dev"

# With APP_ENV=production
# settings.debug -> False
# settings.database.host -> "prod-db.example.com"
# settings.database.name -> "myapp_prod"
```

## Concept 4: Environment Variables

### What It Is

Settings can be overridden via environment variables using a configurable prefix, supporting nested keys and type casting.

### Why It Matters

- 12-factor app compliance
- Container and cloud-friendly
- No file changes needed for deployment
- Secrets can stay out of files entirely

### How It Works

```python
settings = Dynaconf(
    envvar_prefix="MYAPP",  # Use MYAPP_ prefix
    settings_files=["settings.toml"],
)
```

```bash
# Simple override
export MYAPP_DEBUG=true           # -> settings.debug = True

# With type casting (use @type syntax)
export MYAPP_PORT=@int 8080       # -> settings.port = 8080 (int)
export MYAPP_HOSTS=@json ["a","b"]  # -> settings.hosts = ["a", "b"]

# Nested settings (use double underscore)
export MYAPP_DATABASE__HOST=prod.db.com  # -> settings.database.host

# Boolean conversions (automatic)
export MYAPP_ENABLED=true   # True
export MYAPP_ENABLED=1      # True
export MYAPP_ENABLED=yes    # True
export MYAPP_ENABLED=false  # False
```

## Concept 5: Validators

### What It Is

Validators ensure configuration values meet requirements at application startup, failing fast if configuration is invalid.

### Why It Matters

- Catches misconfiguration early
- Documents configuration requirements
- Provides clear error messages
- Supports default values

### How It Works

```python
from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    settings_files=["settings.toml"],
    validators=[
        # Required settings
        Validator("DATABASE_URL", must_exist=True),
        Validator("API_KEY", must_exist=True, messages={
            "must_exist": "API_KEY is required for authentication"
        }),

        # Type validation
        Validator("DEBUG", is_type_of=bool),
        Validator("PORT", is_type_of=int),

        # Range validation
        Validator("PORT", gte=1024, lte=65535),
        Validator("WORKERS", gte=1, lte=32),

        # Conditional validation
        Validator("SSL_CERT", must_exist=True, when=Validator("USE_SSL", eq=True)),

        # Default values
        Validator("LOG_LEVEL", default="INFO"),
        Validator("TIMEOUT", default=30, is_type_of=int),

        # Environment-specific
        Validator("DEBUG", eq=False, env="production"),
    ],
)

# Validates immediately on instantiation
# Raises ValidationError with details if any validator fails
```

## Concept 6: Secrets Management

### What It Is

Dynaconf supports separating sensitive configuration into dedicated files or external sources that are never committed to version control.

### Why It Matters

- Security best practice
- Prevents accidental secret exposure
- Supports different secret values per environment
- Compatible with secret management tools

### How It Works

```python
settings = Dynaconf(
    settings_files=[
        "settings.toml",      # General configuration (committed)
        ".secrets.toml",      # Local secrets (gitignored)
    ],
    envvar_prefix="MYAPP",
)

# .gitignore
# .secrets.toml
# .secrets.yaml
# .secrets.json
```

```toml
# .secrets.toml (never commit!)
[default]
database_password = "dev-password"
api_key = "dev-api-key"

[production]
database_password = "@vault path/to/secret"  # Optional vault integration
api_key = "prod-api-key"
```

For production, prefer environment variables:
```bash
export MYAPP_DATABASE_PASSWORD="production-password"
export MYAPP_API_KEY="production-api-key"
```

## Summary

Key takeaways from these concepts:

1. **Settings Instance** is your gateway to all configuration
2. **Precedence rules** let you layer defaults, files, and env vars
3. **Environments** enable same code, different configs
4. **Environment Variables** enable 12-factor app compliance
5. **Validators** catch misconfiguration at startup
6. **Secrets** stay secure with proper separation

Together, these concepts enable robust, secure, and maintainable configuration for any Python application.
