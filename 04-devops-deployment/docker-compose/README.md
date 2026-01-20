# Docker Compose

Master multi-container orchestration with Docker Compose for local development and testing environments.

## Learning Objectives

After completing this skill, you will be able to:
- Define and run multi-container applications
- Configure service dependencies and health checks
- Manage environment variables and secrets
- Set up volumes for data persistence
- Create custom networks for service isolation
- Use profiles for environment-specific configurations

## Prerequisites

- Docker and Docker Compose installed
- Completed [Docker/ECR](../docker-ecr/) skill
- Basic understanding of YAML syntax
- Familiarity with networking concepts

## Quick Start

```bash
# Verify installation
make setup

# Run examples
make examples

# Start example application
make up

# Stop and clean up
make down
```

## Concepts

### Compose File Structure

Docker Compose uses YAML files to define multi-container applications:

```yaml
# docker-compose.yml
version: "3.9"  # Optional in Compose V2

services:
  api:
    build: ./api
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgres://db:5432/app

  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password

volumes:
  postgres_data:
```

### Service Dependencies

Define startup order and health check dependencies:

```yaml
services:
  api:
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started

  db:
    image: postgres:16-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
```

### Environment Configuration

Multiple approaches for environment variables:

```yaml
services:
  api:
    # Inline variables
    environment:
      - NODE_ENV=production
      - API_KEY=${API_KEY}  # From host environment

    # From file
    env_file:
      - .env
      - .env.local

    # Build args
    build:
      context: .
      args:
        - BUILD_VERSION=1.0.0
```

## Examples

### Example 1: Basic Web Stack

A simple web application with API and database.

```bash
make example-1
```

See [examples/01-web-stack/](./examples/01-web-stack/) for details.

### Example 2: Microservices Architecture

Multiple services with message queue and cache.

```bash
make example-2
```

See [examples/02-microservices/](./examples/02-microservices/) for details.

### Example 3: Development Environment

Complete dev environment with hot reload and debugging.

```bash
make example-3
```

See [examples/03-dev-environment/](./examples/03-dev-environment/) for details.

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Create a three-tier application (frontend, API, database)
2. **Exercise 2**: Add health checks and proper dependency ordering
3. **Exercise 3**: Configure profiles for dev/test/prod environments

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Not Using Health Checks for Dependencies

```yaml
# Bad - api may start before db is ready
services:
  api:
    depends_on:
      - db

# Good - wait for db to be healthy
services:
  api:
    depends_on:
      db:
        condition: service_healthy
  db:
    healthcheck:
      test: ["CMD", "pg_isready"]
```

### Hardcoding Secrets

```yaml
# Bad - secrets in compose file
environment:
  - DB_PASSWORD=mysecretpassword

# Good - use environment variables or secrets
environment:
  - DB_PASSWORD=${DB_PASSWORD}
secrets:
  - db_password
```

### Not Persisting Data

```yaml
# Bad - data lost when container restarts
services:
  db:
    image: postgres

# Good - persistent volume
services:
  db:
    image: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Key Commands

```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Stop and remove volumes
docker compose down -v

# Rebuild images
docker compose build --no-cache

# Scale a service
docker compose up -d --scale worker=3

# Execute command in running container
docker compose exec api sh
```

## Further Reading

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Compose File Reference](https://docs.docker.com/compose/compose-file/)
- Related skills in this repository:
  - [Docker/ECR](../docker-ecr/)
  - [GitHub Actions](../github-actions/)
