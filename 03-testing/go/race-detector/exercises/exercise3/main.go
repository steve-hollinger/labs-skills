// Exercise 3: Fix the Racy Metrics Collector
//
// This metrics collector has multiple race conditions. Your task is to
// fix all of them to make it thread-safe.
//
// Instructions:
// 1. Run this code: go run main.go
// 2. Run with race detector: go run -race main.go
// 3. Notice multiple race conditions are detected
// 4. Fix ALL race conditions in the MetricsCollector
// 5. Verify with: go run -race main.go
//
// Expected Output (after fix):
// - Total requests should be 1000
// - Error count should be 100 (10% of requests)
// - Endpoint counts should sum to 1000
// - No race detector warnings
//
// Hints:
// - Consider using atomic operations for simple counters
// - Use mutex for the map operations
// - Think about which operations need which type of synchronization
// - The snapshot method needs to return a consistent view
package main

import (
	"fmt"
	"sync"
	"time"
)

// MetricsCollector collects various metrics - fix all race conditions!
type MetricsCollector struct {
	// TODO: Add synchronization as needed
	totalRequests int64
	errorCount    int64
	lastRequest   time.Time
	endpoints     map[string]int64
}

// NewMetricsCollector creates a new collector
func NewMetricsCollector() *MetricsCollector {
	return &MetricsCollector{
		endpoints: make(map[string]int64),
	}
}

// RecordRequest records a request to an endpoint - fix the races!
func (m *MetricsCollector) RecordRequest(endpoint string, isError bool) {
	// TODO: Make these operations thread-safe
	m.totalRequests++
	m.lastRequest = time.Now()
	m.endpoints[endpoint]++

	if isError {
		m.errorCount++
	}
}

// GetTotalRequests returns total request count - fix the race!
func (m *MetricsCollector) GetTotalRequests() int64 {
	// TODO: Make this thread-safe
	return m.totalRequests
}

// GetErrorCount returns error count - fix the race!
func (m *MetricsCollector) GetErrorCount() int64 {
	// TODO: Make this thread-safe
	return m.errorCount
}

// GetEndpointCount returns count for a specific endpoint - fix the race!
func (m *MetricsCollector) GetEndpointCount(endpoint string) int64 {
	// TODO: Make this thread-safe
	return m.endpoints[endpoint]
}

// Snapshot returns a copy of all metrics - fix the race!
func (m *MetricsCollector) Snapshot() map[string]interface{} {
	// TODO: Make this thread-safe and return consistent data
	snapshot := make(map[string]interface{})
	snapshot["total_requests"] = m.totalRequests
	snapshot["error_count"] = m.errorCount
	snapshot["last_request"] = m.lastRequest

	endpointsCopy := make(map[string]int64)
	for k, v := range m.endpoints {
		endpointsCopy[k] = v
	}
	snapshot["endpoints"] = endpointsCopy

	return snapshot
}

func main() {
	collector := NewMetricsCollector()
	var wg sync.WaitGroup

	endpoints := []string{"/api/users", "/api/products", "/api/orders", "/api/health"}

	// Simulate 1000 concurrent requests
	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			endpoint := endpoints[id%len(endpoints)]
			isError := id%10 == 0 // 10% error rate
			collector.RecordRequest(endpoint, isError)
		}(i)
	}

	wg.Wait()

	// Get final metrics
	fmt.Println("=== Metrics Report ===")
	fmt.Printf("Total Requests: %d (expected: 1000)\n", collector.GetTotalRequests())
	fmt.Printf("Error Count: %d (expected: 100)\n", collector.GetErrorCount())

	var endpointSum int64
	for _, ep := range endpoints {
		count := collector.GetEndpointCount(ep)
		fmt.Printf("  %s: %d\n", ep, count)
		endpointSum += count
	}
	fmt.Printf("Endpoint Sum: %d (expected: 1000)\n", endpointSum)

	// Verify
	success := true
	if collector.GetTotalRequests() != 1000 {
		fmt.Println("FAILED: Total requests incorrect")
		success = false
	}
	if collector.GetErrorCount() != 100 {
		fmt.Println("FAILED: Error count incorrect")
		success = false
	}
	if endpointSum != 1000 {
		fmt.Println("FAILED: Endpoint sum incorrect")
		success = false
	}

	if success {
		fmt.Println("\nSUCCESS! All metrics are correct.")
	} else {
		fmt.Println("\nFAILED! Metrics are incorrect due to race conditions.")
	}
}
