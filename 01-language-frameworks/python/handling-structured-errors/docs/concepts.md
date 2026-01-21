# Core Concepts: Structured Error Handling

## What

Structured error handling is a pattern for managing exceptions in distributed systems using typed exception hierarchies, correlation IDs for request tracing, and standardized error responses. In FastAPI services, this means creating custom exception classes that carry context, registering exception handlers that convert exceptions to JSON responses, and propagating correlation IDs through the entire request lifecycle.

At Fetch, every error includes a correlation ID (UUID) that traces the request across multiple services, enabling debugging of failures in distributed workflows. Exception handlers map Python exceptions to appropriate HTTP status codes and structured error responses that clients can parse programmatically.

## Why

**Problem:**
Generic exception handling loses critical context when errors occur. Without correlation IDs, debugging failures that span multiple services becomes nearly impossible. Unstructured error messages make it difficult for clients to handle errors programmatically, and exposing stack traces or internal details creates security vulnerabilities.

**Solution:**
Structured error handling with custom exception hierarchies provides type safety and context. Correlation IDs enable distributed tracing across service boundaries. FastAPI exception handlers ensure consistent error response formats with appropriate HTTP status codes. Structured logging with correlation IDs allows searching logs across services to reconstruct the full error context.

**Fetch Context:**
Fetch's microservices architecture requires tracking requests across multiple services (Auth, Rewards, User, etc.). When a user action fails, correlation IDs allow tracing the request through the entire call chain. Integration with OpenTelemetry and structured logging means correlation IDs appear in traces, logs, and metrics, providing full observability into error conditions.

## How

**Exception Hierarchy:**
Create a base `ServiceError` class that includes message, error_code, and correlation_id. Derive specific exceptions like `ValidationError`, `ResourceNotFoundError`, `AuthenticationError` that set appropriate error codes. Each exception type maps to a specific HTTP status code in handlers.

**FastAPI Exception Handlers:**
Register exception handlers using `app.add_exception_handler()` that catch specific exception types, log with correlation ID and context, and return JSONResponse with standardized ErrorResponse model. Handlers extract correlation IDs from request headers (X-Correlation-ID) or generate new ones.

**Correlation ID Propagation:**
Extract correlation IDs from incoming request headers using FastAPI middleware or dependency injection. Pass correlation IDs to all service calls, database operations, and external API requests. Include in all log messages and exception constructors. Return in response headers and error response bodies.

**OpenTelemetry Integration:**
Attach correlation IDs as span attributes in OpenTelemetry traces. This links logs to traces, allowing full distributed tracing of errors. When an exception occurs, the correlation ID appears in both the error log and the trace span, enabling correlation of logs and traces in monitoring tools like DataDog or Grafana.

## When to Use

**Use when:**
- Building FastAPI services that need robust error handling with correlation IDs
- Working in microservices architectures requiring distributed tracing across services
- Creating APIs where clients need to handle different error types programmatically
- Implementing error logging and monitoring that requires searchable correlation IDs
- Integrating with OpenTelemetry or other observability platforms for full tracing

**Avoid when:**
- Building simple scripts or single-purpose tools that don't need distributed tracing
- Prototyping where detailed error handling adds unnecessary complexity
- Working with synchronous single-service applications where basic try/except suffices
- Creating internal utilities where generic exceptions provide adequate context

## Key Terminology

- **Correlation ID** - A UUID that uniquely identifies a request and propagates through all services involved in processing it, enabling distributed tracing and log correlation
- **Exception Hierarchy** - A tree of custom exception classes inheriting from a base exception, allowing type-based exception handling and specific error scenarios
- **Exception Handler** - A FastAPI function registered with `add_exception_handler()` that catches specific exception types and converts them to HTTP responses
- **HTTPException** - FastAPI's built-in exception class for HTTP errors, but custom exceptions with correlation IDs provide better context
- **ErrorResponse Model** - A Pydantic model defining the structure of error responses (error_code, message, correlation_id, timestamp)
- **OpenTelemetry** - An observability framework for distributed tracing, metrics, and logging that integrates with correlation IDs for end-to-end request tracking
