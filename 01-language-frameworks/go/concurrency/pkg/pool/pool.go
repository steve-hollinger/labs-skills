// Package pool provides a reusable worker pool implementation.
package pool

import (
	"context"
	"sync"
)

// Task represents a unit of work
type Task func() (interface{}, error)

// Result represents the outcome of a task
type Result struct {
	Value interface{}
	Error error
}

// Pool manages a fixed number of workers processing tasks
type Pool struct {
	numWorkers int
	taskQueue  chan Task
	results    chan Result
	wg         sync.WaitGroup
	ctx        context.Context
	cancel     context.CancelFunc
	started    bool
	mu         sync.Mutex
}

// New creates a new worker pool
func New(numWorkers int, queueSize int) *Pool {
	ctx, cancel := context.WithCancel(context.Background())
	return &Pool{
		numWorkers: numWorkers,
		taskQueue:  make(chan Task, queueSize),
		results:    make(chan Result, queueSize),
		ctx:        ctx,
		cancel:     cancel,
	}
}

// Start initializes the workers
func (p *Pool) Start() {
	p.mu.Lock()
	if p.started {
		p.mu.Unlock()
		return
	}
	p.started = true
	p.mu.Unlock()

	for i := 0; i < p.numWorkers; i++ {
		p.wg.Add(1)
		go p.worker()
	}

	// Close results when all workers complete
	go func() {
		p.wg.Wait()
		close(p.results)
	}()
}

// worker processes tasks from the queue
func (p *Pool) worker() {
	defer p.wg.Done()

	for {
		select {
		case <-p.ctx.Done():
			return
		case task, ok := <-p.taskQueue:
			if !ok {
				return
			}

			// Execute task
			value, err := task()

			// Send result
			select {
			case <-p.ctx.Done():
				return
			case p.results <- Result{Value: value, Error: err}:
			}
		}
	}
}

// Submit adds a task to the pool
// Returns false if pool is stopped or context is cancelled
func (p *Pool) Submit(task Task) bool {
	select {
	case <-p.ctx.Done():
		return false
	case p.taskQueue <- task:
		return true
	}
}

// SubmitWait adds a task and waits for it to complete
func (p *Pool) SubmitWait(task Task) (interface{}, error) {
	resultCh := make(chan Result, 1)

	wrappedTask := func() (interface{}, error) {
		value, err := task()
		resultCh <- Result{Value: value, Error: err}
		return value, err
	}

	if !p.Submit(wrappedTask) {
		return nil, p.ctx.Err()
	}

	select {
	case <-p.ctx.Done():
		return nil, p.ctx.Err()
	case result := <-resultCh:
		return result.Value, result.Error
	}
}

// Results returns the results channel
func (p *Pool) Results() <-chan Result {
	return p.results
}

// Stop gracefully shuts down the pool
// Waits for pending tasks to complete
func (p *Pool) Stop() {
	close(p.taskQueue)
}

// StopNow immediately cancels all workers
func (p *Pool) StopNow() {
	p.cancel()
}

// Wait blocks until all workers have finished
func (p *Pool) Wait() {
	p.wg.Wait()
}

// Len returns the number of pending tasks
func (p *Pool) Len() int {
	return len(p.taskQueue)
}

// NumWorkers returns the number of workers
func (p *Pool) NumWorkers() int {
	return p.numWorkers
}
