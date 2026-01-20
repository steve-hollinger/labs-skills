// Example 1: Basic HTTP Server
//
// This example demonstrates the fundamental patterns for building HTTP servers
// in Go using the standard library. It covers:
// - Creating a basic HTTP server
// - Handling different routes
// - Reading request data
// - Writing JSON responses
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"
)

// Response types
type HealthResponse struct {
	Status    string    `json:"status"`
	Timestamp time.Time `json:"timestamp"`
}

type WelcomeResponse struct {
	Message string `json:"message"`
	Version string `json:"version"`
}

type EchoResponse struct {
	Method      string            `json:"method"`
	Path        string            `json:"path"`
	QueryParams map[string]string `json:"query_params"`
	Headers     map[string]string `json:"headers"`
}

// healthHandler returns a simple health check response
func healthHandler(w http.ResponseWriter, r *http.Request) {
	// Only allow GET requests
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	response := HealthResponse{
		Status:    "healthy",
		Timestamp: time.Now(),
	}

	// Set content type header before writing response
	w.Header().Set("Content-Type", "application/json")

	// Encode and write JSON response
	if err := json.NewEncoder(w).Encode(response); err != nil {
		log.Printf("Error encoding response: %v", err)
	}
}

// welcomeHandler returns a welcome message
func welcomeHandler(w http.ResponseWriter, r *http.Request) {
	// Check for exact path match (ServeMux "/" matches everything without a more specific handler)
	if r.URL.Path != "/" {
		http.NotFound(w, r)
		return
	}

	response := WelcomeResponse{
		Message: "Welcome to the Go HTTP Services skill!",
		Version: "1.0.0",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// echoHandler returns information about the incoming request
func echoHandler(w http.ResponseWriter, r *http.Request) {
	// Collect query parameters
	queryParams := make(map[string]string)
	for key, values := range r.URL.Query() {
		queryParams[key] = values[0] // Take first value if multiple
	}

	// Collect select headers
	headers := make(map[string]string)
	interestingHeaders := []string{"User-Agent", "Accept", "Content-Type"}
	for _, h := range interestingHeaders {
		if v := r.Header.Get(h); v != "" {
			headers[h] = v
		}
	}

	response := EchoResponse{
		Method:      r.Method,
		Path:        r.URL.Path,
		QueryParams: queryParams,
		Headers:     headers,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	// Create a new ServeMux (router)
	mux := http.NewServeMux()

	// Register handlers
	mux.HandleFunc("/", welcomeHandler)
	mux.HandleFunc("/health", healthHandler)
	mux.HandleFunc("/echo", echoHandler)

	// Configure server
	server := &http.Server{
		Addr:         ":8080",
		Handler:      mux,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 10 * time.Second,
	}

	fmt.Println("Example 1: Basic HTTP Server")
	fmt.Println("========================================")
	fmt.Println()
	fmt.Println("Starting server on http://localhost:8080")
	fmt.Println()
	fmt.Println("Available endpoints:")
	fmt.Println("  GET /        - Welcome message")
	fmt.Println("  GET /health  - Health check")
	fmt.Println("  GET /echo    - Echo request details")
	fmt.Println()
	fmt.Println("Try these commands:")
	fmt.Println("  curl http://localhost:8080/")
	fmt.Println("  curl http://localhost:8080/health")
	fmt.Println("  curl 'http://localhost:8080/echo?name=test&value=123'")
	fmt.Println()
	fmt.Println("Press Ctrl+C to stop the server")
	fmt.Println()

	// Start the server
	if err := server.ListenAndServe(); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}
