# FSD YAML Config

Learn to write FSD (Full-Stack Definition) YAML service configurations for deploying cloud applications across multiple AWS compute platforms.

## Learning Objectives

After completing this skill, you will be able to:
- Understand the FSD YAML schema structure and required fields
- Write service definitions for ECS, EKS, Lambda, and Batch platforms
- Configure compute resources, networking, and environment variables
- Apply best practices for production-ready configurations
- Translate application requirements into valid FSD YAML

## Prerequisites

- Basic understanding of YAML syntax
- Familiarity with AWS services (ECS, EKS, Lambda, Batch)
- Understanding of containerized applications
- Docker Compose skill recommended

## Quick Start

```bash
# Validate example configurations
make validate-all

# Validate a specific example
make validate YAML=examples/01-basic-ecs-service.yml

# Run exercises
make exercises

# Check your solutions
make check-solutions
```

## Platform Types

FSD supports four primary compute platforms:

| Platform | Use Case | Container Support |
|----------|----------|-------------------|
| **ECS** | Long-running services, APIs | Docker containers on Fargate/EC2 |
| **EKS** | Kubernetes workloads | Kubernetes pods |
| **Lambda** | Event-driven functions | Container images or code packages |
| **Batch** | Job processing, ETL | Docker containers with job queues |

## Concepts

### Service Definition Structure

Every FSD YAML file follows this basic structure:

```yaml
name: my-service
platform: ecs

# Service metadata
description: Brief description of the service
team: platform-team
tags:
  environment: production
  cost-center: engineering

# Platform-specific configuration
compute:
  cpu: 256
  memory: 512

# Environment configuration
environment:
  LOG_LEVEL: info

# Dependencies (covered in fsd-dependencies skill)
dependencies: []
```

### Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| `name` | Unique service identifier | `user-api` |
| `platform` | Target compute platform | `ecs`, `eks`, `lambda`, `batch` |
| `compute` | Resource allocation | CPU, memory, scaling |

### Platform-Specific Fields

#### ECS Services

```yaml
platform: ecs
compute:
  cpu: 512
  memory: 1024
  desired_count: 2

networking:
  port: 8080
  health_check:
    path: /health
    interval: 30
```

#### EKS Services

```yaml
platform: eks
compute:
  replicas: 3
  resources:
    requests:
      cpu: "250m"
      memory: "256Mi"
    limits:
      cpu: "500m"
      memory: "512Mi"
```

#### Lambda Functions

```yaml
platform: lambda
compute:
  memory: 256
  timeout: 30
  runtime: python3.11

triggers:
  - type: api_gateway
    path: /users
    method: GET
```

#### Batch Jobs

```yaml
platform: batch
compute:
  vcpus: 2
  memory: 4096

job:
  type: array
  size: 100
  retry_attempts: 3
```

## Examples

### Example 1: Basic ECS Service

A simple REST API service running on ECS Fargate.

```bash
make validate YAML=examples/01-basic-ecs-service.yml
```

See [examples/01-basic-ecs-service.yml](./examples/01-basic-ecs-service.yml)

### Example 2: EKS Worker Service

A Kubernetes worker deployment with autoscaling.

```bash
make validate YAML=examples/02-eks-worker-service.yml
```

See [examples/02-eks-worker-service.yml](./examples/02-eks-worker-service.yml)

### Example 3: Lambda Event Handler

A serverless function triggered by API Gateway and SQS.

```bash
make validate YAML=examples/03-lambda-event-handler.yml
```

See [examples/03-lambda-event-handler.yml](./examples/03-lambda-event-handler.yml)

### Example 4: Batch Data Processor

A batch job for processing large datasets.

```bash
make validate YAML=examples/04-batch-data-processor.yml
```

See [examples/04-batch-data-processor.yml](./examples/04-batch-data-processor.yml)

### Example 5: Production-Ready Service

A full production configuration with all best practices.

```bash
make validate YAML=examples/05-production-service.yml
```

See [examples/05-production-service.yml](./examples/05-production-service.yml)

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Convert a Docker Compose service to FSD YAML
2. **Exercise 2**: Write an EKS deployment for a microservice
3. **Exercise 3**: Create a Lambda function with multiple triggers
4. **Exercise 4**: Design a batch processing pipeline

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Mistake 1: Invalid CPU/Memory Combinations (ECS)
ECS Fargate has specific valid CPU/memory combinations. Not all values are allowed.

```yaml
# Invalid - 256 CPU cannot have 2048 memory
compute:
  cpu: 256
  memory: 2048

# Valid combinations for 256 CPU
compute:
  cpu: 256
  memory: 512  # or 1024
```

### Mistake 2: Missing Health Check Configuration
Services without health checks will have deployment issues.

```yaml
# Always include health checks for ECS/EKS services
networking:
  health_check:
    path: /health
    interval: 30
    timeout: 5
    healthy_threshold: 2
    unhealthy_threshold: 3
```

### Mistake 3: Hardcoded Secrets
Never put secrets directly in YAML files.

```yaml
# Bad - secret in plain text
environment:
  DATABASE_PASSWORD: mysecretpassword

# Good - reference from Secrets Manager
environment:
  DATABASE_PASSWORD: ${secrets:my-service/db-password}
```

## Further Reading

- [FSD Dependencies](../fsd-dependencies/) - Managing service dependencies
- [FSD IAM Policies](../fsd-iam-policies/) - IAM policy configuration
- [Docker Compose](../docker-compose/) - Local container orchestration
- [Docker/ECR](../docker-ecr/) - Container image management
