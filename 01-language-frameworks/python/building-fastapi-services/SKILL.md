---
name: building-fastapi-services
description: Build production-grade FastAPI services with OpenTelemetry, middleware, and best practices. Use when creating async Python web services.
tags: ['python', 'fastapi', 'async', 'api', 'opentelemetry', 'fetch']
---

# FastAPI Application Structure

## Quick Start
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup/shutdown with lifespan context."""
    # Startup: Initialize services
    kafka_service = app.state.kafka = KafkaService()
    await kafka_service.start()
    yield
    # Shutdown: Cleanup resources
    await kafka_service.stop()

def create_app() -> FastAPI:
    app = FastAPI(title="my-service", lifespan=lifespan)
    app.include_router(health_router, prefix="/health")
    FastAPIInstrumentor.instrument_app(app)  # OpenTelemetry
    return app
```

## Key Points
- Use `lifespan` context manager for startup/shutdown (replaces deprecated `on_event`)
- Always include `/health` endpoint for ECS health checks
- Instrument with OpenTelemetry using `FastAPIInstrumentor.instrument_app(app)`
- Disable `/docs` in production: `docs_url="/docs" if env != "prod" else None`
- Use dependency injection for services instead of global state

## Common Mistakes
1. **Using deprecated `@app.on_event("startup")`** - Use `lifespan` context manager instead (FastAPI 0.109+)
2. **Missing health check endpoint** - ECS requires `/health` for container health monitoring
3. **Not instrumenting with OpenTelemetry** - All Fetch services must have distributed tracing
4. **Exposing /docs in production** - Disable Swagger docs in prod to prevent information disclosure
5. **Blocking I/O in async handlers** - Use `await` for all I/O operations (DB, HTTP, Kafka)

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
