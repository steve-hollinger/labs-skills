---
name: initializing-python-projects
description: Initialize Python microservices with standardized structure and tooling. Use when starting a new Python service at Fetch.
tags: ['python', 'project-setup', 'uv', 'poetry', 'structure']
---

# Python Project Initialization

## Quick Start
```yaml
skill: python-project-init
inputs:
  - service_name
  - service_type: [fastapi, lambda, cli, library]
outputs:
  - project structure
  - pyproject.toml with dependencies
  - Dockerfile
  - .pre-commit-config.yaml
  - Makefile
  - README.md template
```

## Key Points
- Mirror test structure to source structure
- Keep services under 5000 lines
- Use type hints everywhere
- Include health check endpoint

## Common Mistakes
1. **TODO: Common Mistake 1** - Add description and how to avoid
2. **TODO: Common Mistake 2** - Add description and how to avoid
3. **TODO: Common Mistake 3** - Add description and how to avoid

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
