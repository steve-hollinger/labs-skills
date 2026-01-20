# Core Concepts

## Overview

FSD (Full-Stack Definition) is a declarative configuration format for defining cloud services. It abstracts platform-specific complexity while providing precise control over deployment configurations. This document covers the fundamental concepts you need to understand FSD YAML configurations.

## Concept 1: Service Identity

### What It Is

Every FSD service has a unique identity defined by its `name` field. This identifier is used across the entire deployment pipeline for resource naming, monitoring, and service discovery.

### Why It Matters

The service name becomes part of:
- AWS resource names (ECS services, Lambda functions, etc.)
- CloudWatch log groups and metrics
- Service discovery DNS names
- IAM role names

### How It Works

```yaml
# Service identity block
name: user-api
description: REST API for user management
team: platform-team
tags:
  environment: production
  cost-center: engineering
  tier: critical
```

**Naming Rules:**
- Lowercase alphanumeric characters and hyphens only
- Must start with a letter
- Maximum 64 characters
- Must be unique within the deployment namespace

## Concept 2: Platform Selection

### What It Is

The `platform` field determines which AWS compute service will run your workload. Each platform has unique characteristics and configuration options.

### Why It Matters

Choosing the right platform affects:
- Cost structure and billing model
- Scaling behavior and latency
- Operational complexity
- Available features and integrations

### How It Works

```yaml
# Platform determines the deployment target
platform: ecs    # Long-running containers on Fargate/EC2
platform: eks    # Kubernetes pods on managed EKS
platform: lambda # Serverless functions
platform: batch  # Job processing with AWS Batch
```

**Platform Comparison:**

| Aspect | ECS | EKS | Lambda | Batch |
|--------|-----|-----|--------|-------|
| Startup Time | ~30s | ~30s | ~100ms | ~1min |
| Min Cost | $0.01/hr | $0.01/hr | Per-invocation | Per-job |
| Max Duration | Unlimited | Unlimited | 15 min | Days |
| Scaling | Manual/Auto | HPA/VPA | Automatic | Queue-based |
| Complexity | Medium | High | Low | Medium |

## Concept 3: Compute Configuration

### What It Is

The `compute` block defines the resource allocation for your service. Configuration varies by platform but always specifies CPU and memory.

### Why It Matters

Proper resource configuration ensures:
- Application performance meets requirements
- Cost optimization without over-provisioning
- Predictable scaling behavior
- Compliance with platform constraints

### How It Works

#### ECS Compute

ECS uses AWS-defined vCPU units and memory in MB. Fargate has specific valid combinations.

```yaml
platform: ecs
compute:
  cpu: 512        # vCPU units (256, 512, 1024, 2048, 4096)
  memory: 1024    # Memory in MB
  desired_count: 3 # Number of running tasks

  # Optional: Fargate Spot for cost savings
  capacity_provider: FARGATE_SPOT
```

#### EKS Compute

EKS uses Kubernetes resource specifications with requests and limits.

```yaml
platform: eks
compute:
  replicas: 3
  resources:
    requests:
      cpu: "250m"      # 250 millicores = 0.25 vCPU
      memory: "256Mi"  # 256 mebibytes
    limits:
      cpu: "500m"
      memory: "512Mi"
```

#### Lambda Compute

Lambda is memory-based; CPU scales proportionally.

```yaml
platform: lambda
compute:
  memory: 256        # MB (128-10240)
  timeout: 30        # Seconds (1-900)
  runtime: python3.11

  # Optional: Reserved concurrency
  reserved_concurrency: 100
```

#### Batch Compute

Batch uses vCPUs and memory for job definitions.

```yaml
platform: batch
compute:
  vcpus: 2
  memory: 4096      # MB

  # GPU support
  gpu: 1
```

## Concept 4: Networking Configuration

### What It Is

The `networking` block configures how your service communicates with clients and other services, including ports, load balancing, and health checks.

### Why It Matters

Proper networking configuration enables:
- Service discovery and routing
- Health monitoring and automatic recovery
- Security through network isolation
- Load balancing across instances

### How It Works

```yaml
networking:
  # Container port exposure
  port: 8080
  protocol: http    # http, https, tcp, grpc

  # Health check configuration
  health_check:
    path: /health
    port: 8080
    interval: 30       # Seconds between checks
    timeout: 5         # Seconds to wait for response
    healthy_threshold: 2    # Consecutive successes
    unhealthy_threshold: 3  # Consecutive failures

  # Load balancer settings (ECS/EKS)
  load_balancer:
    type: application  # application, network
    internal: false    # Internal vs internet-facing
    idle_timeout: 60

  # Service discovery
  service_discovery:
    namespace: production
    dns_ttl: 10
```

## Concept 5: Environment Configuration

### What It Is

The `environment` block defines environment variables available to your application at runtime, including static values and dynamic references.

### Why It Matters

Environment configuration provides:
- Runtime customization without code changes
- Secret injection from secure sources
- Environment-specific settings (dev/staging/prod)
- Integration with AWS services

### How It Works

```yaml
environment:
  # Static values
  LOG_LEVEL: info
  AWS_REGION: us-east-1

  # References to Secrets Manager
  DATABASE_URL: ${secrets:my-service/database-url}
  API_KEY: ${secrets:my-service/api-key}

  # References to SSM Parameter Store
  FEATURE_FLAGS: ${ssm:/my-service/feature-flags}

  # References to other services
  USER_SERVICE_URL: ${service:user-service:url}
```

**Reference Syntax:**
- `${secrets:path}` - AWS Secrets Manager
- `${ssm:path}` - SSM Parameter Store
- `${service:name:attribute}` - Service discovery
- `${env:VARIABLE}` - Build-time environment

## Concept 6: Scaling Configuration

### What It Is

Scaling configuration determines how your service adjusts capacity based on demand, including minimum and maximum instances and scaling triggers.

### Why It Matters

Proper scaling ensures:
- Cost efficiency during low traffic
- Performance during high traffic
- Automatic recovery from failures
- Predictable capacity planning

### How It Works

#### ECS Autoscaling

```yaml
scaling:
  min_count: 2
  max_count: 20

  # Target tracking policies
  policies:
    - type: target_tracking
      metric: cpu
      target: 70
      scale_in_cooldown: 300
      scale_out_cooldown: 60

    - type: target_tracking
      metric: memory
      target: 80
```

#### EKS Horizontal Pod Autoscaler

```yaml
compute:
  autoscaling:
    enabled: true
    min_replicas: 2
    max_replicas: 20
    metrics:
      - type: Resource
        resource:
          name: cpu
          target:
            type: Utilization
            averageUtilization: 70
```

#### Lambda Provisioned Concurrency

```yaml
compute:
  provisioned_concurrency: 10  # Warm instances
  reserved_concurrency: 100    # Max concurrent executions
```

## Summary

Key takeaways from these concepts:

1. **Service Identity**: Use meaningful, unique names that follow naming conventions
2. **Platform Selection**: Choose based on workload characteristics, not just familiarity
3. **Compute Configuration**: Right-size resources based on actual requirements
4. **Networking**: Always configure health checks for production services
5. **Environment**: Use secure references for secrets, never hardcode
6. **Scaling**: Configure autoscaling to handle variable load efficiently

The combination of these concepts creates a complete service definition that can be deployed consistently across environments.
