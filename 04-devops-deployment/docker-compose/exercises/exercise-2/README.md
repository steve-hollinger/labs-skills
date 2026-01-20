# Exercise 2: Health Checks and Dependencies

## Objective

Add proper health checks and dependency ordering to an existing Docker Compose configuration to ensure services start in the correct order and wait for dependencies to be ready.

## Starting Point

The provided `docker-compose.yml` has services that sometimes fail on startup because:
- The API starts before the database is ready
- The worker starts before both API and message queue are ready
- There are no health checks to verify service readiness

## Requirements

1. **Add health checks** to all services that need them
2. **Configure dependencies** with proper conditions
3. **Ensure startup order**: db -> api -> worker
4. **Handle message queue**: rabbitmq must be healthy before worker starts

## Files

- `docker-compose.yml` - Configuration to fix
- `api/` - API service code
- `worker/` - Worker service code

## Current Issues

```yaml
# Current (problematic):
services:
  api:
    depends_on:
      - db  # Only waits for container start, not readiness!
```

## Steps

1. Review the current `docker-compose.yml`

2. Add health checks to:
   - `db` service (PostgreSQL)
   - `rabbitmq` service
   - `api` service

3. Update `depends_on` to use conditions:
   ```yaml
   depends_on:
     db:
       condition: service_healthy
   ```

4. Test the startup:
   ```bash
   docker compose up -d
   docker compose ps  # All should be healthy
   docker compose logs api  # No connection errors
   ```

## Health Check Commands

| Service | Health Check Command |
|---------|---------------------|
| PostgreSQL | `pg_isready -U postgres` |
| RabbitMQ | `rabbitmq-diagnostics -q ping` |
| HTTP API | `curl -f http://localhost:PORT/health` |

## Success Criteria

- [ ] All services have appropriate health checks
- [ ] Services wait for dependencies to be healthy
- [ ] No connection errors in logs on fresh startup
- [ ] `docker compose ps` shows all services as "healthy"
