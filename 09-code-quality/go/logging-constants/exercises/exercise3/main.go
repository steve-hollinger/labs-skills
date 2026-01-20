// Exercise 3: Context-Aware Logging Middleware
//
// Implement HTTP middleware that propagates logging context.
package main

import (
	"context"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"time"
)

// Log key constants
const (
	KeyRequestID  = "request_id"
	KeyUserID     = "user_id"
	KeyHTTPMethod = "http_method"
	KeyHTTPPath   = "http_path"
	KeyHTTPStatus = "http_status"
	KeyDuration   = "duration_ms"
	KeyComponent  = "component"
	KeyOperation  = "operation"
	KeyError      = "error"
)

// Log message constants
const (
	MsgRequestStarted   = "request started"
	MsgRequestCompleted = "request completed"
	MsgUserFetched      = "user fetched"
	MsgUserNotFound     = "user not found"
)

// Context key type
type ctxKey string

const loggerCtxKey ctxKey = "logger"

// TODO: Implement these functions
// WithLogger adds a logger to the context
func WithLogger(ctx context.Context, logger *slog.Logger) context.Context {
	// YOUR CODE HERE
	return ctx
}

// FromContext retrieves the logger from context
func FromContext(ctx context.Context) *slog.Logger {
	// YOUR CODE HERE
	// Return slog.Default() if no logger in context
	return slog.Default()
}

// TODO: Implement logging middleware
func LoggingMiddleware(logger *slog.Logger) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// YOUR CODE HERE
			// 1. Get or generate request ID from X-Request-ID header
			// 2. Create request-scoped logger with context
			// 3. Log request start
			// 4. Add logger to context
			// 5. Create response wrapper to capture status code
			// 6. Call next handler
			// 7. Log request completion with duration

			next.ServeHTTP(w, r)
		})
	}
}

// responseWriter wraps http.ResponseWriter to capture status code
type responseWriter struct {
	http.ResponseWriter
	status int
}

func (rw *responseWriter) WriteHeader(code int) {
	rw.status = code
	rw.ResponseWriter.WriteHeader(code)
}

func main() {
	fmt.Println("Exercise 3: Context-Aware Logging")
	fmt.Println("===================================")
	fmt.Println()

	logger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelDebug,
	}))

	// Create services
	repo := NewUserRepository(logger)
	svc := NewUserService(repo, logger)
	handler := NewUserHandler(svc)

	// Setup routes with middleware
	mux := http.NewServeMux()
	mux.HandleFunc("/users/", handler.GetUser)

	// Apply middleware
	wrappedMux := LoggingMiddleware(logger)(mux)

	fmt.Println("Starting server on :8080")
	fmt.Println("Test with: curl localhost:8080/users/123")
	fmt.Println("Test with: curl -H 'X-Request-ID: custom-id' localhost:8080/users/123")
	fmt.Println()

	// For exercise purposes, simulate a request instead of starting server
	simulateRequest(wrappedMux, logger)
}

func simulateRequest(handler http.Handler, logger *slog.Logger) {
	fmt.Println("=== Simulating Request ===")
	fmt.Println()

	// Create a test request
	req, _ := http.NewRequest("GET", "/users/123", nil)
	req.Header.Set("X-Request-ID", "test-req-001")

	// Create a test response writer
	w := &testResponseWriter{headers: make(http.Header)}

	// Handle the request
	handler.ServeHTTP(w, req)

	fmt.Println()
	fmt.Printf("Response Status: %d\n", w.status)
}

type testResponseWriter struct {
	headers http.Header
	status  int
	body    []byte
}

func (w *testResponseWriter) Header() http.Header         { return w.headers }
func (w *testResponseWriter) Write(b []byte) (int, error) { w.body = append(w.body, b...); return len(b), nil }
func (w *testResponseWriter) WriteHeader(code int)        { w.status = code }

// UserHandler handles HTTP requests
type UserHandler struct {
	service *UserService
}

func NewUserHandler(service *UserService) *UserHandler {
	return &UserHandler{service: service}
}

func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
	// TODO: Get logger from context and add handler-specific fields
	logger := FromContext(r.Context()).With(
		KeyComponent, "user_handler",
		KeyOperation, "get_user",
	)

	// Extract user ID from path
	userID := r.URL.Path[len("/users/"):]

	logger.Debug("handling get user request", KeyUserID, userID)

	// Call service
	user, err := h.service.GetUser(r.Context(), userID)
	if err != nil {
		logger.Warn(MsgUserNotFound, KeyUserID, userID)
		http.Error(w, "User not found", http.StatusNotFound)
		return
	}

	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "User: %s - %s", user.ID, user.Name)
}

// UserService handles business logic
type UserService struct {
	repo   *UserRepository
	logger *slog.Logger
}

func NewUserService(repo *UserRepository, logger *slog.Logger) *UserService {
	return &UserService{repo: repo, logger: logger}
}

func (s *UserService) GetUser(ctx context.Context, userID string) (*User, error) {
	// TODO: Get logger from context and add service-specific fields
	logger := FromContext(ctx).With(
		KeyComponent, "user_service",
		KeyOperation, "get_user",
	)

	logger.Debug("fetching user", KeyUserID, userID)

	return s.repo.FindByID(ctx, userID)
}

// UserRepository handles data access
type UserRepository struct {
	logger *slog.Logger
}

func NewUserRepository(logger *slog.Logger) *UserRepository {
	return &UserRepository{logger: logger}
}

func (r *UserRepository) FindByID(ctx context.Context, userID string) (*User, error) {
	// TODO: Get logger from context and add repo-specific fields
	logger := FromContext(ctx).With(
		KeyComponent, "user_repo",
		KeyOperation, "find_by_id",
	)

	start := time.Now()

	// Simulate database query
	time.Sleep(10 * time.Millisecond)

	logger.Debug("database query completed",
		KeyUserID, userID,
		KeyDuration, time.Since(start).Milliseconds(),
	)

	return &User{ID: userID, Name: "John Doe"}, nil
}

// User represents a user entity
type User struct {
	ID   string
	Name string
}
