# Core Concepts

## What is ECS and Fargate?

**Amazon ECS (Elastic Container Service)** is AWS's container orchestration service. It manages running Docker containers across a cluster of servers.

**AWS Fargate** is a serverless compute engine for containers. Instead of managing EC2 instances, you just specify CPU and memory requirements, and AWS runs your containers.

**Key benefits:**
- No server management - AWS handles the infrastructure
- Pay only for what you use (per-second billing)
- Automatic scaling and health monitoring
- Built-in load balancing and service discovery

## How FSD Simplifies Deployment

**Without FSD (manual AWS setup):**
1. Create ECS cluster
2. Configure VPC, subnets, security groups
3. Create Application Load Balancer (ALB)
4. Configure target groups and health checks
5. Create IAM roles (task execution role, task role)
6. Write ECS task definition JSON
7. Create ECS service with scaling policies
8. Configure CloudWatch logging

**With FSD (declarative configuration):**
1. Write `my-service.yml` (20 lines of YAML)
2. Run `fsd deploy my-service.yml`

FSD generates all the AWS resources automatically based on your YAML configuration. Changes to the YAML are applied incrementally (like Terraform).

**Declarative vs Imperative:**
- **Declarative (FSD):** "I want a service with these properties" → FSD figures out how to make it happen
- **Imperative (Manual):** "Create resource A, then B, then link them with C" → You manage every step

## Container Lifecycle and Health Checks

### ECS Task Lifecycle

```
PROVISIONING → PENDING → ACTIVATING → RUNNING → DEACTIVATING → STOPPING → STOPPED
```

**Key stages:**
1. **PROVISIONING** - AWS allocates Fargate capacity
2. **PENDING** - Pulling Docker image from ECR
3. **ACTIVATING** - Registering task with load balancer
4. **RUNNING** - Container is running, health checks start
5. **DEACTIVATING** - Task is being replaced (deployment or failure)

### Health Check Mechanics

ECS performs **two types of health checks:**

**1. Container Health Check** (Docker HEALTHCHECK)
```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```
- Runs inside the container
- If fails, Docker marks container as "unhealthy"
- ECS kills and restarts unhealthy containers

**2. ELB Target Health Check** (Application Load Balancer)
```yaml
healthCheck:
  path: /health
  interval: 30           # Check every 30 seconds
  timeout: 5             # Wait 5 seconds for response
  healthyThreshold: 2    # 2 consecutive successes = healthy
  unhealthyThreshold: 3  # 3 consecutive failures = unhealthy
```
- Load balancer sends HTTP GET to `/health`
- Only routes traffic to healthy targets
- If fails, ECS considers deployment failed

**Critical:** Both must pass for a successful deployment.

## CI/CD Pipeline Overview

**Traditional deployment process:**
1. Developer writes code
2. Manual build: `docker build -t my-service .`
3. Manual tag: `docker tag my-service:latest 123456.dkr.ecr.us-east-1.amazonaws.com/my-service:v1`
4. Manual push: `docker push ...`
5. Manual deploy: `fsd deploy my-service.yml`
6. Hope everything works 🤞

**Automated CI/CD pipeline (GitHub Actions):**
1. Developer pushes code to `staging` branch
2. GitHub Actions automatically:
   - Runs tests
   - Builds Docker image
   - Tags with commit SHA
   - Pushes to ECR
   - Deploys to staging environment with FSD
3. Developer verifies in staging
4. Merges to `main` for production deployment

**Key benefits:**
- **Consistency** - Same build process every time
- **Traceability** - Know exactly which code is deployed (commit SHA)
- **Fast feedback** - See deployment failures within minutes
- **Reduced human error** - No manual steps to forget

**Typical GitHub Actions workflow:**
```yaml
on:
  push:
    branches: [staging, main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
      - name: Configure AWS credentials
      - name: Login to ECR
      - name: Build Docker image
      - name: Push to ECR
      - name: Deploy with FSD
```

## When to Use SQLite vs DynamoDB

### Decision Matrix

| Factor | SQLite | DynamoDB |
|--------|--------|----------|
| **Query volume** | < 1,000 QPS | > 1,000 QPS |
| **Data size** | < 100 GB | Unlimited |
| **Concurrent writes** | Single writer | Unlimited writers |
| **Local development** | ✅ Works offline | ❌ Needs AWS credentials |
| **Cost** | $0 (included in ECS) | Pay per request/storage |
| **Queries** | Full SQL support | NoSQL (key-value, limited queries) |
| **Setup complexity** | Low (just a file) | Medium (IAM, table schema) |

### Use SQLite When:
- Building a prototype or MVP
- Service handles < 1,000 requests/second
- Read-heavy workload with occasional writes
- Need full SQL queries (JOINs, aggregations)
- Want zero external dependencies for local development

### Use DynamoDB When:
- Need high write throughput (> 100 writes/second)
- Multiple services write to the same data
- Data size may exceed 100 GB
- Need single-digit millisecond latency at scale
- Require automatic backups and point-in-time recovery

### Graduation Path

**Start with SQLite:**
- Fast to implement
- Easy to test locally
- No AWS costs during development

**Migrate to DynamoDB when:**
- SQLite database file exceeds 50 GB
- Seeing "database is locked" errors (write contention)
- Need to scale horizontally (multiple ECS tasks writing)
- Query latency exceeds SLA requirements

**Migration is straightforward:**
1. Add DynamoDB dependency to FSD YAML
2. Update application code to use DynamoDB SDK
3. Run one-time data migration script
4. Deploy new version

## Container Persistence Considerations

**Important:** ECS Fargate containers are **ephemeral** - when a task stops, all data in the container is lost.

**SQLite file locations:**
- ❌ `/tmp/app.db` - Lost when container restarts
- ❌ `/app/app.db` - Lost when container restarts
- ✅ EFS mounted volume - Persists across restarts (requires FSD EFS dependency)
- ✅ Container-local for caching/temporary data - Acceptable for non-critical data

**For production SQLite deployments:**
1. Use EFS (Elastic File System) for persistent storage
2. Add EFS dependency to FSD YAML
3. Mount EFS volume at `/mnt/efs`
4. Store SQLite database at `/mnt/efs/app.db`

**For prototypes (acceptable data loss):**
- Store SQLite in container filesystem
- Accept that data resets on each deployment
- Good for demos, testing, non-critical data

## Summary

- **ECS + Fargate** = Serverless container orchestration
- **FSD** = Declarative infrastructure-as-code for Fetch services
- **Health checks** = Critical for ECS to know your service is working
- **CI/CD** = Automated build → test → deploy pipeline
- **SQLite** = Great for prototypes, small services, local development
- **DynamoDB** = Scales to production workloads, costs more

Next: See [patterns.md](patterns.md) for step-by-step deployment tutorials.
