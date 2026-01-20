# CLAUDE.md - Go Race Detector

This skill teaches race condition detection and prevention in Go using the built-in race detector.

## Key Concepts

- **Data Race**: When two+ goroutines access the same memory concurrently with at least one write
- **Race Detector**: Go's `-race` flag that instruments memory accesses to detect races
- **Synchronization**: Using mutexes, atomics, and channels to prevent races
- **Happens-Before**: The ordering relationship that prevents data races

## Common Commands

```bash
make setup        # Download dependencies
make examples     # Run all examples
make example-1    # Run basic race detection example
make example-2    # Run common race patterns example
make example-3    # Run race fixing example
make test         # Run go test
make test-race    # Run tests with race detector (IMPORTANT)
make demo-race    # Demonstrate race detection output
make lint         # Run golangci-lint
make clean        # Remove build artifacts
```

## Project Structure

```
race-detector/
├── cmd/examples/
│   ├── example1/main.go    # Basic race detection
│   ├── example2/main.go    # Common race patterns
│   └── example3/main.go    # Fixing races
├── internal/
│   └── race/               # Race demonstration code
├── exercises/
│   ├── exercise1/          # Fix counter race
│   ├── exercise2/          # Fix map race
│   ├── exercise3/          # Fix cache race
│   └── solutions/
├── tests/
│   └── race_test.go        # Tests demonstrating races
└── docs/
    ├── concepts.md         # Deep dive on race concepts
    └── patterns.md         # Common patterns and fixes
```

## Code Patterns

### Pattern 1: Mutex Protection
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

### Pattern 2: Atomic Operations
```go
var counter int64

func Inc() {
    atomic.AddInt64(&counter, 1)
}

func Get() int64 {
    return atomic.LoadInt64(&counter)
}
```

### Pattern 3: Channel-Based Synchronization
```go
type Counter struct {
    ch chan func()
}

func NewCounter() *Counter {
    c := &Counter{ch: make(chan func())}
    go func() {
        var v int
        for f := range c.ch {
            f()
        }
    }()
    return c
}
```

## Common Mistakes

1. **Forgetting defer with mutex**
   - Why it happens: Early returns leave mutex locked
   - How to fix: Always use `defer mu.Unlock()` immediately after Lock

2. **Copying mutex by value**
   - Why it happens: Passing struct with mutex by value
   - How to fix: Pass by pointer or embed as pointer

3. **Loop variable capture**
   - Why it happens: Closure captures loop variable by reference
   - How to fix: Pass loop variable as function argument

4. **Read-only optimization that isn't**
   - Why it happens: Assuming reads don't need synchronization
   - How to fix: Use RWMutex or atomic loads

## When Users Ask About...

### "How do I enable the race detector?"
```bash
go test -race ./...
go run -race main.go
go build -race -o myapp
```
Explain that it's a runtime detector with overhead, so use in testing not production.

### "The race detector didn't find anything"
Explain that it only detects races that actually occur during execution. Suggest:
- Run more comprehensive tests
- Increase concurrency in tests
- Use fuzzing or property-based testing

### "How do I fix this race?"
1. Identify what's being shared
2. Choose synchronization method:
   - Mutex for complex operations
   - Atomic for simple counters/flags
   - Channel for communication patterns
3. Verify with `-race` flag

### "What's the performance impact?"
- 2-10x CPU slowdown
- 5-10x memory overhead
- Don't use in production
- Do use in CI/CD tests

## Testing Notes

- ALWAYS run `make test-race` not just `make test`
- Tests should exercise concurrent code paths
- Use `-count=N` to repeat tests and increase race detection chances
- Example: `go test -race -count=100 ./...`

## Dependencies

Key dependencies in go.mod:
- Standard library only (sync, sync/atomic)
- github.com/stretchr/testify v1.9.0 for test assertions

## Debugging Races

When a race is detected, output shows:
```
WARNING: DATA RACE
Write at 0x00c0000140a8 by goroutine 7:
  main.increment()
      /path/to/file.go:15 +0x3c

Previous read at 0x00c0000140a8 by goroutine 6:
  main.increment()
      /path/to/file.go:15 +0x2c

Goroutine 7 (running) created at:
  main.main()
      /path/to/file.go:22 +0x58
```

Help users read this output:
1. What operation caused the race (Write/Read)
2. Memory address involved
3. Stack trace showing where the access happened
4. Where the goroutine was created
