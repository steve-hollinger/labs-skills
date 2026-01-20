// Example 1: Basic Race Detection
//
// This example demonstrates a simple data race and how the race detector catches it.
// Run with: go run main.go
// Run with race detector: go run -race main.go
package main

import (
	"fmt"
	"sync"
	"time"
)

// counter is shared between goroutines without synchronization
var counter int

// unsafeIncrement demonstrates a race condition
func unsafeIncrement() {
	counter++ // READ, INCREMENT, WRITE - not atomic!
}

// demonstrateRace shows a basic race condition
func demonstrateRace() {
	counter = 0
	var wg sync.WaitGroup

	// Launch 100 goroutines, each incrementing counter 100 times
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < 100; j++ {
				unsafeIncrement()
			}
		}()
	}

	wg.Wait()

	// Expected: 10000, but due to race condition, result is unpredictable
	fmt.Printf("Expected counter: 10000\n")
	fmt.Printf("Actual counter:   %d\n", counter)
	fmt.Printf("Lost increments:  %d\n", 10000-counter)
}

// SafeCounter demonstrates a race-free counter using mutex
type SafeCounter struct {
	mu    sync.Mutex
	value int
}

func (c *SafeCounter) Increment() {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.value++
}

func (c *SafeCounter) Value() int {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.value
}

// demonstrateFix shows how to fix the race with a mutex
func demonstrateFix() {
	safe := &SafeCounter{}
	var wg sync.WaitGroup

	// Same workload but with proper synchronization
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < 100; j++ {
				safe.Increment()
			}
		}()
	}

	wg.Wait()

	fmt.Printf("\n--- With Mutex Fix ---\n")
	fmt.Printf("Expected counter: 10000\n")
	fmt.Printf("Actual counter:   %d\n", safe.Value())
}

func main() {
	fmt.Println("Example 1: Basic Race Detection")
	fmt.Println("================================")
	fmt.Println()
	fmt.Println("This example demonstrates a simple counter race condition.")
	fmt.Println("Run with -race flag to see the race detector in action:")
	fmt.Println("  go run -race main.go")
	fmt.Println()

	fmt.Println("--- Without Synchronization (RACE!) ---")
	// Run multiple times to see variability
	for i := 0; i < 3; i++ {
		fmt.Printf("\nRun %d:\n", i+1)
		demonstrateRace()
		time.Sleep(10 * time.Millisecond)
	}

	demonstrateFix()

	fmt.Println("\n================================")
	fmt.Println("Notice: The unsafe counter shows different results each run.")
	fmt.Println("The safe counter always shows 10000.")
	fmt.Println()
	fmt.Println("Try running with: go run -race main.go")
	fmt.Println("The race detector will report the data race.")
}
