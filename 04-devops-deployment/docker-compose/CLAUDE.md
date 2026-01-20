# CLAUDE.md - Docker Compose

This skill teaches multi-container orchestration with Docker Compose for development and testing environments.

## Key Concepts

- **Services**: Individual containers defined in the compose file
- **Networks**: Isolated networks for service communication
- **Volumes**: Persistent data storage across container restarts
- **Dependencies**: Service startup ordering with health checks
- **Profiles**: Environment-specific service configurations
- **Secrets**: Secure handling of sensitive data

## Common Commands

```bash
make setup      # Verify Docker Compose installation
make examples   # Run all examples
make example-1  # Run basic web stack
make example-2  # Run microservices example
make example-3  # Run dev environment
make up         # Start services
make down       # Stop services
make logs       # View service logs
make clean      # Remove all containers and volumes
```

## Project Structure

```
docker-compose/
├── README.md
├── CLAUDE.md
├── Makefile
├── examples/
│   ├── 01-web-stack/
│   │   ├── docker-compose.yml
│   │   ├── api/
│   │   └── .env.example
│   ├── 02-microservices/
│   │   ├── docker-compose.yml
│   │   ├── services/
│   │   └── .env.example
│   └── 03-dev-environment/
│       ├── docker-compose.yml
│       ├── docker-compose.override.yml
│       └── app/
├── exercises/
│   ├── exercise-1/
│   ├── exercise-2/
│   ├── exercise-3/
│   └── solutions/
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Service with Health Check
```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s
    volumes:
      - db_data:/var/lib/postgresql/data
```

### Pattern 2: Service with Dependencies
```yaml
services:
  api:
    build: ./api
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy
    environment:
      DATABASE_URL: postgres://db:5432/app
      REDIS_URL: redis://cache:6379
```

### Pattern 3: Development Override
```yaml
# docker-compose.override.yml (auto-loaded)
services:
  api:
    build:
      target: development
    volumes:
      - ./api:/app:cached
      - /app/node_modules
    command: npm run dev
    environment:
      - DEBUG=*
```

## Common Mistakes

1. **Using `depends_on` without health checks**
   - `depends_on` only waits for container start, not readiness
   - Always use `condition: service_healthy` with proper health checks

2. **Not using `.env` file for secrets**
   - Never commit secrets to docker-compose.yml
   - Use .env files (git-ignored) or environment variables

3. **Forgetting to define volumes**
   - Named volumes must be declared in top-level `volumes:`
   - Without this, data is lost on `docker compose down`

4. **Not using networks for isolation**
   - Services on different networks cannot communicate
   - Use explicit networks for security boundaries

## When Users Ask About...

### "Services can't connect to each other"
1. Check they're on the same network
2. Use service names as hostnames (not localhost)
3. Ensure target service is healthy
4. Verify port is exposed (not just published)

### "Data is lost on restart"
1. Use named volumes, not bind mounts for databases
2. Ensure volumes are declared in top-level section
3. Don't use `docker compose down -v` unless intended

### "Container starts but exits immediately"
1. Check logs: `docker compose logs service_name`
2. Verify health check command is correct
3. Ensure required env vars are set
4. Check if service expects foreground process

### "How do I debug?"
```bash
# Logs for specific service
docker compose logs -f api

# Shell into running container
docker compose exec api sh

# Run one-off command
docker compose run --rm api npm test

# Inspect container
docker compose ps
docker inspect <container_id>
```

## Testing Notes

- Start services with `make up`
- Verify health with `docker compose ps`
- Check connectivity between services
- Test volume persistence by restarting

## Dependencies

Key tools:
- Docker Engine 20.10+
- Docker Compose V2 (docker compose command)
- Optional: lazydocker for TUI management
