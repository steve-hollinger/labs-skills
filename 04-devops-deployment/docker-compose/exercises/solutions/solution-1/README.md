# Solution 1: Three-Tier Application

## Key Points

### 1. Service Configuration

- **frontend**: Uses `nginx:alpine` with volume mounts for static files and nginx config
- **api**: Built from Dockerfile, connects to database
- **db**: PostgreSQL with persistent volume

### 2. Networking

Two networks provide isolation:
- `frontend-net`: frontend <-> api communication
- `backend-net`: api <-> db communication

The frontend cannot directly access the database.

### 3. Dependencies

```yaml
api:
  depends_on:
    db:
      condition: service_healthy
```

API waits for database to pass health check before starting.

### 4. Health Checks

PostgreSQL health check:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
```

### 5. Persistent Storage

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:  # Named volume declaration
```

## Testing

```bash
# Start services
cd solutions/solution-1
docker compose up -d

# Check all services are healthy
docker compose ps

# Test frontend
curl http://localhost:3000

# Test API directly
curl http://localhost:8000/health

# Test API through nginx proxy
curl http://localhost:3000/api/health

# Test database connection
curl http://localhost:8000/db-status

# Verify persistence
docker compose down
docker compose up -d
curl http://localhost:8000/db-status  # Data should still exist
```
