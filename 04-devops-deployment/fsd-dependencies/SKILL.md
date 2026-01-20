---
name: defining-fsd-dependencies
description: This skill teaches FSD dependency configuration for AWS services (DynamoDB, S3, SQS, RDS) and cross-service integrations. Use when writing or improving tests.
---

# Fsd Dependencies

## Commands
```bash
make validate-all        # Validate all dependency examples
make validate YAML=file  # Validate a specific file
make exercises           # List available exercises
make check-solutions     # Validate exercise solutions
make lint               # Run YAML linting
make clean              # Remove temporary files
```

## Key Points
- Dependency Types
- Access Modes
- IAM Policy Generation

## Common Mistakes
1. **Over-permissive modes** - Always use the minimum required mode
2. **Missing GSI/LSI permissions** - Explicitly list all indexes used by the service
3. **Hardcoded bucket/table names** - Use logical names or environment variables

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples