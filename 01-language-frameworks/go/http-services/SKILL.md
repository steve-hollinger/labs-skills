---
name: building-http-services
description: This skill teaches building HTTP APIs using Go's standard library `net/http` package without external frameworks. Use when implementing authentication or verifying tokens.
---

# Http Services

## Quick Start
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

## Commands
```bash
make setup      # Download dependencies
make examples   # Run all examples
make example-1  # Run basic server example
make example-2  # Run middleware example
make example-3  # Run production API example
make test       # Run go test
```

## Key Points
- http.Handler Interface
- Middleware Pattern
- ServeMux Routing

## Common Mistakes
1. **Forgetting to return after error responses** - Always `return` after writing error responses
2. **Not handling all HTTP methods** - Explicitly check `r.Method` and return 405 for unsupported methods
3. **Writing headers after body** - Set all headers before calling Write() or WriteHeader()

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples