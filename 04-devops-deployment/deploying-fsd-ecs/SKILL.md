---
name: deploying-fsd-ecs
description: Deploy Python services to ECS using FSD with proper configuration, scaling, and dependencies. Use when deploying Python services to Fetch's infrastructure.
tags: ['python', 'fsd', 'ecs', 'deployment', 'aws', 'fetch']
---

# FSD YAML Configuration

## Quick Start
```yaml
# my-service.yml
apiVersion: fsd/v1
kind: Service

metadata:
  name: my-service
  pack: my-pack

service:
  type: ecs
  port: 8000
  healthCheck:
    path: /health
    interval: 30
  resources:
    cpu: 1024      # 1 vCPU
    memory: 2048   # 2 GB
  environment:
    SERVICE_NAME: my-service
    ENVIRONMENT: ${ENV}
```

## Key Points
- Health check path must match FastAPI `/health` endpoint (required for ECS)
- Resources: Start with 1 vCPU (1024) and 2GB RAM (2048) for Python services
- Use `${ENV}` placeholder for environment-specific values (dev/stage/prod)
- Always define MSK dependencies with IAM permissions for Kafka consumers
- Store secrets in AWS Secrets Manager, reference by ARN in `secrets:` section

## Common Mistakes
1. **Missing health check configuration** - ECS will fail to route traffic without health checks
2. **Hardcoding environment values** - Use `${ENV}` for environment-agnostic configs
3. **Not defining MSK permissions** - Kafka consumers need IAM cluster permissions (Connect, ReadData, DescribeGroup)
4. **Over-provisioning resources** - Start small (1 vCPU/2GB), scale based on actual usage metrics
5. **Exposing secrets in environment variables** - Use `secrets:` with Secrets Manager ARNs, not plaintext

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
