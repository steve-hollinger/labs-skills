---
name: handling-structured-errors
description: Implement structured error handling with correlation IDs and custom exception handlers. Use when building robust error handling for FastAPI services.
tags: ['python', 'error-handling', 'exceptions', 'fastapi', 'correlation-id']
---

# Structured Error Handling

## Quick Start
```python
# src/exceptions.py
from uuid import UUID, uuid4

class ServiceError(Exception):
    """Base exception for all service errors with correlation ID."""

    def __init__(self, message: str, error_code: str, correlation_id: UUID = None):
        self.message = message
        self.error_code = error_code
        self.correlation_id = correlation_id or uuid4()
        super().__init__(self.message)

class ValidationError(ServiceError):
    """Input validation failed."""
    def __init__(self, message: str, correlation_id: UUID = None):
        super().__init__(message, "VALIDATION_ERROR", correlation_id)

class ResourceNotFoundError(ServiceError):
    """Requested resource not found."""
    def __init__(self, resource: str, resource_id: str, correlation_id: UUID = None):
        super().__init__(f"{resource} {resource_id} not found", "NOT_FOUND", correlation_id)
        self.resource = resource
        self.resource_id = resource_id
```

## Key Points
- Always include correlation IDs for distributed tracing across services and requests
- Use custom exception hierarchy to distinguish error types (validation, not found, auth, etc.)
- Register FastAPI exception handlers to convert exceptions to structured JSON responses
- Log errors with correlation IDs and structured context for debugging and monitoring
- Never expose internal stack traces or sensitive information to API clients

## Common Mistakes
1. **Missing correlation ID propagation** - Forgetting to pass correlation IDs through the call chain breaks distributed tracing. Always extract from headers and pass to exceptions.
2. **Generic exception catching** - Using bare `except Exception` loses type information. Create specific exception classes for different error scenarios.
3. **Exposing internal details** - Returning stack traces or database errors to clients leaks implementation details. Use generic messages with correlation IDs for investigation.
4. **Wrong HTTP status codes** - Using 500 for validation errors or 404 for auth failures confuses clients. Map exception types to appropriate status codes (400, 401, 404, 500).
5. **Not logging exceptions** - Swallowing errors without logging makes debugging impossible. Always log with correlation ID, context, and severity level.

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
