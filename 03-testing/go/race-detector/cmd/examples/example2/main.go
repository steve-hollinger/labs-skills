// Example 2: Common Race Patterns
//
// This example demonstrates various common race condition patterns found in Go code.
// Each pattern shows a problematic implementation and its fix.
package main

import (
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

// ============================================================================
// Pattern 1: Map Race
// ============================================================================

// UnsafeCache demonstrates a map race condition
type UnsafeCache struct {
	data map[string]string
}

func (c *UnsafeCache) Get(key string) string {
	return c.data[key] // RACE: concurrent read
}

func (c *UnsafeCache) Set(key, value string) {
	c.data[key] = value // RACE: concurrent write
}

// SafeCache fixes the race with a mutex
type SafeCache struct {
	mu   sync.RWMutex
	data map[string]string
}

func (c *SafeCache) Get(key string) string {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.data[key]
}

func (c *SafeCache) Set(key, value string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.data[key] = value
}

func demonstrateMapRace() {
	fmt.Println("=== Pattern 1: Map Race ===")

	// Unsafe version - would crash or corrupt with -race flag
	unsafe := &UnsafeCache{data: make(map[string]string)}
	var wg sync.WaitGroup

	// Comment: In real scenarios, this would cause panic or data corruption
	// We're keeping iterations low to avoid panic in demo
	for i := 0; i < 10; i++ {
		wg.Add(2)
		key := fmt.Sprintf("key%d", i)
		go func(k string) {
			defer wg.Done()
			unsafe.Set(k, "value")
		}(key)
		go func(k string) {
			defer wg.Done()
			_ = unsafe.Get(k)
		}(key)
	}
	wg.Wait()
	fmt.Println("Unsafe cache: completed (may have corrupted data)")

	// Safe version
	safe := &SafeCache{data: make(map[string]string)}
	for i := 0; i < 100; i++ {
		wg.Add(2)
		key := fmt.Sprintf("key%d", i)
		go func(k string) {
			defer wg.Done()
			safe.Set(k, "value")
		}(key)
		go func(k string) {
			defer wg.Done()
			_ = safe.Get(k)
		}(key)
	}
	wg.Wait()
	fmt.Println("Safe cache: completed correctly")
	fmt.Println()
}

// ============================================================================
// Pattern 2: Slice Race
// ============================================================================

func demonstrateSliceRace() {
	fmt.Println("=== Pattern 2: Slice Race ===")

	// Unsafe: appending to slice concurrently
	var unsafeSlice []int
	var wg sync.WaitGroup

	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(val int) {
			defer wg.Done()
			unsafeSlice = append(unsafeSlice, val) // RACE!
		}(i)
	}
	wg.Wait()
	fmt.Printf("Unsafe slice length: %d (expected 100)\n", len(unsafeSlice))

	// Safe: using mutex
	var safeSlice []int
	var mu sync.Mutex

	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(val int) {
			defer wg.Done()
			mu.Lock()
			safeSlice = append(safeSlice, val)
			mu.Unlock()
		}(i)
	}
	wg.Wait()
	fmt.Printf("Safe slice length: %d (expected 100)\n", len(safeSlice))
	fmt.Println()
}

// ============================================================================
// Pattern 3: Loop Variable Capture Race
// ============================================================================

func demonstrateLoopRace() {
	fmt.Println("=== Pattern 3: Loop Variable Capture ===")

	// Unsafe: capturing loop variable by reference
	fmt.Print("Unsafe (values may be duplicated): ")
	var wg sync.WaitGroup
	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			fmt.Print(i, " ") // RACE: i is shared!
		}()
	}
	wg.Wait()
	fmt.Println()

	// Safe: pass loop variable as argument
	fmt.Print("Safe (all values appear): ")
	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func(val int) {
			defer wg.Done()
			fmt.Print(val, " ")
		}(i)
	}
	wg.Wait()
	fmt.Println()
	fmt.Println()
}

// ============================================================================
// Pattern 4: Struct Field Race
// ============================================================================

type Stats struct {
	Requests int64
	Errors   int64
	// No synchronization - races on both fields
}

type SafeStats struct {
	requests int64 // Use atomic operations
	errors   int64
}

func (s *SafeStats) RecordRequest() {
	atomic.AddInt64(&s.requests, 1)
}

func (s *SafeStats) RecordError() {
	atomic.AddInt64(&s.errors, 1)
}

func (s *SafeStats) GetStats() (int64, int64) {
	return atomic.LoadInt64(&s.requests), atomic.LoadInt64(&s.errors)
}

func demonstrateStructRace() {
	fmt.Println("=== Pattern 4: Struct Field Race ===")

	// Unsafe
	unsafe := &Stats{}
	var wg sync.WaitGroup

	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			unsafe.Requests++ // RACE!
			if unsafe.Requests%10 == 0 {
				unsafe.Errors++ // RACE!
			}
		}()
	}
	wg.Wait()
	fmt.Printf("Unsafe: Requests=%d, Errors=%d\n", unsafe.Requests, unsafe.Errors)

	// Safe with atomics
	safe := &SafeStats{}
	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			safe.RecordRequest()
			reqs, _ := safe.GetStats()
			if reqs%10 == 0 {
				safe.RecordError()
			}
		}()
	}
	wg.Wait()
	reqs, errs := safe.GetStats()
	fmt.Printf("Safe: Requests=%d, Errors=%d\n", reqs, errs)
	fmt.Println()
}

// ============================================================================
// Pattern 5: Check-Then-Act Race (TOCTOU)
// ============================================================================

type UnsafeRegistry struct {
	mu       sync.Mutex
	services map[string]string
}

func (r *UnsafeRegistry) Register(name, addr string) error {
	// RACE: Check and act are not atomic!
	if _, exists := r.services[name]; exists {
		return fmt.Errorf("service %s already registered", name)
	}
	r.services[name] = addr
	return nil
}

type SafeRegistry struct {
	mu       sync.Mutex
	services map[string]string
}

func (r *SafeRegistry) Register(name, addr string) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	// Check and act are now atomic
	if _, exists := r.services[name]; exists {
		return fmt.Errorf("service %s already registered", name)
	}
	r.services[name] = addr
	return nil
}

func demonstrateTOCTOU() {
	fmt.Println("=== Pattern 5: Check-Then-Act (TOCTOU) ===")

	safe := &SafeRegistry{services: make(map[string]string)}
	var wg sync.WaitGroup
	var successCount int64

	// Multiple goroutines trying to register the same service
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			err := safe.Register("my-service", fmt.Sprintf("addr%d", id))
			if err == nil {
				atomic.AddInt64(&successCount, 1)
			}
		}(i)
	}
	wg.Wait()

	fmt.Printf("Successful registrations: %d (expected: 1)\n", successCount)
	fmt.Println()
}

func main() {
	fmt.Println("Example 2: Common Race Patterns")
	fmt.Println("================================")
	fmt.Println()
	fmt.Println("This example demonstrates common race condition patterns.")
	fmt.Println("Run with -race flag to detect races:")
	fmt.Println("  go run -race main.go")
	fmt.Println()

	demonstrateMapRace()
	time.Sleep(10 * time.Millisecond)

	demonstrateSliceRace()
	time.Sleep(10 * time.Millisecond)

	demonstrateLoopRace()
	time.Sleep(10 * time.Millisecond)

	demonstrateStructRace()
	time.Sleep(10 * time.Millisecond)

	demonstrateTOCTOU()

	fmt.Println("================================")
	fmt.Println("All patterns demonstrated!")
	fmt.Println("Run with: go run -race main.go")
	fmt.Println("to see race detection in action.")
}
