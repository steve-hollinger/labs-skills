# Core Concepts

## Overview

Docker Compose is a tool for defining and running multi-container Docker applications. This document covers the fundamental concepts you need to understand for effective container orchestration.

## Concept 1: Services

### What It Is

A service is a container definition in your compose file. Each service represents one component of your application that runs in one or more containers.

### Why It Matters

Services provide:
- Declarative container configuration
- Easy scaling (multiple instances)
- Automatic DNS-based service discovery
- Consistent environment across team members

### How It Works

```yaml
services:
  # Service name becomes the DNS hostname
  api:
    # Build from Dockerfile
    build:
      context: ./api
      dockerfile: Dockerfile
    # Or use existing image
    # image: nginx:alpine

    # Port mapping: host:container
    ports:
      - "8000:8000"

    # Environment variables
    environment:
      - NODE_ENV=production

    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  # Another service
  worker:
    build: ./worker
    # Scale to 3 instances
    deploy:
      replicas: 3
```

Service names are used for inter-container communication:
```python
# From api container, connect to database
DATABASE_URL = "postgres://db:5432/myapp"  # 'db' is service name
```

## Concept 2: Networks

### What It Is

Networks provide isolated communication channels between services. By default, Compose creates a network for your application, but you can define custom networks for isolation.

### Why It Matters

- **Security**: Services on different networks can't communicate
- **Organization**: Group related services together
- **Clarity**: Explicit network topology

### How It Works

```yaml
services:
  # Frontend can talk to api but not db
  frontend:
    networks:
      - frontend-net

  # API bridges frontend and backend
  api:
    networks:
      - frontend-net
      - backend-net

  # Database isolated to backend
  db:
    networks:
      - backend-net

networks:
  frontend-net:
    driver: bridge
  backend-net:
    driver: bridge
    internal: true  # No external access
```

Network communication:
```
┌─────────────────────────────────────────────────────┐
│                  frontend-net                        │
│  ┌──────────┐              ┌──────────┐            │
│  │ frontend │──────────────│   api    │            │
│  └──────────┘              └────┬─────┘            │
└─────────────────────────────────┼───────────────────┘
                                  │
┌─────────────────────────────────┼───────────────────┐
│                  backend-net    │                    │
│                            ┌────┴─────┐             │
│                            │   api    │             │
│                            └────┬─────┘             │
│                                 │                   │
│                            ┌────┴─────┐             │
│                            │    db    │             │
│                            └──────────┘             │
└─────────────────────────────────────────────────────┘
```

## Concept 3: Volumes

### What It Is

Volumes are persistent storage mechanisms that survive container restarts. They're essential for databases, file uploads, and any data that shouldn't be lost.

### Why It Matters

- **Persistence**: Data survives container lifecycle
- **Performance**: Better than bind mounts for databases
- **Portability**: Managed by Docker, not host-dependent

### How It Works

```yaml
services:
  db:
    image: postgres:16-alpine
    volumes:
      # Named volume for database
      - postgres_data:/var/lib/postgresql/data

  api:
    build: ./api
    volumes:
      # Bind mount for development (live code reload)
      - ./api/src:/app/src:cached

      # Anonymous volume (preserves node_modules in container)
      - /app/node_modules

# Named volumes must be declared
volumes:
  postgres_data:
    # Optional: use external volume
    # external: true

  # Volume with specific driver
  cache_data:
    driver: local
    driver_opts:
      type: tmpfs
      device: tmpfs
```

Volume types:
1. **Named volumes**: `volume_name:/path` - Managed by Docker
2. **Bind mounts**: `./host/path:/container/path` - Direct mapping
3. **Anonymous volumes**: `/container/path` - Temporary, container-specific

## Concept 4: Dependencies and Health Checks

### What It Is

Dependencies define startup order. Health checks verify a service is ready to receive traffic, not just running.

### Why It Matters

Without proper dependencies:
- API might start before database is ready
- Connections fail during startup
- Flaky, inconsistent behavior

### How It Works

```yaml
services:
  api:
    depends_on:
      db:
        condition: service_healthy  # Wait for health check
      cache:
        condition: service_started  # Just wait for start

  db:
    image: postgres:16-alpine
    healthcheck:
      # Command to check health
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      # Check every 5 seconds
      interval: 5s
      # Timeout for each check
      timeout: 5s
      # Mark unhealthy after 5 failures
      retries: 5
      # Grace period before starting checks
      start_period: 10s

  cache:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 3
```

Health check states:
- `starting`: Within start_period, checks not yet passing
- `healthy`: Health check passing
- `unhealthy`: Health check failing after retries

## Concept 5: Environment Configuration

### What It Is

Environment configuration includes variables, secrets, and configuration files that customize service behavior without modifying images.

### Why It Matters

- **Portability**: Same image, different configs
- **Security**: Keep secrets out of images
- **Flexibility**: Easily switch between environments

### How It Works

```yaml
services:
  api:
    # Method 1: Inline definition
    environment:
      - NODE_ENV=production
      - LOG_LEVEL=info

    # Method 2: From .env file
    env_file:
      - .env           # Default
      - .env.local     # Override (git-ignored)

    # Method 3: Variable substitution (from host)
    environment:
      - API_KEY=${API_KEY}
      - DATABASE_URL=${DATABASE_URL:-postgres://localhost:5432/app}

# .env file format:
# NODE_ENV=production
# API_KEY=secret123
# DATABASE_URL=postgres://db:5432/app
```

Priority (highest to lowest):
1. `environment:` in compose file
2. Shell environment variables
3. `.env` file
4. Dockerfile `ENV` defaults

## Summary

Key takeaways:

1. **Services** define your containers with declarative configuration
2. **Networks** provide isolation and communication boundaries
3. **Volumes** persist data beyond container lifecycle
4. **Dependencies + Health checks** ensure proper startup order
5. **Environment configuration** keeps configs portable and secure

These concepts combine to create reproducible, scalable, and maintainable multi-container applications.
