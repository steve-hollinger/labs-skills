# CLAUDE.md - Go HTTP Services

This skill teaches building HTTP APIs using Go's standard library `net/http` package without external frameworks.

## Key Concepts

- **http.Handler Interface**: The core abstraction for HTTP request handling
- **Middleware Pattern**: Function chaining for cross-cutting concerns
- **ServeMux Routing**: Path-based request routing with the standard multiplexer
- **JSON Serialization**: Request/response encoding with `encoding/json`
- **Error Handling**: Structured error responses and status codes

## Common Commands

```bash
make setup      # Download dependencies
make examples   # Run all examples
make example-1  # Run basic server example
make example-2  # Run middleware example
make example-3  # Run production API example
make test       # Run go test
make test-race  # Run tests with race detector
make lint       # Run golangci-lint
make clean      # Remove build artifacts
```

## Project Structure

```
http-services/
├── cmd/examples/
│   ├── example1/main.go     # Basic HTTP server
│   ├── example2/main.go     # RESTful API with middleware
│   └── example3/main.go     # Production-ready patterns
├── pkg/
│   ├── handlers/            # HTTP handler implementations
│   ├── middleware/          # Middleware functions
│   └── router/              # Router utilities
├── exercises/
│   ├── exercise1/           # Health check endpoint
│   ├── exercise2/           # Todo CRUD API
│   ├── exercise3/           # Rate limiting middleware
│   └── solutions/
├── tests/
│   └── *_test.go
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Handler Function
```go
func handler(w http.ResponseWriter, r *http.Request) {
    // Validate request method
    if r.Method != http.MethodGet {
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        return
    }

    // Set response headers
    w.Header().Set("Content-Type", "application/json")

    // Write response
    json.NewEncoder(w).Encode(response)
}
```

### Pattern 2: Middleware Chain
```go
func Chain(h http.Handler, middlewares ...func(http.Handler) http.Handler) http.Handler {
    for i := len(middlewares) - 1; i >= 0; i-- {
        h = middlewares[i](h)
    }
    return h
}

// Usage
handler := Chain(
    finalHandler,
    LoggingMiddleware,
    RecoveryMiddleware,
    CORSMiddleware,
)
```

### Pattern 3: Error Response
```go
type ErrorResponse struct {
    Error   string `json:"error"`
    Code    string `json:"code,omitempty"`
    Details any    `json:"details,omitempty"`
}

func WriteError(w http.ResponseWriter, status int, message string) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(ErrorResponse{Error: message})
}
```

## Common Mistakes

1. **Forgetting to return after error responses**
   - Why it happens: Handler continues executing after http.Error()
   - How to fix: Always `return` after writing error responses

2. **Not handling all HTTP methods**
   - Why it happens: Handlers accept any method by default
   - How to fix: Explicitly check `r.Method` and return 405 for unsupported methods

3. **Writing headers after body**
   - Why it happens: Header modifications after Write() are ignored
   - How to fix: Set all headers before calling Write() or WriteHeader()

4. **Not closing request body**
   - Why it happens: Forgetting `defer r.Body.Close()`
   - How to fix: Always close request body after reading, use defer

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make example-1` and the README.md.

### "How do I add routing?"
Show the ServeMux pattern in Example 2, or recommend chi/gorilla/mux for more complex routing.

### "How do I handle errors?"
Refer to the error response pattern in Example 3 and docs/patterns.md.

### "How do I test HTTP handlers?"
Use `httptest.NewRecorder()` and `httptest.NewRequest()` - see tests/ directory.

### "How do I add authentication?"
Point to the hybrid-authentication skill for comprehensive auth patterns.

## Testing Notes

- Use `httptest.NewServer` for integration tests
- Use `httptest.NewRecorder` for unit testing handlers
- Table-driven tests for multiple request scenarios
- Run with race detector: `make test-race`
- Use testify for assertions

## Dependencies

Key dependencies in go.mod:
- github.com/stretchr/testify: Testing assertions and mocking
- Standard library only for HTTP functionality (no external routers)
