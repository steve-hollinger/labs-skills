# Common Patterns

## Overview

This document covers common patterns and best practices for Docker Compose configurations.

## Pattern 1: Base + Override Files

### When to Use

When you need different configurations for development, testing, and production environments.

### Implementation

```yaml
# docker-compose.yml (base configuration)
services:
  api:
    build: ./api
    environment:
      - NODE_ENV=production
    ports:
      - "8000:8000"

  db:
    image: postgres:16-alpine
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
```

```yaml
# docker-compose.override.yml (auto-loaded in development)
services:
  api:
    build:
      context: ./api
      target: development
    volumes:
      - ./api:/app:cached
    environment:
      - NODE_ENV=development
      - DEBUG=true
    command: npm run dev

  db:
    ports:
      - "5432:5432"  # Expose for local tools
```

```yaml
# docker-compose.prod.yml (production overrides)
services:
  api:
    image: my-registry/api:${VERSION}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

### Usage

```bash
# Development (auto-loads override)
docker compose up

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up

# Testing
docker compose -f docker-compose.yml -f docker-compose.test.yml up
```

## Pattern 2: Service Profiles

### When to Use

When certain services should only run in specific scenarios (e.g., debugging tools, workers).

### Implementation

```yaml
services:
  api:
    build: ./api
    ports:
      - "8000:8000"

  db:
    image: postgres:16-alpine

  # Only runs with 'debug' profile
  adminer:
    image: adminer
    ports:
      - "8080:8080"
    profiles:
      - debug

  # Only runs with 'worker' profile
  worker:
    build: ./worker
    profiles:
      - worker

  # Runs with both 'debug' and 'monitoring' profiles
  prometheus:
    image: prom/prometheus
    profiles:
      - debug
      - monitoring
```

### Usage

```bash
# Start only api and db
docker compose up

# Start with debug tools
docker compose --profile debug up

# Start with workers
docker compose --profile worker up

# Multiple profiles
docker compose --profile debug --profile worker up
```

## Pattern 3: Init Containers

### When to Use

When you need to run setup tasks before the main service starts (migrations, seed data, etc.).

### Implementation

```yaml
services:
  db:
    image: postgres:16-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Init container for migrations
  migrate:
    build: ./api
    command: npm run migrate
    depends_on:
      db:
        condition: service_healthy
    # Exit after running
    restart: "no"

  # Main API waits for migration
  api:
    build: ./api
    depends_on:
      migrate:
        condition: service_completed_successfully
    ports:
      - "8000:8000"
```

## Pattern 4: Shared Configuration with Extensions

### When to Use

When multiple services share common configuration (logging, healthcheck patterns).

### Implementation

```yaml
# Define reusable blocks with x- prefix
x-logging: &default-logging
  driver: json-file
  options:
    max-size: "10m"
    max-file: "3"

x-healthcheck-defaults: &healthcheck-defaults
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 10s

x-common-env: &common-env
  TZ: UTC
  LOG_LEVEL: info

services:
  api:
    build: ./api
    logging: *default-logging
    healthcheck:
      <<: *healthcheck-defaults
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    environment:
      <<: *common-env
      SERVICE_NAME: api

  worker:
    build: ./worker
    logging: *default-logging
    healthcheck:
      <<: *healthcheck-defaults
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
    environment:
      <<: *common-env
      SERVICE_NAME: worker
```

## Pattern 5: Local Development with Hot Reload

### When to Use

For development environments where you want code changes to reflect immediately.

### Implementation

```yaml
services:
  api:
    build:
      context: ./api
      target: development
    volumes:
      # Mount source code
      - ./api/src:/app/src:cached
      # Preserve node_modules from container
      - /app/node_modules
    environment:
      - NODE_ENV=development
    command: npm run dev  # nodemon, etc.
    ports:
      - "8000:8000"
      - "9229:9229"  # Debug port

  frontend:
    build:
      context: ./frontend
      target: development
    volumes:
      - ./frontend/src:/app/src:cached
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000
    command: npm run dev
    ports:
      - "3000:3000"
```

### Dockerfile for Development Target

```dockerfile
# Base stage
FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Development stage
FROM base AS development
RUN npm install -g nodemon
COPY . .
CMD ["nodemon", "--inspect=0.0.0.0:9229", "src/index.js"]

# Production stage
FROM base AS production
COPY . .
RUN npm prune --production
CMD ["node", "src/index.js"]
```

## Anti-Patterns

### Anti-Pattern 1: Using `links` (Deprecated)

```yaml
# Bad - deprecated, use networks instead
services:
  api:
    links:
      - db:database
```

### Better Approach

```yaml
# Good - use default network and service names
services:
  api:
    environment:
      - DATABASE_HOST=db  # Service name as hostname
  db:
    image: postgres
```

### Anti-Pattern 2: Storing Secrets in Compose File

```yaml
# Bad - secrets visible in file
services:
  db:
    environment:
      - POSTGRES_PASSWORD=mysupersecret
```

### Better Approach

```yaml
# Good - use .env file or Docker secrets
services:
  db:
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    # Or use secrets
    secrets:
      - db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

### Anti-Pattern 3: Not Using Health Checks

```yaml
# Bad - no way to know if service is ready
services:
  api:
    depends_on:
      - db
```

### Better Approach

```yaml
# Good - proper health check dependency
services:
  api:
    depends_on:
      db:
        condition: service_healthy
  db:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Different dev/prod configs | Pattern 1: Base + Override |
| Optional debugging tools | Pattern 2: Service Profiles |
| Database migrations | Pattern 3: Init Containers |
| Shared logging config | Pattern 4: Extensions |
| Local development | Pattern 5: Hot Reload |
