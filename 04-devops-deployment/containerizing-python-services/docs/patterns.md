# Code Patterns: Containerizing Python Services

## Pattern 1: Multi-Stage Build for Production

**When to Use:** Deploying Python FastAPI services to ECS with minimal image size and fast build times.

```dockerfile
# Multi-stage Dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml ./

# Create venv and install dependencies
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install --no-cache .

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src/ ./src/

# Create non-root user (ECS requirement)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Health check for ECS
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

EXPOSE 8000

# Run with Gunicorn + Uvicorn workers
CMD ["gunicorn", "src.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

**Image Size Comparison:**
- Single-stage with pip: ~1.2 GB
- Single-stage with uv: ~800 MB
- Multi-stage with uv: ~350 MB (70% reduction!)

**Pitfalls:**
- **Copying entire project directory** - Only copy `pyproject.toml` and `src/`, not `.git/`, `tests/`, etc.
- **Installing dev dependencies** - Use `uv pip install .` without `--dev` flag
- **Not using curl alternative** - ECS doesn't include curl in slim images; use Python's urllib for health checks

---

## Pattern 2: Optimized Layer Caching

**When to Use:** Speeding up Docker builds during development by maximizing layer cache reuse.

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Layer 1: System dependencies (rarely change)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*  # Clean apt cache

# Layer 2: Install uv (rarely changes)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Layer 3: Python dependencies (change occasionally)
COPY pyproject.toml ./
RUN uv pip install --system --no-cache .

# Layer 4: Application code (changes frequently)
COPY src/ ./src/

# Layer 5: User setup (never changes)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["gunicorn", "src.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
```

**Build Time Comparison:**
- Full rebuild: ~3-4 minutes
- Code-only change (layer 4 cached): ~15 seconds
- Dependency change (layers 1-3 cached): ~1 minute

**Pitfalls:**
- **Combining layers** - Don't combine dependency install and code copy in one layer
- **Not cleaning package caches** - Always add `rm -rf /var/lib/apt/lists/*` after apt-get
- **Copying before installing** - Copy `pyproject.toml` before code to cache dependency layer

---

## Pattern 3: Health Check with FastAPI Integration

**When to Use:** Ensuring ECS can properly monitor container health and route traffic.

```dockerfile
FROM python:3.11-slim

# ... (base image setup)

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml ./
RUN uv pip install --system --no-cache .
COPY src/ ./src/

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Health check using Python (no curl needed)
HEALTHCHECK --interval=30s \           # Check every 30 seconds
            --timeout=3s \             # 3 second timeout
            --start-period=5s \        # Allow 5 seconds for app startup
            --retries=3 \              # 3 failures = unhealthy
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

EXPOSE 8000

CMD ["gunicorn", "src.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
```

**FastAPI Health Endpoint:**
```python
# src/router/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Simple health check for ECS."""
    return {"status": "healthy"}
```

**ECS Health Check Configuration (FSD YAML):**
```yaml
healthCheck:
  path: /health
  interval: 30
  timeout: 5
  healthyThreshold: 2
  unhealthyThreshold: 3
```

**Pitfalls:**
- **Using curl in slim images** - Install curl or use Python's urllib for health checks
- **Expensive health checks** - Keep health check endpoint fast (<100ms); don't check databases
- **Wrong port** - Health check must target same port as application (8000)

---

## Pattern 4: .dockerignore for Faster Builds

**When to Use:** Reducing build context size and preventing sensitive files from being copied.

```
# .dockerignore
# Version control
.git
.gitignore

# Python artifacts
__pycache__
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.hypothesis/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment files (contains secrets!)
.env
.env.local
.env.*.local

# Documentation
docs/
*.md
!README.md

# CI/CD
.github/
.gitlab-ci.yml

# Logs
*.log
logs/

# OS files
.DS_Store
Thumbs.db
```

**Build Context Size:**
- Without .dockerignore: ~50-100 MB
- With .dockerignore: ~5-10 MB (90% reduction!)

**Pitfalls:**
- **Not ignoring .git/** - Git history adds 10-50 MB to build context
- **Copying .env files** - Never copy .env files with secrets into Docker images
- **Ignoring necessary files** - Don't ignore `README.md` or `pyproject.toml`

---

## Pattern 5: Development vs Production Dockerfile

**When to Use:** Different requirements for local development (hot reload) vs production (optimized).

**Dockerfile.dev (Development)**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies (including dev dependencies)
COPY pyproject.toml ./
RUN uv pip install --system --no-cache --dev .

# Copy source code
COPY src/ ./src/

# Run with hot reload
CMD ["uvicorn", "src.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--reload"]
```

**Dockerfile (Production)**
```dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml ./

RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install --no-cache .

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

ENV PATH="/app/.venv/bin:$PATH"

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

EXPOSE 8000

CMD ["gunicorn", "src.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
```

**Docker Compose for Development:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src  # Mount source for hot reload
    environment:
      - ENVIRONMENT=dev
      - KAFKA_BROKERS=kafka:9092
```

**Pitfalls:**
- **Using --reload in production** - Hot reload uses more memory and is slower
- **Running as root in development** - Maintain consistency; use non-root user everywhere
- **Not mounting volumes in dev** - Mount `./src` for hot reload during development

---

## Build and Push Workflow

```bash
# Build image
docker build -t my-service:latest .

# Tag for ECR
docker tag my-service:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-service:latest

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Push to ECR
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-service:latest

# Deploy with FSD
fsd deploy --env prod --file my-service.yml --image 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-service:latest
```

## References

- [FastAPI Docker Best Practices](https://betterstack.com/community/guides/scaling-python/fastapi-docker-best-practices/)
- [Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [uv Package Manager](https://github.com/astral-sh/uv)
- [Docker HEALTHCHECK](https://docs.docker.com/engine/reference/builder/#healthcheck)
