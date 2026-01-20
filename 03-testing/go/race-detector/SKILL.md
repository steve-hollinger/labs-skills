---
name: detecting-go-race-conditions
description: Race condition detection and prevention in Go using the built-in race detector. Use when writing or improving tests.
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