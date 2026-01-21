---
name: troubleshooting-ecs-deployments
description: Debug common ECS deployment failures including health check issues, CloudWatch logs, IAM permissions, and network problems. Use when deployments fail or services are unhealthy.
tags: ['ecs', 'troubleshooting', 'debugging', 'cloudwatch', 'health-checks', 'deployment']
---

# Troubleshooting ECS Deployments

## Quick Start

**5-step diagnostic process:**

1. ✅ **Check ECS Console** - View task stopped reason and deployment status
2. ✅ **Read CloudWatch Logs** - Search for application errors and startup issues
3. ✅ **Test health check endpoint** - Verify `/health` returns 200 status locally
4. ✅ **Test container locally** - Run `docker-compose up` to reproduce the issue
5. ✅ **Verify IAM permissions** - Check task role has required AWS permissions

```bash
# Quick diagnostic commands
# 1. Check service status
aws ecs describe-services --cluster my-cluster --services my-service

# 2. Find failed tasks
aws ecs list-tasks --cluster my-cluster --service-name my-service --desired-status STOPPED

# 3. Get task failure reason
aws ecs describe-tasks --cluster my-cluster --tasks <task-id>

# 4. View recent logs
aws logs tail /ecs/my-service --follow
```

## Key Points

- **Most failures are health check issues** - Check `/health` endpoint first (returns 200 status, responds within timeout)
- **CloudWatch Logs are primary debugging tool** - Application errors, startup failures, and crashes appear here first
- **Task failure reasons appear in ECS console/CLI** - `describe-tasks` shows stopped reason (OOM, health check failure, etc.)
- **Health check failures vs startup failures are different** - Health check = app running but unhealthy; startup = app crashed before running
- **IAM permission errors are silent** - Application logs show "Access Denied" for AWS SDK calls, not ECS task failures

## Common Mistakes

1. **Not checking CloudWatch Logs first** - Trying to debug from ECS console alone. Logs show actual error messages from your application.
2. **Debugging in production instead of docker-compose locally** - Faster iteration testing locally with `docker-compose up` before redeploying.
3. **Assuming IAM permissions work** - Test with AWS CLI first: `aws dynamodb list-tables` to verify task role permissions.
4. **Ignoring task stopped reasons in ECS console** - `Essential container in task exited` tells you the app crashed (check logs for why).
5. **Not testing health check endpoint before deploying** - Use `curl http://localhost:8000/health` locally to verify it returns 200.

## More Detail

- [docs/concepts.md](docs/concepts.md) - ECS task lifecycle, health check mechanics, CloudWatch Logs, IAM roles
- [docs/patterns.md](docs/patterns.md) - Diagnostic procedures, testing locally, verifying permissions
- [docs/error-catalog.md](docs/error-catalog.md) - 7+ common errors with step-by-step solutions
