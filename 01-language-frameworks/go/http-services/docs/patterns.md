# Common Patterns

## Overview

This document covers common patterns and best practices for building HTTP services in Go.

## Pattern 1: Middleware Chain

### When to Use

Use middleware for cross-cutting concerns that apply to multiple handlers:
- Logging
- Authentication/Authorization
- CORS
- Rate limiting
- Panic recovery
- Request ID injection

### Implementation

```go
// Middleware function signature
type Middleware func(http.Handler) http.Handler

// Chain applies middlewares in order (last middleware wraps first)
func Chain(h http.Handler, middlewares ...Middleware) http.Handler {
    for i := len(middlewares) - 1; i >= 0; i-- {
        h = middlewares[i](h)
    }
    return h
}
```

### Example

```go
// Logging middleware
func LoggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()

        // Wrap ResponseWriter to capture status code
        wrapped := &responseWriter{ResponseWriter: w, status: http.StatusOK}

        next.ServeHTTP(wrapped, r)

        log.Printf("%s %s %d %v",
            r.Method, r.URL.Path, wrapped.status, time.Since(start))
    })
}

// Recovery middleware
func RecoveryMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if err := recover(); err != nil {
                log.Printf("panic recovered: %v", err)
                http.Error(w, "Internal Server Error", http.StatusInternalServerError)
            }
        }()
        next.ServeHTTP(w, r)
    })
}

// Usage
handler := Chain(
    finalHandler,
    RecoveryMiddleware,  // Outermost (executes first on request)
    LoggingMiddleware,   // Executes second
)
```

### Pitfalls to Avoid

- Don't modify the request body in middleware (it can only be read once)
- Remember middleware executes in reverse order of application
- Always call `next.ServeHTTP()` unless intentionally short-circuiting

## Pattern 2: Structured Error Handling

### When to Use

Use structured errors for consistent API error responses across all endpoints.

### Implementation

```go
// ErrorResponse is the standard error format
type ErrorResponse struct {
    Error   string            `json:"error"`
    Code    string            `json:"code,omitempty"`
    Details map[string]string `json:"details,omitempty"`
}

// APIError represents an API error with status code
type APIError struct {
    Status  int
    Message string
    Code    string
    Details map[string]string
}

func (e *APIError) Error() string {
    return e.Message
}

// WriteError writes a structured error response
func WriteError(w http.ResponseWriter, err *APIError) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(err.Status)
    json.NewEncoder(w).Encode(ErrorResponse{
        Error:   err.Message,
        Code:    err.Code,
        Details: err.Details,
    })
}

// Common errors
var (
    ErrNotFound = &APIError{
        Status:  http.StatusNotFound,
        Message: "Resource not found",
        Code:    "NOT_FOUND",
    }
    ErrBadRequest = &APIError{
        Status:  http.StatusBadRequest,
        Message: "Invalid request",
        Code:    "BAD_REQUEST",
    }
    ErrUnauthorized = &APIError{
        Status:  http.StatusUnauthorized,
        Message: "Authentication required",
        Code:    "UNAUTHORIZED",
    }
)
```

### Example

```go
func getUserHandler(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id")

    user, err := store.GetUser(r.Context(), id)
    if err != nil {
        if errors.Is(err, ErrUserNotFound) {
            WriteError(w, &APIError{
                Status:  http.StatusNotFound,
                Message: "User not found",
                Code:    "USER_NOT_FOUND",
                Details: map[string]string{"id": id},
            })
            return
        }
        WriteError(w, &APIError{
            Status:  http.StatusInternalServerError,
            Message: "Failed to retrieve user",
            Code:    "INTERNAL_ERROR",
        })
        return
    }

    WriteJSON(w, http.StatusOK, user)
}
```

## Pattern 3: Request Validation

### When to Use

Validate all incoming request data before processing.

### Implementation

```go
// ValidationError holds field-level validation errors
type ValidationError struct {
    Field   string `json:"field"`
    Message string `json:"message"`
}

// Validator validates request data
type Validator struct {
    errors []ValidationError
}

func (v *Validator) Required(field, value string) {
    if strings.TrimSpace(value) == "" {
        v.errors = append(v.errors, ValidationError{
            Field:   field,
            Message: "is required",
        })
    }
}

func (v *Validator) Email(field, value string) {
    if !strings.Contains(value, "@") {
        v.errors = append(v.errors, ValidationError{
            Field:   field,
            Message: "must be a valid email",
        })
    }
}

func (v *Validator) MinLength(field, value string, min int) {
    if len(value) < min {
        v.errors = append(v.errors, ValidationError{
            Field:   field,
            Message: fmt.Sprintf("must be at least %d characters", min),
        })
    }
}

func (v *Validator) Valid() bool {
    return len(v.errors) == 0
}

func (v *Validator) Errors() []ValidationError {
    return v.errors
}
```

### Example

```go
type CreateUserRequest struct {
    Name     string `json:"name"`
    Email    string `json:"email"`
    Password string `json:"password"`
}

func (req *CreateUserRequest) Validate() []ValidationError {
    v := &Validator{}
    v.Required("name", req.Name)
    v.Required("email", req.Email)
    v.Email("email", req.Email)
    v.Required("password", req.Password)
    v.MinLength("password", req.Password, 8)
    return v.Errors()
}

func createUserHandler(w http.ResponseWriter, r *http.Request) {
    var req CreateUserRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        WriteError(w, ErrBadRequest)
        return
    }

    if errors := req.Validate(); len(errors) > 0 {
        w.Header().Set("Content-Type", "application/json")
        w.WriteHeader(http.StatusUnprocessableEntity)
        json.NewEncoder(w).Encode(map[string]any{
            "error":   "Validation failed",
            "details": errors,
        })
        return
    }

    // Process valid request...
}
```

## Pattern 4: Graceful Shutdown

### When to Use

Always use graceful shutdown in production to complete in-flight requests.

### Implementation

```go
func main() {
    mux := http.NewServeMux()
    // Register handlers...

    server := &http.Server{
        Addr:         ":8080",
        Handler:      mux,
        ReadTimeout:  15 * time.Second,
        WriteTimeout: 15 * time.Second,
        IdleTimeout:  60 * time.Second,
    }

    // Start server in goroutine
    go func() {
        log.Printf("Server starting on %s", server.Addr)
        if err := server.ListenAndServe(); err != http.ErrServerClosed {
            log.Fatalf("Server error: %v", err)
        }
    }()

    // Wait for interrupt signal
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    log.Println("Shutting down server...")

    // Give outstanding requests 30 seconds to complete
    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := server.Shutdown(ctx); err != nil {
        log.Fatalf("Server forced to shutdown: %v", err)
    }

    log.Println("Server stopped gracefully")
}
```

## Pattern 5: Response Writer Wrapper

### When to Use

Wrap ResponseWriter to capture status codes and response sizes for logging/metrics.

### Implementation

```go
type responseWriter struct {
    http.ResponseWriter
    status      int
    wroteHeader bool
    size        int
}

func wrapResponseWriter(w http.ResponseWriter) *responseWriter {
    return &responseWriter{ResponseWriter: w, status: http.StatusOK}
}

func (rw *responseWriter) WriteHeader(code int) {
    if rw.wroteHeader {
        return
    }
    rw.status = code
    rw.wroteHeader = true
    rw.ResponseWriter.WriteHeader(code)
}

func (rw *responseWriter) Write(b []byte) (int, error) {
    if !rw.wroteHeader {
        rw.WriteHeader(http.StatusOK)
    }
    n, err := rw.ResponseWriter.Write(b)
    rw.size += n
    return n, err
}

// Implement Flusher if underlying writer supports it
func (rw *responseWriter) Flush() {
    if f, ok := rw.ResponseWriter.(http.Flusher); ok {
        f.Flush()
    }
}
```

## Anti-Patterns

### Anti-Pattern 1: Not Returning After Error

Description: Continuing execution after writing an error response.

```go
// Bad - continues executing after error
func badHandler(w http.ResponseWriter, r *http.Request) {
    id := r.URL.Query().Get("id")
    if id == "" {
        http.Error(w, "id required", http.StatusBadRequest)
        // Missing return! Continues to process...
    }

    user, err := getUser(id) // Runs even after error
    json.NewEncoder(w).Encode(user) // Writes again!
}
```

### Better Approach

```go
// Good - returns after error
func goodHandler(w http.ResponseWriter, r *http.Request) {
    id := r.URL.Query().Get("id")
    if id == "" {
        http.Error(w, "id required", http.StatusBadRequest)
        return // Important!
    }

    user, err := getUser(id)
    if err != nil {
        http.Error(w, "user not found", http.StatusNotFound)
        return // Important!
    }

    json.NewEncoder(w).Encode(user)
}
```

### Anti-Pattern 2: Global Mutable State

Description: Sharing mutable state without synchronization.

```go
// Bad - race condition
var requestCount int

func handler(w http.ResponseWriter, r *http.Request) {
    requestCount++ // Race condition!
    // ...
}
```

### Better Approach

```go
// Good - atomic operations or mutex
var requestCount atomic.Int64

func handler(w http.ResponseWriter, r *http.Request) {
    requestCount.Add(1)
    // ...
}
```
