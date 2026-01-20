// Example 2: RESTful API with Middleware
//
// This example demonstrates building a RESTful API with:
// - CRUD operations for a User resource
// - Middleware chain (logging, recovery, request ID)
// - Proper HTTP method handling
// - JSON request/response handling
// - In-memory data store
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"

	"github.com/google/uuid"
)

// User represents our domain model
type User struct {
	ID        string    `json:"id"`
	Name      string    `json:"name"`
	Email     string    `json:"email"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// CreateUserRequest is the request body for creating a user
type CreateUserRequest struct {
	Name  string `json:"name"`
	Email string `json:"email"`
}

// UpdateUserRequest is the request body for updating a user
type UpdateUserRequest struct {
	Name  string `json:"name,omitempty"`
	Email string `json:"email,omitempty"`
}

// UserStore is a simple in-memory store
type UserStore struct {
	mu    sync.RWMutex
	users map[string]*User
}

func NewUserStore() *UserStore {
	return &UserStore{
		users: make(map[string]*User),
	}
}

func (s *UserStore) Create(user *User) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.users[user.ID] = user
}

func (s *UserStore) Get(id string) (*User, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	user, ok := s.users[id]
	return user, ok
}

func (s *UserStore) List() []*User {
	s.mu.RLock()
	defer s.mu.RUnlock()
	users := make([]*User, 0, len(s.users))
	for _, u := range s.users {
		users = append(users, u)
	}
	return users
}

func (s *UserStore) Update(id string, name, email string) (*User, bool) {
	s.mu.Lock()
	defer s.mu.Unlock()
	user, ok := s.users[id]
	if !ok {
		return nil, false
	}
	if name != "" {
		user.Name = name
	}
	if email != "" {
		user.Email = email
	}
	user.UpdatedAt = time.Now()
	return user, true
}

func (s *UserStore) Delete(id string) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.users[id]; !ok {
		return false
	}
	delete(s.users, id)
	return true
}

// Middleware types
type Middleware func(http.Handler) http.Handler

// responseWriter wraps http.ResponseWriter to capture status code
type responseWriter struct {
	http.ResponseWriter
	status int
}

func (rw *responseWriter) WriteHeader(code int) {
	rw.status = code
	rw.ResponseWriter.WriteHeader(code)
}

// LoggingMiddleware logs request details
func LoggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		wrapped := &responseWriter{ResponseWriter: w, status: http.StatusOK}

		next.ServeHTTP(wrapped, r)

		reqID := r.Context().Value("requestID")
		log.Printf("[%s] %s %s %d %v",
			reqID, r.Method, r.URL.Path, wrapped.status, time.Since(start))
	})
}

// RecoveryMiddleware recovers from panics
func RecoveryMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if err := recover(); err != nil {
				log.Printf("Panic recovered: %v", err)
				http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			}
		}()
		next.ServeHTTP(wrapped, r)
	})
}

// RequestIDMiddleware adds a unique request ID
func RequestIDMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		requestID := uuid.New().String()[:8]
		ctx := context.WithValue(r.Context(), "requestID", requestID)
		w.Header().Set("X-Request-ID", requestID)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

// Chain applies middlewares in order
func Chain(h http.Handler, middlewares ...Middleware) http.Handler {
	for i := len(middlewares) - 1; i >= 0; i-- {
		h = middlewares[i](h)
	}
	return h
}

// UserHandler handles user-related HTTP requests
type UserHandler struct {
	store *UserStore
}

func NewUserHandler(store *UserStore) *UserHandler {
	return &UserHandler{store: store}
}

// writeJSON writes a JSON response
func writeJSON(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(data)
}

// writeError writes an error response
func writeError(w http.ResponseWriter, status int, message string) {
	writeJSON(w, status, map[string]string{"error": message})
}

// HandleUsers handles /users endpoint
func (h *UserHandler) HandleUsers(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		h.listUsers(w, r)
	case http.MethodPost:
		h.createUser(w, r)
	default:
		writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
	}
}

// HandleUser handles /users/{id} endpoint
func (h *UserHandler) HandleUser(w http.ResponseWriter, r *http.Request) {
	// Extract ID from path (Go 1.22+ pattern matching)
	id := r.PathValue("id")
	if id == "" {
		// Fallback for older Go versions or manual extraction
		id = r.URL.Path[len("/users/"):]
	}

	if id == "" {
		writeError(w, http.StatusBadRequest, "User ID required")
		return
	}

	switch r.Method {
	case http.MethodGet:
		h.getUser(w, r, id)
	case http.MethodPut:
		h.updateUser(w, r, id)
	case http.MethodDelete:
		h.deleteUser(w, r, id)
	default:
		writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
	}
}

func (h *UserHandler) listUsers(w http.ResponseWriter, r *http.Request) {
	users := h.store.List()
	writeJSON(w, http.StatusOK, map[string]interface{}{
		"users": users,
		"count": len(users),
	})
}

func (h *UserHandler) createUser(w http.ResponseWriter, r *http.Request) {
	var req CreateUserRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "Invalid JSON")
		return
	}
	defer r.Body.Close()

	// Validate required fields
	if req.Name == "" || req.Email == "" {
		writeError(w, http.StatusBadRequest, "Name and email are required")
		return
	}

	user := &User{
		ID:        uuid.New().String(),
		Name:      req.Name,
		Email:     req.Email,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	h.store.Create(user)
	writeJSON(w, http.StatusCreated, user)
}

func (h *UserHandler) getUser(w http.ResponseWriter, r *http.Request, id string) {
	user, ok := h.store.Get(id)
	if !ok {
		writeError(w, http.StatusNotFound, "User not found")
		return
	}
	writeJSON(w, http.StatusOK, user)
}

func (h *UserHandler) updateUser(w http.ResponseWriter, r *http.Request, id string) {
	var req UpdateUserRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "Invalid JSON")
		return
	}
	defer r.Body.Close()

	user, ok := h.store.Update(id, req.Name, req.Email)
	if !ok {
		writeError(w, http.StatusNotFound, "User not found")
		return
	}
	writeJSON(w, http.StatusOK, user)
}

func (h *UserHandler) deleteUser(w http.ResponseWriter, r *http.Request, id string) {
	if !h.store.Delete(id) {
		writeError(w, http.StatusNotFound, "User not found")
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

func main() {
	// Create store and handler
	store := NewUserStore()
	userHandler := NewUserHandler(store)

	// Create router
	mux := http.NewServeMux()

	// Register routes
	mux.HandleFunc("/users", userHandler.HandleUsers)
	mux.HandleFunc("/users/", userHandler.HandleUser)

	// Apply middleware chain
	handler := Chain(
		mux,
		RecoveryMiddleware,
		LoggingMiddleware,
		RequestIDMiddleware,
	)

	// Configure server
	server := &http.Server{
		Addr:         ":8080",
		Handler:      handler,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 10 * time.Second,
	}

	fmt.Println("Example 2: RESTful API with Middleware")
	fmt.Println("========================================")
	fmt.Println()
	fmt.Println("Starting server on http://localhost:8080")
	fmt.Println()
	fmt.Println("Available endpoints:")
	fmt.Println("  GET    /users      - List all users")
	fmt.Println("  POST   /users      - Create a new user")
	fmt.Println("  GET    /users/{id} - Get a user by ID")
	fmt.Println("  PUT    /users/{id} - Update a user")
	fmt.Println("  DELETE /users/{id} - Delete a user")
	fmt.Println()
	fmt.Println("Try these commands:")
	fmt.Println("  # List users")
	fmt.Println("  curl http://localhost:8080/users")
	fmt.Println()
	fmt.Println("  # Create a user")
	fmt.Println(`  curl -X POST http://localhost:8080/users -H "Content-Type: application/json" -d '{"name":"John Doe","email":"john@example.com"}'`)
	fmt.Println()
	fmt.Println("  # Get a user (replace {id} with actual ID)")
	fmt.Println("  curl http://localhost:8080/users/{id}")
	fmt.Println()
	fmt.Println("  # Update a user")
	fmt.Println(`  curl -X PUT http://localhost:8080/users/{id} -H "Content-Type: application/json" -d '{"name":"Jane Doe"}'`)
	fmt.Println()
	fmt.Println("  # Delete a user")
	fmt.Println("  curl -X DELETE http://localhost:8080/users/{id}")
	fmt.Println()
	fmt.Println("Press Ctrl+C to stop the server")
	fmt.Println()

	if err := server.ListenAndServe(); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}
