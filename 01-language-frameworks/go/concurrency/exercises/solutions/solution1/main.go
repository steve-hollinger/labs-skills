// Solution for Exercise 1: Concurrent URL Fetcher
//
// This solution demonstrates concurrent HTTP fetching with timeout handling.

package main

import (
	"context"
	"fmt"
	"net/http"
	"sync"
	"time"
)

// FetchResult holds the result of fetching a URL
type FetchResult struct {
	URL        string
	StatusCode int
	Duration   time.Duration
	Error      error
}

// FetchURLs fetches multiple URLs concurrently with timeout
func FetchURLs(urls []string, timeout time.Duration) []FetchResult {
	results := make([]FetchResult, len(urls))
	var wg sync.WaitGroup

	for i, url := range urls {
		wg.Add(1)
		go func(index int, u string) {
			defer wg.Done()
			results[index] = fetchURL(u, timeout)
		}(i, url)
	}

	wg.Wait()
	return results
}

// fetchURL fetches a single URL with context
func fetchURL(url string, timeout time.Duration) FetchResult {
	start := time.Now()

	// Create context with timeout
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	// Create request with context
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return FetchResult{
			URL:      url,
			Duration: time.Since(start),
			Error:    fmt.Errorf("failed to create request: %w", err),
		}
	}

	// Create HTTP client
	client := &http.Client{}

	// Execute request
	resp, err := client.Do(req)
	duration := time.Since(start)

	if err != nil {
		// Check if it's a timeout
		if ctx.Err() == context.DeadlineExceeded {
			return FetchResult{
				URL:      url,
				Duration: duration,
				Error:    fmt.Errorf("timeout after %v", timeout),
			}
		}
		return FetchResult{
			URL:      url,
			Duration: duration,
			Error:    err,
		}
	}
	defer resp.Body.Close()

	return FetchResult{
		URL:        url,
		StatusCode: resp.StatusCode,
		Duration:   duration,
	}
}

// FetchURLsWithProgress fetches URLs and reports progress via callback
func FetchURLsWithProgress(urls []string, timeout time.Duration, progress func(FetchResult)) []FetchResult {
	results := make([]FetchResult, len(urls))
	resultCh := make(chan struct {
		index  int
		result FetchResult
	}, len(urls))

	var wg sync.WaitGroup

	for i, url := range urls {
		wg.Add(1)
		go func(index int, u string) {
			defer wg.Done()
			result := fetchURL(u, timeout)
			resultCh <- struct {
				index  int
				result FetchResult
			}{index, result}
		}(i, url)
	}

	// Collect results
	go func() {
		wg.Wait()
		close(resultCh)
	}()

	for item := range resultCh {
		results[item.index] = item.result
		if progress != nil {
			progress(item.result)
		}
	}

	return results
}

func main() {
	urls := []string{
		"https://httpbin.org/get",
		"https://httpbin.org/delay/1",
		"https://httpbin.org/status/404",
		"https://invalid-url-that-does-not-exist.com/",
		"https://httpbin.org/delay/5", // This should timeout
	}

	fmt.Println("Solution 1: Concurrent URL Fetcher")
	fmt.Println("===================================")
	fmt.Println()
	fmt.Println("Fetching URLs with 2 second timeout...")
	fmt.Println()

	start := time.Now()

	// Use FetchURLsWithProgress to show results as they complete
	results := FetchURLsWithProgress(urls, 2*time.Second, func(result FetchResult) {
		if result.Error != nil {
			fmt.Printf("COMPLETED: %s - Error: %v (%v)\n",
				result.URL, result.Error, result.Duration.Round(time.Millisecond))
		} else {
			fmt.Printf("COMPLETED: %s - Status: %d (%v)\n",
				result.URL, result.StatusCode, result.Duration.Round(time.Millisecond))
		}
	})

	totalTime := time.Since(start)

	fmt.Println()
	fmt.Println("Final Results (in original order):")
	fmt.Println("-----------------------------------")

	for _, result := range results {
		if result.Error != nil {
			fmt.Printf("FAIL: %s - Error: %v (%v)\n",
				result.URL, result.Error, result.Duration.Round(time.Millisecond))
		} else {
			fmt.Printf("OK:   %s - Status: %d (%v)\n",
				result.URL, result.StatusCode, result.Duration.Round(time.Millisecond))
		}
	}

	fmt.Printf("\nTotal time: %v\n", totalTime.Round(time.Millisecond))
	fmt.Println("(Should be ~2-3 seconds since fetches run concurrently)")
}
