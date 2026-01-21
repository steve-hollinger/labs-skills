# Code Patterns: Deploying Python Services with FSD

## Pattern 1: Complete FastAPI Service with Kafka Consumer

**When to Use:** Deploying a Python FastAPI service that consumes from MSK and uses DynamoDB for caching.

```yaml
# category-service.yml
apiVersion: fsd/v1
kind: Service

metadata:
  name: category-service
  pack: consumer-agent
  owners:
    - "@pack-consumer-agent"

service:
  type: ecs
  port: 8000

  healthCheck:
    path: /health
    interval: 30
    timeout: 5
    healthyThreshold: 2
    unhealthyThreshold: 3

  resources:
    cpu: 1024          # 1 vCPU
    memory: 2048       # 2 GB
    desiredCount: 2
    minCapacity: 2
    maxCapacity: 10

  autoScaling:
    targetCPUUtilization: 70
    targetMemoryUtilization: 80
    scaleInCooldown: 300
    scaleOutCooldown: 60

  environment:
    SERVICE_NAME: category-service
    ENVIRONMENT: ${ENV}
    LOG_LEVEL: INFO
    AWS_REGION: us-east-1

    # Kafka
    KAFKA_TOPIC: cvs-category-crud-events
    KAFKA_CONSUMER_GROUP: category-service-${ENV}
    USE_MSK_IAM: "true"

    # Application settings
    CATEGORY_LEXICAL_THRESHOLD: "0.75"
    CATEGORY_SEMANTIC_THRESHOLD: "0.5"

  secrets:
    - name: OPENAI_API_KEY
      valueFrom: arn:aws:secretsmanager:us-east-1:123456789012:secret:openai-api-key-abc123

  networking:
    vpc: true
    loadBalancer:
      type: application
      internal: true
      certificateArn: arn:aws:acm:us-east-1:123456789012:certificate/abc-123

  observability:
    metrics:
      enabled: true
      port: 9090
      path: /metrics

    traces:
      enabled: true
      otlpEndpoint: http://otel-collector:4317

    logs:
      enabled: true
      retention: 30  # days

dependencies:
  - type: aws_msk_cluster
    name: ${ENV}-services
    permissions:
      - kafka-cluster:Connect
      - kafka-cluster:DescribeCluster
      - kafka-cluster:ReadData
      - kafka-cluster:DescribeGroup

  - type: aws_dynamodb_table
    name: ${ENV}-category-cache
    permissions:
      - dynamodb:GetItem
      - dynamodb:PutItem
      - dynamodb:Query
      - dynamodb:Scan
```

**Pitfalls:**
- **Missing MSK permissions** - Consumers need all four permissions: Connect, DescribeCluster, ReadData, DescribeGroup
- **Wrong IAM auth flag** - Must set `USE_MSK_IAM: "true"` in environment variables for aiokafka
- **No retention on logs** - Default is infinite; set reasonable retention (30 days) to control costs

---

## Pattern 2: Simple API Service (No Kafka)

**When to Use:** Deploying a simple REST API that only needs DynamoDB or S3 access.

```yaml
# api-service.yml
apiVersion: fsd/v1
kind: Service

metadata:
  name: offer-api
  pack: pack-digdog

service:
  type: ecs
  port: 8000

  healthCheck:
    path: /health
    interval: 30

  resources:
    cpu: 512           # 0.5 vCPU (smaller for simple API)
    memory: 1024       # 1 GB
    desiredCount: 2
    minCapacity: 2
    maxCapacity: 5

  autoScaling:
    targetCPUUtilization: 70

  environment:
    SERVICE_NAME: offer-api
    ENVIRONMENT: ${ENV}
    AWS_REGION: us-east-1

  networking:
    vpc: true
    loadBalancer:
      type: application
      internal: true

dependencies:
  - type: aws_dynamodb_table
    name: ${ENV}-offers
    permissions:
      - dynamodb:GetItem
      - dynamodb:Query
```

**Pitfalls:**
- **Over-provisioning** - Simple APIs don't need 1 vCPU; start with 512 CPU/1024 memory
- **External ALB by default** - Always set `internal: true` for service-to-service communication
- **Missing VPC** - Services without `vpc: true` deploy in public subnets (security risk)

---

## Pattern 3: Service with Secrets Manager Integration

**When to Use:** Service needs API keys, database passwords, or other sensitive configuration.

```yaml
# ml-service.yml
apiVersion: fsd/v1
kind: Service

metadata:
  name: ereceipt-ml-submitter
  pack: pack-digdog

service:
  type: ecs
  port: 8000

  healthCheck:
    path: /health

  resources:
    cpu: 2048          # 2 vCPU for ML workloads
    memory: 4096       # 4 GB

  environment:
    SERVICE_NAME: ereceipt-ml-submitter
    ENVIRONMENT: ${ENV}
    MODEL_ENDPOINT: https://sagemaker-endpoint.us-east-1.amazonaws.com

  secrets:
    # Secrets Manager ARNs - values injected as env vars at runtime
    - name: OPENAI_API_KEY
      valueFrom: arn:aws:secretsmanager:us-east-1:123456789012:secret:openai-key-abc123

    - name: SAGEMAKER_API_KEY
      valueFrom: arn:aws:secretsmanager:us-east-1:123456789012:secret:sagemaker-key-def456

    - name: DATABASE_PASSWORD
      valueFrom: arn:aws:secretsmanager:us-east-1:123456789012:secret:db-password-ghi789

dependencies:
  - type: aws_s3_bucket
    name: ${ENV}-ml-models
    permissions:
      - s3:GetObject
      - s3:PutObject
```

**Secrets Manager Best Practices:**
```python
# In Python code, access secrets as regular environment variables
import os

openai_key = os.environ["OPENAI_API_KEY"]  # Injected by ECS from Secrets Manager
```

**Pitfalls:**
- **Hardcoding secrets in YAML** - Never put secrets in `environment:`, always use `secrets:` with ARNs
- **Wrong ARN format** - Must be full ARN, not just secret name
- **Missing IAM permissions** - FSD auto-creates permissions, but verify in IAM console if secrets aren't loading

---

## Pattern 4: Multi-Environment Configuration with Overrides

**When to Use:** Need different resource limits or configurations per environment (dev smaller, prod larger).

```yaml
# service.yml (base configuration)
apiVersion: fsd/v1
kind: Service

metadata:
  name: analytics-service
  pack: data-platform

service:
  type: ecs
  port: 8000

  healthCheck:
    path: /health

  resources:
    cpu: 1024
    memory: 2048
    desiredCount: 2
    minCapacity: 2
    maxCapacity: 10

  environment:
    SERVICE_NAME: analytics-service
    ENVIRONMENT: ${ENV}
    BATCH_SIZE: "100"    # Dev default

# FSD CLI overrides for production
# fsd deploy --env prod --override resources.cpu=2048 --override resources.memory=4096
```

**Environment-Specific Overrides:**
```bash
# Dev deployment (smaller resources)
fsd deploy --env dev --file service.yml

# Prod deployment (larger resources, more replicas)
fsd deploy --env prod --file service.yml \
  --override resources.cpu=2048 \
  --override resources.memory=4096 \
  --override resources.desiredCount=5 \
  --override resources.minCapacity=5 \
  --override resources.maxCapacity=20
```

**Pitfalls:**
- **Same resources in all environments** - Prod needs more resources than dev; use overrides
- **Forgetting to scale desiredCount** - Prod should have more replicas for high availability
- **Not testing in staging first** - Always deploy to stage before prod

---

## Pattern 5: Service with S3 Access for Data Processing

**When to Use:** Service needs to read/write files to S3 (logs, models, data exports).

```yaml
# data-processor.yml
apiVersion: fsd/v1
kind: Service

metadata:
  name: data-processor
  pack: data-platform

service:
  type: ecs
  port: 8000

  healthCheck:
    path: /health

  resources:
    cpu: 1024
    memory: 2048

  environment:
    SERVICE_NAME: data-processor
    ENVIRONMENT: ${ENV}
    S3_BUCKET: ${ENV}-data-exports

dependencies:
  - type: aws_s3_bucket
    name: ${ENV}-data-exports
    permissions:
      - s3:GetObject
      - s3:PutObject
      - s3:ListBucket

  - type: aws_s3_bucket
    name: ${ENV}-ml-models
    permissions:
      - s3:GetObject  # Read-only for models
```

**Usage in Python:**
```python
import boto3

s3 = boto3.client("s3")
bucket = os.environ["S3_BUCKET"]

# Upload file
s3.put_object(Bucket=bucket, Key="exports/data.json", Body=json_data)

# Download file
response = s3.get_object(Bucket=bucket, Key="models/model.pkl")
model_data = response["Body"].read()
```

**Pitfalls:**
- **Missing ListBucket permission** - Needed to check if objects exist before reading
- **Not using ${ENV} in bucket names** - Bucket names must be environment-specific
- **Granting full S3 access** - Only grant specific permissions (GetObject, PutObject, not s3:*)

---

## Pattern 6: Deploying with GitHub Actions CI/CD

**When to Use:** Automating FSD deployments via GitHub Actions after tests pass.

```yaml
# .github/workflows/deploy.yml
name: Deploy to ECS

on:
  push:
    branches:
      - main
      - staging

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
          aws-region: us-east-1

      - name: Build and push Docker image
        run: |
          docker build -t my-service:${{ github.sha }} .
          docker tag my-service:${{ github.sha }} 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-service:${{ github.sha }}
          aws ecr get-login-password | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
          docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-service:${{ github.sha }}

      - name: Install FSD CLI
        run: |
          curl -L https://fsd-cli-download-url | tar xz
          sudo mv fsd /usr/local/bin/

      - name: Deploy to dev
        if: github.ref == 'refs/heads/staging'
        run: |
          fsd deploy --env dev --file my-service.yml --image 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-service:${{ github.sha }}

      - name: Deploy to prod
        if: github.ref == 'refs/heads/main'
        run: |
          fsd deploy --env prod --file my-service.yml --image 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-service:${{ github.sha }}
```

**Pitfalls:**
- **Deploying on every commit** - Only deploy after tests pass
- **No rollback strategy** - Tag images with commit SHA for easy rollback
- **Not using OIDC for AWS auth** - Use `aws-actions/configure-aws-credentials` with OIDC instead of access keys

---

## Deployment Workflow

```bash
# 1. Validate FSD YAML locally
fsd validate --file my-service.yml

# 2. Deploy to dev environment
fsd deploy --env dev --file my-service.yml

# 3. Check deployment status
fsd status --service my-service --env dev

# 4. View logs
aws logs tail /ecs/my-service-dev --follow

# 5. Deploy to prod (after testing in dev)
fsd deploy --env prod --file my-service.yml

# 6. Rollback if needed
fsd rollback --service my-service --env prod --to-version v1.2.3
```

## Common FSD CLI Commands

```bash
# Validate YAML schema
fsd validate --file service.yml

# Deploy service
fsd deploy --env dev --file service.yml

# Check deployment status
fsd status --service my-service --env dev

# Scale service
fsd scale --service my-service --env prod --count 10

# Restart service (force new deployment)
fsd restart --service my-service --env prod

# Delete service
fsd delete --service my-service --env dev
```

## References

- FSD Documentation (internal Fetch docs)
- [AWS ECS Task Definition Parameters](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html)
- [AWS Secrets Manager Integration](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/specifying-sensitive-data-secrets.html)
- Fetch services: category-service, ereceipt-ml-submitter, rover-mcp
