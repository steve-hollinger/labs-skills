# Common Patterns

## Pattern 1: Diagnosing Health Check Failures

**When to Use:** Task enters RUNNING state but stops after 2-5 minutes with "Task failed ELB health checks".

### Step-by-Step Diagnosis

**Step 1: Verify health endpoint exists**

```bash
# Test locally first
docker-compose up

# In another terminal
curl -v http://localhost:8000/health

# Expected output:
# HTTP/1.1 200 OK
# {"status": "healthy"}
```

**If 404 Not Found:**
- Health endpoint not implemented
- Add `/health` route to your application

**If 500 Internal Server Error:**
- Health endpoint has a bug
- Check application logs for error during health check

**If Connection refused:**
- App not listening on expected port
- Check app listens on `0.0.0.0` not `127.0.0.1`

**Step 2: Check FSD YAML matches application**

```yaml
# FSD YAML
service:
  port: 8000              # ← Must match app listen port
  healthCheck:
    path: /health         # ← Must match app route exactly
    interval: 30
    timeout: 5
```

```python
# Application (FastAPI)
@app.get("/health")      # ← Must match FSD healthCheck.path
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)  # ← Must match FSD port
```

**Common mismatches:**

| FSD YAML | Application | Result |
|----------|-------------|--------|
| `path: /health` | `@app.get("/health")` | ✅ Works |
| `path: /health` | `@app.get("/healthz")` | ❌ 404 |
| `path: /api/health` | `@app.get("/health")` | ❌ 404 |
| `port: 8000` | `app.listen(3000)` | ❌ Connection refused |

**Step 3: Check health check timing**

```yaml
healthCheck:
  path: /health
  interval: 30           # Check every 30 seconds
  timeout: 5             # Wait 5 seconds for response
  unhealthyThreshold: 3  # 3 failures = unhealthy (90 seconds total)
```

**If app takes > 5 seconds to respond:**
- Increase `timeout` to 10 or 15 seconds
- Or: Optimize health check endpoint (don't query database)

**If app needs startup time:**
- Add Docker HEALTHCHECK `--start-period=30s` (grace period)
- App has 30 seconds before health checks fail

**Step 4: Check CloudWatch Logs during health check**

```bash
# Tail logs and watch for /health requests
aws logs tail /ecs/my-service --follow | grep "GET /health"

# Look for:
# 2024-01-20 10:00:30 GET /health → 200 OK ✅
# 2024-01-20 10:01:00 GET /health → 500 Internal Server Error ❌
```

**If logs show 500 errors:**
- Health check endpoint has a bug
- Common cause: Health check queries database, database connection fails

**If logs don't show /health requests at all:**
- ALB can't reach tasks (security group issue)
- Check Pattern 5 (security groups)

**Step 5: Simplify health check endpoint**

```python
# ❌ Complex health check (can fail)
@app.get("/health")
def health_check():
    # Query database
    db.execute("SELECT 1").fetchone()

    # Check external API
    response = requests.get("https://api.example.com/status")

    return {"status": "healthy"}

# ✅ Simple health check (reliable)
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# ✅ Optional: Light database check
@app.get("/health")
def health_check():
    try:
        db.execute("SELECT 1").fetchone()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        # Log error but still return 200 (don't kill task for transient DB issue)
        logger.error(f"Health check database error: {e}")
        return {"status": "degraded", "database": "error"}
```

**Pitfalls:**
- Health check queries slow database (times out)
- Health check calls external APIs (times out)
- Health check returns 200 even when app is broken (false positive)

---

## Pattern 2: Reading CloudWatch Logs

**When to Use:** Task stops immediately with "Essential container in task exited".

### Finding the Right Logs

**Step 1: Get task ID from ECS**

```bash
# List recent stopped tasks
aws ecs list-tasks \
  --cluster my-cluster \
  --service-name my-service \
  --desired-status STOPPED \
  --max-items 5

# Get task stopped reason
aws ecs describe-tasks \
  --cluster my-cluster \
  --tasks <task-id> \
  | jq '.tasks[0].stoppedReason'
```

**Step 2: Find log stream**

```bash
# Log stream name format:
# ecs/my-service/<task-id>

# Example:
# ecs/my-service/abc123def456

# Tail logs for specific task
aws logs tail /ecs/my-service \
  --follow \
  --log-stream-names ecs/my-service/<task-id>
```

**Step 3: Search for common errors**

```bash
# Search for Python errors
aws logs filter-pattern /ecs/my-service \
  --filter-pattern "Traceback" \
  --start-time $(date -u -d '1 hour ago' +%s)000

# Search for Node.js errors
aws logs filter-pattern /ecs/my-service \
  --filter-pattern "Error:" \
  --start-time $(date -u -d '1 hour ago' +%s)000

# Search for Go panics
aws logs filter-pattern /ecs/my-service \
  --filter-pattern "panic:" \
  --start-time $(date -u -d '1 hour ago' +%s)000
```

### Interpreting Common Log Patterns

**Pattern: Missing environment variable**

```
KeyError: 'DATABASE_URL'
```

**Solution:**
```yaml
# Add to FSD YAML
service:
  environment:
    DATABASE_URL: ${DATABASE_URL}  # Set in environment config
```

**Pattern: Missing Python dependency**

```
ModuleNotFoundError: No module named 'requests'
```

**Solution:**
```txt
# Add to requirements.txt
requests==2.31.0
```

**Pattern: Port already in use**

```
OSError: [Errno 98] Address already in use
```

**Solution:**
- Check Dockerfile exposes correct port
- Ensure app listens on `0.0.0.0:8000` not `127.0.0.1:8000`

**Pattern: Database connection failed**

```
psycopg2.OperationalError: could not connect to server: Connection refused
```

**Solution:**
- Check RDS security group allows traffic from ECS tasks
- Verify `DATABASE_URL` environment variable is correct
- Test connection from task: `aws ecs execute-command` (if enabled)

---

## Pattern 3: Testing Containers Locally

**When to Use:** Before every deployment, to catch issues early.

### docker-compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SERVICE_NAME=my-service
      - ENVIRONMENT=local
      - DATABASE_URL=sqlite:////app/data/app.db
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s
```

### Local Testing Workflow

**Step 1: Build and run**

```bash
# Build image
docker-compose build

# Start container
docker-compose up

# Watch for startup errors
# Look for:
# ✅ "Application startup complete"
# ✅ "Uvicorn running on http://0.0.0.0:8000"
# ❌ "ModuleNotFoundError"
# ❌ "KeyError: 'DATABASE_URL'"
```

**Step 2: Test health endpoint**

```bash
# In another terminal
curl http://localhost:8000/health

# Expected:
# HTTP/1.1 200 OK
# {"status": "healthy"}
```

**Step 3: Test application endpoints**

```bash
# Test main functionality
curl http://localhost:8000/

curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Item"}'

curl http://localhost:8000/items/1
```

**Step 4: Check Docker health status**

```bash
# Check container health
docker ps

# CONTAINER ID   IMAGE        STATUS
# abc123def456   my-service   Up 2 minutes (healthy)   # ✅ Good

# If status shows "unhealthy":
docker inspect <container-id> | jq '.[0].State.Health'

# Look for FailingStreak, Log (recent health check results)
```

**Step 5: Test with production-like config**

```bash
# Test without volumes (ephemeral storage like ECS)
docker run -p 8000:8000 \
  -e SERVICE_NAME=my-service \
  -e ENVIRONMENT=staging \
  my-service:latest

# Test with limited resources (match ECS allocation)
docker run -p 8000:8000 \
  --memory=1g \
  --cpus=0.5 \
  my-service:latest
```

### What to Test Locally

| Scenario | Test | Expected Result |
|----------|------|-----------------|
| **Cold start** | `docker-compose up` | Starts without errors in < 30 seconds |
| **Health check** | `curl /health` | Returns 200 within 5 seconds |
| **API functionality** | `curl /api/endpoint` | Returns expected response |
| **Environment variables** | Omit required env var | Clear error message in logs |
| **Resource limits** | `--memory=512m` | Runs without OOM |
| **Database connection** | Query database | Succeeds or fails gracefully |

**Pitfalls:**
- Not testing locally before deploying (slow feedback loop)
- Using `docker run` instead of `docker-compose` (missing health check config)
- Not checking logs during local testing (missing startup warnings)

---

## Pattern 4: Verifying IAM Permissions

**When to Use:** Application logs show "AccessDeniedException" or "Access Denied" for AWS services.

### Step-by-Step Permission Testing

**Step 1: Identify the failing operation**

```python
# Application log shows:
botocore.exceptions.ClientError: An error occurred (AccessDeniedException)
when calling the GetItem operation: User: arn:aws:sts::123456:assumed-role/my-task-role
is not authorized to perform: dynamodb:GetItem on resource: table/my-table
```

**Extract:**
- Action: `dynamodb:GetItem`
- Resource: `arn:aws:dynamodb:us-east-1:123456:table/my-table`
- Role: `my-task-role`

**Step 2: Check current task role permissions**

```bash
# Get task role ARN from FSD YAML or ECS console
TASK_ROLE_ARN=arn:aws:iam::123456789012:role/my-task-role

# List attached policies
aws iam list-attached-role-policies --role-name my-task-role

# Get inline policies
aws iam list-role-policies --role-name my-task-role

# View policy document
aws iam get-role-policy \
  --role-name my-task-role \
  --policy-name my-task-policy
```

**Step 3: Test permissions with AWS CLI**

```bash
# Assume the task role
aws sts assume-role \
  --role-arn arn:aws:iam::123456789012:role/my-task-role \
  --role-session-name test \
  --duration-seconds 3600

# Export credentials (copy from output)
export AWS_ACCESS_KEY_ID=ASI...
export AWS_SECRET_ACCESS_KEY=...
export AWS_SESSION_TOKEN=...

# Test the failing operation
aws dynamodb get-item \
  --table-name my-table \
  --key '{"id": {"S": "test"}}'

# If it fails with AccessDeniedException, permissions are missing
```

**Step 4: Add missing permissions**

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
          - dynamodb:Scan
        resources:
          - arn:aws:dynamodb:us-east-1:123456789012:table/my-table
          - arn:aws:dynamodb:us-east-1:123456789012:table/my-table/index/*
```

**Step 5: Deploy and verify**

```bash
# Deploy updated FSD YAML
fsd deploy my-service.yml --env staging

# New tasks will get updated permissions
# Old tasks keep old permissions until replaced
```

### Common IAM Permission Patterns

**DynamoDB:**
```yaml
taskRole:
  statements:
    - effect: Allow
      actions:
        - dynamodb:GetItem
        - dynamodb:PutItem
        - dynamodb:UpdateItem
        - dynamodb:DeleteItem
        - dynamodb:Query
        - dynamodb:Scan
      resources:
        - arn:aws:dynamodb:${AWS::Region}:${AWS::AccountId}:table/my-table
        - arn:aws:dynamodb:${AWS::Region}:${AWS::AccountId}:table/my-table/index/*
```

**S3:**
```yaml
taskRole:
  statements:
    - effect: Allow
      actions:
        - s3:GetObject
        - s3:PutObject
        - s3:ListBucket
      resources:
        - arn:aws:s3:::my-bucket/*
        - arn:aws:s3:::my-bucket
```

**SQS:**
```yaml
taskRole:
  statements:
    - effect: Allow
      actions:
        - sqs:ReceiveMessage
        - sqs:DeleteMessage
        - sqs:GetQueueAttributes
      resources:
        - arn:aws:sqs:${AWS::Region}:${AWS::AccountId}:my-queue
```

**Secrets Manager:**
```yaml
taskRole:
  statements:
    - effect: Allow
      actions:
        - secretsmanager:GetSecretValue
      resources:
        - arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:my-secret-*
```

**Pitfalls:**
- Adding permissions to task execution role instead of task role
- Using wildcards too broadly (`Resource: "*"` is security risk)
- Not redeploying after adding permissions (old tasks still fail)

---

## Pattern 5: Debugging Security Group/VPC Issues

**When to Use:** Health checks fail with 502 Bad Gateway, or app can't reach database/external services.

### Common Security Group Problems

**Problem 1: ALB can't reach ECS tasks**

```
Symptom: Health checks fail, CloudWatch Logs show no /health requests
Diagnosis: ALB sending health checks, but security group blocks traffic
```

**Solution:**
```bash
# Check task security group ingress rules
aws ec2 describe-security-groups --group-ids sg-12345678

# Look for rule allowing traffic from ALB:
# Port: 8000 (or your app port)
# Source: ALB security group (sg-abcdef12)

# Add rule if missing (FSD auto-configures this usually)
```

**Problem 2: Tasks can't reach RDS database**

```
Symptom: Logs show "Connection refused" or "Connection timeout" to database
Diagnosis: RDS security group doesn't allow traffic from ECS tasks
```

**Solution:**
```bash
# Check RDS security group ingress rules
aws ec2 describe-security-groups --group-ids sg-rds12345

# Should have rule:
# Port: 5432 (Postgres) or 3306 (MySQL)
# Source: ECS task security group (sg-12345678)

# Add via FSD by referencing RDS as dependency
```

**Problem 3: Tasks can't reach internet**

```
Symptom: Logs show "Connection timeout" for external API (api.example.com)
Diagnosis: Tasks in private subnet without NAT Gateway or internet gateway
```

**Solution:**
```yaml
# Option 1: Use public subnet (not recommended for production)
service:
  network:
    assignPublicIp: true
    subnets: ${PUBLIC_SUBNETS}

# Option 2: Add NAT Gateway to VPC (recommended)
# Requires infrastructure change (costs ~$32/month)

# Option 3: Use VPC endpoints for AWS services (free)
# Works for S3, DynamoDB, but not external APIs
```

### Testing Network Connectivity

**From local machine to ALB:**
```bash
# Test ALB endpoint
curl -v https://my-service-alb.us-east-1.elb.amazonaws.com/health

# Should return 200 OK
# If timeout: Check ALB security group allows traffic from your IP
# If 503: No healthy targets (health checks failing)
```

**From ECS task to database (requires ECS Exec):**
```bash
# Enable ECS Exec in FSD YAML
service:
  enableExecuteCommand: true

# Deploy
fsd deploy my-service.yml --env staging

# Connect to running task
aws ecs execute-command \
  --cluster my-cluster \
  --task <task-id> \
  --container my-service \
  --interactive \
  --command "/bin/sh"

# Inside container, test database connection
nc -zv my-db.us-east-1.rds.amazonaws.com 5432

# If "Connection refused": Security group issue
# If "Connection timed out": Network routing issue (no route to DB)
```

---

## Pattern 6: When to Escalate

**When to Ask for Help:** After 30 minutes of debugging without progress.

### Escalation Checklist

**Include in your request:**

1. **Service name and environment**
   - Example: `my-service` in `staging` environment

2. **What you're trying to do**
   - Example: "Deploying new version with SQLite integration"

3. **What's failing**
   - Example: "Tasks start but stop after 2 minutes with health check failures"

4. **Task stopped reason (from ECS)**
```bash
aws ecs describe-tasks --tasks <task-id> | jq '.tasks[0].stoppedReason'
# Output: "Task failed ELB health checks in target-group..."
```

5. **CloudWatch Logs excerpt (last 50 lines)**
```bash
aws logs tail /ecs/my-service --since 10m | tail -50
```

6. **FSD YAML configuration** (relevant sections)
```yaml
service:
  port: 8000
  healthCheck:
    path: /health
    interval: 30
    timeout: 5
  resources:
    cpu: 512
    memory: 1024
```

7. **What you've already tried**
- ✅ Tested `/health` endpoint locally (returns 200)
- ✅ Checked CloudWatch Logs (no errors visible)
- ✅ Verified FSD YAML matches application port
- ❌ Still failing with same error

### When NOT to Escalate

**Don't ask for help if:**
- ❌ Haven't checked CloudWatch Logs yet
- ❌ Haven't tested locally with `docker-compose up`
- ❌ Haven't verified health endpoint works locally
- ❌ Error message is clear and actionable ("ModuleNotFoundError: requests")

**Do more debugging first:**
- Read error message carefully (often tells you exactly what's wrong)
- Google the error message (likely others have hit this)
- Check existing skill documentation (deploying-your-first-service, etc.)

---

## Summary

**Key diagnostic patterns:**
1. **Health check failures** - Test endpoint locally, check FSD YAML matches app
2. **CloudWatch Logs** - Primary debugging tool, search for errors by pattern
3. **Local testing** - Use `docker-compose up` to reproduce issues faster
4. **IAM permissions** - Test with AWS CLI using assumed role
5. **Security groups** - Verify ALB → tasks and tasks → dependencies
6. **Escalation** - After 30 min, provide full context (logs, config, what you tried)

**Next steps:**
- See [error-catalog.md](error-catalog.md) for specific error messages and solutions
- See `deploying-your-first-service` for deployment best practices
- See `understanding-ecs-resources` for resource-related issues (OOM, CPU throttling)
