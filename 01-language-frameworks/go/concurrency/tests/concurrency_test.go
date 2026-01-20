package tests

import (
	"context"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/labs-skills/concurrency/pkg/pool"
	"github.com/labs-skills/concurrency/pkg/pipeline"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestWorkerPool_BasicUsage(t *testing.T) {
	p := pool.New(3, 10)
	p.Start()

	// Submit tasks
	var completed atomic.Int32
	for i := 0; i < 5; i++ {
		submitted := p.Submit(func() (interface{}, error) {
			time.Sleep(10 * time.Millisecond)
			completed.Add(1)
			return "done", nil
		})
		require.True(t, submitted)
	}

	p.Stop()
	p.Wait()

	// Collect results
	var results []pool.Result
	for result := range p.Results() {
		results = append(results, result)
	}

	assert.Equal(t, 5, len(results))
	assert.Equal(t, int32(5), completed.Load())
}

func TestWorkerPool_Concurrent(t *testing.T) {
	p := pool.New(5, 100)
	p.Start()

	var maxConcurrent atomic.Int32
	var current atomic.Int32

	// Submit many tasks
	for i := 0; i < 50; i++ {
		p.Submit(func() (interface{}, error) {
			c := current.Add(1)
			for {
				max := maxConcurrent.Load()
				if c <= max || maxConcurrent.CompareAndSwap(max, c) {
					break
				}
			}
			time.Sleep(10 * time.Millisecond)
			current.Add(-1)
			return nil, nil
		})
	}

	p.Stop()
	p.Wait()

	// Should have seen at least some concurrent execution
	assert.GreaterOrEqual(t, maxConcurrent.Load(), int32(2))
	assert.LessOrEqual(t, maxConcurrent.Load(), int32(5))
}

func TestWorkerPool_StopNow(t *testing.T) {
	p := pool.New(2, 10)
	p.Start()

	// Submit slow tasks
	var started atomic.Int32
	for i := 0; i < 10; i++ {
		p.Submit(func() (interface{}, error) {
			started.Add(1)
			time.Sleep(100 * time.Millisecond)
			return nil, nil
		})
	}

	// Give tasks time to start
	time.Sleep(20 * time.Millisecond)

	// Cancel immediately
	p.StopNow()

	// Not all tasks should have started
	assert.Less(t, started.Load(), int32(10))
}

func TestPipeline_Generator(t *testing.T) {
	ctx := context.Background()
	ch := pipeline.Generator(ctx, 1, 2, 3, 4, 5)

	var results []int
	for v := range ch {
		results = append(results, v)
	}

	assert.Equal(t, []int{1, 2, 3, 4, 5}, results)
}

func TestPipeline_GeneratorWithCancel(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())

	ch := pipeline.Generator(ctx, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

	var results []int
	for v := range ch {
		results = append(results, v)
		if len(results) == 3 {
			cancel()
			break
		}
	}

	assert.LessOrEqual(t, len(results), 4) // Might get one more before cancel takes effect
}

func TestPipeline_Map(t *testing.T) {
	ctx := context.Background()
	input := pipeline.Generator(ctx, 1, 2, 3, 4, 5)

	squared := pipeline.Map(ctx, input, func(n int) int {
		return n * n
	})

	results := pipeline.Collect(ctx, squared)
	assert.Equal(t, []int{1, 4, 9, 16, 25}, results)
}

func TestPipeline_Filter(t *testing.T) {
	ctx := context.Background()
	input := pipeline.Generator(ctx, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

	evens := pipeline.Filter(ctx, input, func(n int) bool {
		return n%2 == 0
	})

	results := pipeline.Collect(ctx, evens)
	assert.Equal(t, []int{2, 4, 6, 8, 10}, results)
}

func TestPipeline_FanIn(t *testing.T) {
	ctx := context.Background()
	ch1 := pipeline.Generator(ctx, 1, 2, 3)
	ch2 := pipeline.Generator(ctx, 10, 20, 30)
	ch3 := pipeline.Generator(ctx, 100, 200, 300)

	merged := pipeline.FanIn(ctx, ch1, ch2, ch3)
	results := pipeline.Collect(ctx, merged)

	// Order is non-deterministic, but should have all values
	assert.Len(t, results, 9)

	// Check all expected values are present
	expected := map[int]bool{
		1: true, 2: true, 3: true,
		10: true, 20: true, 30: true,
		100: true, 200: true, 300: true,
	}
	for _, v := range results {
		assert.True(t, expected[v], "unexpected value: %d", v)
		delete(expected, v)
	}
	assert.Empty(t, expected)
}

func TestPipeline_Take(t *testing.T) {
	ctx := context.Background()
	input := pipeline.Generator(ctx, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

	first5 := pipeline.Take(ctx, input, 5)
	results := pipeline.Collect(ctx, first5)

	assert.Equal(t, []int{1, 2, 3, 4, 5}, results)
}

func TestPipeline_Skip(t *testing.T) {
	ctx := context.Background()
	input := pipeline.Generator(ctx, 1, 2, 3, 4, 5)

	skipped := pipeline.Skip(ctx, input, 2)
	results := pipeline.Collect(ctx, skipped)

	assert.Equal(t, []int{3, 4, 5}, results)
}

func TestPipeline_Batch(t *testing.T) {
	ctx := context.Background()
	input := pipeline.Generator(ctx, 1, 2, 3, 4, 5, 6, 7)

	batched := pipeline.Batch(ctx, input, 3)
	results := pipeline.Collect(ctx, batched)

	assert.Equal(t, [][]int{{1, 2, 3}, {4, 5, 6}, {7}}, results)
}

func TestPipeline_ChainedOperations(t *testing.T) {
	ctx := context.Background()

	// Generate -> Filter (evens) -> Map (square) -> Take (3)
	input := pipeline.Generator(ctx, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
	evens := pipeline.Filter(ctx, input, func(n int) bool { return n%2 == 0 })
	squared := pipeline.Map(ctx, evens, func(n int) int { return n * n })
	first3 := pipeline.Take(ctx, squared, 3)

	results := pipeline.Collect(ctx, first3)
	assert.Equal(t, []int{4, 16, 36}, results) // 2^2, 4^2, 6^2
}

// Test for race conditions - run with -race flag
func TestConcurrentMapAccess(t *testing.T) {
	var mu sync.Mutex
	counter := make(map[int]int)

	var wg sync.WaitGroup
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			mu.Lock()
			counter[id%10]++
			mu.Unlock()
		}(i)
	}

	wg.Wait()

	total := 0
	for _, v := range counter {
		total += v
	}
	assert.Equal(t, 100, total)
}

// Test atomic operations
func TestAtomicCounter(t *testing.T) {
	var counter atomic.Int64

	var wg sync.WaitGroup
	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			counter.Add(1)
		}()
	}

	wg.Wait()
	assert.Equal(t, int64(1000), counter.Load())
}

// Test channel closing
func TestChannelClose(t *testing.T) {
	ch := make(chan int, 5)

	// Send values
	go func() {
		for i := 0; i < 5; i++ {
			ch <- i
		}
		close(ch)
	}()

	// Receive all values
	var results []int
	for v := range ch {
		results = append(results, v)
	}

	assert.Equal(t, []int{0, 1, 2, 3, 4}, results)

	// Channel is closed, receive returns zero value and false
	v, ok := <-ch
	assert.Equal(t, 0, v)
	assert.False(t, ok)
}

// Test select with timeout
func TestSelectTimeout(t *testing.T) {
	ch := make(chan int)

	start := time.Now()
	select {
	case <-ch:
		t.Fatal("Should not receive value")
	case <-time.After(50 * time.Millisecond):
		// Expected
	}

	elapsed := time.Since(start)
	assert.GreaterOrEqual(t, elapsed, 50*time.Millisecond)
	assert.Less(t, elapsed, 100*time.Millisecond)
}

// Test context cancellation
func TestContextCancellation(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())

	done := make(chan bool)
	go func() {
		<-ctx.Done()
		done <- true
	}()

	// Cancel should trigger done
	cancel()

	select {
	case <-done:
		// Expected
	case <-time.After(100 * time.Millisecond):
		t.Fatal("Goroutine did not receive cancellation")
	}
}

// Test WaitGroup
func TestWaitGroup(t *testing.T) {
	var wg sync.WaitGroup
	var completed atomic.Int32

	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			time.Sleep(10 * time.Millisecond)
			completed.Add(1)
		}()
	}

	wg.Wait()
	assert.Equal(t, int32(10), completed.Load())
}
