// Demo file for showing race detector output
//
// This file intentionally contains race conditions to demonstrate
// the race detector's output. Run with: go run -race demo.go
package main

import (
	"fmt"
	"sync"
)

var sharedCounter int

func main() {
	fmt.Println("Race Detector Demo")
	fmt.Println("==================")
	fmt.Println()
	fmt.Println("This program intentionally has a data race.")
	fmt.Println("The race detector will show output like:")
	fmt.Println()
	fmt.Println("  WARNING: DATA RACE")
	fmt.Println("  Write at 0x... by goroutine N:")
	fmt.Println("    main.increment()")
	fmt.Println("  Previous read at 0x... by goroutine M:")
	fmt.Println("    main.increment()")
	fmt.Println()

	var wg sync.WaitGroup

	// Create a race condition
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < 100; j++ {
				// This is a race condition!
				// Multiple goroutines read and write sharedCounter
				sharedCounter++
			}
		}()
	}

	wg.Wait()

	fmt.Printf("Final counter value: %d (expected: 1000)\n", sharedCounter)
	fmt.Println()
	fmt.Println("Note: With -race flag, you'll see WARNING: DATA RACE above.")
}
