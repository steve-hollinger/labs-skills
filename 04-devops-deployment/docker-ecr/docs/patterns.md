# Common Patterns

## Overview

This document covers common patterns and best practices for Docker containerization and ECR workflows.

## Pattern 1: Optimized Python Image

### When to Use

For any Python application that needs to be containerized for production.

### Implementation

```dockerfile
# Use specific slim version
FROM python:3.12-slim-bookworm AS base

# Prevent Python from writing bytecode and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user
RUN groupadd -r appgroup && \
    useradd -r -g appgroup -d /app -s /sbin/nologin appuser

WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Example

```python
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "healthy"}
```

### Pitfalls to Avoid

- Don't use `python:3.12` (full image is 1GB+, slim is ~150MB)
- Don't forget `--no-cache-dir` for pip
- Don't run as root in production

## Pattern 2: Distroless Go Image

### When to Use

For Go applications where you want the smallest possible image with minimal attack surface.

### Implementation

```dockerfile
# Build stage
FROM golang:1.22-alpine AS builder

# Install CA certificates for HTTPS
RUN apk --no-cache add ca-certificates

WORKDIR /build

# Download dependencies first (better caching)
COPY go.mod go.sum ./
RUN go mod download

# Copy source and build
COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build -ldflags="-s -w" -o /app

# Runtime stage using distroless
FROM gcr.io/distroless/static-debian12

# Copy CA certs from builder
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Copy binary
COPY --from=builder /app /app

ENTRYPOINT ["/app"]
```

### Example

```go
// main.go
package main

import (
    "net/http"
    "encoding/json"
)

func main() {
    http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        json.NewEncoder(w).Encode(map[string]string{"status": "healthy"})
    })
    http.ListenAndServe(":8080", nil)
}
```

### Pitfalls to Avoid

- Don't forget CA certificates if making HTTPS calls
- Don't use `FROM scratch` if you need timezone data or DNS resolution
- Always use `-ldflags="-s -w"` to strip debug info

## Pattern 3: Node.js Production Image

### When to Use

For Node.js applications that need production hardening.

### Implementation

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application
COPY . .

# Runtime stage
FROM node:20-alpine AS runtime

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

WORKDIR /app

# Copy from builder
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app .

USER nodejs

EXPOSE 3000

# Use dumb-init as PID 1
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]
```

### Pitfalls to Avoid

- Don't use `npm install` in production (use `npm ci`)
- Don't skip `dumb-init` or `tini` for proper signal handling
- Don't include dev dependencies in production

## Pattern 4: ECR CI/CD Push Script

### When to Use

For automated builds that push to ECR from CI/CD pipelines.

### Implementation

```bash
#!/bin/bash
set -euo pipefail

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
IMAGE_NAME="${IMAGE_NAME:?IMAGE_NAME required}"
VERSION="${VERSION:-$(git describe --tags --always)}"

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Authenticate to ECR
echo "Authenticating to ECR..."
aws ecr get-login-password --region "${AWS_REGION}" | \
    docker login --username AWS --password-stdin "${ECR_REGISTRY}"

# Create repository if it doesn't exist
echo "Ensuring repository exists..."
aws ecr describe-repositories --repository-names "${IMAGE_NAME}" 2>/dev/null || \
    aws ecr create-repository \
        --repository-name "${IMAGE_NAME}" \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256

# Build image
echo "Building image..."
docker build \
    --build-arg VERSION="${VERSION}" \
    --build-arg BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    -t "${IMAGE_NAME}:${VERSION}" \
    -t "${IMAGE_NAME}:latest" \
    .

# Tag for ECR
docker tag "${IMAGE_NAME}:${VERSION}" "${ECR_REGISTRY}/${IMAGE_NAME}:${VERSION}"
docker tag "${IMAGE_NAME}:latest" "${ECR_REGISTRY}/${IMAGE_NAME}:latest"

# Push to ECR
echo "Pushing to ECR..."
docker push "${ECR_REGISTRY}/${IMAGE_NAME}:${VERSION}"
docker push "${ECR_REGISTRY}/${IMAGE_NAME}:latest"

echo "Successfully pushed ${ECR_REGISTRY}/${IMAGE_NAME}:${VERSION}"
```

## Pattern 5: .dockerignore for Efficient Builds

### When to Use

Always. Every project should have a `.dockerignore` file.

### Implementation

```dockerignore
# Version control
.git
.gitignore

# IDE
.idea
.vscode
*.swp
*.swo

# Dependencies (will be installed in container)
node_modules
vendor
__pycache__
*.pyc
.venv
venv

# Build artifacts
dist
build
*.egg-info

# Test and coverage
.pytest_cache
.coverage
coverage
htmlcov

# Documentation
docs
*.md
!README.md

# Environment and secrets
.env
.env.*
*.pem
*.key

# Docker
Dockerfile*
docker-compose*
.docker

# CI/CD
.github
.gitlab-ci.yml
Jenkinsfile

# Misc
.DS_Store
Thumbs.db
*.log
```

## Anti-Patterns

### Anti-Pattern 1: Installing and Removing in Separate Layers

```dockerfile
# Bad - deleted files still exist in earlier layer
RUN apt-get update && apt-get install -y gcc
RUN pip install cryptography
RUN apt-get remove -y gcc && apt-get autoremove -y
```

### Better Approach

```dockerfile
# Good - install, use, and clean in single layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    pip install cryptography && \
    apt-get remove -y gcc && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*
```

### Anti-Pattern 2: COPY . . Before Installing Dependencies

```dockerfile
# Bad - any source change invalidates cache
COPY . .
RUN pip install -r requirements.txt
```

### Better Approach

```dockerfile
# Good - dependencies cached separately
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Python web app | Pattern 1: Optimized Python Image |
| Go microservice | Pattern 2: Distroless Go Image |
| Node.js API | Pattern 3: Node.js Production Image |
| CI/CD deployment | Pattern 4: ECR Push Script |
| Any Docker build | Pattern 5: .dockerignore |
