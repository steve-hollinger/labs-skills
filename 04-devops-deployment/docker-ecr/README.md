# Docker/ECR

Master Docker containerization best practices and AWS Elastic Container Registry (ECR) workflows for production-ready container deployments.

## Learning Objectives

After completing this skill, you will be able to:
- Write optimized, secure Dockerfiles following best practices
- Implement multi-stage builds to minimize image size
- Push and pull images to/from Amazon ECR
- Scan container images for security vulnerabilities
- Optimize Docker images for production deployment

## Prerequisites

- Docker installed locally
- AWS CLI configured with appropriate permissions
- Basic understanding of containerization concepts
- Familiarity with Linux command line

## Quick Start

```bash
# Install dependencies (verify Docker is available)
make setup

# Run examples
make examples

# Validate Dockerfiles
make lint
```

## Concepts

### Dockerfile Best Practices

Well-structured Dockerfiles lead to smaller, faster, more secure images.

```dockerfile
# Use specific version tags (not latest)
FROM python:3.12-slim-bookworm

# Set metadata
LABEL maintainer="team@example.com"
LABEL version="1.0.0"

# Create non-root user early
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Set working directory
WORKDIR /app

# Copy only dependency files first (better cache utilization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

# Use exec form for CMD
CMD ["python", "main.py"]
```

### Multi-Stage Builds

Multi-stage builds allow you to use multiple FROM statements to create optimized final images.

```dockerfile
# Build stage
FROM golang:1.22-alpine AS builder
WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o app

# Runtime stage
FROM alpine:3.19
RUN apk --no-cache add ca-certificates
COPY --from=builder /build/app /app
ENTRYPOINT ["/app"]
```

### ECR Workflow

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Create repository
aws ecr create-repository --repository-name my-app

# Tag and push
docker tag my-app:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
```

## Examples

### Example 1: Basic Python Application

A minimal but production-ready Python application Dockerfile.

```bash
make example-1
```

See [examples/01-python-basic/](./examples/01-python-basic/) for the complete example.

### Example 2: Multi-Stage Go Build

Demonstrates multi-stage builds for compiled languages.

```bash
make example-2
```

See [examples/02-go-multistage/](./examples/02-go-multistage/) for the complete example.

### Example 3: Node.js with Security Hardening

Production Node.js image with security best practices.

```bash
make example-3
```

See [examples/03-node-secure/](./examples/03-node-secure/) for the complete example.

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Optimize an inefficient Dockerfile - Reduce image size by 80%
2. **Exercise 2**: Implement multi-stage build - Convert a single-stage build to multi-stage
3. **Exercise 3**: ECR deployment workflow - Create a complete build and push script

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Using `latest` Tags

```dockerfile
# Bad - unpredictable builds
FROM python:latest

# Good - reproducible builds
FROM python:3.12-slim-bookworm
```

### Running as Root

```dockerfile
# Bad - security risk
COPY . /app
CMD ["python", "main.py"]

# Good - principle of least privilege
RUN useradd -r appuser
USER appuser
COPY --chown=appuser . /app
CMD ["python", "main.py"]
```

### Bloated Images

```dockerfile
# Bad - includes build tools in final image
FROM python:3.12
RUN apt-get update && apt-get install -y gcc
RUN pip install numpy

# Good - use slim base or multi-stage
FROM python:3.12-slim-bookworm
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*
```

## Security Scanning

### Using Trivy

```bash
# Scan a local image
trivy image my-app:latest

# Scan with severity filter
trivy image --severity HIGH,CRITICAL my-app:latest

# Exit with error code on findings
trivy image --exit-code 1 --severity CRITICAL my-app:latest
```

### ECR Scanning

```bash
# Enable scanning on push
aws ecr put-image-scanning-configuration \
  --repository-name my-app \
  --image-scanning-configuration scanOnPush=true

# Get scan results
aws ecr describe-image-scan-findings \
  --repository-name my-app \
  --image-id imageTag=latest
```

## Further Reading

- [Docker Official Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [AWS ECR Documentation](https://docs.aws.amazon.com/AmazonECR/latest/userguide/what-is-ecr.html)
- Related skills in this repository:
  - [Docker Compose](../docker-compose/)
  - [GitHub Actions](../github-actions/)
