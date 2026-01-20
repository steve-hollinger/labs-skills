# Solution 2: Health Checks and Dependencies

## Key Points

### 1. Health Check Configuration

Each health check has these parameters:
- `test`: Command to check health
- `interval`: How often to check
- `timeout`: Max time for check to complete
- `retries`: Number of failures before unhealthy
- `start_period`: Grace period for container startup

### 2. PostgreSQL Health Check

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 5s
  timeout: 5s
  retries: 5
  start_period: 10s
```

`pg_isready` is a PostgreSQL utility that checks if the server is accepting connections.

### 3. RabbitMQ Health Check

```yaml
healthcheck:
  test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
  interval: 10s
  timeout: 10s
  retries: 5
  start_period: 30s  # Longer - RabbitMQ takes time to start
```

RabbitMQ's `rabbitmq-diagnostics ping` checks the Erlang node.

### 4. HTTP API Health Check

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 10s
```

Uses curl to check HTTP endpoint. `-f` flag makes curl fail on HTTP errors.

### 5. Dependency Conditions

```yaml
depends_on:
  db:
    condition: service_healthy  # Waits for health check to pass
  rabbitmq:
    condition: service_healthy
```

Without `condition: service_healthy`, Docker only waits for container to start.

## Testing

```bash
# Start from scratch
docker compose down -v
docker compose up -d

# Watch startup sequence
docker compose logs -f

# Check health status
docker compose ps

# All should show "healthy" state
```

## Common Issues Fixed

1. **API crashes on startup**: Now waits for DB to be healthy
2. **Worker connection errors**: Waits for RabbitMQ
3. **Flaky tests**: Services reliably ready when accessed
