---
name: deploying-your-first-service
description: Deploy your first service (frontend or backend with SQLite) to ECS staging using FSD and GitHub Actions. Use when you need to deploy a simple service to AWS for the first time.
tags: ['deployment', 'ecs', 'fsd', 'github-actions', 'tutorial', 'beginner']
---

# Deploying Your First Service

## Quick Start

**End-to-end deployment checklist (30-45 minutes):**

1. ✅ Create API with `/health` endpoint (returns 200 status)
2. ✅ Add Dockerfile with HEALTHCHECK instruction
3. ✅ Test locally with `docker-compose up`
4. ✅ Create FSD YAML (service name, health check, resources)
5. ✅ Add GitHub Actions workflow (build → push ECR → deploy FSD)
6. ✅ Push to staging branch
7. ✅ Monitor deployment in ECS console
8. ✅ Verify service responds at ALB endpoint

```yaml
# my-service.yml - Minimal FSD configuration
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
    cpu: 512       # Start small
    memory: 1024   # 1 GB
  environment:
    SERVICE_NAME: my-service
    ENVIRONMENT: ${ENV}
```

## Key Points

- **Health check endpoint is mandatory for ECS** - Without `/health` returning 200, ECS tasks fail and restart continuously
- **FSD abstracts AWS infrastructure** - No manual ECS cluster, ALB, target group, or IAM role setup needed
- **Start with minimal resources** - 512 CPU (0.5 vCPU) and 1024 memory (1 GB), scale based on actual metrics
- **Use docker-compose for local testing** - Catch issues before deploying (missing dependencies, port conflicts, environment variables)
- **GitHub Actions automates the pipeline** - Build Docker image → Push to ECR → Deploy with FSD CLI on every push to staging

## Common Mistakes

1. **Missing /health endpoint** - ECS health checks fail → tasks never become healthy → deployment hangs. Always implement a health endpoint that returns 200 status.
2. **Dockerfile missing HEALTHCHECK** - Container passes ECS checks but application crashes silently. Add `HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1`.
3. **FSD healthCheck.path doesn't match app route** - FSD YAML says `/health` but app only has `/healthz`. Paths must match exactly.
4. **Running container as root user (UID 0)** - ECS security policy rejects root containers. Use `USER 1000` in Dockerfile.
5. **Hardcoding environment values instead of using ${ENV}** - Can't promote from staging to prod. Use `ENVIRONMENT: ${ENV}` for environment-agnostic configs.

## More Detail

- [docs/concepts.md](docs/concepts.md) - ECS, Fargate, containers, FSD fundamentals, CI/CD pipeline overview
- [docs/patterns.md](docs/patterns.md) - Step-by-step tutorials with Python, Node.js, and Go examples
