// Package pipeline provides utilities for building concurrent pipelines.
package pipeline

import (
	"context"
	"sync"
)

// Stage represents a pipeline stage that transforms values
type Stage[T any] func(ctx context.Context, in <-chan T) <-chan T

// Generator creates a channel that produces values
func Generator[T any](ctx context.Context, values ...T) <-chan T {
	out := make(chan T)
	go func() {
		defer close(out)
		for _, v := range values {
			select {
			case <-ctx.Done():
				return
			case out <- v:
			}
		}
	}()
	return out
}

// GeneratorFunc creates a channel using a generator function
func GeneratorFunc[T any](ctx context.Context, gen func() (T, bool)) <-chan T {
	out := make(chan T)
	go func() {
		defer close(out)
		for {
			v, ok := gen()
			if !ok {
				return
			}
			select {
			case <-ctx.Done():
				return
			case out <- v:
			}
		}
	}()
	return out
}

// Map transforms each value using a function
func Map[T, U any](ctx context.Context, in <-chan T, fn func(T) U) <-chan U {
	out := make(chan U)
	go func() {
		defer close(out)
		for {
			select {
			case <-ctx.Done():
				return
			case v, ok := <-in:
				if !ok {
					return
				}
				select {
				case <-ctx.Done():
					return
				case out <- fn(v):
				}
			}
		}
	}()
	return out
}

// Filter keeps only values that pass the predicate
func Filter[T any](ctx context.Context, in <-chan T, predicate func(T) bool) <-chan T {
	out := make(chan T)
	go func() {
		defer close(out)
		for {
			select {
			case <-ctx.Done():
				return
			case v, ok := <-in:
				if !ok {
					return
				}
				if predicate(v) {
					select {
					case <-ctx.Done():
						return
					case out <- v:
					}
				}
			}
		}
	}()
	return out
}

// FanOut distributes input to n workers
func FanOut[T, U any](ctx context.Context, in <-chan T, n int, worker func(T) U) []<-chan U {
	outputs := make([]<-chan U, n)
	for i := 0; i < n; i++ {
		outputs[i] = workerChan(ctx, in, worker)
	}
	return outputs
}

func workerChan[T, U any](ctx context.Context, in <-chan T, worker func(T) U) <-chan U {
	out := make(chan U)
	go func() {
		defer close(out)
		for {
			select {
			case <-ctx.Done():
				return
			case v, ok := <-in:
				if !ok {
					return
				}
				select {
				case <-ctx.Done():
					return
				case out <- worker(v):
				}
			}
		}
	}()
	return out
}

// FanIn merges multiple channels into one
func FanIn[T any](ctx context.Context, inputs ...<-chan T) <-chan T {
	out := make(chan T)
	var wg sync.WaitGroup

	for _, ch := range inputs {
		wg.Add(1)
		go func(c <-chan T) {
			defer wg.Done()
			for {
				select {
				case <-ctx.Done():
					return
				case v, ok := <-c:
					if !ok {
						return
					}
					select {
					case <-ctx.Done():
						return
					case out <- v:
					}
				}
			}
		}(ch)
	}

	go func() {
		wg.Wait()
		close(out)
	}()

	return out
}

// Collect gathers all values from a channel into a slice
func Collect[T any](ctx context.Context, in <-chan T) []T {
	var results []T
	for {
		select {
		case <-ctx.Done():
			return results
		case v, ok := <-in:
			if !ok {
				return results
			}
			results = append(results, v)
		}
	}
}

// Take returns a channel that yields at most n values
func Take[T any](ctx context.Context, in <-chan T, n int) <-chan T {
	out := make(chan T)
	go func() {
		defer close(out)
		count := 0
		for {
			if count >= n {
				return
			}
			select {
			case <-ctx.Done():
				return
			case v, ok := <-in:
				if !ok {
					return
				}
				select {
				case <-ctx.Done():
					return
				case out <- v:
					count++
				}
			}
		}
	}()
	return out
}

// Skip returns a channel that skips the first n values
func Skip[T any](ctx context.Context, in <-chan T, n int) <-chan T {
	out := make(chan T)
	go func() {
		defer close(out)
		count := 0
		for {
			select {
			case <-ctx.Done():
				return
			case v, ok := <-in:
				if !ok {
					return
				}
				if count >= n {
					select {
					case <-ctx.Done():
						return
					case out <- v:
					}
				} else {
					count++
				}
			}
		}
	}()
	return out
}

// Batch groups values into batches of size n
func Batch[T any](ctx context.Context, in <-chan T, size int) <-chan []T {
	out := make(chan []T)
	go func() {
		defer close(out)
		batch := make([]T, 0, size)

		for {
			select {
			case <-ctx.Done():
				if len(batch) > 0 {
					out <- batch
				}
				return
			case v, ok := <-in:
				if !ok {
					if len(batch) > 0 {
						out <- batch
					}
					return
				}
				batch = append(batch, v)
				if len(batch) >= size {
					select {
					case <-ctx.Done():
						return
					case out <- batch:
						batch = make([]T, 0, size)
					}
				}
			}
		}
	}()
	return out
}
