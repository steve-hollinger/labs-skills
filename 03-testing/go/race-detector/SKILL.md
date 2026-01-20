---
name: detecting-go-race-conditions
description: This skill teaches race condition detection and prevention in Go using the built-in race detector. Use when writing or improving tests.
---

# Race Detector

## Quick Start
```go
type SafeCounter struct {
    mu sync.Mutex
    v  int
}

func (c *SafeCounter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.v++
}
```

## Commands
```bash
make setup        # Download dependencies
make examples     # Run all examples
make example-1    # Run basic race detection example
make example-2    # Run common race patterns example
make example-3    # Run race fixing example
make test         # Run go test
```

## Key Points
- Data Race
- Race Detector
- Synchronization

## Common Mistakes
1. **Forgetting defer with mutex** - Always use `defer mu.Unlock()` immediately after Lock
2. **Copying mutex by value** - Pass by pointer or embed as pointer
3. **Loop variable capture** - Pass loop variable as function argument

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples