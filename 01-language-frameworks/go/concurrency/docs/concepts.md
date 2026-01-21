# Core Concepts

## Overview

Go's concurrency model is based on CSP (Communicating Sequential Processes), where goroutines communicate by sending values through channels rather than sharing memory directly. This document covers the fundamental concepts.

## Concept 1: Goroutines

### What It Is

A goroutine is a lightweight thread managed by the Go runtime. They're much cheaper than OS threads (starting at ~2KB stack) and the runtime multiplexes thousands of goroutines onto a smaller number of OS threads.

### Why It Matters

Goroutines enable:
- High concurrency with low overhead
- Simple concurrent code without complex thread management
- Efficient use of multicore processors

### How It Works

```go
// Start a goroutine with the go keyword
go func() {
    // This runs concurrently
    fmt.Println("Hello from goroutine")
}()

// Named function as goroutine
go processItem(item)

// Method as goroutine
go server.handleRequest(conn)
```

**Important**: The main function is itself a goroutine. When main returns, all other goroutines are terminated immediately.

```go
func main() {
    go longRunningTask() // This may not complete!
    // main exits immediately, killing the goroutine
}

// Fix: wait for goroutines to complete
func main() {
    done := make(chan bool)
    go func() {
        longRunningTask()
        done <- true
    }()
    <-done // Wait for completion
}
```

## Concept 2: Channels

### What It Is

Channels are typed conduits through which goroutines communicate. They provide synchronization and data transfer in a single operation.

### Why It Matters

Channels enable:
- Safe data transfer between goroutines
- Synchronization without explicit locks
- Clear ownership transfer of data

### How It Works

```go
// Create an unbuffered channel
ch := make(chan int)

// Create a buffered channel (capacity 10)
ch := make(chan int, 10)

// Send a value (blocks until receiver ready for unbuffered)
ch <- 42

// Receive a value (blocks until value available)
value := <-ch

// Receive with ok idiom (check if channel closed)
value, ok := <-ch
if !ok {
    fmt.Println("Channel closed")
}

// Range over channel (exits when channel closed)
for value := range ch {
    process(value)
}

// Close channel (signals no more values)
close(ch)
```

**Channel Direction**: Restrict channel operations in function signatures:

```go
// Send-only channel
func producer(out chan<- int) {
    out <- 42
}

// Receive-only channel
func consumer(in <-chan int) {
    value := <-in
}
```

## Concept 3: Select Statement

### What It Is

Select lets a goroutine wait on multiple channel operations simultaneously, proceeding with whichever operation is ready first.

### Why It Matters

Select enables:
- Non-blocking channel operations
- Timeout handling
- Multiplexing multiple channels
- Graceful cancellation

### How It Works

```go
select {
case msg := <-ch1:
    // Received from ch1
    fmt.Println("ch1:", msg)
case msg := <-ch2:
    // Received from ch2
    fmt.Println("ch2:", msg)
case ch3 <- value:
    // Sent to ch3
    fmt.Println("sent to ch3")
case <-time.After(1 * time.Second):
    // Timeout
    fmt.Println("timeout")
default:
    // No channel ready (non-blocking)
    fmt.Println("no channel ready")
}
```

**Common Patterns**:

```go
// Timeout pattern
select {
case result := <-ch:
    return result, nil
case <-time.After(5 * time.Second):
    return nil, errors.New("timeout")
}

// Cancellation pattern
select {
case result := <-ch:
    return result
case <-ctx.Done():
    return ctx.Err()
}

// Non-blocking send
select {
case ch <- value:
    // Sent successfully
default:
    // Channel full, handle backpressure
}
```

## Concept 4: Synchronization Primitives

### What It Is

The `sync` package provides traditional synchronization primitives when channels aren't the best fit.

### Why It Matters

Synchronization primitives are useful for:
- Protecting shared state (Mutex)
- Waiting for groups of goroutines (WaitGroup)
- One-time initialization (Once)
- Signaling conditions (Cond)

### How It Works

**WaitGroup**:
```go
var wg sync.WaitGroup

for i := 0; i < 5; i++ {
    wg.Add(1)
    go func(id int) {
        defer wg.Done()
        doWork(id)
    }(i)
}

wg.Wait() // Block until all goroutines complete
```

**Mutex**:
```go
type SafeCounter struct {
    mu    sync.Mutex
    count int
}

func (c *SafeCounter) Increment() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}

func (c *SafeCounter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.count
}
```

**RWMutex** (for read-heavy workloads):
```go
type Cache struct {
    mu   sync.RWMutex
    data map[string]string
}

func (c *Cache) Get(key string) (string, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    value, ok := c.data[key]
    return value, ok
}

func (c *Cache) Set(key, value string) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.data[key] = value
}
```

**Once**:
```go
var once sync.Once
var config *Config

func GetConfig() *Config {
    once.Do(func() {
        config = loadConfig() // Only runs once
    })
    return config
}
```

## Concept 5: Atomic Operations

### What It Is

The `sync/atomic` package provides low-level atomic memory operations for simple counters and flags.

### Why It Matters

Atomic operations are:
- Lock-free (no blocking)
- Faster than mutexes for simple operations
- Safe for concurrent access

### How It Works

```go
var counter atomic.Int64

// Increment
counter.Add(1)

// Load current value
value := counter.Load()

// Store value
counter.Store(100)

// Compare and swap
swapped := counter.CompareAndSwap(100, 200)

// Atomic pointer
var ptr atomic.Pointer[Config]
ptr.Store(&Config{...})
config := ptr.Load()
```

## Concept 6: Context

### What It Is

The `context` package provides a standard way to propagate cancellation signals and deadlines across API boundaries.

### Why It Matters

Context enables:
- Cancellation propagation
- Deadline/timeout enforcement
- Request-scoped values

### How It Works

```go
// Create context with cancellation
ctx, cancel := context.WithCancel(context.Background())
defer cancel() // Always call cancel to release resources

// Create context with timeout
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

// Create context with deadline
deadline := time.Now().Add(10 * time.Second)
ctx, cancel := context.WithDeadline(context.Background(), deadline)
defer cancel()

// Check for cancellation in goroutine
func worker(ctx context.Context) error {
    for {
        select {
        case <-ctx.Done():
            return ctx.Err() // context.Canceled or context.DeadlineExceeded
        default:
            if err := doWork(); err != nil {
                return err
            }
        }
    }
}
```

## Summary

Key takeaways:

1. **Goroutines**: Lightweight, cheap to create, managed by runtime
2. **Channels**: First-class synchronization and communication
3. **Select**: Multiplex channel operations, handle timeouts
4. **sync Package**: WaitGroup, Mutex, RWMutex, Once for traditional sync
5. **atomic Package**: Lock-free operations for simple cases
6. **Context**: Cancellation and timeout propagation

Remember: "Don't communicate by sharing memory; share memory by communicating."
