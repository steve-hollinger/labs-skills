# Core Concepts: Containerizing Python Services

## What

Docker containerization for Python FastAPI services involves creating optimized images for ECS deployment. Key components:
- **Multi-stage builds** - Separate build and runtime stages to reduce image size
- **uv package manager** - Fast dependency installation (5-10x faster than pip)
- **Non-root user** - Security requirement for ECS (UID 1000)
- **Health checks** - ECS health monitoring via HEALTHCHECK directive
- **Gunicorn + Uvicorn** - Production server with worker processes

At Fetch, all Python services run in Docker containers on ECS Fargate, requiring standardized Dockerfiles that balance image size, build speed, and security.

## Why

**Problem**: Default Python Docker images are:
- Too large (1-2 GB) due to unnecessary build tools
- Insecure (running as root)
- Slow to build (pip is single-threaded)
- Missing health checks for ECS

**Solution**: Optimized Dockerfiles provide:
- **Smaller images** - Multi-stage builds reduce size by 50-70%
- **Faster builds** - uv parallelizes dependency installation
- **Security** - Non-root user prevents privilege escalation
- **Reliability** - Health checks ensure ECS routes to healthy containers

**Context at Fetch**:
- 100+ Python services deployed to ECS
- Standard stack: Python 3.11-slim base, uv for deps, Gunicorn+Uvicorn
- Average image size: 200-400 MB (vs 1-2 GB without optimization)
- Build time: 2-4 minutes (vs 8-12 minutes with pip)
- Security: All containers run as UID 1000, not root

## How

### Multi-Stage Build Architecture

```
┌──────────────────────────────────────┐
│   Stage 1: Builder                   │
│   - python:3.11-slim                 │
│   - Install uv                       │
│   - Install build tools (gcc, g++)  │
│   - Create virtual environment       │
│   - Install dependencies             │
└──────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│   Stage 2: Runtime                   │
│   - python:3.11-slim (fresh)         │
│   - Copy venv from builder           │
│   - Copy source code                 │
│   - Create non-root user             │
│   - Set health check                 │
│   - Configure Gunicorn               │
└──────────────────────────────────────┘
```

### Layer Optimization

Docker caches layers, so order matters for fast rebuilds:

```dockerfile
# 1. Base image (rarely changes)
FROM python:3.11-slim

# 2. System dependencies (rarely change)
RUN apt-get update && apt-get install...

# 3. Python dependencies (change occasionally)
COPY pyproject.toml ./
RUN uv pip install...

# 4. Source code (changes frequently)
COPY src/ ./src/
```

### Worker Configuration

For async FastAPI services:
- **Worker count = CPU cores** (not 2×CPU+1)
- **Worker class = UvicornWorker** (async ASGI)
- **Timeout = 120s** (match ECS health check)
- **Graceful timeout = 30s** (allow in-flight requests to finish)

```bash
gunicorn src.main:app \
  --workers 4 \              # 4 vCPU = 4 workers
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --graceful-timeout 30
```

## When to Use

**Use Docker for:**
- All Python services deploying to ECS
- Services requiring consistent environments (dev/stage/prod)
- Services with complex dependencies (ML libraries, native extensions)
- Services needing horizontal scaling

**Alternatives:**
- **Lambda** - For event-driven, short-lived functions (<15 min)
- **Batch** - For long-running batch jobs with specific resource needs
- **EC2** - For legacy services not yet containerized (rare at Fetch)

## Key Terminology

- **Multi-stage build** - Dockerfile with multiple FROM statements, copying artifacts between stages
- **uv** - Rust-based Python package installer, 5-10x faster than pip
- **Gunicorn** - WSGI/ASGI server that manages multiple worker processes
- **UvicornWorker** - Gunicorn worker class for async ASGI apps (FastAPI)
- **HEALTHCHECK** - Docker directive that runs periodic checks, used by ECS for routing
- **Non-root user** - User with UID 1000, required for ECS security policies
- **Layer caching** - Docker reuses unchanged layers from previous builds

## Related Skills

- [building-fastapi-services](../../01-language-frameworks/python/building-fastapi-services/) - FastAPI health checks
- [deploying-fsd-ecs](../deploying-fsd-ecs/) - ECS deployment with FSD
