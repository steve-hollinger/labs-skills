# Exercise 1: Convert Docker Compose to FSD YAML

## Objective

Convert a Docker Compose service definition into a valid FSD YAML configuration for ECS Fargate deployment.

## Background

Your team has been running a notification service locally using Docker Compose. Now you need to deploy it to AWS ECS. Your task is to convert the Docker Compose configuration to FSD YAML format.

## Given Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  notification-service:
    image: notifications:latest
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - PORT=3000
      - LOG_LEVEL=info
      - SMTP_HOST=smtp.example.com
      - SMTP_USER=notifications@example.com
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

## Requirements

Create an FSD YAML file that:

1. Uses the service name `notification-service`
2. Targets the `ecs` platform
3. Maps the compute resources appropriately for ECS Fargate
4. Configures networking with the correct port and health check
5. Includes all environment variables (but uses `${secrets:...}` for SMTP_USER)
6. Includes appropriate metadata tags

## Hints

- ECS CPU is in units: 256 = 0.25 vCPU, 512 = 0.5 vCPU
- ECS memory is in MB
- `desired_count` maps to Docker's `replicas`
- Convert the health check interval from `30s` to seconds (integer)

## Validation

Test your solution:

```bash
make validate YAML=exercises/solutions/solution-1.yml
```

## Expected Fields

Your solution should include:
- `name`
- `platform`
- `description`
- `team`
- `tags`
- `compute` (cpu, memory, desired_count)
- `networking` (port, health_check)
- `environment`

## Submit Your Solution

Save your solution to `exercises/solutions/solution-1.yml`
