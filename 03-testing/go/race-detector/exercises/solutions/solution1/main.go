// Solution for Exercise 1: Fix the Counter Race
//
// This solution uses sync.Mutex to protect the counter from concurrent access.
package main

import (
	"fmt"
	"sync"
)

// Counter is now thread-safe with a mutex
type Counter struct {
	mu    sync.Mutex // Added mutex
	value int
}

// Inc increments the counter safely
func (c *Counter) Inc() {
	c.mu.Lock()         // Lock before accessing
	defer c.mu.Unlock() // Unlock when done (defer ensures it happens)
	c.value++
}

// Value returns the current value safely
func (c *Counter) Value() int {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.value
}

func main() {
	counter := &Counter{}
	var wg sync.WaitGroup

	// Launch 100 goroutines, each incrementing 100 times
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < 100; j++ {
				counter.Inc()
			}
		}()
	}

	wg.Wait()

	fmt.Printf("Expected: 10000\n")
	fmt.Printf("Actual:   %d\n", counter.Value())

	if counter.Value() == 10000 {
		fmt.Println("SUCCESS! Counter is correct.")
	} else {
		fmt.Println("FAILED! Counter has wrong value due to race condition.")
	}
}

/*
Key Changes:
1. Added sync.Mutex field to Counter struct
2. Added Lock/Unlock calls in Inc() method
3. Added Lock/Unlock calls in Value() method
4. Used defer for Unlock to ensure it always happens

Alternative Solution using sync/atomic:

type Counter struct {
    value int64
}

func (c *Counter) Inc() {
    atomic.AddInt64(&c.value, 1)
}

func (c *Counter) Value() int64 {
    return atomic.LoadInt64(&c.value)
}

The atomic solution is faster but only works for simple operations.
Use mutex when you need to protect multiple operations or complex logic.
*/
