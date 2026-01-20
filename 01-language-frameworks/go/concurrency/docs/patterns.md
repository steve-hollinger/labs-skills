# Common Patterns

## Overview

This document covers common concurrency patterns in Go and when to use them.

## Pattern 1: Worker Pool

### When to Use

Use a worker pool when you need to:
- Process many tasks with limited concurrency
- Control resource usage (connections, memory)
- Implement backpressure

### Implementation

```go
type Job struct {
    ID   int
    Data string
}

type Result struct {
    JobID int
    Value string
    Error error
}

func WorkerPool(numWorkers int, jobs <-chan Job, results chan<- Result) {
    var wg sync.WaitGroup

    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func(workerID int) {
            defer wg.Done()
            for job := range jobs {
                result := processJob(job)
                results <- result
            }
        }(i)
    }

    // Close results when all workers done
    go func() {
        wg.Wait()
        close(results)
    }()
}

func processJob(job Job) Result {
    // Process the job
    return Result{JobID: job.ID, Value: "processed"}
}
```

### Example Usage

```go
func main() {
    jobs := make(chan Job, 100)
    results := make(chan Result, 100)

    // Start worker pool
    WorkerPool(5, jobs, results)

    // Send jobs
    go func() {
        for i := 0; i < 50; i++ {
            jobs <- Job{ID: i, Data: fmt.Sprintf("job-%d", i)}
        }
        close(jobs)
    }()

    // Collect results
    for result := range results {
        fmt.Printf("Result: %+v\n", result)
    }
}
```

### Pitfalls to Avoid

- Don't forget to close the jobs channel
- Always close results after workers complete
- Handle panics within workers

## Pattern 2: Fan-out/Fan-in

### When to Use

Use fan-out/fan-in when you need to:
- Distribute work across multiple goroutines
- Collect results from multiple sources
- Implement parallel processing pipelines

### Implementation

```go
// Fan-out: distribute input to multiple workers
func FanOut(input <-chan int, numWorkers int) []<-chan int {
    outputs := make([]<-chan int, numWorkers)
    for i := 0; i < numWorkers; i++ {
        outputs[i] = worker(input)
    }
    return outputs
}

func worker(input <-chan int) <-chan int {
    output := make(chan int)
    go func() {
        defer close(output)
        for n := range input {
            output <- process(n)
        }
    }()
    return output
}

// Fan-in: merge multiple channels into one
func FanIn(inputs ...<-chan int) <-chan int {
    output := make(chan int)
    var wg sync.WaitGroup

    for _, ch := range inputs {
        wg.Add(1)
        go func(c <-chan int) {
            defer wg.Done()
            for n := range c {
                output <- n
            }
        }(ch)
    }

    go func() {
        wg.Wait()
        close(output)
    }()

    return output
}
```

### Example Usage

```go
func main() {
    // Create input channel
    input := make(chan int)
    go func() {
        defer close(input)
        for i := 0; i < 100; i++ {
            input <- i
        }
    }()

    // Fan out to 4 workers
    outputs := FanOut(input, 4)

    // Fan in results
    results := FanIn(outputs...)

    // Collect results
    for result := range results {
        fmt.Println(result)
    }
}
```

## Pattern 3: Pipeline

### When to Use

Use pipelines when you need to:
- Process data through multiple stages
- Chain transformations
- Enable concurrent processing at each stage

### Implementation

```go
// Generator: produces values
func Generator(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            out <- n
        }
    }()
    return out
}

// Square: transform stage
func Square(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            out <- n * n
        }
    }()
    return out
}

// Filter: filter stage
func Filter(in <-chan int, predicate func(int) bool) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            if predicate(n) {
                out <- n
            }
        }
    }()
    return out
}

// Sink: consume results
func Sink(in <-chan int) {
    for n := range in {
        fmt.Println(n)
    }
}
```

### Example Usage

```go
func main() {
    // Build pipeline: generate -> square -> filter (even) -> print
    numbers := Generator(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    squared := Square(numbers)
    evens := Filter(squared, func(n int) bool { return n%2 == 0 })
    Sink(evens)
}
```

## Pattern 4: Semaphore (Bounded Concurrency)

### When to Use

Use a semaphore when you need to:
- Limit concurrent access to a resource
- Implement rate limiting
- Control parallelism without a full worker pool

### Implementation

```go
type Semaphore struct {
    sem chan struct{}
}

func NewSemaphore(max int) *Semaphore {
    return &Semaphore{
        sem: make(chan struct{}, max),
    }
}

func (s *Semaphore) Acquire() {
    s.sem <- struct{}{}
}

func (s *Semaphore) Release() {
    <-s.sem
}

func (s *Semaphore) TryAcquire() bool {
    select {
    case s.sem <- struct{}{}:
        return true
    default:
        return false
    }
}
```

### Example Usage

```go
func main() {
    sem := NewSemaphore(3) // Max 3 concurrent operations
    var wg sync.WaitGroup

    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            sem.Acquire()
            defer sem.Release()

            fmt.Printf("Worker %d starting\n", id)
            time.Sleep(time.Second)
            fmt.Printf("Worker %d done\n", id)
        }(i)
    }

    wg.Wait()
}
```

## Pattern 5: Timeout and Cancellation

### When to Use

Use timeout/cancellation patterns when you need to:
- Prevent operations from running forever
- Cancel work on user request or shutdown
- Implement graceful degradation

### Implementation

```go
func DoWorkWithTimeout(ctx context.Context, timeout time.Duration) (string, error) {
    ctx, cancel := context.WithTimeout(ctx, timeout)
    defer cancel()

    resultCh := make(chan string, 1)
    errCh := make(chan error, 1)

    go func() {
        result, err := doActualWork()
        if err != nil {
            errCh <- err
            return
        }
        resultCh <- result
    }()

    select {
    case result := <-resultCh:
        return result, nil
    case err := <-errCh:
        return "", err
    case <-ctx.Done():
        return "", ctx.Err()
    }
}
```

### Cancellable Long-Running Work

```go
func LongRunningWork(ctx context.Context) error {
    ticker := time.NewTicker(100 * time.Millisecond)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            // Clean up and return
            return ctx.Err()
        case <-ticker.C:
            if err := doWorkUnit(); err != nil {
                return err
            }
        }
    }
}
```

## Anti-Patterns

### Anti-Pattern 1: Goroutine Leak

```go
// Bad - goroutine leaks if response is slow
func fetchWithTimeout(url string) (string, error) {
    ch := make(chan string)
    go func() {
        resp := fetch(url) // May take forever
        ch <- resp         // Blocks if timeout occurred
    }()

    select {
    case resp := <-ch:
        return resp, nil
    case <-time.After(time.Second):
        return "", errors.New("timeout")
    }
}
```

### Better Approach

```go
// Good - use buffered channel or context
func fetchWithTimeout(ctx context.Context, url string) (string, error) {
    ch := make(chan string, 1) // Buffered so goroutine can exit

    go func() {
        resp := fetch(url)
        select {
        case ch <- resp:
        default: // Drop if nobody listening
        }
    }()

    select {
    case resp := <-ch:
        return resp, nil
    case <-ctx.Done():
        return "", ctx.Err()
    }
}
```

### Anti-Pattern 2: Shared State Without Protection

```go
// Bad - race condition
var results []string
var wg sync.WaitGroup

for i := 0; i < 10; i++ {
    wg.Add(1)
    go func() {
        defer wg.Done()
        results = append(results, doWork()) // Race!
    }()
}
```

### Better Approach

```go
// Good - use channel to collect results
results := make(chan string, 10)
var wg sync.WaitGroup

for i := 0; i < 10; i++ {
    wg.Add(1)
    go func() {
        defer wg.Done()
        results <- doWork()
    }()
}

go func() {
    wg.Wait()
    close(results)
}()

var collected []string
for r := range results {
    collected = append(collected, r)
}
```
