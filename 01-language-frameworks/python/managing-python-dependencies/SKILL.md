---
name: managing-python-dependencies
description: Manage Python dependencies with pyproject.toml using uv or poetry. Use when configuring package dependencies for a Python project.
tags: ['python', 'dependencies', 'pyproject', 'uv', 'poetry']
---

# Dependency Management with pyproject.toml

## Quick Start
```toml
[tool.poetry]
name = "service-name"
version = "0.1.0"
description = "Service description"
authors = ["Fetch Rewards"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.95.1"
pydantic = "^2.6.0"  # Use v2 for new projects
uvicorn = {extras = ["standard"], version = "*"}
boto3 = "*"
aiokafka = "*"
opentelemetry-api = "^1.27.0"
opentelemetry-sdk = "^1.27.0"
opentelemetry-exporter-otlp-proto-grpc = "^1.27.0"
opentelemetry-instrumentation-fastapi = "^0.48b0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.2.2"
```

## Key Points
- TODO: Add key point 1
- TODO: Add key point 2
- TODO: Add key point 3

## Common Mistakes
1. **TODO: Common Mistake 1** - Add description and how to avoid
2. **TODO: Common Mistake 2** - Add description and how to avoid
3. **TODO: Common Mistake 3** - Add description and how to avoid

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
