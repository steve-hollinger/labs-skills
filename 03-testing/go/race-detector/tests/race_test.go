package tests

import (
	"fmt"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// ============================================================================
// Tests for Safe Counter Implementations
// ============================================================================

// SafeCounter for testing
type SafeCounter struct {
	mu    sync.Mutex
	value int
}

func (c *SafeCounter) Inc() {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.value++
}

func (c *SafeCounter) Value() int {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.value
}

func TestSafeCounter_Concurrent(t *testing.T) {
	counter := &SafeCounter{}
	var wg sync.WaitGroup

	numGoroutines := 100
	incrementsPerGoroutine := 100

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < incrementsPerGoroutine; j++ {
				counter.Inc()
			}
		}()
	}

	wg.Wait()

	expected := numGoroutines * incrementsPerGoroutine
	assert.Equal(t, expected, counter.Value(), "Counter should be exactly %d", expected)
}

// AtomicCounter for testing
type AtomicCounter struct {
	value int64
}

func (c *AtomicCounter) Inc() {
	atomic.AddInt64(&c.value, 1)
}

func (c *AtomicCounter) Value() int64 {
	return atomic.LoadInt64(&c.value)
}

func TestAtomicCounter_Concurrent(t *testing.T) {
	counter := &AtomicCounter{}
	var wg sync.WaitGroup

	numGoroutines := 100
	incrementsPerGoroutine := 100

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < incrementsPerGoroutine; j++ {
				counter.Inc()
			}
		}()
	}

	wg.Wait()

	expected := int64(numGoroutines * incrementsPerGoroutine)
	assert.Equal(t, expected, counter.Value(), "Atomic counter should be exactly %d", expected)
}

// ============================================================================
// Tests for Safe Map Implementations
// ============================================================================

// SafeMap for testing
type SafeMap struct {
	mu   sync.RWMutex
	data map[string]int
}

func NewSafeMap() *SafeMap {
	return &SafeMap{data: make(map[string]int)}
}

func (m *SafeMap) Get(key string) (int, bool) {
	m.mu.RLock()
	defer m.mu.RUnlock()
	v, ok := m.data[key]
	return v, ok
}

func (m *SafeMap) Set(key string, value int) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.data[key] = value
}

func (m *SafeMap) Len() int {
	m.mu.RLock()
	defer m.mu.RUnlock()
	return len(m.data)
}

func TestSafeMap_Concurrent(t *testing.T) {
	m := NewSafeMap()
	var wg sync.WaitGroup

	numGoroutines := 100

	// Concurrent writes
	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			m.Set(fmt.Sprintf("key%d", id), id)
		}(i)
	}

	// Concurrent reads
	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			m.Get(fmt.Sprintf("key%d", id))
		}(i)
	}

	wg.Wait()

	assert.Equal(t, numGoroutines, m.Len(), "Map should have %d entries", numGoroutines)
}

func TestSafeMap_ReadWriteConcurrency(t *testing.T) {
	m := NewSafeMap()
	m.Set("shared", 0)

	var wg sync.WaitGroup
	done := make(chan struct{})

	// Writer goroutine
	wg.Add(1)
	go func() {
		defer wg.Done()
		for i := 0; i < 1000; i++ {
			m.Set("shared", i)
		}
	}()

	// Reader goroutines
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for {
				select {
				case <-done:
					return
				default:
					m.Get("shared")
				}
			}
		}()
	}

	// Wait for writer to finish
	time.Sleep(10 * time.Millisecond)
	close(done)
	wg.Wait()

	val, ok := m.Get("shared")
	require.True(t, ok)
	assert.Equal(t, 999, val)
}

// ============================================================================
// Tests for sync.Once Pattern
// ============================================================================

type LazyConfig struct {
	once   sync.Once
	config string
}

func (l *LazyConfig) Get() string {
	l.once.Do(func() {
		l.config = "initialized"
	})
	return l.config
}

func TestLazyConfig_ConcurrentInit(t *testing.T) {
	lazy := &LazyConfig{}
	var wg sync.WaitGroup

	results := make(chan string, 100)

	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			results <- lazy.Get()
		}()
	}

	wg.Wait()
	close(results)

	// All results should be the same
	for result := range results {
		assert.Equal(t, "initialized", result)
	}
}

// ============================================================================
// Tests for Channel-Based Synchronization
// ============================================================================

type ChannelCounter struct {
	inc  chan int
	get  chan chan int
	stop chan struct{}
}

func NewChannelCounter() *ChannelCounter {
	c := &ChannelCounter{
		inc:  make(chan int),
		get:  make(chan chan int),
		stop: make(chan struct{}),
	}
	go c.run()
	return c
}

func (c *ChannelCounter) run() {
	var count int
	for {
		select {
		case delta := <-c.inc:
			count += delta
		case reply := <-c.get:
			reply <- count
		case <-c.stop:
			return
		}
	}
}

func (c *ChannelCounter) Add(delta int) {
	c.inc <- delta
}

func (c *ChannelCounter) Value() int {
	reply := make(chan int)
	c.get <- reply
	return <-reply
}

func (c *ChannelCounter) Close() {
	close(c.stop)
}

func TestChannelCounter_Concurrent(t *testing.T) {
	counter := NewChannelCounter()
	defer counter.Close()

	var wg sync.WaitGroup

	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			counter.Add(1)
		}()
	}

	wg.Wait()

	assert.Equal(t, 100, counter.Value())
}

// ============================================================================
// Table-Driven Tests for Race-Free Implementations
// ============================================================================

func TestRaceFreeImplementations(t *testing.T) {
	tests := []struct {
		name        string
		goroutines  int
		operations  int
		implementation func() (incFunc func(), getFunc func() int64)
	}{
		{
			name:       "Mutex counter with 10 goroutines",
			goroutines: 10,
			operations: 100,
			implementation: func() (func(), func() int64) {
				var mu sync.Mutex
				var count int64
				return func() {
						mu.Lock()
						count++
						mu.Unlock()
					}, func() int64 {
						mu.Lock()
						defer mu.Unlock()
						return count
					}
			},
		},
		{
			name:       "Mutex counter with 100 goroutines",
			goroutines: 100,
			operations: 100,
			implementation: func() (func(), func() int64) {
				var mu sync.Mutex
				var count int64
				return func() {
						mu.Lock()
						count++
						mu.Unlock()
					}, func() int64 {
						mu.Lock()
						defer mu.Unlock()
						return count
					}
			},
		},
		{
			name:       "Atomic counter with 10 goroutines",
			goroutines: 10,
			operations: 100,
			implementation: func() (func(), func() int64) {
				var count int64
				return func() {
						atomic.AddInt64(&count, 1)
					}, func() int64 {
						return atomic.LoadInt64(&count)
					}
			},
		},
		{
			name:       "Atomic counter with 100 goroutines",
			goroutines: 100,
			operations: 100,
			implementation: func() (func(), func() int64) {
				var count int64
				return func() {
						atomic.AddInt64(&count, 1)
					}, func() int64 {
						return atomic.LoadInt64(&count)
					}
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			inc, get := tt.implementation()
			var wg sync.WaitGroup

			for i := 0; i < tt.goroutines; i++ {
				wg.Add(1)
				go func() {
					defer wg.Done()
					for j := 0; j < tt.operations; j++ {
						inc()
					}
				}()
			}

			wg.Wait()

			expected := int64(tt.goroutines * tt.operations)
			actual := get()
			assert.Equal(t, expected, actual, "Expected %d, got %d", expected, actual)
		})
	}
}

// ============================================================================
// Benchmark Tests
// ============================================================================

func BenchmarkMutexCounter(b *testing.B) {
	var mu sync.Mutex
	var count int

	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			mu.Lock()
			count++
			mu.Unlock()
		}
	})
}

func BenchmarkAtomicCounter(b *testing.B) {
	var count int64

	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			atomic.AddInt64(&count, 1)
		}
	})
}

func BenchmarkRWMutexRead(b *testing.B) {
	var mu sync.RWMutex
	data := make(map[string]int)
	data["key"] = 42

	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			mu.RLock()
			_ = data["key"]
			mu.RUnlock()
		}
	})
}

func BenchmarkSyncMap(b *testing.B) {
	var m sync.Map
	m.Store("key", 42)

	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			m.Load("key")
		}
	})
}
