# Core Concepts: Deploying Python Services with FSD to ECS

## What

FSD (Fetch Service Deploy) is Fetch's internal infrastructure-as-code tool for deploying services to AWS ECS. It provides a declarative YAML format for defining:
- Service metadata (name, pack, owners)
- Compute resources (CPU, memory, scaling policies)
- Networking (VPC, load balancers, service discovery)
- Dependencies (MSK, DynamoDB, S3)
- Observability (metrics, traces, logs)

FSD abstracts away ECS task definitions, IAM roles, security groups, and target groups into a single YAML file that works across all environments (dev/stage/preprod/prod).

## Why

**Problem:** Manually configuring ECS deployments requires:
- Writing complex CloudFormation/Terraform
- Managing IAM roles and policies per service
- Coordinating security groups across VPCs
- Configuring load balancers and target groups
- Setting up service discovery and health checks

**Solution:** FSD provides:
- **Standardization** - All Fetch services use the same deployment pattern
- **Environment Parity** - Same YAML works in dev/stage/prod with `${ENV}` placeholders
- **Dependency Management** - Automatic IAM permissions for MSK, DynamoDB, S3
- **Security** - Built-in secrets management, VPC isolation, least-privilege IAM
- **Observability** - Automatic CloudWatch logs, OTLP traces, Prometheus metrics

**Context at Fetch:**
- 100+ services deployed via FSD across all environments
- Primary platform: ECS Fargate (serverless containers)
- Standard stack: Python FastAPI + MSK + DynamoDB + OTLP
- Deployment flow: GitHub Actions → FSD CLI → CloudFormation → ECS
- Environments: dev (sandbox), stage (pre-prod), preprod (prod-like), prod

## How

### FSD Architecture

```
┌─────────────────────────────────────────────────────┐
│           FSD YAML Configuration                    │
│     (my-service.yml)                                │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│              FSD CLI                                │
│  - Validates YAML schema                            │
│  - Resolves ${ENV} placeholders                     │
│  - Generates CloudFormation                         │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│         AWS CloudFormation Stack                    │
│  - ECS Service + Task Definition                    │
│  - IAM Roles (Execution + Task)                     │
│  - Security Groups                                  │
│  - ALB Target Group + Listeners                     │
│  - CloudWatch Log Group                             │
│  - Service Discovery (Cloud Map)                    │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│              ECS Cluster                            │
│  ┌──────────────────────────────────────┐          │
│  │       ECS Service (my-service)       │          │
│  │  ┌───────────┐      ┌───────────┐   │          │
│  │  │  Task 1   │      │  Task 2   │   │          │
│  │  │ (Fargate) │      │ (Fargate) │   │          │
│  │  └───────────┘      └───────────┘   │          │
│  └──────────────────────────────────────┘          │
└─────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│   Application Load Balancer (Internal ALB)         │
│   - Health checks to /health                        │
│   - Routes to healthy tasks only                    │
└─────────────────────────────────────────────────────┘
```

### Resource Sizing Guidelines

**Python FastAPI Services:**
```
Small (simple APIs):
- CPU: 512 (0.5 vCPU)
- Memory: 1024 (1 GB)
- Use case: Health checks, simple CRUD

Medium (typical services):
- CPU: 1024 (1 vCPU)
- Memory: 2048 (2 GB)
- Use case: FastAPI + Kafka + DynamoDB

Large (ML/heavy processing):
- CPU: 2048 (2 vCPU)
- Memory: 4096 (4 GB)
- Use case: ML inference, large batch processing
```

**Auto-Scaling Targets:**
- CPU: 70% (scale before bottleneck)
- Memory: 80% (avoid OOM)
- Scale-out cooldown: 60s (quick response to load)
- Scale-in cooldown: 300s (avoid flapping)

## When to Use

**Use FSD for:**
- Deploying long-running Python services (FastAPI, consumers)
- Services that need MSK, DynamoDB, or S3 access
- Services that require load balancing
- Services that need auto-scaling
- Anything running on ECS

**Don't use FSD for:**
- Lambda functions (use FSD `kind: Lambda` instead)
- One-off batch jobs (use AWS Batch or ECS tasks directly)
- Infrastructure resources (use Terraform for VPCs, MSK clusters)

## Key Terminology

- **FSD** - Fetch Service Deploy, the internal deployment tool
- **ECS** - Elastic Container Service, AWS managed container platform
- **Fargate** - Serverless ECS compute (no EC2 management)
- **Task Definition** - Container spec (image, CPU, memory, env vars)
- **Service** - Maintains desired count of tasks, integrates with ALB
- **Target Group** - ALB routing destination, performs health checks
- **Pack** - Organizational unit at Fetch (e.g., consumer-agent, pack-digdog)
- **${ENV}** - Environment placeholder (dev, stage, preprod, prod)
- **ALB** - Application Load Balancer (Layer 7 HTTP/HTTPS routing)
- **IAM Task Role** - Permissions for application code (MSK, DynamoDB access)
- **IAM Execution Role** - Permissions for ECS agent (pull Docker image, write logs)

## Related Skills

- [building-fastapi-services](../../01-language-frameworks/python/building-fastapi-services/) - FastAPI health checks
- [containerizing-python-services](../containerizing-python-services/) - Docker images for ECS
- [consuming-kafka-aiokafka](../../01-language-frameworks/python/consuming-kafka-aiokafka/) - MSK dependencies
- [fsd-yaml-config](../fsd-yaml-config/) - General FSD configuration patterns
