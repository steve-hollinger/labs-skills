# Core Concepts

## Overview

This document covers the fundamental concepts of Docker containerization and AWS ECR that you need to master for production-ready container deployments.

## Concept 1: Docker Image Layers

### What It Is

Docker images are built in layers. Each instruction in a Dockerfile creates a new layer. Layers are cached and reused, which speeds up builds but also affects image size.

### Why It Matters

Understanding layers helps you:
- Optimize build speed through effective caching
- Reduce image size by minimizing layer count
- Debug build issues by understanding what changed

### How It Works

```dockerfile
# Each instruction creates a layer
FROM python:3.12-slim    # Layer 1: Base image (~120MB)
WORKDIR /app             # Layer 2: Metadata only (~0B)
COPY requirements.txt .  # Layer 3: Single file (~1KB)
RUN pip install -r requirements.txt  # Layer 4: Dependencies (~50MB)
COPY . .                 # Layer 5: Application code (~1MB)
```

Layer caching works from top to bottom. If a layer changes, all subsequent layers must be rebuilt.

```bash
# View layers and their sizes
docker history my-image:latest

# Inspect layer details
docker inspect my-image:latest | jq '.[0].RootFS.Layers'
```

## Concept 2: Multi-Stage Builds

### What It Is

Multi-stage builds use multiple `FROM` statements in a single Dockerfile. Each `FROM` starts a new stage, and you can copy artifacts between stages.

### Why It Matters

- **Smaller final images**: Build tools aren't included in production image
- **Better security**: Fewer packages means smaller attack surface
- **Faster deployments**: Smaller images deploy faster

### How It Works

```dockerfile
# Stage 1: Build
FROM golang:1.22-alpine AS builder
WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o app

# Stage 2: Runtime
FROM alpine:3.19
RUN apk --no-cache add ca-certificates
COPY --from=builder /build/app /app
ENTRYPOINT ["/app"]
```

Size comparison:
- Single stage with Go toolchain: ~800MB
- Multi-stage final image: ~15MB

## Concept 3: Container Security

### What It Is

Container security encompasses practices for building and running secure containers: non-root users, minimal base images, vulnerability scanning, and secrets management.

### Why It Matters

Containers share the host kernel. A compromised container with root access can potentially escape to the host. Security should be designed in, not added later.

### How It Works

```dockerfile
# 1. Use minimal base images
FROM python:3.12-slim-bookworm

# 2. Create and use non-root user
RUN groupadd -r appgroup && \
    useradd -r -g appgroup -d /app -s /sbin/nologin appuser

# 3. Set proper permissions
COPY --chown=appuser:appgroup . /app

# 4. Drop all capabilities (in compose or run)
# docker run --cap-drop=ALL my-image

# 5. Make filesystem read-only where possible
# docker run --read-only my-image

# 6. Switch to non-root user
USER appuser

# 7. Don't store secrets in images
# Use environment variables or secrets managers
```

## Concept 4: ECR Architecture

### What It Is

Amazon Elastic Container Registry (ECR) is a fully managed container registry that stores, manages, and deploys container images.

### Why It Matters

- **Integrated with AWS**: Works seamlessly with ECS, EKS, Lambda
- **Security**: Encryption at rest, IAM authentication, vulnerability scanning
- **High availability**: Replicated across multiple AZs

### How It Works

```
┌─────────────────────────────────────────────────────────┐
│                    AWS Account                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │              ECR Registry                        │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐ │   │
│  │  │ my-app     │  │ api-svc    │  │ worker     │ │   │
│  │  │ Repository │  │ Repository │  │ Repository │ │   │
│  │  │            │  │            │  │            │ │   │
│  │  │ - v1.0.0   │  │ - latest   │  │ - v2.1.0   │ │   │
│  │  │ - v1.1.0   │  │ - v3.0.0   │  │ - v2.1.1   │ │   │
│  │  │ - latest   │  │            │  │            │ │   │
│  │  └────────────┘  └────────────┘  └────────────┘ │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────┐     ┌─────────────┐                   │
│  │    ECS      │     │    EKS      │                   │
│  │   Cluster   │────▶│   Cluster   │                   │
│  └─────────────┘     └─────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

ECR authentication:
```bash
# Get login token (valid for 12 hours)
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789.dkr.ecr.us-east-1.amazonaws.com
```

## Concept 5: Image Tagging Strategy

### What It Is

Image tags identify specific versions of your container image. A tagging strategy ensures you can track, deploy, and rollback versions reliably.

### Why It Matters

- **Reproducibility**: Deploy exactly the same version every time
- **Traceability**: Know which code is running in production
- **Rollback**: Quickly revert to a previous version

### How It Works

```bash
# Semantic versioning
docker tag my-app:latest my-app:1.2.3

# Git SHA for traceability
docker tag my-app:latest my-app:abc123f

# Environment-based
docker tag my-app:latest my-app:staging
docker tag my-app:1.2.3 my-app:production

# Combined strategy (recommended)
docker tag my-app:latest my-app:1.2.3-abc123f
```

Best practices:
- Never rely solely on `latest` tag
- Use immutable tags (version + commit SHA)
- Implement lifecycle policies to clean old images

```bash
# ECR lifecycle policy example
aws ecr put-lifecycle-policy \
  --repository-name my-app \
  --lifecycle-policy-text '{
    "rules": [{
      "rulePriority": 1,
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countUnit": "days",
        "countNumber": 7
      },
      "action": {"type": "expire"}
    }]
  }'
```

## Summary

Key takeaways:
1. **Layers**: Optimize order for caching, minimize layer count
2. **Multi-stage**: Use for compiled languages, keep runtime images minimal
3. **Security**: Non-root users, minimal base images, scan for vulnerabilities
4. **ECR**: Integrated AWS registry with scanning and lifecycle policies
5. **Tagging**: Use semantic versioning + commit SHA for traceability
