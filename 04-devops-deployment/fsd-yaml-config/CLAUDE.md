# CLAUDE.md - FSD YAML Config

This skill teaches FSD (Full-Stack Definition) YAML configuration for defining cloud services across multiple AWS compute platforms.

## Key Concepts

- **Platform Types**: ECS (containers), EKS (Kubernetes), Lambda (serverless), Batch (job processing)
- **Service Definition**: Name, platform, compute resources, networking, environment
- **Configuration Patterns**: Resource allocation, scaling, health checks, environment variables
- **Best Practices**: Security, observability, resource optimization

## Common Commands

```bash
make validate-all        # Validate all example YAML files
make validate YAML=file  # Validate a specific YAML file
make exercises           # List available exercises
make check-solutions     # Validate exercise solutions
make lint               # Run YAML linting
make clean              # Remove temporary files
```

## Project Structure

```
fsd-yaml-config/
├── README.md
├── CLAUDE.md
├── Makefile
├── docs/
│   ├── concepts.md          # Core FSD concepts
│   └── patterns.md          # Configuration patterns
├── examples/
│   ├── 01-basic-ecs-service.yml
│   ├── 02-eks-worker-service.yml
│   ├── 03-lambda-event-handler.yml
│   ├── 04-batch-data-processor.yml
│   └── 05-production-service.yml
└── exercises/
    ├── exercise-1-docker-to-fsd.md
    ├── exercise-2-eks-microservice.md
    ├── exercise-3-lambda-triggers.md
    ├── exercise-4-batch-pipeline.md
    └── solutions/
        ├── solution-1.yml
        ├── solution-2.yml
        ├── solution-3.yml
        └── solution-4.yml
```

## FSD YAML Schema

### Required Fields

```yaml
name: string           # Service identifier (lowercase, hyphens)
platform: string       # ecs | eks | lambda | batch
compute: object        # Platform-specific compute config
```

### Optional Fields

```yaml
description: string    # Human-readable description
team: string          # Owning team
tags: object          # Key-value metadata
environment: object   # Environment variables
networking: object    # Network configuration
dependencies: array   # External dependencies (see fsd-dependencies)
```

## Platform-Specific Patterns

### ECS Pattern
```yaml
name: api-service
platform: ecs
compute:
  cpu: 512           # vCPU units (256, 512, 1024, 2048, 4096)
  memory: 1024       # Memory in MB
  desired_count: 2   # Number of tasks
networking:
  port: 8080
  health_check:
    path: /health
```

### EKS Pattern
```yaml
name: worker-service
platform: eks
compute:
  replicas: 3
  resources:
    requests:
      cpu: "250m"
      memory: "256Mi"
```

### Lambda Pattern
```yaml
name: event-handler
platform: lambda
compute:
  memory: 256        # MB (128-10240)
  timeout: 30        # Seconds (1-900)
  runtime: python3.11
triggers:
  - type: api_gateway
```

### Batch Pattern
```yaml
name: data-processor
platform: batch
compute:
  vcpus: 2
  memory: 4096
job:
  type: array
  size: 100
```

## Valid ECS CPU/Memory Combinations

| CPU (units) | Valid Memory (MB) |
|-------------|-------------------|
| 256 | 512, 1024, 2048 |
| 512 | 1024, 2048, 3072, 4096 |
| 1024 | 2048, 3072, 4096, 5120, 6144, 7168, 8192 |
| 2048 | 4096-16384 (1024 increments) |
| 4096 | 8192-30720 (1024 increments) |

## Common Mistakes

1. **Invalid CPU/Memory combinations for ECS**
   - ECS Fargate has strict valid combinations
   - Use the table above to verify

2. **Missing health checks**
   - Services without health checks fail gracefully
   - Always define path, interval, timeout

3. **Hardcoded secrets**
   - Use `${secrets:path}` syntax for secrets
   - Never commit plain-text credentials

4. **Incorrect resource units**
   - ECS: CPU in units (256, 512...), memory in MB
   - EKS: CPU in millicores ("250m"), memory with unit ("256Mi")
   - Lambda: memory in MB only

5. **Missing networking for web services**
   - ECS/EKS web services need port and health_check
   - Lambda with API Gateway needs triggers configured

## When Users Ask About...

### "How do I choose a platform?"
- **ECS**: Long-running services, REST APIs, background workers
- **EKS**: Complex Kubernetes needs, multi-cloud, advanced orchestration
- **Lambda**: Event-driven, sporadic traffic, quick scaling needs
- **Batch**: Data processing, ETL, scheduled jobs

### "What's the minimum configuration?"
```yaml
name: my-service
platform: ecs
compute:
  cpu: 256
  memory: 512
```

### "How do I add environment variables?"
```yaml
environment:
  LOG_LEVEL: info
  DATABASE_URL: ${secrets:my-service/db-url}
  AWS_REGION: us-east-1
```

### "How do I configure autoscaling?"
```yaml
# ECS autoscaling
scaling:
  min_count: 2
  max_count: 10
  target_cpu_utilization: 70

# EKS autoscaling
compute:
  autoscaling:
    enabled: true
    min_replicas: 2
    max_replicas: 10
    metrics:
      - type: cpu
        target: 70
```

### "How do I validate my YAML?"
```bash
make validate YAML=my-service.yml
```

## Testing Notes

- YAML validation uses schema checks for structure
- Platform-specific validation ensures valid configurations
- Run `make validate-all` before committing changes

## Dependencies

Key tools used:
- `yamllint`: YAML syntax validation
- FSD CLI: Schema validation (if available)
- `yq`: YAML processing

## Related Skills

- [FSD Dependencies](../fsd-dependencies/) - External service dependencies
- [FSD IAM Policies](../fsd-iam-policies/) - IAM configuration
- [Docker Compose](../docker-compose/) - Local development equivalent
