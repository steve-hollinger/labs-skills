// Example 2: Worker Pool
//
// This example demonstrates implementing a worker pool pattern in Go:
// - Fixed number of workers processing jobs concurrently
// - Job queue with backpressure
// - Result collection
// - Graceful shutdown
package main

import (
	"context"
	"fmt"
	"math/rand"
	"sync"
	"time"
)

// Job represents a unit of work
type Job struct {
	ID   int
	Data string
}

// Result represents the outcome of processing a job
type Result struct {
	JobID      int
	Output     string
	WorkerID   int
	Duration   time.Duration
	Error      error
}

// SimpleWorkerPool demonstrates the basic worker pool pattern
func SimpleWorkerPool() {
	fmt.Println("1. Simple Worker Pool")
	fmt.Println("---------------------")

	const numWorkers = 3
	const numJobs = 10

	jobs := make(chan Job, numJobs)
	results := make(chan Result, numJobs)

	// Start workers
	var wg sync.WaitGroup
	for w := 1; w <= numWorkers; w++ {
		wg.Add(1)
		go worker(w, jobs, results, &wg)
	}

	// Send jobs
	for j := 1; j <= numJobs; j++ {
		jobs <- Job{ID: j, Data: fmt.Sprintf("task-%d", j)}
	}
	close(jobs) // Signal no more jobs

	// Wait for all workers to finish, then close results
	go func() {
		wg.Wait()
		close(results)
	}()

	// Collect results
	for result := range results {
		fmt.Printf("  Job %d completed by worker %d in %v\n",
			result.JobID, result.WorkerID, result.Duration)
	}
	fmt.Println()
}

// worker processes jobs from the jobs channel
func worker(id int, jobs <-chan Job, results chan<- Result, wg *sync.WaitGroup) {
	defer wg.Done()

	for job := range jobs {
		start := time.Now()

		// Simulate work with random duration
		duration := time.Duration(rand.Intn(100)) * time.Millisecond
		time.Sleep(duration)

		results <- Result{
			JobID:    job.ID,
			Output:   fmt.Sprintf("processed %s", job.Data),
			WorkerID: id,
			Duration: time.Since(start),
		}
	}
}

// WorkerPool is a reusable worker pool implementation
type WorkerPool struct {
	numWorkers int
	jobs       chan Job
	results    chan Result
	wg         sync.WaitGroup
	ctx        context.Context
	cancel     context.CancelFunc
}

// NewWorkerPool creates a new worker pool
func NewWorkerPool(numWorkers, jobQueueSize int) *WorkerPool {
	ctx, cancel := context.WithCancel(context.Background())
	return &WorkerPool{
		numWorkers: numWorkers,
		jobs:       make(chan Job, jobQueueSize),
		results:    make(chan Result, jobQueueSize),
		ctx:        ctx,
		cancel:     cancel,
	}
}

// Start initializes the workers
func (p *WorkerPool) Start() {
	for i := 1; i <= p.numWorkers; i++ {
		p.wg.Add(1)
		go p.runWorker(i)
	}

	// Close results when all workers done
	go func() {
		p.wg.Wait()
		close(p.results)
	}()
}

func (p *WorkerPool) runWorker(id int) {
	defer p.wg.Done()

	for {
		select {
		case <-p.ctx.Done():
			return
		case job, ok := <-p.jobs:
			if !ok {
				return
			}
			result := p.processJob(id, job)
			select {
			case p.results <- result:
			case <-p.ctx.Done():
				return
			}
		}
	}
}

func (p *WorkerPool) processJob(workerID int, job Job) Result {
	start := time.Now()

	// Simulate work
	duration := time.Duration(50+rand.Intn(100)) * time.Millisecond
	time.Sleep(duration)

	return Result{
		JobID:    job.ID,
		Output:   fmt.Sprintf("processed %s", job.Data),
		WorkerID: workerID,
		Duration: time.Since(start),
	}
}

// Submit adds a job to the pool
func (p *WorkerPool) Submit(job Job) error {
	select {
	case <-p.ctx.Done():
		return p.ctx.Err()
	case p.jobs <- job:
		return nil
	}
}

// Results returns the results channel
func (p *WorkerPool) Results() <-chan Result {
	return p.results
}

// Stop gracefully shuts down the pool
func (p *WorkerPool) Stop() {
	close(p.jobs)
}

// Cancel immediately stops all workers
func (p *WorkerPool) Cancel() {
	p.cancel()
}

// ReusableWorkerPoolDemo demonstrates the reusable pool
func ReusableWorkerPoolDemo() {
	fmt.Println("2. Reusable Worker Pool")
	fmt.Println("-----------------------")

	pool := NewWorkerPool(4, 20)
	pool.Start()

	// Submit jobs
	go func() {
		for i := 1; i <= 15; i++ {
			if err := pool.Submit(Job{ID: i, Data: fmt.Sprintf("task-%d", i)}); err != nil {
				fmt.Printf("  Failed to submit job %d: %v\n", i, err)
			}
		}
		pool.Stop()
	}()

	// Collect results
	var completed int
	for result := range pool.Results() {
		completed++
		fmt.Printf("  [%d/%d] Job %d: %s (worker %d, %v)\n",
			completed, 15, result.JobID, result.Output, result.WorkerID, result.Duration)
	}

	fmt.Printf("  Completed %d jobs\n", completed)
	fmt.Println()
}

// WorkerPoolWithErrorHandling demonstrates error handling
func WorkerPoolWithErrorHandling() {
	fmt.Println("3. Worker Pool with Error Handling")
	fmt.Println("-----------------------------------")

	const numWorkers = 3
	const numJobs = 8

	jobs := make(chan Job, numJobs)
	results := make(chan Result, numJobs)

	var wg sync.WaitGroup
	for w := 1; w <= numWorkers; w++ {
		wg.Add(1)
		go workerWithErrors(w, jobs, results, &wg)
	}

	// Send jobs (some will fail)
	for j := 1; j <= numJobs; j++ {
		jobs <- Job{ID: j, Data: fmt.Sprintf("task-%d", j)}
	}
	close(jobs)

	go func() {
		wg.Wait()
		close(results)
	}()

	// Collect results and handle errors
	var successCount, errorCount int
	for result := range results {
		if result.Error != nil {
			errorCount++
			fmt.Printf("  Job %d FAILED: %v\n", result.JobID, result.Error)
		} else {
			successCount++
			fmt.Printf("  Job %d succeeded: %s\n", result.JobID, result.Output)
		}
	}

	fmt.Printf("  Summary: %d succeeded, %d failed\n", successCount, errorCount)
	fmt.Println()
}

func workerWithErrors(id int, jobs <-chan Job, results chan<- Result, wg *sync.WaitGroup) {
	defer wg.Done()

	for job := range jobs {
		start := time.Now()
		time.Sleep(time.Duration(rand.Intn(50)) * time.Millisecond)

		// Simulate random failures (30% chance)
		if rand.Float32() < 0.3 {
			results <- Result{
				JobID:    job.ID,
				WorkerID: id,
				Duration: time.Since(start),
				Error:    fmt.Errorf("random failure"),
			}
			continue
		}

		results <- Result{
			JobID:    job.ID,
			Output:   fmt.Sprintf("processed %s", job.Data),
			WorkerID: id,
			Duration: time.Since(start),
		}
	}
}

func main() {
	fmt.Println("Example 2: Worker Pool")
	fmt.Println("======================")
	fmt.Println()

	SimpleWorkerPool()
	ReusableWorkerPoolDemo()
	WorkerPoolWithErrorHandling()

	fmt.Println("Example 2 completed!")
}
