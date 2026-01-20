# CLAUDE.md - Logging Constants

This skill teaches structured logging best practices in Go using constants to eliminate magic strings and ensure consistent, searchable log output.

## Key Concepts

- **Log Key Constants**: Named constants for log field keys ensure consistency
- **Log Message Constants**: Predefined messages for common operations
- **Log Levels**: DEBUG, INFO, WARN, ERROR with proper usage guidelines
- **Context Propagation**: Passing logger context through request chains

## Common Commands

```bash
make setup      # Download dependencies
make examples   # Run all examples
make example-1  # Run basic constants example
make example-2  # Run log level management example
make example-3  # Run context propagation example
make test       # Run go test
make test-race  # Run tests with race detector
make lint       # Run golangci-lint
make clean      # Remove build artifacts
```

## Project Structure

```
logging-constants/
├── cmd/examples/
│   ├── example1/main.go      # Basic logging constants
│   ├── example2/main.go      # Log level management
│   └── example3/main.go      # Context propagation
├── internal/
│   └── logger/               # Internal logger utilities
├── pkg/
│   └── logkeys/              # Reusable log key constants
├── exercises/
│   ├── exercise1/            # Define constants exercise
│   ├── exercise2/            # Refactor exercise
│   ├── exercise3/            # Context exercise
│   └── solutions/
├── tests/
│   └── *_test.go
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Log Key Constants
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
)
```

### Pattern 2: Log Message Constants
```go
// pkg/logmsg/messages.go
package logmsg

const (
    UserCreated     = "user created"
    UserUpdated     = "user updated"
    UserDeleted     = "user deleted"
    RequestStarted  = "request started"
    RequestComplete = "request completed"
)
```

### Pattern 3: Context Logger
```go
// Create logger with context
func WithContext(ctx context.Context, logger *slog.Logger) *slog.Logger {
    if requestID := ctx.Value(RequestIDKey); requestID != nil {
        logger = logger.With(logkey.RequestID, requestID)
    }
    return logger
}
```

## Common Mistakes

1. **Mixing naming conventions**
   - Why it happens: Different developers use different styles
   - How to fix it: Document and enforce a single convention (snake_case recommended)

2. **Too granular constants**
   - Why it happens: Over-engineering
   - How to fix it: Group related keys, don't create constants for one-off uses

3. **Not including context**
   - Why it happens: Seems like extra work
   - How to fix it: Always include who, what, when, result

4. **Logging sensitive data**
   - Why it happens: Not thinking about what goes in logs
   - How to fix it: Define sensitive keys separately, add sanitization

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make examples` and the README.md. Example 1 shows basic setup.

### "Which logger should I use?"
Go 1.21+ has `log/slog` built-in. For older code, zerolog and zap are excellent choices.

### "How do I organize constants?"
Group by domain: identity (user_id, tenant_id), request (request_id, trace_id), operation (action, status).

### "Should I log errors at Error level?"
Not always. Expected errors (user not found) might be WARN or INFO. Unexpected errors are ERROR.

### "How do I add logging to existing code?"
1. Define constants for existing keys
2. Replace strings with constants one file at a time
3. Add tests to verify log output

## Testing Notes

- Tests verify constant values and naming conventions
- Use captured log output for testing
- Run with race detector: `make test-race`
- Use testify for assertions

## Dependencies

Key dependencies in go.mod:
- github.com/stretchr/testify: Testing assertions
- log/slog: Go's built-in structured logging (1.21+)

## Log Level Guidelines

| Level | When to Use | Examples |
|-------|-------------|----------|
| DEBUG | Development details | Variable values, loop iterations |
| INFO | Normal operations | User actions, request completion |
| WARN | Concerning but handled | Retry, fallback, deprecated usage |
| ERROR | Failures needing attention | DB errors, external service failures |

## Naming Conventions

**Recommended: snake_case**
- `user_id`, `request_id`, `error_message`
- Consistent with JSON conventions
- Works well with log aggregation tools

**Avoid:**
- camelCase: `userId` - harder to read in logs
- PascalCase: `UserId` - looks like type names
- kebab-case: `user-id` - can cause issues in some systems
