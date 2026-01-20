# Logging Constants

A comprehensive skill for mastering structured logging with constants in Go, eliminating magic strings and ensuring consistent, searchable log messages.

## Learning Objectives

After completing this skill, you will be able to:
- Design and implement logging key constants for structured logging
- Eliminate magic strings from log statements
- Implement proper log level management
- Propagate context through logging chains
- Create consistent, searchable log patterns across services

## Prerequisites

- Go 1.22+
- Basic Go knowledge (functions, packages, error handling)
- Understanding of structured logging concepts

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Concepts

### Why Use Logging Constants?

Magic strings in logging create several problems:

```go
// Bad: Magic strings everywhere
logger.Info("user logged in",
    "user_id", userID,      // Is it "user_id" or "userId"?
    "ip_address", ip,       // Or "ip" or "ipAddress"?
)

// Good: Constants ensure consistency
logger.Info(logmsg.UserLoggedIn,
    logkey.UserID, userID,
    logkey.IPAddress, ip,
)
```

### Benefits

1. **Consistency**: Same key names across all services
2. **Searchability**: Grep/search for log constants in code
3. **Type Safety**: IDE autocomplete and compile-time checks
4. **Documentation**: Constants serve as documentation
5. **Refactoring**: Change once, update everywhere

### Structured Logging Basics

```go
// Define constants
const (
    KeyUserID    = "user_id"
    KeyRequestID = "request_id"
    KeyDuration  = "duration_ms"
)

// Use with any structured logger
logger.Info("request completed",
    KeyUserID, userID,
    KeyRequestID, reqID,
    KeyDuration, duration.Milliseconds(),
)
```

## Examples

### Example 1: Basic Logging Constants

This example demonstrates defining and using basic logging key constants.

```bash
make example-1
```

### Example 2: Log Level Management

Building on the basics with proper log level selection and configuration.

```bash
make example-2
```

### Example 3: Context Propagation

Real-world patterns for propagating logging context through request chains.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Define logging constants for an e-commerce service
2. **Exercise 2**: Refactor code to use logging constants
3. **Exercise 3**: Implement context-aware logging middleware

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Mistake 1: Inconsistent Key Names

Using different names for the same concept:
```go
// Bad: Inconsistent naming
logger.Info("start", "userId", id)
logger.Info("end", "user_id", id)

// Good: Use constants
logger.Info("start", logkey.UserID, id)
logger.Info("end", logkey.UserID, id)
```

### Mistake 2: Not Using Log Levels Properly

```go
// Bad: Using Info for everything
logger.Info("debug info")
logger.Info("CRITICAL ERROR!")

// Good: Appropriate levels
logger.Debug("detailed trace")
logger.Error("critical failure")
```

### Mistake 3: Missing Context

```go
// Bad: No context about what happened
logger.Error("failed")

// Good: Rich context
logger.Error("database query failed",
    logkey.Operation, "user_lookup",
    logkey.UserID, userID,
    logkey.Error, err.Error(),
)
```

## Log Key Categories

| Category | Examples | Purpose |
|----------|----------|---------|
| Identity | user_id, tenant_id | Who/what |
| Request | request_id, trace_id | Request tracking |
| Operation | action, operation | What happened |
| Timing | duration_ms, timestamp | Performance |
| Error | error, error_code | Error details |
| Resource | resource_type, resource_id | What was affected |

## Further Reading

- [Go slog Package](https://pkg.go.dev/log/slog)
- [Structured Logging Best Practices](https://www.honeycomb.io/blog/structured-logging)
- Related skills in this repository:
  - [golangci-lint](../golangci-lint/)
  - [Error Handling](../../01-language-frameworks/go/error-handling/)
