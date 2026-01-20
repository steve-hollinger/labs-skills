# CLAUDE.md - Go Concurrency

This skill teaches Go's concurrency primitives and patterns for building concurrent applications.

## Key Concepts

- **Goroutines**: Lightweight threads managed by Go runtime
- **Channels**: Typed conduits for goroutine communication
- **Select**: Multiplexing channel operations
- **sync Package**: WaitGroup, Mutex, RWMutex, Once, Cond
- **atomic Package**: Low-level atomic memory operations
- **Context**: Cancellation and timeout propagation

## Common Commands

```bash
make setup      # Download dependencies
make examples   # Run all examples
make example-1  # Run goroutines/channels example
make example-2  # Run worker pool example
make example-3  # Run pipeline example
make test       # Run go test
make test-race  # Run tests with race detector (important!)
make lint       # Run golangci-lint
make clean      # Remove build artifacts
```

## Project Structure

```
concurrency/
├── cmd/examples/
│   ├── example1/main.go     # Goroutines and channels
│   ├── example2/main.go     # Worker pool
│   └── example3/main.go     # Fan-out/fan-in pipeline
├── pkg/
│   ├── pool/                # Worker pool implementation
│   └── pipeline/            # Pipeline utilities
├── exercises/
│   ├── exercise1/           # Concurrent URL fetcher
│   ├── exercise2/           # Rate-limited worker pool
│   ├── exercise3/           # File processing pipeline
│   └── solutions/
├── tests/
│   └── *_test.go
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Worker Pool
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

### Pattern 2: Fan-out/Fan-in
```go
func FanOut(input <-chan int, n int) []<-chan int {
    outputs := make([]<-chan int, n)
    for i := 0; i < n; i++ {
        outputs[i] = worker(input)
    }
    return outputs
}

func FanIn(inputs ...<-chan int) <-chan int {
    out := make(chan int)
    var wg sync.WaitGroup
    for _, ch := range inputs {
        wg.Add(1)
        go func(c <-chan int) {
            defer wg.Done()
            for v := range c {
                out <- v
            }
        }(ch)
    }
    go func() {
        wg.Wait()
        close(out)
    }()
    return out
}
```

### Pattern 3: Context Cancellation
```go
func DoWork(ctx context.Context) error {
    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
            // Do work
            if err := processItem(); err != nil {
                return err
            }
        }
    }
}
```

## Common Mistakes

1. **Not running with race detector**
   - Why it happens: Race conditions are hard to spot
   - How to fix: Always use `go test -race` or `go run -race`

2. **Sending on closed channel**
   - Why it happens: Multiple producers, unclear ownership
   - How to fix: Only close from sender side, use sync.Once for multiple senders

3. **Goroutine leaks**
   - Why it happens: Goroutines blocked on channel operations forever
   - How to fix: Use context for cancellation, ensure channels are closed

4. **Deadlocks**
   - Why it happens: Circular wait on channels or locks
   - How to fix: Use buffered channels, consistent lock ordering

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make example-1` for basic goroutine/channel patterns.

### "How do I detect race conditions?"
Always use `make test-race`. The race detector finds most concurrency bugs.

### "When should I use channels vs mutexes?"
- Use channels to transfer ownership of data
- Use mutexes to protect shared state
- Rule of thumb: "Don't communicate by sharing memory; share memory by communicating."

### "How do I limit concurrent operations?"
Use a semaphore pattern with buffered channels or a worker pool (see Example 2).

### "How do I handle timeouts?"
Use `context.WithTimeout` or `time.After` with select. See docs/patterns.md.

## Testing Notes

- ALWAYS run tests with race detector: `make test-race`
- Use table-driven tests for concurrent operations
- Test cancellation paths thoroughly
- Use `-count=100` to catch flaky tests

## Dependencies

Key dependencies in go.mod:
- github.com/stretchr/testify: Testing assertions
- Standard library only for concurrency primitives
