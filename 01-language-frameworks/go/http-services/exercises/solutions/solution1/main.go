// Solution for Exercise 1: Health Check Endpoint
//
// This solution demonstrates a production-ready health check endpoint
// with proper JSON serialization, status tracking, and HTTP handling.

package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// Track when the server started
var serverStartTime = time.Now()

// HealthResponse represents the health check response
type HealthResponse struct {
	Status    string `json:"status"`
	Timestamp string `json:"timestamp"`
	Version   string `json:"version"`
	Uptime    int64  `json:"uptime"`
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	// Only allow GET requests
	if r.Method != http.MethodGet {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusMethodNotAllowed)
		json.NewEncoder(w).Encode(map[string]string{
			"error": "Method not allowed",
		})
		return
	}

	// Calculate uptime in seconds
	uptime := int64(time.Since(serverStartTime).Seconds())

	// Create the response
	response := HealthResponse{
		Status:    "healthy",
		Timestamp: time.Now().Format(time.RFC3339),
		Version:   "1.0.0",
		Uptime:    uptime,
	}

	// Set Content-Type header
	w.Header().Set("Content-Type", "application/json")

	// Encode and send response
	if err := json.NewEncoder(w).Encode(response); err != nil {
		// Log the error in production
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
}

func main() {
	http.HandleFunc("/health", healthHandler)

	fmt.Println("Solution 1: Health Check Endpoint")
	fmt.Println("Starting server on http://localhost:8080")
	fmt.Println()
	fmt.Println("Test with:")
	fmt.Println("  curl http://localhost:8080/health")
	fmt.Println("  curl -X POST http://localhost:8080/health  # Should return 405")
	fmt.Println()

	if err := http.ListenAndServe(":8080", nil); err != nil {
		fmt.Printf("Server error: %v\n", err)
	}
}
