// Solution for Exercise 2: Rate-Limited Worker Pool
//
// This solution implements a worker pool with token bucket rate limiting.

package main

import (
	"context"
	"fmt"
	"sync"
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

// RateLimiter controls the rate of operations using token bucket
type RateLimiter struct {
	tokens chan struct{}
	done   chan struct{}
	once   sync.Once
}

// NewRateLimiter creates a new rate limiter
func NewRateLimiter(ratePerSecond int) *RateLimiter {
	rl := &RateLimiter{
		tokens: make(chan struct{}, ratePerSecond), // Bucket size = rate
		done:   make(chan struct{}),
	}

	// Start token replenishment
	go rl.replenish(ratePerSecond)

	return rl
}

// replenish adds tokens at the specified rate
func (rl *RateLimiter) replenish(ratePerSecond int) {
	interval := time.Second / time.Duration(ratePerSecond)
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-rl.done:
			return
		case <-ticker.C:
			select {
			case rl.tokens <- struct{}{}:
				// Token added
			default:
				// Bucket full, discard token
			}
		}
	}
}

// Wait blocks until a token is available
func (rl *RateLimiter) Wait(ctx context.Context) error {
	select {
	case <-ctx.Done():
		return ctx.Err()
	case <-rl.tokens:
		return nil
	}
}

// Stop stops the rate limiter
func (rl *RateLimiter) Stop() {
	rl.once.Do(func() {
		close(rl.done)
	})
}

// RateLimitedPool is a worker pool with rate limiting
type RateLimitedPool struct {
	numWorkers  int
	rateLimiter *RateLimiter
	jobs        chan Job
	results     chan Result
	wg          sync.WaitGroup
	ctx         context.Context
	cancel      context.CancelFunc
}

// NewRateLimitedPool creates a new rate-limited pool
func NewRateLimitedPool(numWorkers, ratePerSecond, queueSize int) *RateLimitedPool {
	ctx, cancel := context.WithCancel(context.Background())
	return &RateLimitedPool{
		numWorkers:  numWorkers,
		rateLimiter: NewRateLimiter(ratePerSecond),
		jobs:        make(chan Job, queueSize),
		results:     make(chan Result, queueSize),
		ctx:         ctx,
		cancel:      cancel,
	}
}

// Start begins processing jobs
func (p *RateLimitedPool) Start() {
	for i := 0; i < p.numWorkers; i++ {
		p.wg.Add(1)
		go p.worker(i)
	}

	// Close results when all workers done
	go func() {
		p.wg.Wait()
		close(p.results)
	}()
}

// worker processes jobs with rate limiting
func (p *RateLimitedPool) worker(id int) {
	defer p.wg.Done()

	for {
		select {
		case <-p.ctx.Done():
			return
		case job, ok := <-p.jobs:
			if !ok {
				return
			}

			// Wait for rate limiter token
			if err := p.rateLimiter.Wait(p.ctx); err != nil {
				return
			}

			// Process the job
			startedAt := time.Now()
			result := p.processJob(job)
			result.StartedAt = startedAt
			result.Duration = time.Since(startedAt)

			select {
			case <-p.ctx.Done():
				return
			case p.results <- result:
			}
		}
	}
}

// processJob performs the actual work
func (p *RateLimitedPool) processJob(job Job) Result {
	// Simulate work (50-100ms)
	time.Sleep(50 * time.Millisecond)

	return Result{
		JobID:  job.ID,
		Output: fmt.Sprintf("processed %s", job.Data),
	}
}

// Submit adds a job to the pool
func (p *RateLimitedPool) Submit(job Job) error {
	select {
	case <-p.ctx.Done():
		return p.ctx.Err()
	case p.jobs <- job:
		return nil
	}
}

// Results returns the results channel
func (p *RateLimitedPool) Results() <-chan Result {
	return p.results
}

// Stop gracefully shuts down the pool
func (p *RateLimitedPool) Stop() {
	close(p.jobs)
	p.rateLimiter.Stop()
}

// StopNow immediately cancels all workers
func (p *RateLimitedPool) StopNow() {
	p.cancel()
	p.rateLimiter.Stop()
}

func main() {
	fmt.Println("Solution 2: Rate-Limited Worker Pool")
	fmt.Println("=====================================")
	fmt.Println()

	// Create pool: 3 workers, 5 ops/sec, queue of 20
	pool := NewRateLimitedPool(3, 5, 20)
	pool.Start()

	start := time.Now()

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

	count := 0
	for result := range pool.Results() {
		count++
		elapsed := result.StartedAt.Sub(start).Round(time.Millisecond)
		fmt.Printf("[%8v] Job %2d: %s (processed in %v)\n",
			elapsed,
			result.JobID,
			result.Output,
			result.Duration.Round(time.Millisecond))
	}

	totalTime := time.Since(start)
	fmt.Printf("\nProcessed %d jobs in %v\n", count, totalTime.Round(time.Millisecond))
	fmt.Printf("Effective rate: %.1f jobs/sec\n", float64(count)/totalTime.Seconds())
	fmt.Println("(Target rate: 5 jobs/sec)")
}
