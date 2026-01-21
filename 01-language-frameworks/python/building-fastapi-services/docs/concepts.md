# Core Concepts: Building FastAPI Services

## What

FastAPI is an async Python web framework built on Starlette (ASGI) and Pydantic for building high-performance REST APIs. At Fetch, FastAPI is the standard for new Python microservices due to its:
- Native async/await support for I/O-bound workloads (Kafka, DynamoDB, S3)
- Automatic OpenAPI/Swagger documentation generation
- Built-in request/response validation with Pydantic v2
- Excellent integration with OpenTelemetry for distributed tracing

Production-grade FastAPI services require structured startup/shutdown management, middleware stacks, exception handling, and observability.

## Why

**Problem:** Python microservices at Fetch need to handle high throughput while integrating with Kafka, AWS services, and distributed tracing. Synchronous frameworks (Flask, Django) block the event loop, limiting concurrency.

**Solution:** FastAPI's async architecture allows services to handle thousands of concurrent requests with minimal resource usage. Combined with Fetch's standard stack (OpenTelemetry, Pydantic v2, aiokafka), it provides:
- **Concurrency** - Non-blocking I/O for Kafka consumers, DynamoDB queries, S3 uploads
- **Type Safety** - Pydantic models catch validation errors at API boundaries
- **Observability** - Automatic span generation for all requests
- **Developer Experience** - Auto-generated interactive docs, editor autocomplete

**Context at Fetch:**
- 15+ FastAPI services in production (ereceipt-ml-submitter, anomaly-detection-service, rover-mcp)
- Deployed to ECS via FSD with Gunicorn + Uvicorn workers
- All services integrate with MSK (Kafka), DynamoDB, and OTLP collectors
- Standard ports: 8000 (HTTP), 8080 (metrics), health checks on `/health`

## How

### Architecture Layers

```
┌──────────────────────────────────────────────┐
│         FastAPI Application (ASGI)           │
├──────────────────────────────────────────────┤
│  Middleware Stack                            │
│  - Request ID injection                      │
│  - CORS handling                             │
│  - OpenTelemetry auto-instrumentation        │
├──────────────────────────────────────────────┤
│  Routers (Endpoints)                         │
│  - /health  (ECS health checks)              │
│  - /metrics (Prometheus)                     │
│  - /api/v1/* (Business logic)                │
├──────────────────────────────────────────────┤
│  Dependency Injection                        │
│  - Settings (Pydantic)                       │
│  - Services (Kafka, DynamoDB, S3)            │
│  - Clients (HTTP, gRPC)                      │
├──────────────────────────────────────────────┤
│  Lifespan Management                         │
│  - Startup: Initialize connections           │
│  - Shutdown: Graceful cleanup                │
└──────────────────────────────────────────────┘
```

### Key Design Patterns

1. **Lifespan Context Manager** (FastAPI 0.109+)
   - Replaces deprecated `@app.on_event("startup"/"shutdown")`
   - Uses `@asynccontextmanager` for resource management
   - Ensures cleanup even if startup fails

2. **Dependency Injection**
   - Use `Depends()` for settings, database connections, services
   - Enables easy mocking in tests
   - Avoids global state

3. **Middleware Stack**
   - Request ID: Propagate `X-Request-ID` for tracing
   - CORS: Configure allowed origins for frontend access
   - Error handlers: Catch exceptions and return structured errors

4. **OpenTelemetry Integration**
   - `FastAPIInstrumentor.instrument_app(app)` adds automatic spans
   - Captures request/response details, timing, errors
   - Exports to OTLP gRPC collectors (Fetch's Grafana/Tempo)

### Best Practices from Fetch

- **Worker Configuration** (Gunicorn + Uvicorn)
  ```bash
  gunicorn src.main:app \
    --workers 4 \                    # CPU count (not 2×CPU+1 for async)
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \                  # Match ECS health check timeout
    --graceful-timeout 30            # Allow in-flight requests to finish
  ```

- **Health Check Endpoint**
  ```python
  @router.get("/health")
  async def health_check():
      return {"status": "healthy", "version": settings.version}
  ```
  - ECS target groups require HTTP 200 from `/health` every 30s
  - Should check critical dependencies (DB, Kafka) in `/health/ready`

- **Structured Logging**
  - Use `structlog` with JSON formatting
  - Include `request_id`, `service_name`, `environment` in all logs
  - Correlate logs with traces using trace IDs

## When to Use

**Use FastAPI when:**
- Building new REST APIs or microservices at Fetch
- Service needs async I/O (Kafka, DynamoDB, S3, external APIs)
- You want automatic request/response validation with Pydantic
- Service requires high concurrency (>100 requests/sec)
- You need auto-generated OpenAPI docs for internal consumers

**Avoid FastAPI when:**
- Building synchronous batch jobs or CLI tools (use plain Python)
- Service is CPU-bound (image processing, ML inference) - consider Lambda or Batch
- You need WebSockets or long-lived connections (use Starlette directly)
- Team lacks async Python experience (but this is rare at Fetch)

## Key Terminology

- **ASGI** (Asynchronous Server Gateway Interface) - Python standard for async web frameworks, like WSGI for Flask/Django
- **Lifespan** - Context manager that runs code on startup/shutdown, replacing `on_event` hooks
- **Dependency Injection** - FastAPI's `Depends()` system for providing services to endpoints
- **OpenAPI Schema** - Auto-generated API specification accessible at `/docs` (Swagger UI) and `/redoc`
- **Middleware** - Functions that process requests/responses globally before reaching endpoints
- **Uvicorn** - ASGI server that runs FastAPI apps (like Gunicorn but for async)
- **Gunicorn** - Process manager that spawns multiple Uvicorn workers for production
- **FastAPIInstrumentor** - OpenTelemetry library that auto-instruments FastAPI apps with traces

## Related Skills

- [managing-pydantic-settings](../../managing-pydantic-settings/) - Configuration management
- [instrumenting-opentelemetry](../../instrumenting-opentelemetry/) - Distributed tracing
- [handling-structured-errors](../../handling-structured-errors/) - Exception handling
- [consuming-kafka-aiokafka](../../consuming-kafka-aiokafka/) - Kafka integration
- [containerizing-python-services](../../../04-devops-deployment/containerizing-python-services/) - Docker builds
- [deploying-fsd-ecs](../../../04-devops-deployment/deploying-fsd-ecs/) - ECS deployment
