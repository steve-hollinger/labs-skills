# Go Concurrency

Master Go's powerful concurrency primitives. This skill covers goroutines, channels, synchronization, and advanced patterns like worker pools and pipelines.

## Learning Objectives

After completing this skill, you will be able to:
- Create and manage goroutines effectively
- Use channels for communication and synchronization
- Implement common concurrency patterns (worker pools, fan-out/fan-in)
- Avoid race conditions with mutexes and atomic operations
- Use select for non-blocking operations and timeouts
- Design concurrent pipelines for data processing

## Prerequisites

- Go 1.22+
- Solid understanding of Go basics (functions, structs, interfaces)
- Basic understanding of concurrent programming concepts

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests with race detector
make test-race
```

## Concepts

### Goroutines

Goroutines are lightweight threads managed by the Go runtime:

```go
func main() {
    // Start a goroutine
    go func() {
        fmt.Println("Hello from goroutine!")
    }()

    // Wait to prevent main from exiting
    time.Sleep(100 * time.Millisecond)
}
```

### Channels

Channels are typed conduits for communication between goroutines:

```go
// Create a channel
ch := make(chan int)

// Send value
go func() {
    ch <- 42
}()

// Receive value
value := <-ch
```

### Select Statement

Select lets you wait on multiple channel operations:

```go
select {
case msg := <-ch1:
    fmt.Println("Received from ch1:", msg)
case msg := <-ch2:
    fmt.Println("Received from ch2:", msg)
case <-time.After(1 * time.Second):
    fmt.Println("Timeout!")
default:
    fmt.Println("No message ready")
}
```

### WaitGroup

WaitGroup waits for a collection of goroutines to finish:

```go
var wg sync.WaitGroup

for i := 0; i < 3; i++ {
    wg.Add(1)
    go func(id int) {
        defer wg.Done()
        fmt.Printf("Worker %d done\n", id)
    }(i)
}

wg.Wait() // Block until all goroutines complete
```

## Examples

### Example 1: Goroutines and Channels

Basic patterns for starting goroutines and communicating via channels.

```bash
make example-1
```

### Example 2: Worker Pool

Implementing a worker pool for concurrent task processing.

```bash
make example-2
```

### Example 3: Fan-out/Fan-in Pipeline

Building concurrent data processing pipelines.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Implement a concurrent URL fetcher with timeout handling
2. **Exercise 2**: Build a rate-limited worker pool with configurable concurrency
3. **Exercise 3**: Create a pipeline that processes files concurrently

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Forgetting to Close Channels

Always close channels when no more values will be sent:

```go
// Bad - consumers may block forever
func produce(ch chan int) {
    for i := 0; i < 10; i++ {
        ch <- i
    }
    // Missing close(ch)
}

// Good - signal completion
func produce(ch chan int) {
    defer close(ch)
    for i := 0; i < 10; i++ {
        ch <- i
    }
}
```

### Race Conditions

Use the race detector to find data races:

```go
// Bad - race condition
var counter int
for i := 0; i < 1000; i++ {
    go func() {
        counter++ // Race!
    }()
}

// Good - use atomic or mutex
var counter atomic.Int64
for i := 0; i < 1000; i++ {
    go func() {
        counter.Add(1)
    }()
}
```

### Goroutine Leaks

Always ensure goroutines can exit:

```go
// Bad - goroutine leaks if context cancelled
go func() {
    for {
        ch <- work() // May block forever
    }
}()

// Good - check for cancellation
go func() {
    for {
        select {
        case ch <- work():
        case <-ctx.Done():
            return
        }
    }
}()
```

## Further Reading

- [Go Concurrency Patterns](https://go.dev/blog/pipelines)
- [Go Memory Model](https://go.dev/ref/mem)
- Related skills in this repository:
  - [Go HTTP Services](../http-services/)
  - [Hybrid Authentication](../../../02-architecture-design/hybrid-authentication/)
