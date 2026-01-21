---
name: configuring-fsd-services
description: FSD YAML configuration for deploying services to AWS (ECS, EKS, Lambda, Batch). Use when deploying or updating cloud services.
---

# FSD YAML Config

## Quick Start
```yaml
# my-service.yml - Minimal ECS service
name: my-service
platform: ecs

compute:
  cpu: 512
  memory: 1024
  desired_count: 2

networking:
  port: 8080
  health_check:
    path: /health

environment:
  LOG_LEVEL: info
```

Deploy with:
```bash
fsd service ecs deploy --env stage --account 123456789 my-service.yml
```

## Key Points
- **Platforms**: ecs, eks, lambda, batch, ec2, flink, helm, sagemaker
- **Auto-provisioned**: Load balancers, security groups, DNS, IAM roles, log groups
- **Dependencies**: Declare AWS resources and FSD generates IAM policies

## Common Mistakes
1. **Missing health check** - Always configure health_check for ECS/EKS services
2. **Hardcoded secrets** - Use `${secrets:path}` for Secrets Manager references
3. **Wrong platform** - Use lambda for event-driven, ecs/eks for long-running

## More Detail
- docs/concepts.md - Platform selection, compute configuration, networking
- docs/patterns.md - Web API, background worker, batch job patterns

## MCP Integration
The FSD MCP server (`fsd-docs`) provides tools for generating, validating, and looking up FSD configurations. Use it when available for schema validation and CLI command suggestions.