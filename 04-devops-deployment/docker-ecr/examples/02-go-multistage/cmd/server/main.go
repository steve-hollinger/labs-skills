// Package main provides a simple HTTP server demonstrating multi-stage Docker builds.
package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"runtime"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)

// version is set at build time via ldflags
var version = "dev"

// HealthResponse represents the health check response.
type HealthResponse struct {
	Status    string `json:"status"`
	Timestamp string `json:"timestamp"`
	Version   string `json:"version"`
}

// InfoResponse represents system information.
type InfoResponse struct {
	GoVersion string `json:"go_version"`
	OS        string `json:"os"`
	Arch      string `json:"arch"`
	Hostname  string `json:"hostname"`
	NumCPU    int    `json:"num_cpu"`
}

// MessageResponse represents a generic message response.
type MessageResponse struct {
	Message string `json:"message"`
}

func main() {
	r := chi.NewRouter()

	// Middleware
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(middleware.RealIP)

	// Routes
	r.Get("/", rootHandler)
	r.Get("/health", healthHandler)
	r.Get("/info", infoHandler)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("Starting server on port %s (version: %s)", port, version)
	if err := http.ListenAndServe(":"+port, r); err != nil {
		log.Fatal(err)
	}
}

func rootHandler(w http.ResponseWriter, r *http.Request) {
	resp := MessageResponse{
		Message: "Hello from Go in Docker!",
	}
	writeJSON(w, http.StatusOK, resp)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	resp := HealthResponse{
		Status:    "healthy",
		Timestamp: time.Now().UTC().Format(time.RFC3339),
		Version:   version,
	}
	writeJSON(w, http.StatusOK, resp)
}

func infoHandler(w http.ResponseWriter, r *http.Request) {
	hostname, _ := os.Hostname()
	resp := InfoResponse{
		GoVersion: runtime.Version(),
		OS:        runtime.GOOS,
		Arch:      runtime.GOARCH,
		Hostname:  hostname,
		NumCPU:    runtime.NumCPU(),
	}
	writeJSON(w, http.StatusOK, resp)
}

func writeJSON(w http.ResponseWriter, status int, v interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(v); err != nil {
		log.Printf("Error encoding JSON: %v", err)
	}
}
