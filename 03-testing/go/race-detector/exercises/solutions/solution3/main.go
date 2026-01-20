// Solution for Exercise 3: Fix the Racy Metrics Collector
//
// This solution uses atomic operations for simple counters and a mutex for the map.
package main

import (
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

// MetricsCollector collects various metrics - now thread-safe
type MetricsCollector struct {
	totalRequests atomic.Int64  // Atomic for simple counter
	errorCount    atomic.Int64  // Atomic for simple counter

	mu          sync.RWMutex    // Mutex for complex operations
	lastRequest time.Time       // Protected by mu
	endpoints   map[string]int64 // Protected by mu
}

// NewMetricsCollector creates a new collector
func NewMetricsCollector() *MetricsCollector {
	return &MetricsCollector{
		endpoints: make(map[string]int64),
	}
}

// RecordRequest records a request to an endpoint - now thread-safe
func (m *MetricsCollector) RecordRequest(endpoint string, isError bool) {
	// Atomic operations for simple counters
	m.totalRequests.Add(1)

	if isError {
		m.errorCount.Add(1)
	}

	// Mutex for map and time operations
	m.mu.Lock()
	m.lastRequest = time.Now()
	m.endpoints[endpoint]++
	m.mu.Unlock()
}

// GetTotalRequests returns total request count - now thread-safe
func (m *MetricsCollector) GetTotalRequests() int64 {
	return m.totalRequests.Load()
}

// GetErrorCount returns error count - now thread-safe
func (m *MetricsCollector) GetErrorCount() int64 {
	return m.errorCount.Load()
}

// GetEndpointCount returns count for a specific endpoint - now thread-safe
func (m *MetricsCollector) GetEndpointCount(endpoint string) int64 {
	m.mu.RLock()
	defer m.mu.RUnlock()
	return m.endpoints[endpoint]
}

// Snapshot returns a copy of all metrics - now thread-safe
func (m *MetricsCollector) Snapshot() map[string]interface{} {
	m.mu.RLock()
	defer m.mu.RUnlock()

	snapshot := make(map[string]interface{})
	snapshot["total_requests"] = m.totalRequests.Load()
	snapshot["error_count"] = m.errorCount.Load()
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

/*
Key Changes:

1. Used atomic.Int64 for totalRequests and errorCount
   - These are simple counters with high contention
   - Atomic operations are faster than mutex for this use case

2. Used sync.RWMutex for lastRequest and endpoints
   - These require more complex operations
   - RWMutex allows concurrent reads

3. In RecordRequest:
   - Atomic Add for counters (no lock needed)
   - Mutex Lock for map and time updates

4. In getter methods:
   - Atomic Load for counters
   - RLock for map access

5. In Snapshot:
   - RLock to get consistent view of all data
   - Copy the map to avoid returning reference to internal data

Design Decisions:

Why mix atomics and mutex?
- Atomics are faster for simple counter operations
- Mutex is needed for map operations and getting consistent snapshots
- This hybrid approach gives the best performance

Why copy the map in Snapshot?
- Returns a safe copy that callers can use without synchronization
- Prevents callers from accidentally modifying internal state
- Snapshot represents a point-in-time view

Alternative: All mutex approach
- Simpler to understand
- Slightly slower for counter operations
- Good choice if simplicity is more important than performance

Alternative: All sync.Map approach
- Eliminates explicit locking
- Loses type safety
- Count operation becomes expensive
*/
