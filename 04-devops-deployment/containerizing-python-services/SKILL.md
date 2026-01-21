---
name: containerizing-python-services
description: Build production Docker images with multi-stage builds, health checks, and optimization. Use when containerizing Python services for ECS deployment.
tags: ['python', 'docker', 'containerization', 'multi-stage', 'gunicorn']
---

# Dockerfile for Python Services

## Quick Start
```dockerfile
# Dockerfile
FROM python:3.11-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies (without dev dependencies)
RUN uv pip install --system --no-cache .
```

## Key Points
- Use multi-stage builds to separate build dependencies from runtime image (reduces size by 50%+)
- Run as non-root user (UID 1000) for security - ECS requires this
- Include HEALTHCHECK directive for ECS health monitoring at `/health` endpoint
- Use `uv` for fast dependency installation instead of pip (5-10x faster)
- Set worker count to CPU cores, not 2×CPU+1 (async doesn't need extra workers)

## Common Mistakes
1. **Installing dev dependencies in production** - Use `uv pip install --system --no-cache .` without `--dev` flag
2. **Running as root user** - Always create and switch to non-root user with `USER appuser`
3. **Not cleaning apt cache** - Add `rm -rf /var/lib/apt/lists/*` after apt-get to reduce layer size
4. **Copying entire project directory** - Copy only necessary files (pyproject.toml, src/) to avoid cache invalidation
5. **Missing health check** - ECS requires HEALTHCHECK directive that curls `/health` endpoint

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
