// Exercise 1: Concurrent URL Fetcher
//
// Build a concurrent URL fetcher that fetches multiple URLs in parallel
// with timeout handling and error reporting.
//
// Requirements:
// 1. Create a function FetchURLs that:
//    - Takes a list of URLs and a timeout duration
//    - Fetches all URLs concurrently
//    - Returns results in order of completion
//    - Respects the timeout for each fetch
//
// 2. Result structure:
//    - URL: the original URL
//    - StatusCode: HTTP status code (or 0 on error)
//    - Duration: time taken to fetch
//    - Error: any error that occurred
//
// 3. Handle these scenarios:
//    - Successful fetch
//    - Timeout
//    - Network error
//    - Invalid URL
//
// Hints:
// - Use context.WithTimeout for per-request timeouts
// - Use a WaitGroup to wait for all fetches
// - Use a channel to collect results
// - Use http.NewRequestWithContext for cancellable requests

package main

import (
	"fmt"
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
	// TODO: Implement concurrent URL fetching
	// 1. Create a results channel
	// 2. Start a goroutine for each URL
	// 3. Use context.WithTimeout for each request
	// 4. Collect results from the channel
	// 5. Return all results

	results := make([]FetchResult, len(urls))
	for i, url := range urls {
		results[i] = FetchResult{
			URL:   url,
			Error: fmt.Errorf("not implemented"),
		}
	}
	return results
}

// fetchURL fetches a single URL with context
func fetchURL(url string, timeout time.Duration) FetchResult {
	// TODO: Implement single URL fetch with timeout
	// 1. Create context with timeout
	// 2. Create HTTP request with context
	// 3. Execute request
	// 4. Return result with duration and status

	return FetchResult{
		URL:   url,
		Error: fmt.Errorf("not implemented"),
	}
}

func main() {
	urls := []string{
		"https://httpbin.org/get",
		"https://httpbin.org/delay/1",
		"https://httpbin.org/status/404",
		"https://invalid-url-that-does-not-exist.com/",
		"https://httpbin.org/delay/5", // This should timeout
	}

	fmt.Println("Exercise 1: Concurrent URL Fetcher")
	fmt.Println("===================================")
	fmt.Println()
	fmt.Println("Fetching URLs with 2 second timeout...")
	fmt.Println()

	start := time.Now()
	results := FetchURLs(urls, 2*time.Second)
	totalTime := time.Since(start)

	for _, result := range results {
		if result.Error != nil {
			fmt.Printf("FAIL: %s - Error: %v (%v)\n",
				result.URL, result.Error, result.Duration)
		} else {
			fmt.Printf("OK:   %s - Status: %d (%v)\n",
				result.URL, result.StatusCode, result.Duration)
		}
	}

	fmt.Printf("\nTotal time: %v\n", totalTime)
	fmt.Println("(Should be ~2-3 seconds if running concurrently)")
}
