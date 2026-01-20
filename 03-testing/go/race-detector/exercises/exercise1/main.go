// Exercise 1: Fix the Counter Race
//
// This code has a race condition in the counter. Your task is to fix it
// so that it produces the correct result and passes the race detector.
//
// Instructions:
// 1. Run this code: go run main.go
// 2. Run with race detector: go run -race main.go
// 3. Notice the race condition is detected
// 4. Fix the Counter type to be thread-safe
// 5. Verify with: go run -race main.go
//
// Expected Output (after fix):
// - Counter value should be exactly 10000
// - No race detector warnings
//
// Hints:
// - Use sync.Mutex to protect the counter
// - Remember to use defer for Unlock
// - The Counter should be passed by pointer
package main

import (
	"fmt"
	"sync"
)

// Counter has a race condition - fix it!
type Counter struct {
	// TODO: Add a mutex field here
	value int
}

// Inc increments the counter - fix the race condition!
func (c *Counter) Inc() {
	// TODO: Add mutex locking here
	c.value++
}

// Value returns the current value - fix the race condition!
func (c *Counter) Value() int {
	// TODO: Add mutex locking here
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
