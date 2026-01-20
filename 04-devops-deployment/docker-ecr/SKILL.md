---
name: building-docker-images
description: This skill teaches Docker containerization best practices and AWS ECR workflows for production deployments. Use when implementing authentication or verifying tokens.
---

# Docker Ecr

## Commands
```bash
make setup      # Verify Docker is installed
make examples   # Build all example images
make example-1  # Build basic Python example
make example-2  # Build multi-stage Go example
make example-3  # Build secure Node.js example
make lint       # Lint Dockerfiles with hadolint
```

## Key Points
- Dockerfile Optimization
- Multi-Stage Builds
- ECR Workflow

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples