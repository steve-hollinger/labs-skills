---
name: managing-go-concurrency
description: Go's concurrency primitives and patterns for building concurrent applications. Use when writing or improving tests.
---

# Concurrency

## Quick Start
```go
func WorkerPool(numWorkers int, jobs <-chan Job, results chan<- Result) {
    var wg sync.WaitGroup
    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobs {
                results <- process(job)
            }
        }()
    }
    wg.Wait()
    close(results)
}
```


## Key Points
- Goroutines
- Channels
- Select

## Common Mistakes
1. **Not running with race detector** - Always use `go test -race` or `go run -race`
2. **Sending on closed channel** - Only close from sender side, use sync.Once for multiple senders
3. **Goroutine leaks** - Use context for cancellation, ensure channels are closed

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples