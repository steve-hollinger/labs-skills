// Exercise 2: Rate-Limited Worker Pool
//
// Build a worker pool with rate limiting that controls how many
// operations can be performed per time window.
//
// Requirements:
// 1. Create a RateLimitedPool that:
//    - Has a configurable number of workers
//    - Limits operations to N per second
//    - Queues excess work instead of dropping
//
// 2. Configuration:
//    - numWorkers: number of concurrent workers
//    - rateLimit: max operations per second
//    - queueSize: max pending jobs
//
// 3. Methods:
//    - Submit(job): add a job to the pool
//    - Start(): begin processing
//    - Stop(): graceful shutdown
//    - Results(): channel to receive results
//
// 4. The rate limiter should use token bucket algorithm:
//    - Tokens are added at a fixed rate
//    - Each operation consumes one token
//    - Operations wait if no tokens available
//
// Hints:
// - Use time.Ticker for token replenishment
// - Use a buffered channel as the token bucket
// - Consider using context for cancellation

package main

import (
	"fmt"
	"time"
)

// Job represents work to be done
type Job struct {
	ID   int
	Data string
}

// Result represents the outcome of a job
type Result struct {
	JobID     int
	Output    string
	StartedAt time.Time
	Duration  time.Duration
	Error     error
}

// RateLimiter controls the rate of operations
type RateLimiter struct {
	// TODO: Add fields
	// - tokens channel (buffered)
	// - rate (operations per second)
	// - done channel
}

// NewRateLimiter creates a new rate limiter
func NewRateLimiter(ratePerSecond int) *RateLimiter {
	// TODO: Implement
	// 1. Create token bucket (buffered channel)
	// 2. Start token replenishment goroutine
	return &RateLimiter{}
}

// Wait blocks until a token is available
func (rl *RateLimiter) Wait() {
	// TODO: Implement
	// Block until a token is available
}

// Stop stops the rate limiter
func (rl *RateLimiter) Stop() {
	// TODO: Implement
}

// RateLimitedPool is a worker pool with rate limiting
type RateLimitedPool struct {
	// TODO: Add fields
	// - numWorkers
	// - rateLimiter
	// - jobs channel
	// - results channel
	// - WaitGroup
}

// NewRateLimitedPool creates a new rate-limited pool
func NewRateLimitedPool(numWorkers, ratePerSecond, queueSize int) *RateLimitedPool {
	// TODO: Implement
	return &RateLimitedPool{}
}

// Start begins processing jobs
func (p *RateLimitedPool) Start() {
	// TODO: Implement
	// 1. Start workers
	// 2. Each worker should wait on rate limiter before processing
}

// Submit adds a job to the pool
func (p *RateLimitedPool) Submit(job Job) error {
	// TODO: Implement
	return fmt.Errorf("not implemented")
}

// Results returns the results channel
func (p *RateLimitedPool) Results() <-chan Result {
	// TODO: Implement
	return nil
}

// Stop gracefully shuts down the pool
func (p *RateLimitedPool) Stop() {
	// TODO: Implement
}

func main() {
	fmt.Println("Exercise 2: Rate-Limited Worker Pool")
	fmt.Println("=====================================")
	fmt.Println()

	// Create pool: 3 workers, 5 ops/sec, queue of 20
	pool := NewRateLimitedPool(3, 5, 20)
	pool.Start()

	// Submit 15 jobs
	go func() {
		for i := 1; i <= 15; i++ {
			job := Job{ID: i, Data: fmt.Sprintf("task-%d", i)}
			if err := pool.Submit(job); err != nil {
				fmt.Printf("Failed to submit job %d: %v\n", i, err)
			}
		}
		// Stop after all jobs submitted
		pool.Stop()
	}()

	// Collect results
	fmt.Println("Processing jobs at 5/second rate limit...")
	fmt.Println()

	start := time.Now()
	count := 0

	for result := range pool.Results() {
		count++
		fmt.Printf("[%v] Job %d: %s (took %v)\n",
			result.StartedAt.Sub(start).Round(time.Millisecond),
			result.JobID,
			result.Output,
			result.Duration)
	}

	fmt.Printf("\nProcessed %d jobs in %v\n", count, time.Since(start))
	fmt.Println("(Should take ~3 seconds due to rate limiting)")
}
