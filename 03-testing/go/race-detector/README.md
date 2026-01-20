# Go Race Detector

Learn to detect and fix race conditions in Go using the built-in race detector.

## Learning Objectives

After completing this skill, you will be able to:
- Understand what race conditions are and why they're dangerous
- Use Go's race detector to identify data races
- Recognize common race condition patterns
- Fix race conditions using proper synchronization
- Write race-free concurrent code

## Prerequisites

- Go 1.22+
- Basic understanding of goroutines and channels
- Familiarity with the `sync` package

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests with race detector
make test-race

# Demonstrate race detection
make demo-race
```

## Concepts

### What is a Data Race?

A data race occurs when two or more goroutines access the same memory location concurrently, and at least one of the accesses is a write. Data races lead to undefined behavior and unpredictable bugs.

```go
// RACE CONDITION - Don't do this!
var counter int

func increment() {
    counter++ // Multiple goroutines read and write counter
}

func main() {
    for i := 0; i < 1000; i++ {
        go increment()
    }
    time.Sleep(time.Second)
    fmt.Println(counter) // Unpredictable result!
}
```

### The Race Detector

Go's race detector is a powerful tool built into the Go toolchain. Enable it with the `-race` flag:

```bash
go test -race ./...
go run -race main.go
go build -race
```

The race detector instruments memory accesses and reports when races are detected at runtime.

### Fixing Data Races

Common solutions include:
1. **Mutexes** - `sync.Mutex` or `sync.RWMutex`
2. **Atomic operations** - `sync/atomic` package
3. **Channels** - Communicate by sharing, don't share by communicating
4. **sync.Once** - For one-time initialization
5. **sync.Map** - Concurrent map access

```go
// Fixed with Mutex
var (
    counter int
    mu      sync.Mutex
)

func increment() {
    mu.Lock()
    counter++
    mu.Unlock()
}
```

## Examples

### Example 1: Basic Race Detection

Demonstrates a simple race condition and how the race detector catches it.

```bash
make example-1
make example-1-race  # Run with race detector
```

### Example 2: Common Race Patterns

Shows multiple common race condition patterns:
- Counter races
- Map races
- Slice races
- Struct field races

```bash
make example-2
```

### Example 3: Fixing Races

Demonstrates proper synchronization techniques to fix race conditions.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Fix a simple counter race using a mutex
2. **Exercise 2**: Fix a concurrent map access race
3. **Exercise 3**: Refactor a racy cache implementation to be thread-safe

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Mistake 1: Forgetting to Unlock

Always use `defer` to ensure mutexes are unlocked:

```go
// Bad - may forget to unlock on early return
mu.Lock()
if condition {
    return // Forgot to unlock!
}
mu.Unlock()

// Good - defer ensures unlock
mu.Lock()
defer mu.Unlock()
if condition {
    return // Mutex will be unlocked
}
```

### Mistake 2: Copying Mutexes

Mutexes must not be copied after first use:

```go
// Bad - copying mutex
type SafeCounter struct {
    mu sync.Mutex
    v  int
}

func process(c SafeCounter) { // Copies the mutex!
    c.mu.Lock()
    // ...
}

// Good - use pointer
func process(c *SafeCounter) {
    c.mu.Lock()
    // ...
}
```

### Mistake 3: Race in Closure

Variables captured by closures in goroutines can cause races:

```go
// Bad - race on loop variable
for i := 0; i < 10; i++ {
    go func() {
        fmt.Println(i) // Race on i
    }()
}

// Good - pass as argument
for i := 0; i < 10; i++ {
    go func(i int) {
        fmt.Println(i)
    }(i)
}
```

## Race Detector Limitations

- Runtime overhead (2-10x slowdown, 5-10x memory)
- Only detects races that actually occur during execution
- Cannot find races in code paths not executed
- Should be used with comprehensive tests

## Further Reading

- [Go Race Detector Documentation](https://go.dev/doc/articles/race_detector)
- [Data Race Detector](https://go.dev/blog/race-detector)
- Related skills in this repository:
  - [Testify Framework](../testify-framework/)
  - [Test Logger Init](../test-logger-init/)
