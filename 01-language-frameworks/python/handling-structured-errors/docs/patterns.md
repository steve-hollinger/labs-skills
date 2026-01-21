# Code Patterns: Structured Error Handling

## Pattern 1: Custom Exception Hierarchy with Correlation IDs

**When to Use:** Create a custom exception hierarchy for FastAPI services that need distributed tracing across multiple microservices. Use when you need to distinguish between different error types (validation, not found, authentication) and propagate correlation IDs through the call chain.

```python
# src/exceptions.py
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4


class ServiceError(Exception):
    """Base exception for all service errors with correlation ID."""

    def __init__(
        self,
        message: str,
        error_code: str,
        correlation_id: Optional[UUID] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.correlation_id = correlation_id or uuid4()
        self.context = context or {}
        self.timestamp = datetime.utcnow()
        super().__init__(self.message)


class ValidationError(ServiceError):
    """Input validation failed."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        correlation_id: Optional[UUID] = None,
    ):
        context = {"field": field} if field else {}
        super().__init__(message, "VALIDATION_ERROR", correlation_id, context)


class ResourceNotFoundError(ServiceError):
    """Requested resource not found."""

    def __init__(
        self,
        resource: str,
        resource_id: str,
        correlation_id: Optional[UUID] = None,
    ):
        context = {"resource": resource, "resource_id": resource_id}
        message = f"{resource} {resource_id} not found"
        super().__init__(message, "NOT_FOUND", correlation_id, context)


class AuthenticationError(ServiceError):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication required", correlation_id: Optional[UUID] = None):
        super().__init__(message, "AUTH_ERROR", correlation_id)


class AuthorizationError(ServiceError):
    """User lacks permission for requested operation."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        required_permission: Optional[str] = None,
        correlation_id: Optional[UUID] = None,
    ):
        context = {"required_permission": required_permission} if required_permission else {}
        super().__init__(message, "FORBIDDEN", correlation_id, context)


class ExternalServiceError(ServiceError):
    """External service call failed."""

    def __init__(
        self,
        service_name: str,
        message: str,
        correlation_id: Optional[UUID] = None,
    ):
        context = {"service_name": service_name}
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", correlation_id, context)


# Usage in service layer
from typing import Optional
from uuid import UUID


class RewardService:
    def get_reward(self, reward_id: str, correlation_id: Optional[UUID] = None) -> dict:
        """Get reward by ID with correlation tracking."""
        reward = self.repo.get_by_id(reward_id)
        if not reward:
            raise ResourceNotFoundError("Reward", reward_id, correlation_id)
        return reward

    def validate_reward_request(self, data: dict, correlation_id: Optional[UUID] = None):
        """Validate reward request data."""
        if not data.get("amount") or data["amount"] <= 0:
            raise ValidationError(
                "Reward amount must be positive",
                field="amount",
                correlation_id=correlation_id,
            )
        if not data.get("user_id"):
            raise ValidationError(
                "User ID is required",
                field="user_id",
                correlation_id=correlation_id,
            )
```

**Pitfalls:**
- Forgetting to pass correlation_id through the call chain breaks distributed tracing - always accept and propagate it
- Using generic Exception instead of specific exception types loses the ability to handle errors differently
- Not including context dict makes debugging harder - add relevant data like IDs, field names, or service names
- Creating too many exception classes - only create classes for distinct error scenarios that need different handling

## Pattern 2: FastAPI Exception Handlers with Request IDs

**When to Use:** Register FastAPI exception handlers to convert Python exceptions into structured JSON responses with correlation IDs. Use when building REST APIs that need consistent error response formats, proper HTTP status codes, and distributed tracing support.

```python
# src/exception_handlers.py
import logging
from typing import Any, Dict
from uuid import UUID, uuid4

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from opentelemetry import trace

from src.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ExternalServiceError,
    ResourceNotFoundError,
    ServiceError,
    ValidationError,
)
from src.models.api_models import ErrorResponse

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


def get_correlation_id(request: Request) -> UUID:
    """Extract correlation ID from request headers or generate new one."""
    correlation_id_header = request.headers.get("X-Correlation-ID")
    if correlation_id_header:
        try:
            return UUID(correlation_id_header)
        except ValueError:
            logger.warning(f"Invalid correlation ID format: {correlation_id_header}")
    return uuid4()


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle validation errors with 400 Bad Request."""
    correlation_id = exc.correlation_id or get_correlation_id(request)

    # Add to OpenTelemetry span
    span = trace.get_current_span()
    span.set_attribute("error.type", "validation")
    span.set_attribute("correlation_id", str(correlation_id))

    logger.warning(
        "Validation error",
        extra={
            "correlation_id": str(correlation_id),
            "path": request.url.path,
            "error_code": exc.error_code,
            "context": exc.context,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error=exc.error_code,
            message=exc.message,
            correlation_id=str(correlation_id),
            timestamp=exc.timestamp.isoformat(),
            context=exc.context,
        ).model_dump(),
        headers={"X-Correlation-ID": str(correlation_id)},
    )


async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError) -> JSONResponse:
    """Handle resource not found with 404."""
    correlation_id = exc.correlation_id or get_correlation_id(request)

    span = trace.get_current_span()
    span.set_attribute("error.type", "not_found")
    span.set_attribute("correlation_id", str(correlation_id))

    logger.info(
        "Resource not found",
        extra={
            "correlation_id": str(correlation_id),
            "path": request.url.path,
            "context": exc.context,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse(
            error=exc.error_code,
            message=exc.message,
            correlation_id=str(correlation_id),
            timestamp=exc.timestamp.isoformat(),
            context=exc.context,
        ).model_dump(),
        headers={"X-Correlation-ID": str(correlation_id)},
    )


async def authentication_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
    """Handle authentication errors with 401."""
    correlation_id = exc.correlation_id or get_correlation_id(request)

    span = trace.get_current_span()
    span.set_attribute("error.type", "authentication")
    span.set_attribute("correlation_id", str(correlation_id))

    logger.warning(
        "Authentication failed",
        extra={"correlation_id": str(correlation_id), "path": request.url.path},
    )

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=ErrorResponse(
            error=exc.error_code,
            message=exc.message,
            correlation_id=str(correlation_id),
            timestamp=exc.timestamp.isoformat(),
        ).model_dump(),
        headers={"X-Correlation-ID": str(correlation_id)},
    )


async def authorization_error_handler(request: Request, exc: AuthorizationError) -> JSONResponse:
    """Handle authorization errors with 403."""
    correlation_id = exc.correlation_id or get_correlation_id(request)

    span = trace.get_current_span()
    span.set_attribute("error.type", "authorization")
    span.set_attribute("correlation_id", str(correlation_id))

    logger.warning(
        "Authorization failed",
        extra={
            "correlation_id": str(correlation_id),
            "path": request.url.path,
            "context": exc.context,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=ErrorResponse(
            error=exc.error_code,
            message=exc.message,
            correlation_id=str(correlation_id),
            timestamp=exc.timestamp.isoformat(),
            context=exc.context,
        ).model_dump(),
        headers={"X-Correlation-ID": str(correlation_id)},
    )


async def service_error_handler(request: Request, exc: ServiceError) -> JSONResponse:
    """Handle generic service errors with 500."""
    correlation_id = exc.correlation_id or get_correlation_id(request)

    span = trace.get_current_span()
    span.set_attribute("error.type", "service")
    span.set_attribute("correlation_id", str(correlation_id))

    logger.error(
        "Service error",
        extra={
            "correlation_id": str(correlation_id),
            "error_code": exc.error_code,
            "path": request.url.path,
            "context": exc.context,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error=exc.error_code,
            message=exc.message,
            correlation_id=str(correlation_id),
            timestamp=exc.timestamp.isoformat(),
        ).model_dump(),
        headers={"X-Correlation-ID": str(correlation_id)},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all uncaught exceptions with 500."""
    correlation_id = get_correlation_id(request)

    span = trace.get_current_span()
    span.set_attribute("error.type", "unhandled")
    span.set_attribute("correlation_id", str(correlation_id))
    span.record_exception(exc)

    logger.exception(
        "Unhandled exception",
        extra={
            "correlation_id": str(correlation_id),
            "path": request.url.path,
            "exception_type": type(exc).__name__,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="INTERNAL_ERROR",
            message="An unexpected error occurred",
            correlation_id=str(correlation_id),
        ).model_dump(),
        headers={"X-Correlation-ID": str(correlation_id)},
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with FastAPI."""
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(ResourceNotFoundError, resource_not_found_handler)
    app.add_exception_handler(AuthenticationError, authentication_error_handler)
    app.add_exception_handler(AuthorizationError, authorization_error_handler)
    app.add_exception_handler(ExternalServiceError, service_error_handler)
    app.add_exception_handler(ServiceError, service_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
```

**Pitfalls:**
- Not returning correlation ID in response headers makes it hard for clients to report errors
- Missing OpenTelemetry span attributes breaks the link between logs and traces
- Using wrong log levels (error for 404, info for 500) pollutes logs and breaks alerting
- Exposing internal error details in messages leaks implementation - use generic messages for 500 errors
- Order matters when registering handlers - put specific exceptions before generic ServiceError base class

## Pattern 3: Error Response Models with Pydantic

**When to Use:** Define Pydantic models for error responses to ensure consistent JSON structure across all API endpoints. Use when building APIs that need typed, validated error responses that clients can parse reliably.

```python
# src/models/api_models.py
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standardized error response model."""

    error: str = Field(..., description="Error code identifying the error type")
    message: str = Field(..., description="Human-readable error message")
    correlation_id: str = Field(..., description="Unique ID for tracing this request")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="ISO 8601 timestamp")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional error context")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "VALIDATION_ERROR",
                "message": "Reward amount must be positive",
                "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2024-01-20T10:30:00.000Z",
                "context": {"field": "amount"},
            }
        }


class ValidationErrorDetail(BaseModel):
    """Detailed validation error for specific field."""

    field: str = Field(..., description="Field name that failed validation")
    message: str = Field(..., description="Validation error message")
    value: Optional[Any] = Field(default=None, description="Invalid value provided")


class DetailedValidationErrorResponse(ErrorResponse):
    """Enhanced error response for validation with field-level details."""

    details: list[ValidationErrorDetail] = Field(default_factory=list, description="Field-level validation errors")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2024-01-20T10:30:00.000Z",
                "details": [
                    {"field": "amount", "message": "Must be positive", "value": -10},
                    {"field": "user_id", "message": "Required field", "value": None},
                ],
            }
        }


# Usage in FastAPI endpoints
from fastapi import FastAPI, HTTPException, status
from uuid import UUID, uuid4

app = FastAPI()


@app.get(
    "/rewards/{reward_id}",
    responses={
        404: {"model": ErrorResponse, "description": "Reward not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_reward(reward_id: str, correlation_id: Optional[str] = None):
    """Get reward by ID."""
    try:
        corr_id = UUID(correlation_id) if correlation_id else uuid4()
        reward = reward_service.get_reward(reward_id, corr_id)
        return reward
    except ResourceNotFoundError as e:
        # Exception handler will convert to ErrorResponse automatically
        raise
    except Exception as e:
        # Unexpected errors also converted by generic handler
        raise


@app.post(
    "/rewards",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": DetailedValidationErrorResponse, "description": "Validation failed"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def create_reward(data: dict, correlation_id: Optional[str] = None):
    """Create a new reward."""
    corr_id = UUID(correlation_id) if correlation_id else uuid4()
    reward_service.validate_reward_request(data, corr_id)
    reward = reward_service.create_reward(data, corr_id)
    return reward


# Enhanced validation error handler for Pydantic validation errors
from fastapi.exceptions import RequestValidationError


async def pydantic_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors with detailed field information."""
    correlation_id = get_correlation_id(request)

    details = [
        ValidationErrorDetail(
            field=".".join(str(loc) for loc in error["loc"]),
            message=error["msg"],
            value=error.get("input"),
        )
        for error in exc.errors()
    ]

    logger.warning(
        "Request validation failed",
        extra={
            "correlation_id": str(correlation_id),
            "path": request.url.path,
            "errors": exc.errors(),
        },
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=DetailedValidationErrorResponse(
            error="VALIDATION_ERROR",
            message="Request validation failed",
            correlation_id=str(correlation_id),
            details=details,
        ).model_dump(),
        headers={"X-Correlation-ID": str(correlation_id)},
    )


# Register in setup
def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, pydantic_validation_error_handler)
    # ... other handlers
```

**Pitfalls:**
- Not documenting error responses in OpenAPI schema makes it hard for clients to handle errors
- Missing default values for optional fields like timestamp can cause serialization errors
- Inconsistent error code naming (mixing snake_case and UPPER_CASE) confuses clients
- Returning too much context in production errors can leak sensitive data - filter context by environment
- Not versioning error response models makes it hard to evolve the API without breaking clients

---

## Additional Patterns

### Pattern: Correlation ID Middleware

**When to Use:** Automatically extract or generate correlation IDs for all incoming requests, making them available throughout the request lifecycle without manual propagation.

```python
# src/middleware.py
from uuid import UUID, uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware to extract or generate correlation IDs for all requests."""

    async def dispatch(self, request: Request, call_next):
        correlation_id_header = request.headers.get("X-Correlation-ID")

        if correlation_id_header:
            try:
                correlation_id = UUID(correlation_id_header)
            except ValueError:
                correlation_id = uuid4()
        else:
            correlation_id = uuid4()

        request.state.correlation_id = correlation_id

        response = await call_next(request)
        response.headers["X-Correlation-ID"] = str(correlation_id)
        return response


# Register middleware
from fastapi import FastAPI

app = FastAPI()
app.add_middleware(CorrelationIdMiddleware)


# Access in dependencies
from fastapi import Depends, Request


def get_correlation_id(request: Request) -> UUID:
    """Dependency to inject correlation ID into endpoints."""
    return request.state.correlation_id


@app.get("/rewards/{reward_id}")
async def get_reward(reward_id: str, correlation_id: UUID = Depends(get_correlation_id)):
    return reward_service.get_reward(reward_id, correlation_id)
```

