# Core Concepts

## ECS Task Lifecycle

Understanding the task lifecycle is critical for diagnosing where deployments fail.

### Task States

```
PROVISIONING → PENDING → ACTIVATING → RUNNING → DEACTIVATING → STOPPING → STOPPED
```

**State descriptions:**

| State | What's Happening | Duration | Common Issues |
|-------|------------------|----------|---------------|
| **PROVISIONING** | AWS allocating Fargate capacity | 5-30 seconds | Capacity exhaustion (rare) |
| **PENDING** | Pulling Docker image from ECR | 30-120 seconds | Image not found, ECR permissions |
| **ACTIVATING** | Registering with load balancer | 5-15 seconds | Security group misconfiguration |
| **RUNNING** | Container running, health checks active | Indefinite | Health check failures, app crashes |
| **DEACTIVATING** | Draining connections, stopping traffic | 30 seconds | N/A (normal shutdown) |
| **STOPPING** | Sending SIGTERM to container | 30 seconds | N/A (normal shutdown) |
| **STOPPED** | Task terminated | N/A | Check `stoppedReason` |

### Where Failures Happen

**1. PENDING → Failed (Image Pull Errors)**

```
Stopped reason: CannotPullContainerError:
Error response from daemon: pull access denied for 123456.dkr.ecr.us-east-1.amazonaws.com/my-service
```

**Causes:**
- ECR image doesn't exist
- Task execution role lacks ECR permissions
- Wrong image tag in task definition

**2. ACTIVATING → RUNNING → STOPPED (Startup Failures)**

```
Stopped reason: Essential container in task exited
Exit code: 1
```

**Causes:**
- Application crashed on startup
- Missing environment variables
- Port already in use (unlikely in Fargate)
- Database connection failed

**3. RUNNING → STOPPED (Health Check Failures)**

```
Stopped reason: Task failed ELB health checks in (target-group arn)
```

**Causes:**
- `/health` endpoint not implemented
- Health check returns 500 instead of 200
- Health check timeout too short (app slow to respond)
- Port mismatch (FSD YAML says 8000, app listens on 3000)

**4. RUNNING → STOPPED (Out of Memory)**

```
Stopped reason: OutOfMemoryError: Container killed due to memory usage
```

**Causes:**
- Memory allocation too low
- Memory leak in application
- Large batch operation exceeds memory

## Health Check Mechanics

ECS performs **two independent health checks** that both must pass:

### 1. Container Health Check (Docker HEALTHCHECK)

**Configured in Dockerfile:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

**Parameters:**
- `--interval`: How often to check (default: 30s)
- `--timeout`: Max time to wait for response (default: 5s)
- `--start-period`: Grace period after startup (default: 0s)
- `--retries`: Consecutive failures before unhealthy (default: 3)

**What happens on failure:**
```
Attempt 1: curl times out → Status: starting (grace period)
Attempt 2: curl times out → Status: starting
Attempt 3: curl times out → Status: unhealthy
ECS action: Kill and restart container
```

**Check Docker health status:**
```bash
# Local testing
docker ps
# Look for STATUS column: "healthy" or "unhealthy"

docker inspect <container-id> | jq '.[0].State.Health'
```

### 2. ELB Target Health Check

**Configured in FSD YAML:**
```yaml
healthCheck:
  path: /health
  interval: 30           # Seconds between checks
  timeout: 5             # Seconds to wait for response
  healthyThreshold: 2    # Consecutive successes = healthy
  unhealthyThreshold: 3  # Consecutive failures = unhealthy
```

**How it works:**
```
1. ALB sends: GET /health HTTP/1.1
2. App must respond: HTTP 200 OK within 5 seconds
3. ALB tracks consecutive results:
   - 2 consecutive 200s → Target is HEALTHY
   - 3 consecutive failures → Target is UNHEALTHY
```

**What happens on failure:**
```
Check 1: /health returns 500 → Count: 1 failure
Check 2: /health returns 500 → Count: 2 failures
Check 3: /health returns 500 → Count: 3 failures → UNHEALTHY
ECS action: Stop routing traffic, mark task as unhealthy
```

**Common response codes:**

| Response | Result | Meaning |
|----------|--------|---------|
| **200 OK** | ✅ Healthy | Service is working |
| **404 Not Found** | ❌ Unhealthy | `/health` endpoint doesn't exist |
| **500 Internal Server Error** | ❌ Unhealthy | Application error |
| **502 Bad Gateway** | ❌ Unhealthy | App not listening on expected port |
| **504 Gateway Timeout** | ❌ Unhealthy | App too slow to respond (> timeout) |

### Health Check Troubleshooting Matrix

| Symptom | Docker Health | ELB Health | Cause |
|---------|---------------|------------|-------|
| Task restarts every 2 min | ❌ Unhealthy | N/A | Docker HEALTHCHECK failing |
| Task stays RUNNING, no traffic | ✅ Healthy | ❌ Unhealthy | ELB health check failing |
| Both pass, still no traffic | ✅ Healthy | ✅ Healthy | Security group blocking traffic |
| Task stops immediately | N/A | N/A | App crashed on startup (check logs) |

## CloudWatch Logs

**CloudWatch Logs** contain stdout/stderr from your application. This is your primary debugging tool.

### Log Group Structure

```
/ecs/my-service                    # Log group (one per service)
  ├─ ecs/my-service/task-id-1      # Log stream (one per task)
  ├─ ecs/my-service/task-id-2
  └─ ecs/my-service/task-id-3
```

### Viewing Logs

**AWS Console:**
1. Go to CloudWatch → Log Groups
2. Find `/ecs/my-service`
3. Click on most recent log stream
4. Look for ERROR, Exception, Traceback

**AWS CLI:**
```bash
# Tail logs (live view)
aws logs tail /ecs/my-service --follow

# Tail specific stream
aws logs tail /ecs/my-service --follow --log-stream-names ecs/my-service/<task-id>

# Search for errors
aws logs filter-pattern /ecs/my-service \
  --filter-pattern "ERROR" \
  --start-time $(date -u -d '1 hour ago' +%s)000

# Get logs for specific time range
aws logs get-log-events \
  --log-group-name /ecs/my-service \
  --log-stream-name ecs/my-service/<task-id> \
  --start-time 1704067200000
```

### What to Look For

**1. Startup errors:**
```
# Python
ModuleNotFoundError: No module named 'fastapi'
→ Missing dependency in requirements.txt or Dockerfile

# Node.js
Error: Cannot find module 'express'
→ Missing dependency in package.json or npm install failed

# Go
panic: runtime error: invalid memory address
→ Nil pointer dereference on startup
```

**2. Configuration errors:**
```
KeyError: 'DATABASE_URL'
→ Missing environment variable in FSD YAML

ConnectionRefusedError: [Errno 111] Connection refused
→ Database/service not accessible (check security groups)

botocore.exceptions.NoCredentialsError: Unable to locate credentials
→ Task role missing or lacks permissions
```

**3. Health check errors:**
```
# Look for logs during health check interval (every 30s)
2024-01-20 10:00:00 GET /health → 500 Internal Server Error
Traceback (most recent call last):
  File "main.py", line 42, in health_check
    db.execute("SELECT 1").fetchone()
sqlite3.OperationalError: no such table: schema_version

→ Database not initialized on startup
```

**4. Runtime errors:**
```
OutOfMemoryError: Java heap space
→ Insufficient memory allocation

MemoryError: Unable to allocate 1.5 GiB for an array
→ Memory-intensive operation exceeds container limit

database is locked
→ SQLite concurrent write issue (use WAL mode)
```

## Task Failure Reasons

When a task stops, ECS records a `stoppedReason`. This is visible in the console or CLI.

### Common Stopped Reasons

**1. Essential container in task exited**

```bash
aws ecs describe-tasks --tasks <task-id> | jq '.tasks[0].stoppedReason'
"Essential container in task exited"
```

**What it means:** Your application process crashed or exited with non-zero exit code.

**Next step:** Check CloudWatch Logs for error messages.

**2. Task failed ELB health checks**

```
Task failed ELB health checks in (target-group arn:aws:elasticloadbalancing:...)
```

**What it means:** ALB health check to `/health` failed 3 consecutive times.

**Next step:** Test `/health` endpoint locally, check application logs during health check attempts.

**3. OutOfMemoryError: Container killed due to memory usage**

```
OutOfMemoryError: Container killed due to memory usage
```

**What it means:** Container exceeded memory allocation (hard limit).

**Next step:** Check CloudWatch Memory utilization metrics, increase memory in FSD YAML.

**4. CannotPullContainerError**

```
CannotPullContainerError: Error response from daemon:
pull access denied for 123456.dkr.ecr.us-east-1.amazonaws.com/my-service
```

**What it means:** ECS can't pull Docker image from ECR (permissions or image doesn't exist).

**Next step:** Verify image exists in ECR, check task execution role has `ecr:GetAuthorizationToken` and `ecr:BatchGetImage` permissions.

**5. CannotStartContainerError**

```
CannotStartContainerError: Error response from daemon:
OCI runtime create failed: container_linux.go:380: starting container process caused: exec: "python": executable file not found in $PATH
```

**What it means:** Container CMD/ENTRYPOINT references executable that doesn't exist.

**Next step:** Fix Dockerfile CMD (e.g., change `CMD ["python"]` to `CMD ["python3"]` or install Python in image).

**6. ResourceInitializationError**

```
ResourceInitializationError: unable to pull secrets or registry auth:
execution resource retrieval failed: unable to retrieve secret from asm:
service call has been retried 1 time(s): AccessDeniedException: User is not authorized to perform: secretsmanager:GetSecretValue
```

**What it means:** Task execution role can't access Secrets Manager secrets referenced in FSD YAML.

**Next step:** Add `secretsmanager:GetSecretValue` permission to task execution role.

## IAM Roles: Task Execution Role vs Task Role

**Two different IAM roles** are involved in ECS tasks:

### Task Execution Role

**Purpose:** Allows ECS to set up the task (before your app runs).

**Permissions needed:**
- Pull image from ECR (`ecr:GetAuthorizationToken`, `ecr:BatchGetImage`)
- Write logs to CloudWatch (`logs:CreateLogStream`, `logs:PutLogEvents`)
- Read secrets from Secrets Manager (`secretsmanager:GetSecretValue`)

**When you'll see errors:**
- During PENDING state (pulling image)
- During PROVISIONING (setting up task)
- Errors appear in ECS console, not application logs

**Example error:**
```
CannotPullContainerError: Error response from daemon:
pull access denied
```

### Task Role

**Purpose:** Allows your application code to call AWS services.

**Permissions needed:**
- DynamoDB access (`dynamodb:GetItem`, `dynamodb:PutItem`)
- S3 access (`s3:GetObject`, `s3:PutObject`)
- SQS access (`sqs:ReceiveMessage`, `sqs:DeleteMessage`)

**When you'll see errors:**
- During RUNNING state (app is running)
- Errors appear in **CloudWatch Logs** (application logs), not ECS console

**Example error (in logs):**
```python
botocore.exceptions.ClientError: An error occurred (AccessDeniedException) when calling the GetItem operation:
User: arn:aws:sts::123456789012:assumed-role/my-task-role/task-id is not authorized to perform: dynamodb:GetItem on resource: table/my-table
```

### How to Fix IAM Errors

**1. Test permissions with AWS CLI:**
```bash
# Assume the task role
aws sts assume-role \
  --role-arn arn:aws:iam::123456789012:role/my-task-role \
  --role-session-name test

# Export credentials (copy from assume-role output)
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_SESSION_TOKEN=...

# Test the operation that's failing
aws dynamodb get-item \
  --table-name my-table \
  --key '{"id": {"S": "test"}}'

# If this fails, you know permissions are missing
```

**2. Add permissions to task role in FSD YAML:**
```yaml
# FSD YAML
service:
  taskRole:
    statements:
      - effect: Allow
        actions:
          - dynamodb:GetItem
          - dynamodb:PutItem
          - dynamodb:Query
        resources:
          - arn:aws:dynamodb:us-east-1:123456789012:table/my-table
```

**3. Redeploy with updated permissions:**
```bash
fsd deploy my-service.yml --env staging
```

## Security Groups and Networking

**Security groups** control network traffic to/from your ECS tasks.

### Common Networking Issues

**1. Load balancer can't reach tasks (health checks fail)**

```
Symptom: Health checks fail with 502 Bad Gateway
Cause: Security group blocks traffic from ALB to ECS tasks
```

**Fix:**
```yaml
# FSD YAML - Allow ALB to reach tasks
service:
  securityGroups:
    - name: my-service-sg
      ingress:
        - protocol: tcp
          from_port: 8000
          to_port: 8000
          source_security_group_id: ${ALB_SECURITY_GROUP_ID}
```

**2. Tasks can't reach database**

```
Symptom: ConnectionRefusedError: [Errno 111] Connection refused (in logs)
Cause: RDS security group blocks traffic from ECS tasks
```

**Fix:**
- Add ECS task security group to RDS security group's ingress rules
- Or: Configure FSD to reference RDS dependency (auto-configures security groups)

**3. Tasks can't reach internet (for external APIs)**

```
Symptom: ConnectTimeoutError: Connect timeout on endpoint (in logs)
Cause: Tasks in private subnet without NAT Gateway
```

**Fix:**
- Deploy tasks in public subnet with public IP (not recommended for production)
- Or: Add NAT Gateway to VPC (costs ~$32/month)
- Or: Use VPC endpoints for AWS services (S3, DynamoDB, etc.)

## Summary

**Key concepts:**
- **Task lifecycle** - PROVISIONING → PENDING → ACTIVATING → RUNNING → STOPPED
- **Health checks** - Both Docker HEALTHCHECK and ELB health check must pass
- **CloudWatch Logs** - Primary debugging tool for application errors
- **Task failure reasons** - `stoppedReason` in ECS console indicates why task stopped
- **IAM roles** - Task execution role (for ECS setup) vs task role (for app AWS calls)
- **Security groups** - Control network traffic to/from tasks

**Debugging workflow:**
1. Check task stopped reason (ECS console or CLI)
2. Read CloudWatch Logs (application errors)
3. Test health check locally (`curl http://localhost:8000/health`)
4. Verify IAM permissions (AWS CLI with assumed role)
5. Check security groups (ALB → tasks, tasks → database)

**Next:** See [patterns.md](patterns.md) for step-by-step diagnostic procedures and [error-catalog.md](error-catalog.md) for specific error solutions.
