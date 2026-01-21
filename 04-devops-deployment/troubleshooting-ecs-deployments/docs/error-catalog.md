# Error Catalog

Common ECS deployment errors with step-by-step solutions.

---

## Error 1: Task failed ELB health checks

### Error Message

```
Stopped reason: Task failed ELB health checks in (target-group arn:aws:elasticloadbalancing:us-east-1:123456:targetgroup/...)
```

### What It Means

The Application Load Balancer sent 3 consecutive health check requests to `/health` and got non-200 responses (404, 500, timeout).

### Common Causes

**Cause 1: Health endpoint not implemented**

```bash
# Test locally
curl http://localhost:8000/health
# HTTP/1.1 404 Not Found
```

**Solution:**
```python
# Add health endpoint to your app
@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

**Cause 2: Health endpoint returns 500 error**

```bash
# CloudWatch Logs show:
GET /health → 500 Internal Server Error
Traceback (most recent call last):
  File "main.py", line 42, in health_check
    db.execute("SELECT 1").fetchone()
sqlite3.OperationalError: no such table: users
```

**Solution:**
- Initialize database schema on startup (see `working-with-sqlite`)
- Or: Simplify health check (don't query database)

**Cause 3: Port mismatch**

```yaml
# FSD YAML says port 8000
service:
  port: 8000
```

```python
# But app listens on 3000
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)  # ← Wrong port
```

**Solution:** Match ports in FSD YAML and application code.

**Cause 4: Health check timeout**

```yaml
healthCheck:
  path: /health
  timeout: 5    # ← Health check takes 10 seconds, times out
```

**Solution:**
- Increase timeout to 10-15 seconds
- Or: Optimize health check endpoint (remove slow database queries)

**Cause 5: Path mismatch**

```yaml
# FSD YAML
healthCheck:
  path: /health    # ← ALB requests /health
```

```python
# Application
@app.get("/healthz")  # ← App only has /healthz
def health_check():
    return {"status": "healthy"}
```

**Solution:** Match `healthCheck.path` in FSD YAML and application route exactly.

### Debugging Steps

1. **Test health endpoint locally:**
```bash
docker-compose up
curl -v http://localhost:8000/health
# Should return HTTP/1.1 200 OK within 5 seconds
```

2. **Check CloudWatch Logs during health check:**
```bash
aws logs tail /ecs/my-service --follow | grep "/health"
# Look for 500 errors or missing requests
```

3. **Verify FSD YAML matches app:**
- FSD `healthCheck.path` = Application route
- FSD `service.port` = Application listen port

4. **Simplify health check:**
```python
# Remove database queries, external API calls
@app.get("/health")
def health_check():
    return {"status": "healthy"}  # Just return 200
```

---

## Error 2: Essential container in task exited

### Error Message

```
Stopped reason: Essential container in task exited
Exit code: 1
```

### What It Means

Your application process crashed or exited with a non-zero exit code before ECS could mark it as healthy.

### Common Causes

**Cause 1: Missing Python dependency**

```
# CloudWatch Logs:
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```txt
# Add to requirements.txt
fastapi==0.109.0

# Rebuild Docker image
docker build -t my-service .
```

**Cause 2: Missing environment variable**

```
# CloudWatch Logs:
KeyError: 'DATABASE_URL'
File "main.py", line 15, in <module>
    db_url = os.environ['DATABASE_URL']
```

**Solution:**
```yaml
# Add to FSD YAML
service:
  environment:
    DATABASE_URL: ${DATABASE_URL}
```

**Cause 3: Port binding error**

```
# CloudWatch Logs:
OSError: [Errno 98] Address already in use
```

**Solution:**
- Ensure app listens on `0.0.0.0` not `127.0.0.1`
```python
# ❌ Wrong
uvicorn.run(app, host="127.0.0.1", port=8000)

# ✅ Correct
uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Cause 4: Database connection failed**

```
# CloudWatch Logs:
psycopg2.OperationalError: could not connect to server: Connection refused
Is the server running on host "localhost" (127.0.0.1) and accepting TCP/IP connections on port 5432?
```

**Solution:**
- Check `DATABASE_URL` points to correct host (not `localhost`)
- Verify RDS security group allows traffic from ECS tasks
- For SQLite: Initialize database on startup, don't assume it exists

**Cause 5: Python version mismatch**

```
# CloudWatch Logs:
SyntaxError: invalid syntax
    x: int | None = None
           ^
# Union type syntax requires Python 3.10+
```

**Solution:**
```dockerfile
# Update Dockerfile
FROM python:3.11-slim  # ← Use Python 3.10+
```

Or use older syntax:
```python
from typing import Optional
x: Optional[int] = None
```

### Debugging Steps

1. **Read CloudWatch Logs:**
```bash
aws logs tail /ecs/my-service --follow
# Look for Traceback, Error:, panic:
```

2. **Test container locally:**
```bash
docker-compose up
# Watch for startup errors in terminal output
```

3. **Check exit code:**
```bash
aws ecs describe-tasks --tasks <task-id> | jq '.tasks[0].containers[0].exitCode'
# Exit code 1 = general error
# Exit code 137 = OOM kill (out of memory)
# Exit code 139 = segmentation fault
```

4. **Add debug logging:**
```python
# Add to startup
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info("Starting application...")
logger.info(f"Environment: {os.environ}")
logger.info("Application started successfully")
```

---

## Error 3: OutOfMemoryError: Container killed due to memory usage

### Error Message

```
Stopped reason: OutOfMemoryError: Container killed due to memory usage
```

### What It Means

Your container exceeded its memory allocation. The kernel killed it to prevent system instability.

### Common Causes

**Cause 1: Memory allocation too low**

```yaml
# FSD YAML
resources:
  memory: 512  # ← Too small for app + dependencies
```

**Solution:**
```bash
# Check memory usage in CloudWatch before failure
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization \
  --dimensions Name=ServiceName,Value=my-service \
  --start-time $(date -u -d '1 hour ago' --iso-8601=seconds) \
  --end-time $(date -u --iso-8601=seconds) \
  --period 300 \
  --statistics Maximum

# If memory was at 95-100%, increase allocation
```

```yaml
# Increase memory
resources:
  memory: 1024  # ← Doubled
```

**Cause 2: Memory leak**

```
# Memory grows over time:
10:00 AM - 40% memory usage
11:00 AM - 60% memory usage
12:00 PM - 85% memory usage
12:30 PM - 100% memory usage → OOM kill
```

**Solution:**
- Profile application for memory leaks
- Python: Use `tracemalloc` or `memory_profiler`
- Node.js: Use `heapdump` or Chrome DevTools
- Fix leaks: Close database connections, clear caches, avoid global lists

**Cause 3: Large batch operation**

```python
# Load entire table into memory
items = db.execute("SELECT * FROM items").fetchall()  # 1M rows × 1KB = 1GB
```

**Solution:**
- Use pagination/chunking:
```python
# Process in batches
BATCH_SIZE = 1000
offset = 0
while True:
    items = db.execute(
        "SELECT * FROM items LIMIT ? OFFSET ?",
        (BATCH_SIZE, offset)
    ).fetchall()
    if not items:
        break
    process_batch(items)
    offset += BATCH_SIZE
```

**Cause 4: Model size exceeds memory**

```python
# Load 3 GB ML model into 2 GB container
model = torch.load('model.pth')  # OOM
```

**Solution:**
```yaml
# Increase memory to fit model
resources:
  memory: 8192  # 8 GB for 3 GB model + overhead
```

Or use model optimization:
```python
# Quantize model (reduce memory 4x)
quantized_model = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)
```

### Debugging Steps

1. **Check memory utilization before OOM:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization \
  --dimensions Name=ServiceName,Value=my-service \
  --start-time $(date -u -d '2 hours ago' --iso-8601=seconds) \
  --end-time $(date -u --iso-8601=seconds) \
  --period 60 \
  --statistics Maximum
```

2. **Test with more memory locally:**
```bash
docker run --memory=2g my-service
# If it works, increase memory in FSD YAML
```

3. **Profile memory usage:**
```python
# Add memory tracking
import psutil
import logging

logger = logging.getLogger(__name__)

def log_memory_usage():
    process = psutil.Process()
    mem = process.memory_info().rss / 1024 / 1024  # MB
    logger.info(f"Memory usage: {mem:.2f} MB")

# Call periodically
log_memory_usage()
```

4. **Check for memory leaks:**
```python
# Python: Track object counts
import gc
import sys

gc.collect()
objects = gc.get_objects()
type_counts = {}
for obj in objects:
    t = type(obj).__name__
    type_counts[t] = type_counts.get(t, 0) + 1

# Log top 10 types
for t, count in sorted(type_counts.items(), key=lambda x: -x[1])[:10]:
    print(f"{t}: {count}")
```

---

## Error 4: CannotPullContainerError

### Error Message

```
Stopped reason: CannotPullContainerError:
Error response from daemon: pull access denied for 123456.dkr.ecr.us-east-1.amazonaws.com/my-service, repository does not exist or may require 'docker login'
```

### What It Means

ECS tried to pull your Docker image from ECR but failed due to permissions or missing image.

### Common Causes

**Cause 1: Image doesn't exist in ECR**

**Solution:**
```bash
# Check if image exists
aws ecr describe-images \
  --repository-name my-service \
  --region us-east-1

# If empty, push image
docker build -t my-service .
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456.dkr.ecr.us-east-1.amazonaws.com
docker tag my-service:latest 123456.dkr.ecr.us-east-1.amazonaws.com/my-service:latest
docker push 123456.dkr.ecr.us-east-1.amazonaws.com/my-service:latest
```

**Cause 2: Task execution role lacks ECR permissions**

**Solution:**
```yaml
# FSD usually handles this, but if custom execution role:
executionRole:
  statements:
    - effect: Allow
      actions:
        - ecr:GetAuthorizationToken
        - ecr:BatchCheckLayerAvailability
        - ecr:GetDownloadUrlForLayer
        - ecr:BatchGetImage
      resources: "*"
```

**Cause 3: Wrong image tag in task definition**

```yaml
# FSD YAML references image that doesn't exist
service:
  image: 123456.dkr.ecr.us-east-1.amazonaws.com/my-service:v2.0  # ← Tag doesn't exist
```

**Solution:**
```bash
# List available tags
aws ecr list-images --repository-name my-service

# Update FSD YAML to use existing tag
service:
  image: 123456.dkr.ecr.us-east-1.amazonaws.com/my-service:latest
```

**Cause 4: ECR repository in different region**

```yaml
# Task runs in us-west-2, but image is in us-east-1
service:
  image: 123456.dkr.ecr.us-east-1.amazonaws.com/my-service:latest
```

**Solution:**
- Push image to same region as ECS cluster
- Or: Use ECR replication to copy images across regions

### Debugging Steps

1. **Verify image exists:**
```bash
aws ecr describe-images \
  --repository-name my-service \
  --region us-east-1 \
  | jq '.imageDetails[] | {tags: .imageTags, pushed: .imagePushedAt}'
```

2. **Test ECR permissions:**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456.dkr.ecr.us-east-1.amazonaws.com

# Try pulling image
docker pull 123456.dkr.ecr.us-east-1.amazonaws.com/my-service:latest
```

3. **Check task definition:**
```bash
aws ecs describe-task-definition \
  --task-definition my-service \
  | jq '.taskDefinition.containerDefinitions[0].image'
```

---

## Error 5: ResourceInitializationError (Secrets Manager)

### Error Message

```
Stopped reason: ResourceInitializationError:
unable to pull secrets or registry auth: execution resource retrieval failed:
unable to retrieve secret from asm:
service call has been retried 1 time(s): AccessDeniedException:
User: arn:aws:sts::123456:assumed-role/my-execution-role is not authorized to perform: secretsmanager:GetSecretValue on resource: my-secret
```

### What It Means

Task execution role doesn't have permission to read secrets from AWS Secrets Manager.

### Solution

**Add permission to task execution role:**

```yaml
# FSD YAML
service:
  executionRole:
    statements:
      - effect: Allow
        actions:
          - secretsmanager:GetSecretValue
        resources:
          - arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:my-secret-*
```

**Or use FSD's auto-configuration:**

```yaml
service:
  secrets:
    - name: API_KEY
      valueFrom: arn:aws:secretsmanager:us-east-1:123456:secret:my-api-key-AbCdEf
```

FSD automatically adds the required permissions.

### Debugging Steps

1. **Verify secret exists:**
```bash
aws secretsmanager describe-secret \
  --secret-id my-api-key \
  --region us-east-1
```

2. **Test secret access:**
```bash
aws secretsmanager get-secret-value \
  --secret-id my-api-key \
  --region us-east-1
```

3. **Check execution role permissions:**
```bash
aws iam get-role-policy \
  --role-name my-execution-role \
  --policy-name my-execution-policy
```

---

## Error 6: Logs show "Connection refused"

### Error Message (in CloudWatch Logs)

```
requests.exceptions.ConnectionError: HTTPConnectionPool(host='my-db.us-east-1.rds.amazonaws.com', port=5432):
Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object>:
Failed to establish a new connection: [Errno 111] Connection refused'))
```

### What It Means

Your application tried to connect to a service (database, API, etc.) but the connection was refused.

### Common Causes

**Cause 1: Security group blocks traffic**

**Solution:**
```bash
# Check RDS security group allows traffic from ECS tasks
aws ec2 describe-security-groups --group-ids sg-rds12345

# Should have ingress rule:
# Port: 5432
# Source: sg-ecs-tasks (ECS task security group)
```

**Cause 2: Wrong hostname/port**

```python
# Wrong
DATABASE_URL = "postgresql://localhost:5432/mydb"  # ← localhost doesn't work in ECS

# Correct
DATABASE_URL = "postgresql://my-db.us-east-1.rds.amazonaws.com:5432/mydb"
```

**Cause 3: Service not running**

```bash
# RDS instance stopped
aws rds describe-db-instances \
  --db-instance-identifier my-db \
  | jq '.DBInstances[0].DBInstanceStatus'

# Should be "available", not "stopped"
```

**Cause 4: VPC/subnet mismatch**

```
ECS tasks in subnet A
RDS in subnet B
Subnets not routed to each other
```

**Solution:** Deploy ECS tasks and RDS in same VPC, allow communication in security groups.

### Debugging Steps

1. **Test connection from ECS task (requires ECS Exec):**
```bash
aws ecs execute-command \
  --cluster my-cluster \
  --task <task-id> \
  --container my-service \
  --interactive \
  --command "/bin/sh"

# Inside container
nc -zv my-db.us-east-1.rds.amazonaws.com 5432
# Success: "Connection to my-db.us-east-1.rds.amazonaws.com 5432 port [tcp/*] succeeded!"
# Failure: "Connection refused" or "Connection timed out"
```

2. **Check security groups:**
```bash
# Get ECS task ENI
aws ecs describe-tasks --tasks <task-id> | jq '.tasks[0].attachments[0].details[] | select(.name=="networkInterfaceId") | .value'

# Get security groups on ENI
aws ec2 describe-network-interfaces --network-interface-ids eni-12345 | jq '.NetworkInterfaces[0].Groups'

# Check if RDS security group allows traffic from ECS security group
```

---

## Error 7: Task failed to start

### Error Message

```
Stopped reason: Task failed to start
```

### What It Means

Generic error when ECS can't start your task. Check CloudWatch Logs for details.

### Common Causes

**Cause 1: Invalid CPU/memory combination**

```yaml
# Invalid combination
resources:
  cpu: 512
  memory: 8192  # ← Can't have 8 GB memory with 0.5 vCPU
```

**Solution:** See valid combinations in `understanding-ecs-resources` skill.

**Cause 2: Container command not found**

```dockerfile
# Dockerfile
CMD ["python"]  # ← python not in PATH
```

```
# CloudWatch Logs:
CannotStartContainerError: Error response from daemon:
OCI runtime create failed: executable file not found in $PATH
```

**Solution:**
```dockerfile
# Use full path or install Python
CMD ["python3"]  # Most images have python3
# Or
CMD ["/usr/local/bin/python"]
```

**Cause 3: No space left on device**

```
# CloudWatch Logs:
OSError: [Errno 28] No space left on device
```

**Solution:**
- Default Fargate storage: 20 GB ephemeral
- Increase to 200 GB max:
```yaml
service:
  ephemeralStorage: 100  # GB
```

**Cause 4: Invalid environment variable**

```yaml
service:
  environment:
    PATH: /my/custom/path  # ← Overriding PATH breaks everything
```

**Solution:** Don't override system environment variables (PATH, HOME, USER).

### Debugging Steps

1. **Check CloudWatch Logs:**
```bash
aws logs tail /ecs/my-service --follow
```

2. **Verify CPU/memory combination is valid:**
- See `understanding-ecs-resources` skill

3. **Test container locally:**
```bash
docker run my-service
# Should start without errors
```

---

## Summary

**Top 7 errors:**
1. **Task failed ELB health checks** → Fix `/health` endpoint, verify FSD YAML matches app
2. **Essential container in task exited** → Check CloudWatch Logs for startup errors
3. **OutOfMemoryError** → Increase memory allocation or fix memory leaks
4. **CannotPullContainerError** → Verify image exists in ECR, check permissions
5. **ResourceInitializationError (Secrets)** → Add Secrets Manager permissions to execution role
6. **Connection refused** → Fix security groups, verify service hostnames
7. **Task failed to start** → Check valid CPU/memory combination, verify CMD/ENTRYPOINT

**Debugging workflow:**
1. Check task stopped reason (ECS console)
2. Read CloudWatch Logs (application errors)
3. Test locally with `docker-compose up`
4. Verify IAM permissions (AWS CLI with assumed role)
5. Check security groups (ALB → tasks, tasks → dependencies)

**Next steps:**
- See [concepts.md](concepts.md) for ECS fundamentals
- See [patterns.md](patterns.md) for diagnostic procedures
- See `deploying-your-first-service` for deployment best practices
