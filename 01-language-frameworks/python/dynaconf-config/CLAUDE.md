# CLAUDE.md - Dynaconf Config

This skill teaches configuration management using Dynaconf, a powerful and flexible library for managing application settings in Python.

## Key Concepts

- **Settings Files**: TOML, YAML, JSON, or INI files for configuration
- **Environments**: Development, staging, production with automatic switching
- **Environment Variables**: Override settings with env vars using prefixes
- **Secrets**: Separate sensitive data in gitignored files
- **Validators**: Ensure configuration meets requirements at startup
- **Layered Settings**: Multiple sources with clear precedence rules

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run basic configuration example
make example-2  # Run multi-environment example
make example-3  # Run validation example
make example-4  # Run advanced features example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
dynaconf-config/
├── src/dynaconf_config/
│   ├── __init__.py
│   └── examples/
│       ├── example_1_basic_config.py
│       ├── example_2_environments.py
│       ├── example_3_validation.py
│       └── example_4_advanced.py
├── exercises/
│   ├── exercise_1_app_config.py
│   ├── exercise_2_multi_service.py
│   ├── exercise_3_secrets_validation.py
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic Settings Instance
```python
from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["settings.toml", ".secrets.toml"],
    envvar_prefix="MYAPP",
    environments=True,
    env_switcher="MYAPP_ENV",
)
```

### Pattern 2: Settings with Validation
```python
from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    settings_files=["settings.toml"],
    validators=[
        Validator("DATABASE_URL", must_exist=True),
        Validator("DEBUG", is_type_of=bool, default=False),
        Validator("PORT", gte=1024, lte=65535),
    ],
)
```

### Pattern 3: Environment-Specific Settings
```toml
# settings.toml
[default]
debug = false
log_level = "INFO"

[development]
debug = true
log_level = "DEBUG"

[production]
debug = false
log_level = "WARNING"
```

### Pattern 4: Computed Settings
```python
from dynaconf import Dynaconf, LazySettings

settings = Dynaconf(
    settings_files=["settings.toml"],
)

# Computed at access time
@settings.add_validator
def database_pool_size(settings):
    if settings.ENV_FOR_DYNACONF == "production":
        return 20
    return 5
```

## Common Mistakes

1. **Missing envvar_prefix**
   - Without prefix, env vars won't be picked up
   - Set `envvar_prefix="MYAPP"` to use `MYAPP_*` env vars

2. **Wrong environment active**
   - Default is `development`
   - Set `export MYAPP_ENV=production` to switch
   - Or use `env_switcher` parameter

3. **Committing secrets**
   - Never commit `.secrets.toml` or `secrets.yaml`
   - Add to `.gitignore` immediately
   - Use `settings_files=["settings.toml", ".secrets.toml"]`

4. **Type confusion with env vars**
   - Env vars are strings by default
   - Use `@cast` or validators for type conversion
   - Or use TOML/YAML for typed values

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make examples` and the README.md. Start with example_1 for basics.

### "How do I use environment variables?"
Set `envvar_prefix="MYAPP"` in Dynaconf init, then use `export MYAPP_SETTING=value`.

### "How do I switch environments?"
Set the environment switcher env var: `export MYAPP_ENV=production`. Configure with `env_switcher` parameter.

### "How do I keep secrets safe?"
Use a separate secrets file (`.secrets.toml`) that's gitignored, or use environment variables for sensitive data.

### "How do I validate settings?"
Use Dynaconf validators:
```python
from dynaconf import Validator
validators = [Validator("API_KEY", must_exist=True)]
```

### "How do I access nested settings?"
Use dot notation or subscript:
```python
settings.database.host  # or
settings["database"]["host"]
```

## Testing Notes

- Tests use pytest with markers
- Run specific tests: `pytest -k "test_name"`
- Check coverage: `make coverage`
- Tests create temporary config files to avoid state pollution

## Dependencies

Key dependencies in pyproject.toml:
- dynaconf>=3.2.0: Core configuration library
- toml: For TOML file support (included with Python 3.11+)
- pyyaml: For YAML file support
- pytest: Testing framework
