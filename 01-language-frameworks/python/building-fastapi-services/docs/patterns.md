# Code Patterns: Building FastAPI Services

## Pattern 1: Complete Production Application with Lifespan

**When to Use:** Starting a new FastAPI service that needs startup/shutdown lifecycle management, OpenTelemetry tracing, and health checks.

```python
# src/main.py
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from src.config import get_settings
from src.router import health, api_v1
from src.services.kafka_consumer import KafkaConsumerService
from src.middleware import request_id_middleware
from src.exception_handlers import setup_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Manage application lifecycle."""
    # Startup
    settings = get_settings()

    # Initialize services
    kafka_service = KafkaConsumerService(settings)
    await kafka_service.start()
    app.state.kafka = kafka_service

    yield

    # Shutdown
    await kafka_service.stop()


def create_app() -> FastAPI:
    """Create FastAPI application with all middleware and routes."""
    settings = get_settings()

    app = FastAPI(
        title=settings.service_name,
        version=settings.version,
        lifespan=lifespan,
        docs_url="/docs" if settings.environment != "prod" else None,
    )

    # Middleware (order matters!)
    app.middleware("http")(request_id_middleware)  # First: inject request ID
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    setup_exception_handlers(app)

    # Routes
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(api_v1.router, prefix="/api/v1", tags=["api"])

    # OpenTelemetry instrumentation (must be last!)
    FastAPIInstrumentor.instrument_app(app)

    return app


app = create_app()
```

**Pitfalls:**
- **Using `@app.on_event("startup")`** - Deprecated in FastAPI 0.109+, use `lifespan` instead
- **Instrumenting before adding middleware** - OpenTelemetry should be last to capture all middleware spans
- **Not handling startup failures** - Use try/except in lifespan to prevent container restarts

---

## Pattern 2: Health Check Endpoints for ECS

**When to Use:** Deploying to ECS, which requires health checks for target group routing and container lifecycle.

```python
# src/router/health.py
from fastapi import APIRouter, HTTPException, Depends
from src.config import Settings, get_settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic liveness check for ECS health monitoring."""
    return {"status": "healthy"}


@router.get("/health/ready")
async def readiness_check(settings: Settings = Depends(get_settings)):
    """
    Deep health check for readiness probes.
    Checks critical dependencies (DB, Kafka, external APIs).
    """
    checks = {}

    try:
        # Check Kafka connection
        kafka_client = app.state.kafka
        checks["kafka"] = "healthy" if kafka_client.is_connected() else "unhealthy"

        # Check DynamoDB
        dynamodb = app.state.dynamodb
        await dynamodb.describe_table(TableName=settings.dynamodb_table)
        checks["dynamodb"] = "healthy"

    except Exception as e:
        checks["error"] = str(e)
        raise HTTPException(status_code=503, detail=checks)

    return {"status": "ready", "checks": checks}


@router.get("/health/version")
async def version_info(settings: Settings = Depends(get_settings)):
    """Return service version for deployments."""
    return {
        "version": settings.version,
        "service": settings.service_name,
        "environment": settings.environment,
    }
```

**Configuration in FSD YAML:**
```yaml
health_check:
  path: /health
  interval: 30
  timeout: 5
  healthy_threshold: 2
  unhealthy_threshold: 3
```

**Pitfalls:**
- **Expensive checks in `/health`** - Keep basic liveness check fast (<100ms), use `/health/ready` for deep checks
- **Not returning 503 on failure** - ECS needs HTTP 503 to mark container unhealthy
- **Checking all dependencies** - Only check critical dependencies; optional services shouldn't fail health check

---

## Pattern 3: Request ID Middleware for Distributed Tracing

**When to Use:** Need to trace requests across multiple services (API → Worker → Database) using correlation IDs.

```python
# src/middleware.py
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


async def request_id_middleware(request: Request, call_next):
    """
    Inject X-Request-ID header for tracing.
    Propagates existing request ID or generates new one.
    """
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


# Usage in handlers
from fastapi import Request

@router.post("/process")
async def process_data(request: Request, data: InputModel):
    request_id = request.state.request_id
    logger.info("Processing data", request_id=request_id, data=data)
    # ... business logic
```

**Pitfalls:**
- **Not propagating request ID to downstream services** - Pass `X-Request-ID` in HTTP headers to external APIs
- **Overwriting OpenTelemetry trace ID** - Use both; request ID is user-facing, trace ID is for observability backend
- **Forgetting to add to logs** - Include request_id in every log message for correlation

---

## Pattern 4: Dependency Injection for Services

**When to Use:** Testing services with mocks, avoiding global state, managing service lifecycle.

```python
# src/services/user_service.py
from src.client.dynamodb_client import DynamoDBClient
from src.model.user import User


class UserService:
    def __init__(self, db_client: DynamoDBClient):
        self.db = db_client

    async def get_user(self, user_id: str) -> User:
        item = await self.db.get_item(
            TableName="users",
            Key={"user_id": user_id}
        )
        return User(**item)


# Dependency provider
def get_user_service(
    db_client: DynamoDBClient = Depends(get_dynamodb_client)
) -> UserService:
    return UserService(db_client)


# Usage in endpoint
from fastapi import Depends

@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_user(user_id)
    return user
```

**Testing with Dependency Override:**
```python
# tests/test_users.py
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

def test_get_user():
    # Mock service
    mock_service = AsyncMock(spec=UserService)
    mock_service.get_user.return_value = User(user_id="123", name="Test")

    # Override dependency
    app.dependency_overrides[get_user_service] = lambda: mock_service

    client = TestClient(app)
    response = client.get("/users/123")

    assert response.status_code == 200
    assert response.json()["name"] == "Test"
```

**Pitfalls:**
- **Creating service instances per request** - Cache expensive services (DB pools) in `app.state` during lifespan
- **Not using `Depends()` for testing** - Global singletons can't be mocked; always use dependency injection
- **Circular dependencies** - Structure dependencies in layers (handlers → services → clients)

---

## Pattern 5: Structured Exception Handling

**When to Use:** Converting internal exceptions to user-friendly API errors with proper status codes.

```python
# src/exceptions.py
class ServiceException(Exception):
    """Base exception for all service errors."""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundError(ServiceException):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            message=f"{resource} not found",
            status_code=404,
            details={"resource": resource, "id": resource_id}
        )


class ValidationError(ServiceException):
    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"Validation error: {field}",
            status_code=400,
            details={"field": field, "error": message}
        )


# src/exception_handlers.py
from fastapi import Request
from fastapi.responses import JSONResponse
from src.exceptions import ServiceException


def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(ServiceException)
    async def service_exception_handler(request: Request, exc: ServiceException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "details": exc.details,
                "request_id": request.state.request_id,
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception", request_id=request.state.request_id)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "request_id": request.state.request_id,
            }
        )
```

**Usage:**
```python
@router.get("/users/{user_id}")
async def get_user(user_id: str, service: UserService = Depends(get_user_service)):
    user = await service.get_user(user_id)
    if not user:
        raise NotFoundError(resource="User", resource_id=user_id)
    return user
```

**Pitfalls:**
- **Returning 500 for validation errors** - Use 400 for client errors, 500 for server errors
- **Leaking internal details in prod** - Sanitize exception messages; log full details but return generic errors
- **Not including request ID** - Always return request_id in error responses for debugging

---

## Pattern 6: Running with Gunicorn + Uvicorn

**When to Use:** Deploying FastAPI to production (ECS, EC2) with multiple worker processes.

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir poetry && poetry install --no-dev

COPY src/ ./src/

CMD ["gunicorn", "src.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

**Worker Sizing:**
```python
# For CPU-bound work (rare in FastAPI):
workers = (2 * cpu_count) + 1

# For I/O-bound async work (recommended):
workers = cpu_count

# For mixed workloads:
workers = cpu_count + 1
```

**Pitfalls:**
- **Using too many workers** - More workers ≠ better performance for async apps; stick to CPU count
- **Not setting graceful timeout** - Give in-flight requests time to finish before SIGKILL
- **Using Uvicorn alone in prod** - Gunicorn provides process management and zero-downtime restarts

---

## References

- [FastAPI Official Docs - Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)
- [FastAPI Best Practices GitHub](https://github.com/zhanymkanov/fastapi-best-practices)
- [FastAPI Production Deployment](https://render.com/articles/fastapi-production-deployment-best-practices)
- Fetch services: ereceipt-ml-submitter, anomaly-detection-service, rover-mcp
