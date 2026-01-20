// Exercise 1: Health Check Endpoint
//
// Build a health check endpoint that returns structured JSON responses.
// This endpoint should be suitable for use with load balancers and
// container orchestration systems.
//
// Requirements:
// 1. Create a GET /health endpoint
// 2. Return a JSON response with these fields:
//    - status: "healthy" or "unhealthy"
//    - timestamp: current time in RFC3339 format
//    - version: application version (use "1.0.0")
//    - uptime: time since server started (in seconds)
// 3. Set Content-Type header to application/json
// 4. Return 405 for non-GET requests
//
// Expected Response:
// {
//   "status": "healthy",
//   "timestamp": "2024-01-15T10:30:00Z",
//   "version": "1.0.0",
//   "uptime": 3600
// }
//
// Hints:
// - Use time.Now().Format(time.RFC3339) for timestamp
// - Track server start time in a package-level variable
// - Use time.Since(startTime).Seconds() for uptime

package main

import (
	"fmt"
	"net/http"
)

// TODO: Add package-level variable to track server start time

// HealthResponse represents the health check response
// TODO: Define the struct with proper JSON tags

func healthHandler(w http.ResponseWriter, r *http.Request) {
	// TODO: Implement the health check handler
	// 1. Check if method is GET, return 405 if not
	// 2. Create HealthResponse with current values
	// 3. Set Content-Type header
	// 4. Encode and return JSON response

	fmt.Fprintln(w, "Implement your solution")
}

func main() {
	http.HandleFunc("/health", healthHandler)

	fmt.Println("Exercise 1: Health Check Endpoint")
	fmt.Println("Starting server on http://localhost:8080")
	fmt.Println("Test with: curl http://localhost:8080/health")

	http.ListenAndServe(":8080", nil)
}
