// Example 3: Production-Ready API
//
// This example demonstrates production patterns:
// - Graceful shutdown
// - Structured error handling
// - Request validation
// - Health checks with dependencies
// - Configuration management
// - Metrics endpoint
package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"sync"
	"sync/atomic"
	"syscall"
	"time"
)

// Config holds server configuration
type Config struct {
	Port            string
	ReadTimeout     time.Duration
	WriteTimeout    time.Duration
	ShutdownTimeout time.Duration
}

func DefaultConfig() *Config {
	return &Config{
		Port:            getEnv("PORT", "8080"),
		ReadTimeout:     15 * time.Second,
		WriteTimeout:    15 * time.Second,
		ShutdownTimeout: 30 * time.Second,
	}
}

func getEnv(key, defaultVal string) string {
	if val := os.Getenv(key); val != "" {
		return val
	}
	return defaultVal
}

// Metrics tracks request statistics
type Metrics struct {
	RequestCount   atomic.Int64
	ErrorCount     atomic.Int64
	RequestLatency sync.Map // path -> []time.Duration
}

func NewMetrics() *Metrics {
	return &Metrics{}
}

func (m *Metrics) RecordRequest(path string, duration time.Duration, isError bool) {
	m.RequestCount.Add(1)
	if isError {
		m.ErrorCount.Add(1)
	}
}

func (m *Metrics) GetStats() map[string]interface{} {
	return map[string]interface{}{
		"total_requests": m.RequestCount.Load(),
		"total_errors":   m.ErrorCount.Load(),
	}
}

// APIError represents a structured API error
type APIError struct {
	Status  int               `json:"-"`
	Message string            `json:"error"`
	Code    string            `json:"code,omitempty"`
	Details map[string]string `json:"details,omitempty"`
}

func (e *APIError) Error() string {
	return e.Message
}

var (
	ErrValidation = &APIError{
		Status:  http.StatusUnprocessableEntity,
		Message: "Validation failed",
		Code:    "VALIDATION_ERROR",
	}
	ErrNotFound = &APIError{
		Status:  http.StatusNotFound,
		Message: "Resource not found",
		Code:    "NOT_FOUND",
	}
	ErrInternal = &APIError{
		Status:  http.StatusInternalServerError,
		Message: "Internal server error",
		Code:    "INTERNAL_ERROR",
	}
)

// ValidationError holds field validation errors
type ValidationError struct {
	Field   string `json:"field"`
	Message string `json:"message"`
}

// Validator provides validation helpers
type Validator struct {
	errors []ValidationError
}

func (v *Validator) Required(field, value string) {
	if value == "" {
		v.errors = append(v.errors, ValidationError{
			Field:   field,
			Message: "is required",
		})
	}
}

func (v *Validator) MinLength(field, value string, min int) {
	if len(value) < min {
		v.errors = append(v.errors, ValidationError{
			Field:   field,
			Message: fmt.Sprintf("must be at least %d characters", min),
		})
	}
}

func (v *Validator) Valid() bool {
	return len(v.errors) == 0
}

func (v *Validator) Errors() []ValidationError {
	return v.errors
}

// Response helpers
func writeJSON(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(data)
}

func writeError(w http.ResponseWriter, err *APIError) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(err.Status)
	json.NewEncoder(w).Encode(err)
}

func writeValidationErrors(w http.ResponseWriter, errors []ValidationError) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusUnprocessableEntity)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"error":   "Validation failed",
		"code":    "VALIDATION_ERROR",
		"details": errors,
	})
}

// responseWriter wraps ResponseWriter to capture status
type responseWriter struct {
	http.ResponseWriter
	status int
}

func (rw *responseWriter) WriteHeader(code int) {
	rw.status = code
	rw.ResponseWriter.WriteHeader(code)
}

// Middleware
func MetricsMiddleware(metrics *Metrics) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()
			wrapped := &responseWriter{ResponseWriter: w, status: http.StatusOK}

			next.ServeHTTP(wrapped, r)

			isError := wrapped.status >= 400
			metrics.RecordRequest(r.URL.Path, time.Since(start), isError)
		})
	}
}

func RecoveryMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if err := recover(); err != nil {
				log.Printf("Panic recovered: %v", err)
				writeError(w, ErrInternal)
			}
		}()
		next.ServeHTTP(w, r)
	})
}

func LoggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		wrapped := &responseWriter{ResponseWriter: w, status: http.StatusOK}

		next.ServeHTTP(wrapped, r)

		log.Printf("%s %s %d %v", r.Method, r.URL.Path, wrapped.status, time.Since(start))
	})
}

// Order represents a domain model
type Order struct {
	ID        string    `json:"id"`
	Product   string    `json:"product"`
	Quantity  int       `json:"quantity"`
	Price     float64   `json:"price"`
	Status    string    `json:"status"`
	CreatedAt time.Time `json:"created_at"`
}

// CreateOrderRequest with validation
type CreateOrderRequest struct {
	Product  string  `json:"product"`
	Quantity int     `json:"quantity"`
	Price    float64 `json:"price"`
}

func (r *CreateOrderRequest) Validate() []ValidationError {
	v := &Validator{}
	v.Required("product", r.Product)
	v.MinLength("product", r.Product, 2)
	if r.Quantity <= 0 {
		v.errors = append(v.errors, ValidationError{
			Field:   "quantity",
			Message: "must be greater than 0",
		})
	}
	if r.Price <= 0 {
		v.errors = append(v.errors, ValidationError{
			Field:   "price",
			Message: "must be greater than 0",
		})
	}
	return v.Errors()
}

// OrderStore with simulated database operations
type OrderStore struct {
	mu     sync.RWMutex
	orders map[string]*Order
}

func NewOrderStore() *OrderStore {
	return &OrderStore{
		orders: make(map[string]*Order),
	}
}

func (s *OrderStore) Create(ctx context.Context, order *Order) error {
	// Simulate database latency
	select {
	case <-time.After(10 * time.Millisecond):
	case <-ctx.Done():
		return ctx.Err()
	}

	s.mu.Lock()
	defer s.mu.Unlock()
	s.orders[order.ID] = order
	return nil
}

func (s *OrderStore) Get(ctx context.Context, id string) (*Order, error) {
	select {
	case <-time.After(5 * time.Millisecond):
	case <-ctx.Done():
		return nil, ctx.Err()
	}

	s.mu.RLock()
	defer s.mu.RUnlock()
	order, ok := s.orders[id]
	if !ok {
		return nil, errors.New("order not found")
	}
	return order, nil
}

func (s *OrderStore) List(ctx context.Context) ([]*Order, error) {
	select {
	case <-time.After(10 * time.Millisecond):
	case <-ctx.Done():
		return nil, ctx.Err()
	}

	s.mu.RLock()
	defer s.mu.RUnlock()
	orders := make([]*Order, 0, len(s.orders))
	for _, o := range s.orders {
		orders = append(orders, o)
	}
	return orders, nil
}

// Handlers
type Server struct {
	store   *OrderStore
	metrics *Metrics
}

func NewServer(store *OrderStore, metrics *Metrics) *Server {
	return &Server{store: store, metrics: metrics}
}

func (s *Server) handleHealth(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		writeError(w, &APIError{Status: http.StatusMethodNotAllowed, Message: "Method not allowed"})
		return
	}

	// Check dependencies (database, etc.)
	ctx, cancel := context.WithTimeout(r.Context(), 1*time.Second)
	defer cancel()

	_, err := s.store.List(ctx)
	if err != nil {
		writeJSON(w, http.StatusServiceUnavailable, map[string]interface{}{
			"status":  "unhealthy",
			"error":   "Database check failed",
			"checked": time.Now(),
		})
		return
	}

	writeJSON(w, http.StatusOK, map[string]interface{}{
		"status":  "healthy",
		"checked": time.Now(),
	})
}

func (s *Server) handleMetrics(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		writeError(w, &APIError{Status: http.StatusMethodNotAllowed, Message: "Method not allowed"})
		return
	}
	writeJSON(w, http.StatusOK, s.metrics.GetStats())
}

func (s *Server) handleOrders(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		s.listOrders(w, r)
	case http.MethodPost:
		s.createOrder(w, r)
	default:
		writeError(w, &APIError{Status: http.StatusMethodNotAllowed, Message: "Method not allowed"})
	}
}

func (s *Server) listOrders(w http.ResponseWriter, r *http.Request) {
	orders, err := s.store.List(r.Context())
	if err != nil {
		if errors.Is(err, context.Canceled) {
			return // Client disconnected
		}
		writeError(w, ErrInternal)
		return
	}

	writeJSON(w, http.StatusOK, map[string]interface{}{
		"orders": orders,
		"count":  len(orders),
	})
}

func (s *Server) createOrder(w http.ResponseWriter, r *http.Request) {
	var req CreateOrderRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, &APIError{
			Status:  http.StatusBadRequest,
			Message: "Invalid JSON",
			Code:    "INVALID_JSON",
		})
		return
	}
	defer r.Body.Close()

	// Validate request
	if errors := req.Validate(); len(errors) > 0 {
		writeValidationErrors(w, errors)
		return
	}

	order := &Order{
		ID:        fmt.Sprintf("ord_%d", time.Now().UnixNano()),
		Product:   req.Product,
		Quantity:  req.Quantity,
		Price:     req.Price,
		Status:    "pending",
		CreatedAt: time.Now(),
	}

	if err := s.store.Create(r.Context(), order); err != nil {
		if errors.Is(err, context.Canceled) {
			return
		}
		writeError(w, ErrInternal)
		return
	}

	writeJSON(w, http.StatusCreated, order)
}

func main() {
	config := DefaultConfig()

	// Initialize dependencies
	store := NewOrderStore()
	metrics := NewMetrics()
	server := NewServer(store, metrics)

	// Create router
	mux := http.NewServeMux()
	mux.HandleFunc("/health", server.handleHealth)
	mux.HandleFunc("/metrics", server.handleMetrics)
	mux.HandleFunc("/orders", server.handleOrders)

	// Apply middleware
	handler := RecoveryMiddleware(
		LoggingMiddleware(
			MetricsMiddleware(metrics)(mux),
		),
	)

	// Configure HTTP server
	httpServer := &http.Server{
		Addr:         ":" + config.Port,
		Handler:      handler,
		ReadTimeout:  config.ReadTimeout,
		WriteTimeout: config.WriteTimeout,
	}

	// Start server in goroutine
	go func() {
		fmt.Println("Example 3: Production-Ready API")
		fmt.Println("========================================")
		fmt.Println()
		fmt.Printf("Starting server on http://localhost:%s\n", config.Port)
		fmt.Println()
		fmt.Println("Available endpoints:")
		fmt.Println("  GET  /health  - Health check with dependency verification")
		fmt.Println("  GET  /metrics - Request metrics")
		fmt.Println("  GET  /orders  - List all orders")
		fmt.Println("  POST /orders  - Create a new order")
		fmt.Println()
		fmt.Println("Try these commands:")
		fmt.Println("  curl http://localhost:8080/health")
		fmt.Println("  curl http://localhost:8080/metrics")
		fmt.Println(`  curl -X POST http://localhost:8080/orders -H "Content-Type: application/json" -d '{"product":"Widget","quantity":5,"price":29.99}'`)
		fmt.Println()
		fmt.Println("Press Ctrl+C for graceful shutdown")
		fmt.Println()

		if err := httpServer.ListenAndServe(); err != http.ErrServerClosed {
			log.Fatalf("Server error: %v", err)
		}
	}()

	// Wait for interrupt signal
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("Shutting down server...")

	// Create shutdown context with timeout
	ctx, cancel := context.WithTimeout(context.Background(), config.ShutdownTimeout)
	defer cancel()

	// Attempt graceful shutdown
	if err := httpServer.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %v", err)
	}

	log.Println("Server stopped gracefully")
}
