# Common Patterns

## Overview

This document covers common patterns and best practices for implementing structured logging with constants in Go.

## Pattern 1: Package Organization

### When to Use

For any project that uses structured logging across multiple packages.

### Implementation

```
myservice/
├── pkg/
│   ├── logkey/
│   │   └── keys.go       # Log field key constants
│   └── logmsg/
│       └── messages.go   # Log message constants
├── internal/
│   └── logger/
│       └── logger.go     # Logger configuration
└── cmd/
    └── server/
        └── main.go
```

### Example

```go
// pkg/logkey/keys.go
package logkey

// Identity keys - who is acting
const (
    UserID    = "user_id"
    TenantID  = "tenant_id"
    SessionID = "session_id"
    ActorType = "actor_type"
)

// Request keys - request tracking
const (
    RequestID   = "request_id"
    TraceID     = "trace_id"
    SpanID      = "span_id"
    Method      = "http_method"
    Path        = "http_path"
    StatusCode  = "status_code"
)

// Operation keys - what's happening
const (
    Operation = "operation"
    Action    = "action"
    Status    = "status"
    Component = "component"
)

// Timing keys - performance
const (
    DurationMS = "duration_ms"
    StartTime  = "start_time"
    EndTime    = "end_time"
)

// Error keys - error details
const (
    Error     = "error"
    ErrorCode = "error_code"
    ErrorType = "error_type"
    Stack     = "stack_trace"
)

// Resource keys - what's being acted upon
const (
    ResourceType = "resource_type"
    ResourceID   = "resource_id"
    Count        = "count"
)
```

```go
// pkg/logmsg/messages.go
package logmsg

// Request lifecycle
const (
    RequestStarted   = "request started"
    RequestCompleted = "request completed"
    RequestFailed    = "request failed"
)

// User operations
const (
    UserCreated     = "user created"
    UserUpdated     = "user updated"
    UserDeleted     = "user deleted"
    UserLoggedIn    = "user logged in"
    UserLoggedOut   = "user logged out"
)

// Data operations
const (
    RecordCreated = "record created"
    RecordUpdated = "record updated"
    RecordDeleted = "record deleted"
    RecordFetched = "record fetched"
)

// System events
const (
    ServiceStarted  = "service started"
    ServiceStopping = "service stopping"
    ConfigLoaded    = "configuration loaded"
)
```

### Pitfalls to Avoid

- Don't create constants for every possible message
- Don't put business logic in the logging package
- Keep packages focused - keys and messages separate

## Pattern 2: HTTP Middleware Logging

### When to Use

For any HTTP service that needs request/response logging.

### Implementation

```go
package middleware

import (
    "log/slog"
    "net/http"
    "time"

    "myservice/pkg/logkey"
    "myservice/pkg/logmsg"
)

func LoggingMiddleware(logger *slog.Logger) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            start := time.Now()
            requestID := r.Header.Get("X-Request-ID")
            if requestID == "" {
                requestID = generateRequestID()
            }

            // Create request-scoped logger
            reqLogger := logger.With(
                logkey.RequestID, requestID,
                logkey.Method, r.Method,
                logkey.Path, r.URL.Path,
            )

            // Log request start
            reqLogger.Info(logmsg.RequestStarted)

            // Wrap response writer to capture status
            wrapped := &responseWriter{ResponseWriter: w, status: http.StatusOK}

            // Add logger to context
            ctx := WithLogger(r.Context(), reqLogger)

            // Process request
            next.ServeHTTP(wrapped, r.WithContext(ctx))

            // Log request completion
            duration := time.Since(start)
            reqLogger.Info(logmsg.RequestCompleted,
                logkey.StatusCode, wrapped.status,
                logkey.DurationMS, duration.Milliseconds(),
            )
        })
    }
}

type responseWriter struct {
    http.ResponseWriter
    status int
}

func (rw *responseWriter) WriteHeader(code int) {
    rw.status = code
    rw.ResponseWriter.WriteHeader(code)
}
```

## Pattern 3: Service Layer Logging

### When to Use

For domain logic that needs audit trails and debugging.

### Implementation

```go
package service

import (
    "context"
    "log/slog"

    "myservice/pkg/logkey"
    "myservice/pkg/logmsg"
)

type UserService struct {
    repo   UserRepository
    logger *slog.Logger
}

func NewUserService(repo UserRepository, logger *slog.Logger) *UserService {
    return &UserService{
        repo:   repo,
        logger: logger.With(logkey.Component, "user_service"),
    }
}

func (s *UserService) CreateUser(ctx context.Context, input CreateUserInput) (*User, error) {
    // Get context logger (has request_id from middleware)
    logger := FromContext(ctx).With(
        logkey.Operation, "create_user",
    )

    logger.Debug("validating input")

    if err := input.Validate(); err != nil {
        logger.Warn("validation failed",
            logkey.Error, err.Error(),
        )
        return nil, err
    }

    user, err := s.repo.Create(ctx, input)
    if err != nil {
        logger.Error("failed to create user",
            logkey.Error, err.Error(),
            logkey.ErrorType, "repository_error",
        )
        return nil, err
    }

    logger.Info(logmsg.UserCreated,
        logkey.UserID, user.ID,
    )

    return user, nil
}
```

## Pattern 4: Error Logging with Context

### When to Use

When errors need rich context for debugging.

### Implementation

```go
package errors

import (
    "log/slog"

    "myservice/pkg/logkey"
)

// LogError logs an error with standard fields
func LogError(logger *slog.Logger, msg string, err error, fields ...any) {
    allFields := make([]any, 0, len(fields)+2)
    allFields = append(allFields, logkey.Error, err.Error())
    allFields = append(allFields, fields...)

    logger.Error(msg, allFields...)
}

// Usage
func (s *Service) DoSomething(ctx context.Context) error {
    logger := FromContext(ctx)

    result, err := s.externalService.Call()
    if err != nil {
        LogError(logger, "external service call failed", err,
            logkey.Operation, "external_call",
            logkey.ResourceType, "external_service",
        )
        return fmt.Errorf("external call: %w", err)
    }

    return nil
}
```

## Pattern 5: Batch Operation Logging

### When to Use

For operations that process multiple items.

### Implementation

```go
func (s *Service) ProcessBatch(ctx context.Context, items []Item) error {
    logger := FromContext(ctx).With(
        logkey.Operation, "process_batch",
        logkey.Count, len(items),
    )

    logger.Info("batch processing started")

    var processed, failed int
    for i, item := range items {
        if err := s.processItem(ctx, item); err != nil {
            failed++
            logger.Warn("item processing failed",
                logkey.ResourceID, item.ID,
                logkey.Error, err.Error(),
                "index", i,
            )
            continue
        }
        processed++
    }

    logger.Info("batch processing completed",
        "processed", processed,
        "failed", failed,
    )

    if failed > 0 {
        return fmt.Errorf("%d items failed processing", failed)
    }
    return nil
}
```

## Anti-Patterns

### Anti-Pattern 1: Magic Strings

Description: Using string literals directly in log calls.

```go
// DON'T DO THIS
logger.Info("user created", "userId", user.ID)
logger.Info("user created", "user_id", user.ID)
logger.Info("User Created", "USER_ID", user.ID)
```

### Better Approach

```go
// DO THIS
logger.Info(logmsg.UserCreated, logkey.UserID, user.ID)
```

### Anti-Pattern 2: Over-Logging

Description: Logging every minor operation.

```go
// DON'T DO THIS
func add(a, b int) int {
    logger.Debug("entering add")
    result := a + b
    logger.Debug("computed result", "result", result)
    logger.Debug("exiting add")
    return result
}
```

### Better Approach

```go
// DO THIS - Log at appropriate boundaries
func ProcessOrder(ctx context.Context, order Order) error {
    logger := FromContext(ctx)
    logger.Info("processing order", logkey.ResourceID, order.ID)
    // ... do work ...
    logger.Info("order processed", logkey.ResourceID, order.ID, logkey.DurationMS, elapsed)
    return nil
}
```

### Anti-Pattern 3: Logging Sensitive Data

Description: Including PII or secrets in logs.

```go
// DON'T DO THIS
logger.Info("user login",
    "email", user.Email,
    "password", user.Password,
    "ssn", user.SSN,
)
```

### Better Approach

```go
// DO THIS
logger.Info(logmsg.UserLoggedIn,
    logkey.UserID, user.ID,
    // Never log: email, password, SSN, credit cards, etc.
)
```

### Anti-Pattern 4: Wrong Log Levels

Description: Using ERROR for expected conditions.

```go
// DON'T DO THIS
func GetUser(id string) (*User, error) {
    user, err := repo.Find(id)
    if err == ErrNotFound {
        logger.Error("user not found") // This is expected!
        return nil, err
    }
}
```

### Better Approach

```go
// DO THIS
func GetUser(id string) (*User, error) {
    user, err := repo.Find(id)
    if err == ErrNotFound {
        logger.Debug("user not found", logkey.UserID, id) // Expected case
        return nil, err
    }
    if err != nil {
        logger.Error("database error", logkey.Error, err) // Unexpected!
        return nil, err
    }
    return user, nil
}
```
