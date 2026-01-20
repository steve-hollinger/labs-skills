// Example 3: Context Propagation
//
// This example demonstrates how to propagate logging context through
// request chains, ensuring all related logs have consistent identifiers.
package main

import (
	"context"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"time"
)

// Log keys
const (
	KeyUserID      = "user_id"
	KeyRequestID   = "request_id"
	KeyTraceID     = "trace_id"
	KeyOperation   = "operation"
	KeyDuration    = "duration_ms"
	KeyError       = "error"
	KeyComponent   = "component"
	KeyLayer       = "layer"
	KeyHTTPMethod  = "http_method"
	KeyHTTPPath    = "http_path"
	KeyHTTPStatus  = "http_status"
)

// Log messages
const (
	MsgRequestStarted   = "request started"
	MsgRequestCompleted = "request completed"
	MsgUserFetched      = "user fetched"
	MsgDatabaseQuery    = "database query executed"
)

// Context keys
type contextKey string

const (
	loggerKey    contextKey = "logger"
	requestIDKey contextKey = "request_id"
)

func main() {
	fmt.Println("Example 3: Context Propagation")
	fmt.Println("========================================")
	fmt.Println()

	// Create base logger
	baseLogger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelDebug,
	}))

	// Demonstrate the pattern
	fmt.Println("=== Simulating HTTP Request Flow ===")
	fmt.Println()

	// Simulate an incoming request
	ctx := context.Background()
	simulateRequestFlow(ctx, baseLogger)

	fmt.Println()
	fmt.Println("=== Pattern Explanation ===")
	printPatternExplanation()

	fmt.Println("\nExample completed successfully!")
}

// WithLogger adds a logger to the context
func WithLogger(ctx context.Context, logger *slog.Logger) context.Context {
	return context.WithValue(ctx, loggerKey, logger)
}

// FromContext retrieves a logger from context, or returns default
func FromContext(ctx context.Context) *slog.Logger {
	if logger, ok := ctx.Value(loggerKey).(*slog.Logger); ok {
		return logger
	}
	return slog.Default()
}

// WithRequestID adds a request ID to the context
func WithRequestID(ctx context.Context, requestID string) context.Context {
	return context.WithValue(ctx, requestIDKey, requestID)
}

// GetRequestID retrieves request ID from context
func GetRequestID(ctx context.Context) string {
	if id, ok := ctx.Value(requestIDKey).(string); ok {
		return id
	}
	return ""
}

// simulateRequestFlow demonstrates the full flow of a request
func simulateRequestFlow(ctx context.Context, baseLogger *slog.Logger) {
	// Simulate incoming HTTP request
	requestID := fmt.Sprintf("req-%d", time.Now().UnixNano())
	traceID := fmt.Sprintf("trace-%d", time.Now().UnixNano())
	userID := "user-123"

	fmt.Printf("Incoming request: %s\n\n", requestID)

	// === HTTP Handler Layer ===
	fmt.Println("1. HTTP Handler Layer")

	// Create request-scoped logger with context
	requestLogger := baseLogger.With(
		KeyRequestID, requestID,
		KeyTraceID, traceID,
		KeyHTTPMethod, "GET",
		KeyHTTPPath, "/api/users/123",
		KeyLayer, "handler",
	)

	// Add logger and request ID to context
	ctx = WithLogger(ctx, requestLogger)
	ctx = WithRequestID(ctx, requestID)

	requestLogger.Info(MsgRequestStarted)

	start := time.Now()

	// Call service layer
	user, err := handleGetUser(ctx, userID)
	if err != nil {
		requestLogger.Error("request failed", KeyError, err.Error())
		return
	}

	// Log completion with duration
	requestLogger.Info(MsgRequestCompleted,
		KeyDuration, time.Since(start).Milliseconds(),
		KeyHTTPStatus, http.StatusOK,
	)

	fmt.Printf("\nResult: %+v\n", user)
}

// User represents a user entity
type User struct {
	ID    string
	Name  string
	Email string
}

// handleGetUser is the service layer
func handleGetUser(ctx context.Context, userID string) (*User, error) {
	// Get logger from context - it already has request_id and trace_id!
	logger := FromContext(ctx).With(
		KeyLayer, "service",
		KeyComponent, "user_service",
		KeyOperation, "get_user",
	)

	fmt.Println("\n2. Service Layer")

	logger.Debug("fetching user from database",
		KeyUserID, userID,
	)

	// Call repository layer
	user, err := fetchUserFromDB(ctx, userID)
	if err != nil {
		logger.Error("failed to fetch user",
			KeyUserID, userID,
			KeyError, err.Error(),
		)
		return nil, err
	}

	logger.Info(MsgUserFetched,
		KeyUserID, user.ID,
	)

	return user, nil
}

// fetchUserFromDB is the repository layer
func fetchUserFromDB(ctx context.Context, userID string) (*User, error) {
	// Get logger from context - it already has all parent context!
	logger := FromContext(ctx).With(
		KeyLayer, "repository",
		KeyComponent, "user_repo",
	)

	fmt.Println("\n3. Repository Layer")

	start := time.Now()

	// Simulate database query
	time.Sleep(10 * time.Millisecond)

	logger.Debug(MsgDatabaseQuery,
		"query", "SELECT * FROM users WHERE id = ?",
		KeyUserID, userID,
		KeyDuration, time.Since(start).Milliseconds(),
	)

	// Return mock user
	return &User{
		ID:    userID,
		Name:  "John Doe",
		Email: "john@example.com",
	}, nil
}

func printPatternExplanation() {
	fmt.Println(`
The context propagation pattern ensures:

1. CONSISTENT IDENTIFIERS
   All logs from the same request share request_id and trace_id
   regardless of which layer or function generates them.

2. AUTOMATIC ENRICHMENT
   Each layer can add its own context (layer, component, operation)
   without losing parent context.

3. CLEAN CODE
   No need to pass logger as a parameter to every function.
   Just use FromContext(ctx) to get a pre-configured logger.

Code Pattern:
`)

	fmt.Println(`
// In HTTP middleware or handler:
func Handler(w http.ResponseWriter, r *http.Request) {
    requestID := r.Header.Get("X-Request-ID")
    if requestID == "" {
        requestID = uuid.New().String()
    }

    logger := slog.Default().With(
        KeyRequestID, requestID,
        KeyHTTPMethod, r.Method,
        KeyHTTPPath, r.URL.Path,
    )

    ctx := WithLogger(r.Context(), logger)

    // Process request with context
    result, err := service.DoSomething(ctx, input)
}

// In service layer:
func (s *Service) DoSomething(ctx context.Context, input Input) error {
    // Logger automatically has request_id from handler
    logger := FromContext(ctx).With(
        KeyComponent, "my_service",
        KeyOperation, "do_something",
    )

    logger.Info("processing input")

    // Call another service - context carries through
    return s.anotherService.Process(ctx, input)
}
`)

	fmt.Println("Benefits:")
	fmt.Println("  - All logs from a request can be found with one request_id query")
	fmt.Println("  - Distributed tracing with trace_id across services")
	fmt.Println("  - Clear visibility into which layer/component generated logs")
	fmt.Println("  - No boilerplate passing logger through every function")
}
