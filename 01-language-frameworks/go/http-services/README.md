# Go HTTP Services

Learn to build production-ready HTTP APIs using Go's standard library. This skill covers routing, middleware, handlers, JSON serialization, and error handling patterns.

## Learning Objectives

After completing this skill, you will be able to:
- Build HTTP servers using Go's `net/http` package
- Create RESTful API endpoints with proper routing
- Implement middleware for cross-cutting concerns
- Handle JSON request/response serialization
- Apply proper error handling patterns
- Structure HTTP services for maintainability

## Prerequisites

- Go 1.22+
- Basic Go knowledge (variables, functions, structs, interfaces)
- Understanding of HTTP fundamentals (methods, status codes, headers)

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

### HTTP Handler Interface

The foundation of Go HTTP servers is the `http.Handler` interface:

```go
type Handler interface {
    ServeHTTP(ResponseWriter, *Request)
}
```

Any type implementing this interface can handle HTTP requests. The `http.HandlerFunc` adapter lets you use regular functions:

```go
func healthHandler(w http.ResponseWriter, r *http.Request) {
    w.WriteHeader(http.StatusOK)
    w.Write([]byte("OK"))
}

// Use as handler
http.HandleFunc("/health", healthHandler)
```

### Middleware Pattern

Middleware wraps handlers to add cross-cutting functionality:

```go
func LoggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s took %v", r.Method, r.URL.Path, time.Since(start))
    })
}
```

### JSON Handling

Use `encoding/json` for request/response serialization:

```go
type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

func createUserHandler(w http.ResponseWriter, r *http.Request) {
    var user User
    if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
        http.Error(w, "Invalid JSON", http.StatusBadRequest)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(user)
}
```

## Examples

### Example 1: Basic HTTP Server

This example demonstrates a simple HTTP server with basic routing.

```bash
make example-1
```

### Example 2: RESTful API with Middleware

Building on basics with middleware, structured routing, and JSON handling.

```bash
make example-2
```

### Example 3: Production-Ready API

Real-world patterns including error handling, validation, and graceful shutdown.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Build a simple health check endpoint with structured responses
2. **Exercise 2**: Create a CRUD API for a Todo resource with proper error handling
3. **Exercise 3**: Implement rate limiting middleware with configurable limits

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Not Setting Content-Type Header

Always set the Content-Type header for JSON responses:

```go
// Bad - missing Content-Type
json.NewEncoder(w).Encode(data)

// Good - explicit Content-Type
w.Header().Set("Content-Type", "application/json")
json.NewEncoder(w).Encode(data)
```

### Not Handling Request Body Close

The request body should be closed after reading:

```go
defer r.Body.Close()
```

### Writing Headers After Body

Headers must be written before the response body:

```go
// Bad - header ignored after body write
w.Write([]byte("Hello"))
w.Header().Set("X-Custom", "value") // Ignored!

// Good - headers first
w.Header().Set("X-Custom", "value")
w.Write([]byte("Hello"))
```

## Further Reading

- [Official net/http Documentation](https://pkg.go.dev/net/http)
- [Go HTTP Handler Interface](https://golang.org/doc/articles/wiki/#tmp_3)
- Related skills in this repository:
  - [Go Concurrency](../concurrency/)
  - [Hybrid Authentication](../../../02-architecture-design/hybrid-authentication/)
