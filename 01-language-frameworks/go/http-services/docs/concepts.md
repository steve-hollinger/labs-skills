# Core Concepts

## Overview

This document covers the fundamental concepts for building HTTP services in Go using the standard library. Go's `net/http` package provides everything needed to build production-ready HTTP servers without external dependencies.

## Concept 1: The Handler Interface

### What It Is

The `http.Handler` interface is the cornerstone of Go HTTP servers. Any type that implements this interface can handle HTTP requests:

```go
type Handler interface {
    ServeHTTP(ResponseWriter, *Request)
}
```

### Why It Matters

This simple interface enables:
- Composition of handlers through middleware
- Easy testing with mock implementations
- Flexibility to use functions, structs, or any type as handlers

### How It Works

There are two common ways to create handlers:

**Using HandlerFunc adapter:**
```go
func myHandler(w http.ResponseWriter, r *http.Request) {
    w.Write([]byte("Hello, World!"))
}

// HandlerFunc is an adapter that lets functions implement Handler
http.Handle("/", http.HandlerFunc(myHandler))

// Shortcut using HandleFunc
http.HandleFunc("/", myHandler)
```

**Using a struct:**
```go
type UserHandler struct {
    store UserStore
}

func (h *UserHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case http.MethodGet:
        h.getUser(w, r)
    case http.MethodPost:
        h.createUser(w, r)
    default:
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
    }
}
```

## Concept 2: Request and Response

### What It Is

The `*http.Request` contains all information about the incoming request, and `http.ResponseWriter` is used to construct the response.

### Why It Matters

Understanding these types is essential for:
- Reading request data (headers, body, query params, path)
- Writing proper responses with correct headers and status codes
- Handling different content types

### How It Works

**Reading Request Data:**
```go
func handler(w http.ResponseWriter, r *http.Request) {
    // Method and path
    method := r.Method
    path := r.URL.Path

    // Query parameters
    query := r.URL.Query()
    name := query.Get("name")

    // Headers
    contentType := r.Header.Get("Content-Type")

    // Body (for POST/PUT)
    defer r.Body.Close()
    body, err := io.ReadAll(r.Body)
    if err != nil {
        http.Error(w, "Failed to read body", http.StatusBadRequest)
        return
    }

    // Context (for cancellation, values)
    ctx := r.Context()
}
```

**Writing Responses:**
```go
func handler(w http.ResponseWriter, r *http.Request) {
    // Set headers (must be before WriteHeader or Write)
    w.Header().Set("Content-Type", "application/json")
    w.Header().Set("X-Request-ID", "12345")

    // Set status code (optional, defaults to 200)
    w.WriteHeader(http.StatusCreated) // 201

    // Write body
    w.Write([]byte(`{"status": "created"}`))
}
```

## Concept 3: ServeMux (Router)

### What It Is

`http.ServeMux` is Go's built-in request router that matches URLs to handlers.

### Why It Matters

Proper routing is essential for organizing API endpoints and handling different URL patterns.

### How It Works

```go
func main() {
    mux := http.NewServeMux()

    // Exact match
    mux.HandleFunc("/health", healthHandler)

    // Subtree match (note trailing slash)
    mux.HandleFunc("/api/", apiHandler) // Matches /api/*, /api/users, etc.

    // In Go 1.22+, method and path patterns
    mux.HandleFunc("GET /users", listUsersHandler)
    mux.HandleFunc("POST /users", createUserHandler)
    mux.HandleFunc("GET /users/{id}", getUserHandler)
    mux.HandleFunc("PUT /users/{id}", updateUserHandler)
    mux.HandleFunc("DELETE /users/{id}", deleteUserHandler)

    http.ListenAndServe(":8080", mux)
}

// Accessing path parameters (Go 1.22+)
func getUserHandler(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id")
    // ...
}
```

## Concept 4: JSON Handling

### What It Is

The `encoding/json` package provides encoding and decoding of JSON data for API request/response handling.

### Why It Matters

Most modern APIs use JSON for data exchange. Proper JSON handling ensures:
- Correct content negotiation
- Proper error handling for malformed data
- Clean serialization of Go types

### How It Works

**Decoding Request Body:**
```go
type CreateUserRequest struct {
    Name  string `json:"name"`
    Email string `json:"email"`
}

func createUser(w http.ResponseWriter, r *http.Request) {
    var req CreateUserRequest

    // Decode JSON body
    decoder := json.NewDecoder(r.Body)
    decoder.DisallowUnknownFields() // Strict parsing
    if err := decoder.Decode(&req); err != nil {
        http.Error(w, "Invalid JSON: "+err.Error(), http.StatusBadRequest)
        return
    }

    // Validate required fields
    if req.Name == "" || req.Email == "" {
        http.Error(w, "name and email are required", http.StatusBadRequest)
        return
    }

    // Process request...
}
```

**Encoding Response:**
```go
type User struct {
    ID        int       `json:"id"`
    Name      string    `json:"name"`
    Email     string    `json:"email"`
    CreatedAt time.Time `json:"created_at"`
}

func getUser(w http.ResponseWriter, r *http.Request) {
    user := User{
        ID:        1,
        Name:      "John Doe",
        Email:     "john@example.com",
        CreatedAt: time.Now(),
    }

    w.Header().Set("Content-Type", "application/json")
    if err := json.NewEncoder(w).Encode(user); err != nil {
        http.Error(w, "Failed to encode response", http.StatusInternalServerError)
        return
    }
}
```

## Concept 5: Context

### What It Is

The `context.Context` in each request carries deadlines, cancellation signals, and request-scoped values.

### Why It Matters

Context enables:
- Request cancellation when clients disconnect
- Timeout handling for long-running operations
- Passing request-scoped data through middleware chain

### How It Works

```go
func handler(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()

    // Check for cancellation
    select {
    case <-ctx.Done():
        http.Error(w, "Request cancelled", http.StatusServiceUnavailable)
        return
    default:
    }

    // Pass context to downstream operations
    user, err := fetchUserFromDB(ctx, userID)
    if err != nil {
        if ctx.Err() == context.Canceled {
            return // Client disconnected
        }
        http.Error(w, "Database error", http.StatusInternalServerError)
        return
    }
}

// Adding values via middleware
func WithRequestID(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        ctx := context.WithValue(r.Context(), "requestID", uuid.New().String())
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

## Summary

Key takeaways:

1. **Handler Interface**: The foundation - implement `ServeHTTP` or use `HandlerFunc`
2. **Request/Response**: Read from Request, write to ResponseWriter (headers before body)
3. **ServeMux**: Built-in router with pattern matching (enhanced in Go 1.22+)
4. **JSON**: Use `encoding/json` with proper error handling
5. **Context**: Carry deadlines, cancellation, and request-scoped values

These concepts form the building blocks for all Go HTTP services. Master them before exploring third-party frameworks.
