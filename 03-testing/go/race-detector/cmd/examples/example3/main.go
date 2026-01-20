// Example 3: Fixing Races - Comprehensive Solutions
//
// This example demonstrates various techniques for fixing race conditions.
// All code in this file is race-free and can be verified with: go run -race main.go
package main

import (
	"context"
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

// ============================================================================
// Solution 1: Mutex-Based Thread-Safe Map
// ============================================================================

// ThreadSafeMap demonstrates a production-ready concurrent map
type ThreadSafeMap[K comparable, V any] struct {
	mu   sync.RWMutex
	data map[K]V
}

func NewThreadSafeMap[K comparable, V any]() *ThreadSafeMap[K, V] {
	return &ThreadSafeMap[K, V]{
		data: make(map[K]V),
	}
}

func (m *ThreadSafeMap[K, V]) Get(key K) (V, bool) {
	m.mu.RLock()
	defer m.mu.RUnlock()
	val, ok := m.data[key]
	return val, ok
}

func (m *ThreadSafeMap[K, V]) Set(key K, value V) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.data[key] = value
}

func (m *ThreadSafeMap[K, V]) Delete(key K) {
	m.mu.Lock()
	defer m.mu.Unlock()
	delete(m.data, key)
}

func (m *ThreadSafeMap[K, V]) Len() int {
	m.mu.RLock()
	defer m.mu.RUnlock()
	return len(m.data)
}

// GetOrSet atomically gets existing value or sets new one
func (m *ThreadSafeMap[K, V]) GetOrSet(key K, value V) (V, bool) {
	m.mu.Lock()
	defer m.mu.Unlock()
	if existing, ok := m.data[key]; ok {
		return existing, true
	}
	m.data[key] = value
	return value, false
}

func demonstrateMutexMap() {
	fmt.Println("=== Solution 1: Mutex-Based Thread-Safe Map ===")

	cache := NewThreadSafeMap[string, int]()
	var wg sync.WaitGroup

	// Concurrent writes
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(val int) {
			defer wg.Done()
			cache.Set(fmt.Sprintf("key%d", val), val)
		}(i)
	}

	// Concurrent reads
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(val int) {
			defer wg.Done()
			cache.Get(fmt.Sprintf("key%d", val))
		}(i)
	}

	wg.Wait()
	fmt.Printf("Cache size: %d (expected: 100)\n", cache.Len())
	fmt.Println()
}

// ============================================================================
// Solution 2: Atomic Operations for Counters
// ============================================================================

// Metrics demonstrates atomic operations for high-performance counters
type Metrics struct {
	requestCount  atomic.Int64
	errorCount    atomic.Int64
	bytesReceived atomic.Int64
	bytesSent     atomic.Int64
}

func (m *Metrics) RecordRequest(received, sent int64) {
	m.requestCount.Add(1)
	m.bytesReceived.Add(received)
	m.bytesSent.Add(sent)
}

func (m *Metrics) RecordError() {
	m.errorCount.Add(1)
}

func (m *Metrics) Snapshot() map[string]int64 {
	return map[string]int64{
		"requests":       m.requestCount.Load(),
		"errors":         m.errorCount.Load(),
		"bytes_received": m.bytesReceived.Load(),
		"bytes_sent":     m.bytesSent.Load(),
	}
}

func demonstrateAtomics() {
	fmt.Println("=== Solution 2: Atomic Operations ===")

	metrics := &Metrics{}
	var wg sync.WaitGroup

	// Simulate high-throughput concurrent updates
	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			metrics.RecordRequest(100, 50)
			if id%10 == 0 {
				metrics.RecordError()
			}
		}(i)
	}

	wg.Wait()
	snapshot := metrics.Snapshot()
	fmt.Printf("Requests: %d (expected: 1000)\n", snapshot["requests"])
	fmt.Printf("Errors: %d (expected: 100)\n", snapshot["errors"])
	fmt.Printf("Bytes received: %d\n", snapshot["bytes_received"])
	fmt.Println()
}

// ============================================================================
// Solution 3: Channel-Based State Management
// ============================================================================

// ChannelCounter manages state through a single goroutine
type ChannelCounter struct {
	incCh    chan int
	getCh    chan chan int
	doneCh   chan struct{}
	shutdown chan struct{}
}

func NewChannelCounter() *ChannelCounter {
	c := &ChannelCounter{
		incCh:    make(chan int),
		getCh:    make(chan chan int),
		doneCh:   make(chan struct{}),
		shutdown: make(chan struct{}),
	}
	go c.run()
	return c
}

func (c *ChannelCounter) run() {
	var count int
	for {
		select {
		case delta := <-c.incCh:
			count += delta
		case replyCh := <-c.getCh:
			replyCh <- count
		case <-c.shutdown:
			close(c.doneCh)
			return
		}
	}
}

func (c *ChannelCounter) Add(delta int) {
	c.incCh <- delta
}

func (c *ChannelCounter) Get() int {
	replyCh := make(chan int)
	c.getCh <- replyCh
	return <-replyCh
}

func (c *ChannelCounter) Close() {
	close(c.shutdown)
	<-c.doneCh
}

func demonstrateChannels() {
	fmt.Println("=== Solution 3: Channel-Based State ===")

	counter := NewChannelCounter()
	var wg sync.WaitGroup

	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			counter.Add(1)
		}()
	}

	wg.Wait()
	fmt.Printf("Counter: %d (expected: 100)\n", counter.Get())
	counter.Close()
	fmt.Println()
}

// ============================================================================
// Solution 4: sync.Once for Lazy Initialization
// ============================================================================

// Config demonstrates thread-safe lazy initialization
type Config struct {
	DatabaseURL string
	APIKey      string
	Timeout     time.Duration
}

type ConfigLoader struct {
	once   sync.Once
	config *Config
	err    error
}

func (l *ConfigLoader) Load() (*Config, error) {
	l.once.Do(func() {
		fmt.Println("  Loading config (this only runs once)...")
		// Simulate loading from file/environment
		time.Sleep(10 * time.Millisecond)
		l.config = &Config{
			DatabaseURL: "postgres://localhost/db",
			APIKey:      "secret-key",
			Timeout:     30 * time.Second,
		}
	})
	return l.config, l.err
}

func demonstrateSyncOnce() {
	fmt.Println("=== Solution 4: sync.Once for Initialization ===")

	loader := &ConfigLoader{}
	var wg sync.WaitGroup

	// Multiple goroutines trying to load config
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			config, _ := loader.Load()
			fmt.Printf("  Goroutine %d got config: %s\n", id, config.DatabaseURL)
		}(i)
	}

	wg.Wait()
	fmt.Println()
}

// ============================================================================
// Solution 5: Context-Aware Cancellation
// ============================================================================

// Worker demonstrates safe concurrent work with cancellation
type Worker struct {
	id     int
	done   chan struct{}
	result atomic.Int64
}

func NewWorker(id int) *Worker {
	return &Worker{
		id:   id,
		done: make(chan struct{}),
	}
}

func (w *Worker) Start(ctx context.Context) {
	go func() {
		defer close(w.done)
		for {
			select {
			case <-ctx.Done():
				return
			default:
				// Simulate work
				w.result.Add(1)
				time.Sleep(time.Millisecond)
			}
		}
	}()
}

func (w *Worker) Wait() {
	<-w.done
}

func (w *Worker) Result() int64 {
	return w.result.Load()
}

func demonstrateContextCancellation() {
	fmt.Println("=== Solution 5: Context-Aware Cancellation ===")

	ctx, cancel := context.WithTimeout(context.Background(), 50*time.Millisecond)
	defer cancel()

	workers := make([]*Worker, 5)
	for i := 0; i < 5; i++ {
		workers[i] = NewWorker(i)
		workers[i].Start(ctx)
	}

	// Wait for context to expire
	<-ctx.Done()

	var totalWork int64
	for _, w := range workers {
		w.Wait()
		totalWork += w.Result()
	}

	fmt.Printf("Total work completed by all workers: %d\n", totalWork)
	fmt.Println()
}

// ============================================================================
// Solution 6: sync.Pool for Object Reuse
// ============================================================================

// Buffer pool for reducing allocations in concurrent code
var bufferPool = sync.Pool{
	New: func() interface{} {
		return make([]byte, 1024)
	},
}

func demonstrateSyncPool() {
	fmt.Println("=== Solution 6: sync.Pool for Object Reuse ===")

	var wg sync.WaitGroup
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			// Get buffer from pool
			buf := bufferPool.Get().([]byte)
			defer bufferPool.Put(buf)

			// Use buffer (simulated work)
			copy(buf, fmt.Sprintf("Worker %d data", id))
		}(i)
	}

	wg.Wait()
	fmt.Println("Completed 100 concurrent operations with pooled buffers")
	fmt.Println()
}

func main() {
	fmt.Println("Example 3: Fixing Races - Comprehensive Solutions")
	fmt.Println("==================================================")
	fmt.Println()
	fmt.Println("All code in this example is race-free.")
	fmt.Println("Verify with: go run -race main.go")
	fmt.Println()

	demonstrateMutexMap()
	demonstrateAtomics()
	demonstrateChannels()
	demonstrateSyncOnce()
	demonstrateContextCancellation()
	demonstrateSyncPool()

	fmt.Println("==================================================")
	fmt.Println("All solutions demonstrated successfully!")
	fmt.Println("Run with -race flag to verify no races: go run -race main.go")
}
