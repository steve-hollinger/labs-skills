# Core Concepts

## Overview

Structured logging with constants eliminates magic strings, ensures consistency across services, and makes logs searchable and maintainable.

## Concept 1: Log Key Constants

### What They Are

Log key constants are named string constants that define field names for structured logging.

```go
// Define once
const (
    KeyUserID    = "user_id"
    KeyRequestID = "request_id"
    KeyDuration  = "duration_ms"
)

// Use everywhere
logger.Info("request", KeyUserID, "123", KeyRequestID, "abc")
```

### Why They Matter

1. **Consistency**: `user_id` is always `user_id`, never `userId` or `userID`
2. **Searchability**: Find all uses of a key with IDE search
3. **Refactoring**: Change a key name once, update everywhere
4. **Documentation**: Constants document what keys exist

### How to Organize

Group constants by domain:

```go
// Identity - who is doing something
const (
    KeyUserID    = "user_id"
    KeyTenantID  = "tenant_id"
    KeySessionID = "session_id"
)

// Request - tracking requests
const (
    KeyRequestID = "request_id"
    KeyTraceID   = "trace_id"
    KeySpanID    = "span_id"
)

// Operation - what is happening
const (
    KeyAction    = "action"
    KeyOperation = "operation"
    KeyStatus    = "status"
)

// Timing - performance data
const (
    KeyDurationMS = "duration_ms"
    KeyStartTime  = "start_time"
    KeyEndTime    = "end_time"
)

// Error - error details
const (
    KeyError     = "error"
    KeyErrorCode = "error_code"
    KeyErrorType = "error_type"
)
```

## Concept 2: Log Message Constants

### What They Are

Predefined strings for common log messages that appear in your system.

```go
const (
    MsgUserCreated    = "user created"
    MsgUserUpdated    = "user updated"
    MsgRequestStarted = "request started"
    MsgRequestFailed  = "request failed"
)
```

### Why They Matter

1. **Searchability**: Find all "user created" logs across codebase
2. **Consistency**: Same message format everywhere
3. **Metrics**: Easier to create alerts based on message patterns

### When to Use

- High-frequency operations (request start/end)
- Business events (user created, order placed)
- Error conditions (operation failed)

### When NOT to Use

- One-off debugging messages
- Messages with dynamic content only

```go
// Good: Constant for common operation
logger.Info(MsgRequestStarted, KeyRequestID, id)

// Fine: Dynamic message for specific situation
logger.Debug(fmt.Sprintf("processing batch %d of %d", i, total))
```

## Concept 3: Log Levels

### What They Are

Severity indicators that help filter and prioritize log messages.

| Level | Purpose | Examples |
|-------|---------|----------|
| DEBUG | Development details | Variable values, loop iterations |
| INFO | Normal operations | User actions, request completion |
| WARN | Concerning but handled | Retry, fallback, deprecated |
| ERROR | Failures needing attention | DB errors, service failures |

### How to Choose

```go
// DEBUG: Detailed information for debugging
logger.Debug("cache lookup", KeyKey, key, KeyHit, hit)

// INFO: Normal, successful operations
logger.Info(MsgUserCreated, KeyUserID, id)

// WARN: Something concerning but handled
logger.Warn("retry attempt", KeyAttempt, 2, KeyMaxRetries, 3)

// ERROR: Something failed that needs attention
logger.Error("database connection failed", KeyError, err)
```

### Common Mistakes

```go
// BAD: Using ERROR for expected conditions
if user == nil {
    logger.Error("user not found") // This isn't an error!
}

// GOOD: Use appropriate level
if user == nil {
    logger.Info("user not found", KeyUserID, id) // Expected case
}

// BAD: DEBUG in production for critical path
logger.Debug("processing payment") // Won't see this in production!

// GOOD: INFO for operations you need visibility into
logger.Info("processing payment", KeyAmount, amount)
```

## Concept 4: Context Propagation

### What It Is

Carrying logging context (request ID, user ID, etc.) through function calls without passing logger explicitly.

### Why It Matters

1. **Traceability**: Follow a request through the entire system
2. **Debugging**: All related logs have the same request ID
3. **Clean Code**: Don't need to pass logger to every function

### Implementation

```go
// Define context key
type ctxKey string
const LoggerKey ctxKey = "logger"

// Add logger to context
func WithLogger(ctx context.Context, logger *slog.Logger) context.Context {
    return context.WithValue(ctx, LoggerKey, logger)
}

// Get logger from context
func FromContext(ctx context.Context) *slog.Logger {
    if logger, ok := ctx.Value(LoggerKey).(*slog.Logger); ok {
        return logger
    }
    return slog.Default()
}

// Usage in handler
func HandleRequest(ctx context.Context, req *Request) {
    logger := slog.Default().With(
        KeyRequestID, req.ID,
        KeyUserID, req.UserID,
    )
    ctx = WithLogger(ctx, logger)

    processRequest(ctx, req)
}

func processRequest(ctx context.Context, req *Request) {
    logger := FromContext(ctx)
    logger.Info("processing request") // Has request_id and user_id

    validateRequest(ctx, req)
}
```

## Concept 5: Sensitive Data Handling

### What It Is

Ensuring sensitive data doesn't end up in logs.

### Categories of Sensitive Data

- **PII**: Email, phone, address, SSN
- **Credentials**: Passwords, API keys, tokens
- **Financial**: Credit card, bank account
- **Health**: Medical information

### Strategies

1. **Never log sensitive fields**
```go
// BAD
logger.Info("user", "email", user.Email)

// GOOD
logger.Info("user", KeyUserID, user.ID)
```

2. **Mask sensitive data**
```go
func maskEmail(email string) string {
    parts := strings.Split(email, "@")
    if len(parts) != 2 {
        return "***"
    }
    return parts[0][:2] + "***@" + parts[1]
}
```

3. **Use separate logging constants**
```go
// Mark sensitive keys
const (
    KeyUserID = "user_id"           // Safe
    KeyEmail  = "email_masked"      // Reminds to mask
)
```

## Summary

Key takeaways:

1. **Define constants** for all log keys used in your system
2. **Use message constants** for high-frequency, searchable operations
3. **Choose log levels** based on what needs attention, not emotion
4. **Propagate context** to maintain traceability
5. **Never log sensitive data** - define policies and enforce them
