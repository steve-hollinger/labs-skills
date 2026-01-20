// Example 1: Goroutines and Channels
//
// This example demonstrates the fundamental concurrency primitives in Go:
// - Starting goroutines
// - Creating and using channels
// - Channel directions (send-only, receive-only)
// - Closing channels and range
// - Select statement for multiplexing
package main

import (
	"fmt"
	"math/rand"
	"sync"
	"time"
)

func main() {
	fmt.Println("Example 1: Goroutines and Channels")
	fmt.Println("===================================")
	fmt.Println()

	// Demo 1: Basic Goroutine
	fmt.Println("1. Basic Goroutine")
	fmt.Println("------------------")
	basicGoroutine()
	fmt.Println()

	// Demo 2: Channels for Communication
	fmt.Println("2. Channels for Communication")
	fmt.Println("-----------------------------")
	channelDemo()
	fmt.Println()

	// Demo 3: Buffered Channels
	fmt.Println("3. Buffered Channels")
	fmt.Println("--------------------")
	bufferedChannelDemo()
	fmt.Println()

	// Demo 4: Range over Channels
	fmt.Println("4. Range over Channels")
	fmt.Println("----------------------")
	rangeDemo()
	fmt.Println()

	// Demo 5: Select Statement
	fmt.Println("5. Select Statement")
	fmt.Println("-------------------")
	selectDemo()
	fmt.Println()

	// Demo 6: WaitGroup
	fmt.Println("6. WaitGroup for Synchronization")
	fmt.Println("---------------------------------")
	waitGroupDemo()
	fmt.Println()

	fmt.Println("Example 1 completed!")
}

// basicGoroutine demonstrates starting a simple goroutine
func basicGoroutine() {
	done := make(chan bool)

	go func() {
		fmt.Println("  Hello from goroutine!")
		time.Sleep(100 * time.Millisecond)
		fmt.Println("  Goroutine finished work")
		done <- true
	}()

	fmt.Println("  Main function continues...")
	<-done // Wait for goroutine to complete
	fmt.Println("  Main received done signal")
}

// channelDemo shows basic channel operations
func channelDemo() {
	// Create an unbuffered channel
	messages := make(chan string)

	// Start sender goroutine
	go func() {
		messages <- "ping"
	}()

	// Receive message
	msg := <-messages
	fmt.Println("  Received:", msg)

	// Bidirectional example with producer/consumer
	numbers := make(chan int)

	// Producer
	go func() {
		for i := 1; i <= 3; i++ {
			fmt.Printf("  Sending: %d\n", i)
			numbers <- i
		}
		close(numbers)
	}()

	// Consumer
	for n := range numbers {
		fmt.Printf("  Received: %d\n", n)
	}
}

// bufferedChannelDemo shows buffered channel behavior
func bufferedChannelDemo() {
	// Buffered channel with capacity 3
	ch := make(chan string, 3)

	// Can send without blocking (up to capacity)
	ch <- "first"
	ch <- "second"
	ch <- "third"
	fmt.Println("  Sent 3 messages without blocking")

	// Receive all messages
	fmt.Println("  Received:", <-ch)
	fmt.Println("  Received:", <-ch)
	fmt.Println("  Received:", <-ch)

	// Check length and capacity
	ch <- "another"
	fmt.Printf("  Channel length: %d, capacity: %d\n", len(ch), cap(ch))
}

// rangeDemo shows iterating over a channel
func rangeDemo() {
	ch := make(chan int)

	// Generator goroutine
	go func() {
		for i := 1; i <= 5; i++ {
			ch <- i * i
		}
		close(ch) // Important: close to signal completion
	}()

	// Range automatically stops when channel is closed
	fmt.Print("  Squares: ")
	for square := range ch {
		fmt.Printf("%d ", square)
	}
	fmt.Println()
}

// selectDemo demonstrates the select statement
func selectDemo() {
	ch1 := make(chan string)
	ch2 := make(chan string)

	// Goroutine that sends to ch1 after random delay
	go func() {
		time.Sleep(time.Duration(rand.Intn(100)) * time.Millisecond)
		ch1 <- "message from channel 1"
	}()

	// Goroutine that sends to ch2 after random delay
	go func() {
		time.Sleep(time.Duration(rand.Intn(100)) * time.Millisecond)
		ch2 <- "message from channel 2"
	}()

	// Receive from whichever is ready first
	for i := 0; i < 2; i++ {
		select {
		case msg := <-ch1:
			fmt.Println("  Received:", msg)
		case msg := <-ch2:
			fmt.Println("  Received:", msg)
		}
	}

	// Select with timeout
	ch3 := make(chan string)
	go func() {
		time.Sleep(200 * time.Millisecond)
		ch3 <- "delayed message"
	}()

	select {
	case msg := <-ch3:
		fmt.Println("  Received:", msg)
	case <-time.After(100 * time.Millisecond):
		fmt.Println("  Timeout waiting for message")
	}

	// Non-blocking select with default
	select {
	case msg := <-ch3:
		fmt.Println("  Received:", msg)
	default:
		fmt.Println("  No message ready (non-blocking)")
	}
}

// waitGroupDemo shows synchronizing multiple goroutines
func waitGroupDemo() {
	var wg sync.WaitGroup

	// Start 3 workers
	for i := 1; i <= 3; i++ {
		wg.Add(1) // Increment counter before starting goroutine

		go func(id int) {
			defer wg.Done() // Decrement counter when done

			fmt.Printf("  Worker %d starting\n", id)
			time.Sleep(time.Duration(rand.Intn(100)) * time.Millisecond)
			fmt.Printf("  Worker %d done\n", id)
		}(i)
	}

	wg.Wait() // Block until counter is 0
	fmt.Println("  All workers completed")
}
