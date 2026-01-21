---
name: defining-logging-constants
description: Structured logging best practices in Go using constants to eliminate magic strings and ensure consistent, searchable log output. Use when writing or improving tests.
---

# Logging Constants

## Quick Start
```go
// pkg/logkeys/keys.go
package logkeys

// Identity keys
const (
    UserID   = "user_id"
    TenantID = "tenant_id"
    SessionID = "session_id"
)

// Request keys
const (
    RequestID = "request_id"
    TraceID   = "trace_id"
    SpanID    = "span_id"
    # ... see docs/patterns.md for more
```


## Key Points
- Log Key Constants
- Log Message Constants
- Log Levels

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples