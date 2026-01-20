# Exercise 3: Context-Aware Logging Middleware

## Objective

Implement HTTP middleware that adds logging context and propagates it through the request lifecycle.

## Instructions

1. Create a logging middleware that extracts/generates request ID
2. Add the logger to the request context
3. Create helper functions to retrieve the logger from context
4. Demonstrate context propagation through handler -> service -> repository

## Requirements

### Middleware

- Extract X-Request-ID header (or generate one)
- Create a logger with request context
- Add logger to request context
- Log request start and completion
- Calculate and log request duration

### Context Helpers

Create a `ctxlog` package with:
- `WithLogger(ctx, logger)` - add logger to context
- `FromContext(ctx)` - get logger from context
- `WithFields(ctx, fields...)` - add fields to existing logger

### Layers to Implement

1. HTTP Handler
2. Service Layer
3. Repository Layer

Each layer should add its own context (component, operation) while preserving parent context.

## Starting Point

The `main.go` file contains skeleton code to fill in.

## Expected Output

All logs from a single request should share the same request_id.

```
level=INFO msg="request started" request_id=abc-123 method=GET path=/users/1
level=DEBUG msg="fetching user" request_id=abc-123 component=user_service user_id=1
level=DEBUG msg="database query" request_id=abc-123 component=user_repo query=...
level=INFO msg="request completed" request_id=abc-123 duration_ms=45 status=200
```

## Hints

- Use context.WithValue for storing the logger
- Create a custom type for context keys to avoid collisions
- Each layer should call FromContext then add its own fields
- Don't forget to handle the case where no logger is in context

## Verification

```bash
# Run the server
go run main.go

# In another terminal, make requests
curl localhost:8080/users/1
curl -H "X-Request-ID: custom-123" localhost:8080/users/1

# Check that logs have consistent request_id
```
