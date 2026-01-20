// Example 3: Fan-out/Fan-in Pipeline
//
// This example demonstrates building concurrent data processing pipelines:
// - Generator pattern (producer)
// - Fan-out to multiple workers
// - Fan-in to collect results
// - Pipeline stages with transformations
// - Context cancellation for cleanup
package main

import (
	"context"
	"fmt"
	"math/rand"
	"sync"
	"time"
)

func main() {
	fmt.Println("Example 3: Fan-out/Fan-in Pipeline")
	fmt.Println("===================================")
	fmt.Println()

	// Demo 1: Simple Pipeline
	fmt.Println("1. Simple Pipeline")
	fmt.Println("------------------")
	simplePipeline()
	fmt.Println()

	// Demo 2: Fan-out Pattern
	fmt.Println("2. Fan-out Pattern")
	fmt.Println("------------------")
	fanOutDemo()
	fmt.Println()

	// Demo 3: Fan-in Pattern
	fmt.Println("3. Fan-in Pattern")
	fmt.Println("-----------------")
	fanInDemo()
	fmt.Println()

	// Demo 4: Complete Pipeline
	fmt.Println("4. Complete Fan-out/Fan-in Pipeline")
	fmt.Println("------------------------------------")
	completePipeline()
	fmt.Println()

	// Demo 5: Cancellable Pipeline
	fmt.Println("5. Cancellable Pipeline")
	fmt.Println("-----------------------")
	cancellablePipeline()
	fmt.Println()

	fmt.Println("Example 3 completed!")
}

// Generator creates a channel that produces values
func Generator(nums ...int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for _, n := range nums {
			out <- n
		}
	}()
	return out
}

// Square transforms input by squaring each value
func Square(in <-chan int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for n := range in {
			out <- n * n
		}
	}()
	return out
}

// Double transforms input by doubling each value
func Double(in <-chan int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for n := range in {
			out <- n * 2
		}
	}()
	return out
}

// simplePipeline demonstrates chaining stages
func simplePipeline() {
	// Pipeline: generate -> square -> double -> print
	numbers := Generator(1, 2, 3, 4, 5)
	squared := Square(numbers)
	doubled := Double(squared)

	fmt.Print("  Results: ")
	for result := range doubled {
		fmt.Printf("%d ", result)
	}
	fmt.Println()
}

// ProcessorFunc transforms an integer
type ProcessorFunc func(int) int

// FanOut distributes input to n workers
func FanOut(in <-chan int, n int, processor ProcessorFunc) []<-chan int {
	outputs := make([]<-chan int, n)
	for i := 0; i < n; i++ {
		outputs[i] = processAsync(in, processor)
	}
	return outputs
}

func processAsync(in <-chan int, processor ProcessorFunc) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for n := range in {
			// Simulate varying processing time
			time.Sleep(time.Duration(rand.Intn(50)) * time.Millisecond)
			out <- processor(n)
		}
	}()
	return out
}

func fanOutDemo() {
	// Create input channel
	input := make(chan int)
	go func() {
		defer close(input)
		for i := 1; i <= 6; i++ {
			input <- i
		}
	}()

	// Fan out to 3 workers
	processor := func(n int) int { return n * n }
	outputs := FanOut(input, 3, processor)

	// Collect from all outputs
	fmt.Print("  Results from 3 workers: ")
	var wg sync.WaitGroup
	var mu sync.Mutex
	var results []int

	for i, ch := range outputs {
		wg.Add(1)
		go func(workerID int, c <-chan int) {
			defer wg.Done()
			for v := range c {
				mu.Lock()
				results = append(results, v)
				mu.Unlock()
				fmt.Printf("w%d:%d ", workerID, v)
			}
		}(i, ch)
	}
	wg.Wait()
	fmt.Println()
}

// FanIn merges multiple channels into one
func FanIn(inputs ...<-chan int) <-chan int {
	out := make(chan int)
	var wg sync.WaitGroup

	// Start a goroutine for each input channel
	for _, ch := range inputs {
		wg.Add(1)
		go func(c <-chan int) {
			defer wg.Done()
			for n := range c {
				out <- n
			}
		}(ch)
	}

	// Close output when all inputs are exhausted
	go func() {
		wg.Wait()
		close(out)
	}()

	return out
}

func fanInDemo() {
	// Create 3 separate sources
	ch1 := Generator(1, 2, 3)
	ch2 := Generator(10, 20, 30)
	ch3 := Generator(100, 200, 300)

	// Merge all sources
	merged := FanIn(ch1, ch2, ch3)

	fmt.Print("  Merged values: ")
	for v := range merged {
		fmt.Printf("%d ", v)
	}
	fmt.Println()
}

// completePipeline demonstrates full fan-out/fan-in
func completePipeline() {
	const numWorkers = 4
	const numItems = 12

	// Stage 1: Generate input
	input := make(chan int)
	go func() {
		defer close(input)
		for i := 1; i <= numItems; i++ {
			input <- i
		}
	}()

	// Stage 2: Fan out to workers (each worker squares input)
	workers := make([]<-chan int, numWorkers)
	for i := 0; i < numWorkers; i++ {
		workerID := i
		workers[i] = func(in <-chan int) <-chan int {
			out := make(chan int)
			go func() {
				defer close(out)
				for n := range in {
					time.Sleep(time.Duration(rand.Intn(30)) * time.Millisecond)
					result := n * n
					fmt.Printf("  Worker %d: %d -> %d\n", workerID, n, result)
					out <- result
				}
			}()
			return out
		}(input)
	}

	// Stage 3: Fan in results
	results := FanIn(workers...)

	// Stage 4: Collect and sum
	var sum int
	for result := range results {
		sum += result
	}

	fmt.Printf("  Sum of all squared values: %d\n", sum)
}

// Cancellable pipeline functions with context

// GeneratorWithContext produces values until cancelled
func GeneratorWithContext(ctx context.Context, nums ...int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for _, n := range nums {
			select {
			case <-ctx.Done():
				return
			case out <- n:
			}
		}
	}()
	return out
}

// SquareWithContext transforms with cancellation support
func SquareWithContext(ctx context.Context, in <-chan int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for {
			select {
			case <-ctx.Done():
				return
			case n, ok := <-in:
				if !ok {
					return
				}
				// Simulate slow processing
				time.Sleep(50 * time.Millisecond)
				select {
				case <-ctx.Done():
					return
				case out <- n * n:
				}
			}
		}
	}()
	return out
}

func cancellablePipeline() {
	// Create context with timeout
	ctx, cancel := context.WithTimeout(context.Background(), 150*time.Millisecond)
	defer cancel()

	// Build pipeline
	numbers := GeneratorWithContext(ctx, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
	squared := SquareWithContext(ctx, numbers)

	fmt.Print("  Processing (will timeout): ")
	count := 0
	for result := range squared {
		count++
		fmt.Printf("%d ", result)
	}
	fmt.Println()

	if ctx.Err() != nil {
		fmt.Printf("  Pipeline cancelled after %d items: %v\n", count, ctx.Err())
	} else {
		fmt.Printf("  Pipeline completed with %d items\n", count)
	}
}
