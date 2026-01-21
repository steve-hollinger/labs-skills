# Common Patterns

## Overview

This document covers common patterns and best practices for FSD YAML configurations across different service types and platforms.

## Pattern 1: Web API Service (ECS)

### When to Use

Use this pattern for HTTP REST APIs, GraphQL endpoints, or any web service that needs:
- Consistent uptime with multiple instances
- Load balancing across instances
- Health monitoring and automatic recovery

### Implementation

```yaml
name: product-api
platform: ecs
description: Product catalog REST API

compute:
  cpu: 512
  memory: 1024
  desired_count: 3

networking:
  port: 8080
  protocol: http
  health_check:
    path: /health
    interval: 30
    timeout: 5
    healthy_threshold: 2
    unhealthy_threshold: 3
  load_balancer:
    type: application
    internal: false
    idle_timeout: 60

scaling:
  min_count: 2
  max_count: 10
  policies:
    - type: target_tracking
      metric: cpu
      target: 70

environment:
  LOG_LEVEL: info
  PORT: "8080"
```

### Example Use Case

```yaml
# E-commerce product catalog API
name: catalog-api
platform: ecs

compute:
  cpu: 1024
  memory: 2048
  desired_count: 5

networking:
  port: 8080
  health_check:
    path: /api/health
    interval: 15
```

### Pitfalls to Avoid

- Not configuring health checks (deployment failures go undetected)
- Setting desired_count to 1 (no redundancy)
- Missing load balancer idle timeout (causes connection drops)

## Pattern 2: Background Worker (EKS)

### When to Use

Use this pattern for services that:
- Process messages from queues
- Perform background computations
- Don't need HTTP endpoints

### Implementation

```yaml
name: order-processor
platform: eks
description: Processes orders from SQS queue

compute:
  replicas: 3
  resources:
    requests:
      cpu: "500m"
      memory: "512Mi"
    limits:
      cpu: "1000m"
      memory: "1Gi"
  autoscaling:
    enabled: true
    min_replicas: 2
    max_replicas: 20
    metrics:
      - type: External
        external:
          metric:
            name: sqs_queue_length
          target:
            type: AverageValue
            averageValue: "10"

environment:
  QUEUE_URL: ${ssm:/order-processor/queue-url}
  BATCH_SIZE: "10"
  VISIBILITY_TIMEOUT: "300"
```

### Example Use Case

```yaml
# Email notification worker
name: notification-worker
platform: eks

compute:
  replicas: 5
  resources:
    requests:
      cpu: "250m"
      memory: "256Mi"

environment:
  SES_REGION: us-east-1
  MAX_BATCH_SIZE: "50"
```

### Pitfalls to Avoid

- Not setting resource limits (can starve other pods)
- Scaling on wrong metric (CPU may not reflect queue depth)
- Missing visibility timeout configuration

## Pattern 3: Event-Driven Function (Lambda)

### When to Use

Use this pattern for:
- API endpoints with variable traffic
- Event processing from AWS services
- Scheduled tasks (cron jobs)

### Implementation

```yaml
name: image-processor
platform: lambda
description: Processes uploaded images, creates thumbnails

compute:
  memory: 1024
  timeout: 60
  runtime: python3.11

triggers:
  - type: s3
    bucket: user-uploads
    events:
      - s3:ObjectCreated:*
    filter:
      prefix: images/
      suffix: .jpg

  - type: s3
    bucket: user-uploads
    events:
      - s3:ObjectCreated:*
    filter:
      prefix: images/
      suffix: .png

environment:
  OUTPUT_BUCKET: processed-images
  THUMBNAIL_SIZE: "200x200"
```

### Example Use Case

```yaml
# API endpoint with scheduled warmup
name: user-preferences-api
platform: lambda

compute:
  memory: 512
  timeout: 10
  runtime: nodejs20.x
  provisioned_concurrency: 5

triggers:
  - type: api_gateway
    path: /preferences/{userId}
    method: GET

  - type: api_gateway
    path: /preferences/{userId}
    method: PUT

  - type: schedule
    rate: rate(5 minutes)
    description: Keep function warm
```

### Pitfalls to Avoid

- Timeout longer than necessary (increases costs)
- Not using provisioned concurrency for latency-sensitive endpoints
- Missing filter configuration (processes unwanted events)

## Pattern 4: Batch Processing Job (Batch)

### When to Use

Use this pattern for:
- Large-scale data processing
- ETL pipelines
- Machine learning training jobs

### Implementation

```yaml
name: daily-report-generator
platform: batch
description: Generates daily analytics reports

compute:
  vcpus: 4
  memory: 8192

job:
  type: single
  retry_attempts: 3
  timeout: 3600  # 1 hour

  # Job scheduling
  schedule:
    type: cron
    expression: "0 2 * * *"  # 2 AM daily

environment:
  REPORT_DATE: ${batch:array_index}
  OUTPUT_BUCKET: analytics-reports
  DATABASE_URL: ${secrets:reports/database-url}
```

### Example Use Case

```yaml
# Array job for parallel processing
name: video-transcoder
platform: batch

compute:
  vcpus: 2
  memory: 4096
  gpu: 1

job:
  type: array
  size: 1000
  array_properties:
    size: 1000
  retry_attempts: 2
  timeout: 7200

environment:
  INPUT_BUCKET: raw-videos
  OUTPUT_BUCKET: transcoded-videos
  QUALITY: high
```

### Pitfalls to Avoid

- Not setting timeout (runaway jobs waste resources)
- Missing retry configuration (transient failures cause job loss)
- Incorrect array size (too many or too few parallel jobs)

## Pattern 5: Production-Ready Service

### When to Use

Use this comprehensive pattern for production services that need:
- High availability
- Comprehensive monitoring
- Security hardening

### Implementation

```yaml
name: payment-service
platform: ecs
description: Payment processing service
team: payments-team

tags:
  environment: production
  compliance: pci-dss
  tier: critical
  cost-center: payments

compute:
  cpu: 1024
  memory: 2048
  desired_count: 5
  capacity_provider: FARGATE

networking:
  port: 8443
  protocol: https
  health_check:
    path: /health
    port: 8443
    protocol: HTTPS
    interval: 10
    timeout: 5
    healthy_threshold: 2
    unhealthy_threshold: 2
  load_balancer:
    type: application
    internal: true  # No public access
    idle_timeout: 120
    ssl_policy: ELBSecurityPolicy-TLS13-1-2-2021-06

scaling:
  min_count: 5
  max_count: 50
  policies:
    - type: target_tracking
      metric: cpu
      target: 60
      scale_in_cooldown: 300
      scale_out_cooldown: 60
    - type: target_tracking
      metric: request_count
      target: 1000
      scale_in_cooldown: 300

observability:
  logging:
    driver: awslogs
    retention_days: 90
  tracing:
    enabled: true
    sampling_rate: 0.1
  metrics:
    custom:
      - name: PaymentSuccessRate
        unit: Percent
      - name: TransactionLatency
        unit: Milliseconds

environment:
  LOG_LEVEL: info
  PAYMENT_GATEWAY_URL: ${secrets:payment-service/gateway-url}
  API_KEY: ${secrets:payment-service/api-key}
  ENCRYPTION_KEY: ${secrets:payment-service/encryption-key}

security:
  network_mode: awsvpc
  readonly_root_filesystem: true
  no_new_privileges: true
```

### Pitfalls to Avoid

- Public load balancers for internal services
- Missing encryption for sensitive data
- Insufficient logging retention for compliance

## Anti-Patterns

### Anti-Pattern 1: Hardcoded Secrets

Never include secrets directly in YAML files.

```yaml
# BAD - Secrets in plain text
environment:
  DATABASE_PASSWORD: supersecretpassword123
  API_KEY: sk_live_abc123xyz
```

### Better Approach

```yaml
# GOOD - Reference secrets securely
environment:
  DATABASE_PASSWORD: ${secrets:my-service/db-password}
  API_KEY: ${secrets:my-service/api-key}
```

### Anti-Pattern 2: Over-Provisioned Resources

Don't allocate maximum resources "just in case."

```yaml
# BAD - Wasteful over-provisioning
compute:
  cpu: 4096
  memory: 30720
  desired_count: 20
```

### Better Approach

```yaml
# GOOD - Right-sized with autoscaling
compute:
  cpu: 512
  memory: 1024
  desired_count: 2

scaling:
  min_count: 2
  max_count: 20
  policies:
    - type: target_tracking
      metric: cpu
      target: 70
```

### Anti-Pattern 3: Missing Health Checks

Services without health checks fail silently.

```yaml
# BAD - No health check
networking:
  port: 8080
```

### Better Approach

```yaml
# GOOD - Comprehensive health check
networking:
  port: 8080
  health_check:
    path: /health
    interval: 30
    timeout: 5
    healthy_threshold: 2
    unhealthy_threshold: 3
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| REST API with steady traffic | Web API Service (ECS) |
| REST API with variable traffic | Event-Driven Function (Lambda) |
| Queue message processing | Background Worker (EKS or ECS) |
| Scheduled data processing | Batch Processing Job |
| Real-time event processing | Event-Driven Function (Lambda) |
| ML model serving | Web API Service (ECS with GPU) |
| ETL pipeline | Batch Processing Job |
| High-security service | Production-Ready Service pattern |
