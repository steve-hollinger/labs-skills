"""Generator for CLAUDE.md files from templates."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from jinja2 import Environment, BaseLoader


class ProjectType(Enum):
    """Types of projects for template generation."""

    WEB_API = "web_api"
    CLI_TOOL = "cli_tool"
    LIBRARY = "library"
    MONOREPO = "monorepo"
    FRONTEND = "frontend"
    DATA_PIPELINE = "data_pipeline"


@dataclass
class ProjectConfig:
    """Configuration for generating a CLAUDE.md file."""

    name: str
    project_type: ProjectType
    description: str
    language: str = "python"
    framework: Optional[str] = None
    test_framework: str = "pytest"
    additional_sections: Optional[dict[str, str]] = None


# Base template for CLAUDE.md files
BASE_TEMPLATE = """# CLAUDE.md - {{ config.name }}

{{ config.description }}

## Overview

{% if config.project_type == ProjectType.WEB_API %}
This is a web API service that provides HTTP endpoints for {{ config.name | lower }}.
{% elif config.project_type == ProjectType.CLI_TOOL %}
This is a command-line tool for {{ config.name | lower }}.
{% elif config.project_type == ProjectType.LIBRARY %}
This is a reusable library providing {{ config.name | lower }} functionality.
{% elif config.project_type == ProjectType.FRONTEND %}
This is a frontend application for {{ config.name | lower }}.
{% elif config.project_type == ProjectType.DATA_PIPELINE %}
This is a data pipeline for processing {{ config.name | lower }}.
{% else %}
This is a {{ config.project_type.value }} project.
{% endif %}

## Key Commands

```bash
{% if config.language == "python" %}
# Setup
make setup          # Install dependencies with UV
make dev            # Start development server

# Testing
make test           # Run all tests
make test-unit      # Run unit tests only
make coverage       # Run tests with coverage

# Code Quality
make lint           # Run linter checks
make format         # Auto-format code
make typecheck      # Run type checker
{% elif config.language == "go" %}
# Setup
make setup          # Download dependencies

# Testing
make test           # Run all tests
make test-race      # Run tests with race detector

# Code Quality
make lint           # Run golangci-lint
make fmt            # Format code
{% elif config.language == "typescript" %}
# Setup
npm install         # Install dependencies

# Development
npm run dev         # Start development server
npm run build       # Build for production

# Testing
npm test            # Run tests
npm run lint        # Run linter
{% endif %}
```

## Project Structure

```
{{ config.name | lower | replace(" ", "-") }}/
{% if config.language == "python" %}
├── src/
│   └── {{ config.name | lower | replace(" ", "_") | replace("-", "_") }}/
│       ├── __init__.py
│       ├── main.py
│       └── ...
├── tests/
│   ├── unit/
│   └── integration/
├── pyproject.toml
└── Makefile
{% elif config.language == "go" %}
├── cmd/
│   └── {{ config.name | lower | replace(" ", "-") }}/
│       └── main.go
├── internal/
│   └── ...
├── go.mod
└── Makefile
{% elif config.language == "typescript" %}
├── src/
│   ├── components/
│   ├── hooks/
│   └── index.ts
├── tests/
├── package.json
└── tsconfig.json
{% endif %}
```

## Code Patterns

{% if config.language == "python" %}
### Error Handling
Use custom exceptions with context:
```python
from {{ config.name | lower | replace(" ", "_") | replace("-", "_") }}.exceptions import {{ config.name | replace(" ", "") }}Error

# Good
raise {{ config.name | replace(" ", "") }}Error("Description", context={"key": "value"})

# Bad
raise Exception("Something went wrong")
```

### Type Hints
All functions must have type hints:
```python
# Good
def process_data(items: list[Item], limit: int = 100) -> ProcessResult:
    ...

# Bad
def process_data(items, limit=100):
    ...
```
{% elif config.language == "go" %}
### Error Handling
Wrap errors with context:
```go
// Good
return fmt.Errorf("failed to process item %s: %w", itemID, err)

// Bad
return err
```

### Logging
Use structured logging:
```go
// Good
log.Info("processing item", "item_id", itemID, "status", status)

// Bad
log.Printf("processing item %s", itemID)
```
{% endif %}

## Common Mistakes

1. **[Mistake 1 - customize for your project]**
   - Why it happens: ...
   - How to avoid: ...

2. **[Mistake 2 - customize for your project]**
   - Why it happens: ...
   - How to avoid: ...

## When Users Ask About...

### "How do I run this locally?"
```bash
make setup && make dev
```

### "How do I add a new feature?"
1. Create a branch from main
2. Implement the feature with tests
3. Run `make lint && make test`
4. Submit a pull request

### "How do I debug issues?"
{% if config.language == "python" %}
- Check logs: `tail -f logs/app.log`
- Run with debug: `DEBUG=1 make dev`
- Use debugger: `python -m pdb src/main.py`
{% elif config.language == "go" %}
- Check logs: `tail -f logs/app.log`
- Run with verbose: `go run -v ./cmd/...`
- Use delve: `dlv debug ./cmd/main`
{% endif %}

## Testing Notes

- All PRs require passing tests
- Minimum coverage: 80%
- Integration tests require: {% if config.project_type == ProjectType.WEB_API %}running database{% elif config.project_type == ProjectType.DATA_PIPELINE %}test data fixtures{% else %}no external dependencies{% endif %}

{% if config.framework %}
## Framework-Specific Notes

This project uses {{ config.framework }}. Key conventions:
- [Add framework-specific guidance here]
{% endif %}

{% if config.additional_sections %}
{% for section_name, section_content in config.additional_sections.items() %}
## {{ section_name }}

{{ section_content }}

{% endfor %}
{% endif %}
"""


def generate_claude_md(config: ProjectConfig) -> str:
    """Generate a CLAUDE.md file from a project configuration.

    Args:
        config: Project configuration specifying type, language, etc.

    Returns:
        Generated CLAUDE.md content as a string.
    """
    env = Environment(loader=BaseLoader())
    template = env.from_string(BASE_TEMPLATE)

    # Make ProjectType available in template
    return template.render(config=config, ProjectType=ProjectType)


def generate_from_prompts() -> ProjectConfig:
    """Interactive prompt-based configuration builder.

    Returns:
        ProjectConfig based on user input.
    """
    print("CLAUDE.md Generator")
    print("=" * 40)

    name = input("Project name: ").strip()
    description = input("Brief description: ").strip()

    print("\nProject types:")
    for i, pt in enumerate(ProjectType, 1):
        print(f"  {i}. {pt.value}")
    type_choice = int(input("Select type (1-6): ").strip())
    project_type = list(ProjectType)[type_choice - 1]

    print("\nLanguages: python, go, typescript")
    language = input("Primary language: ").strip().lower()

    framework = input("Framework (or press Enter to skip): ").strip() or None

    return ProjectConfig(
        name=name,
        project_type=project_type,
        description=description,
        language=language,
        framework=framework,
    )


# Convenience functions for common project types
def generate_web_api_template(
    name: str,
    description: str,
    language: str = "python",
    framework: Optional[str] = None,
) -> str:
    """Generate CLAUDE.md for a web API project."""
    config = ProjectConfig(
        name=name,
        project_type=ProjectType.WEB_API,
        description=description,
        language=language,
        framework=framework,
    )
    return generate_claude_md(config)


def generate_cli_template(
    name: str,
    description: str,
    language: str = "python",
) -> str:
    """Generate CLAUDE.md for a CLI tool."""
    config = ProjectConfig(
        name=name,
        project_type=ProjectType.CLI_TOOL,
        description=description,
        language=language,
    )
    return generate_claude_md(config)


def generate_library_template(
    name: str,
    description: str,
    language: str = "python",
) -> str:
    """Generate CLAUDE.md for a library."""
    config = ProjectConfig(
        name=name,
        project_type=ProjectType.LIBRARY,
        description=description,
        language=language,
    )
    return generate_claude_md(config)
