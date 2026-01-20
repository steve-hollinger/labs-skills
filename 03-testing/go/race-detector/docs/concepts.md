# Core Concepts - Race Detector

## Overview

This document covers the fundamental concepts of race conditions in Go and how to detect them using Go's built-in race detector.

## Concept 1: Data Races

### What It Is

A data race occurs when two or more goroutines access the same memory location concurrently, and at least one of the accesses is a write operation. This violates Go's memory model and results in undefined behavior.

### Why It Matters

Data races are among the most difficult bugs to diagnose:
- They're non-deterministic (may not reproduce consistently)
- Symptoms may appear far from the actual bug
- They can cause data corruption, crashes, or security vulnerabilities
- Traditional debugging techniques often mask them

### How It Works

```go
// Data race example
var counter int

func main() {
    // Goroutine 1: writes to counter
    go func() {
        counter = 1
    }()

    // Goroutine 2: reads from counter
    go func() {
        fmt.Println(counter)
    }()

    // No synchronization = data race!
}
```

The race detector instruments all memory accesses and maintains a happens-before graph. When it detects conflicting accesses without proper synchronization, it reports a race.

## Concept 2: Happens-Before Relationship

### What It Is

The "happens-before" relationship is Go's memory model concept that defines when one operation is guaranteed to be visible to another.

### Why It Matters

Understanding happens-before helps you write correct concurrent code. If operation A happens-before operation B, then A's effects are visible to B.

### Key Happens-Before Rules

1. **Within a goroutine**: Statements execute in program order
2. **Channel send**: Happens-before the corresponding receive completes
3. **Channel close**: Happens-before receive of zero value
4. **Mutex unlock**: Happens-before subsequent lock
5. **sync.Once**: The function completes happens-before any Once.Do returns

```go
var data string
var done = make(chan bool)

func setup() {
    data = "hello"  // (1)
    done <- true    // (2) Send happens-before...
}

func main() {
    go setup()
    <-done          // (3) ...receive completes
    fmt.Println(data)  // (4) Safe: (1) happens-before (4)
}
```

## Concept 3: The Race Detector

### What It Is

Go's race detector is a tool built into the Go toolchain that dynamically analyzes your program to find data races.

### Why It Matters

- Catches races that are otherwise extremely hard to find
- Provides precise stack traces showing both accesses
- Integrates seamlessly with go test, go run, go build

### How It Works

The race detector uses a technique called "happens-before" detection:

1. Instruments all memory accesses (reads/writes)
2. Tracks synchronization operations (locks, channels, atomics)
3. Maintains vector clocks for each goroutine
4. Reports when unordered conflicting accesses are detected

```bash
# Enable race detector
go test -race ./...
go run -race main.go
go build -race -o myapp
```

### Race Detector Output

When a race is detected:

```
==================
WARNING: DATA RACE
Read at 0x00c000014080 by goroutine 7:
  main.reader()
      /path/main.go:25 +0x3c
  main.main.func2()
      /path/main.go:33 +0x28

Previous write at 0x00c000014080 by goroutine 6:
  main.writer()
      /path/main.go:20 +0x48
  main.main.func1()
      /path/main.go:32 +0x28

Goroutine 7 (running) created at:
  main.main()
      /path/main.go:33 +0x88

Goroutine 6 (finished) created at:
  main.main()
      /path/main.go:32 +0x68
==================
```

## Concept 4: Synchronization Primitives

### Mutexes (sync.Mutex, sync.RWMutex)

Mutual exclusion locks ensure only one goroutine accesses protected data at a time.

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

func (c *SafeCounter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.v
}
```

### Atomic Operations (sync/atomic)

Lock-free operations for simple types like int64, uint64, pointers.

```go
var counter int64

func Inc() {
    atomic.AddInt64(&counter, 1)
}

func Load() int64 {
    return atomic.LoadInt64(&counter)
}
```

### Channels

Go's preferred synchronization mechanism for communication.

```go
func worker(jobs <-chan int, results chan<- int) {
    for j := range jobs {
        results <- j * 2
    }
}
```

### sync.Once

Ensures initialization code runs exactly once.

```go
var (
    instance *Config
    once     sync.Once
)

func GetConfig() *Config {
    once.Do(func() {
        instance = loadConfig()
    })
    return instance
}
```

## Concept 5: Common Race Patterns

### Counter Race

```go
// RACE!
var count int
for i := 0; i < 1000; i++ {
    go func() { count++ }()
}

// Fixed with atomic
var count int64
for i := 0; i < 1000; i++ {
    go func() { atomic.AddInt64(&count, 1) }()
}
```

### Map Race

```go
// RACE!
m := make(map[string]int)
go func() { m["key"] = 1 }()
go func() { _ = m["key"] }()

// Fixed with sync.Map
var m sync.Map
go func() { m.Store("key", 1) }()
go func() { v, _ := m.Load("key") }()
```

### Closure Race

```go
// RACE on loop variable!
for i := 0; i < 10; i++ {
    go func() {
        fmt.Println(i)
    }()
}

// Fixed: pass as argument
for i := 0; i < 10; i++ {
    go func(i int) {
        fmt.Println(i)
    }(i)
}
```

## Summary

Key takeaways:
1. Data races occur with concurrent unsynchronized access where at least one is a write
2. Use `-race` flag during development and in CI/CD
3. Choose appropriate synchronization: mutex, atomic, or channel
4. The race detector has overhead; use in testing, not production
5. Race-free code is not just correct, it's more maintainable
