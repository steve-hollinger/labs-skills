// Solution 3: Context-Aware Logging Middleware
//
// This solution demonstrates full context propagation through layers.
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
	MsgDatabaseQuery    = "database query executed"
)

// Context key type - use a custom type to avoid collisions
type ctxKey string

const loggerCtxKey ctxKey = "logger"

// WithLogger adds a logger to the context
func WithLogger(ctx context.Context, logger *slog.Logger) context.Context {
	return context.WithValue(ctx, loggerCtxKey, logger)
}

// FromContext retrieves the logger from context, returns default if not found
func FromContext(ctx context.Context) *slog.Logger {
	if logger, ok := ctx.Value(loggerCtxKey).(*slog.Logger); ok {
		return logger
	}
	return slog.Default()
}

// LoggingMiddleware adds request context to all logs
func LoggingMiddleware(baseLogger *slog.Logger) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()

			// Get or generate request ID
			requestID := r.Header.Get("X-Request-ID")
			if requestID == "" {
				requestID = fmt.Sprintf("req-%d", time.Now().UnixNano())
			}

			// Create request-scoped logger with context
			requestLogger := baseLogger.With(
				KeyRequestID, requestID,
				KeyHTTPMethod, r.Method,
				KeyHTTPPath, r.URL.Path,
			)

			// Log request start
			requestLogger.Info(MsgRequestStarted)

			// Add logger to context
			ctx := WithLogger(r.Context(), requestLogger)

			// Wrap response writer to capture status code
			wrapped := &responseWriter{
				ResponseWriter: w,
				status:         http.StatusOK,
			}

			// Call next handler with enriched context
			next.ServeHTTP(wrapped, r.WithContext(ctx))

			// Log request completion
			requestLogger.Info(MsgRequestCompleted,
				KeyHTTPStatus, wrapped.status,
				KeyDuration, time.Since(start).Milliseconds(),
			)
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
	fmt.Println("Solution 3: Context-Aware Logging")
	fmt.Println("===================================")
	fmt.Println()

	logger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelDebug,
	}))

	// Create services
	repo := NewUserRepository()
	svc := NewUserService(repo)
	handler := NewUserHandler(svc)

	// Setup routes with middleware
	mux := http.NewServeMux()
	mux.HandleFunc("/users/", handler.GetUser)

	// Apply middleware
	wrappedMux := LoggingMiddleware(logger)(mux)

	fmt.Println("=== Simulating Request Flow ===")
	fmt.Println()

	// Simulate requests
	simulateRequest(wrappedMux, "GET", "/users/123", "custom-req-001")

	fmt.Println()
	fmt.Println("=== Pattern Summary ===")
	printPatternSummary()
}

func simulateRequest(handler http.Handler, method, path, requestID string) {
	req, _ := http.NewRequest(method, path, nil)
	if requestID != "" {
		req.Header.Set("X-Request-ID", requestID)
	}

	w := &testResponseWriter{headers: make(http.Header)}
	handler.ServeHTTP(w, req)

	fmt.Printf("\nResponse Status: %d\n", w.status)
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
	// Get logger from context - it already has request_id, method, path
	// Add handler-specific fields
	logger := FromContext(r.Context()).With(
		KeyComponent, "user_handler",
		KeyOperation, "get_user",
	)

	// Extract user ID from path
	userID := r.URL.Path[len("/users/"):]

	logger.Debug("handling get user request", KeyUserID, userID)

	// Call service with context (logger travels along)
	user, err := h.service.GetUser(r.Context(), userID)
	if err != nil {
		logger.Warn(MsgUserNotFound, KeyUserID, userID)
		http.Error(w, "User not found", http.StatusNotFound)
		return
	}

	logger.Info(MsgUserFetched, KeyUserID, user.ID)

	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "User: %s - %s", user.ID, user.Name)
}

// UserService handles business logic
type UserService struct {
	repo *UserRepository
}

func NewUserService(repo *UserRepository) *UserService {
	return &UserService{repo: repo}
}

func (s *UserService) GetUser(ctx context.Context, userID string) (*User, error) {
	// Get logger from context - already has request_id from middleware!
	// Add service-specific fields
	logger := FromContext(ctx).With(
		KeyComponent, "user_service",
		KeyOperation, "get_user",
	)

	logger.Debug("fetching user from service layer", KeyUserID, userID)

	// Call repository with context
	return s.repo.FindByID(ctx, userID)
}

// UserRepository handles data access
type UserRepository struct{}

func NewUserRepository() *UserRepository {
	return &UserRepository{}
}

func (r *UserRepository) FindByID(ctx context.Context, userID string) (*User, error) {
	// Get logger from context - has request_id from middleware!
	// Add repository-specific fields
	logger := FromContext(ctx).With(
		KeyComponent, "user_repo",
		KeyOperation, "find_by_id",
	)

	start := time.Now()

	// Simulate database query
	time.Sleep(10 * time.Millisecond)

	logger.Debug(MsgDatabaseQuery,
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

func printPatternSummary() {
	fmt.Println(`
Key Implementation Details:

1. CONTEXT KEY TYPE
   Use a custom type to avoid key collisions:
   type ctxKey string
   const loggerCtxKey ctxKey = "logger"

2. MIDDLEWARE ENRICHMENT
   Middleware adds base context (request_id, method, path)
   that automatically flows to all downstream logs.

3. LAYER-SPECIFIC FIELDS
   Each layer adds its own fields (component, operation)
   using logger.With() without losing parent context.

4. FROM CONTEXT PATTERN
   FromContext(ctx) returns the logger with all accumulated
   context, or a default logger if none exists.

5. CONSISTENT REQUEST TRACKING
   All logs from a single request share the same request_id,
   making it easy to trace the entire request flow.

Benefits:
  - No need to pass logger as a parameter
  - Clean separation of concerns
  - Easy to add new context at any layer
  - All related logs can be queried by request_id
  - Works with distributed tracing (add trace_id in middleware)
`)
}
