package tests

import (
	"bytes"
	"context"
	"log/slog"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Context key type for testing
type ctxKey string

const testLoggerKey ctxKey = "logger"

// WithLogger adds a logger to context
func WithLogger(ctx context.Context, logger *slog.Logger) context.Context {
	return context.WithValue(ctx, testLoggerKey, logger)
}

// FromContext retrieves logger from context
func FromContext(ctx context.Context) *slog.Logger {
	if logger, ok := ctx.Value(testLoggerKey).(*slog.Logger); ok {
		return logger
	}
	return slog.Default()
}

// TestWithLogger verifies logger is stored in context
func TestWithLogger(t *testing.T) {
	var buf bytes.Buffer
	logger := slog.New(slog.NewTextHandler(&buf, nil))

	ctx := context.Background()
	ctx = WithLogger(ctx, logger)

	// Verify logger is in context
	retrieved := ctx.Value(testLoggerKey)
	require.NotNil(t, retrieved, "Logger should be in context")

	retrievedLogger, ok := retrieved.(*slog.Logger)
	require.True(t, ok, "Value should be a *slog.Logger")
	assert.Equal(t, logger, retrievedLogger)
}

// TestFromContext verifies logger retrieval
func TestFromContext(t *testing.T) {
	var buf bytes.Buffer
	logger := slog.New(slog.NewTextHandler(&buf, nil))

	ctx := context.Background()
	ctx = WithLogger(ctx, logger)

	retrieved := FromContext(ctx)
	assert.Equal(t, logger, retrieved)
}

// TestFromContextDefault verifies default logger when none in context
func TestFromContextDefault(t *testing.T) {
	ctx := context.Background()

	retrieved := FromContext(ctx)
	assert.NotNil(t, retrieved, "Should return default logger")
}

// TestLoggerPropagation verifies context propagation pattern
func TestLoggerPropagation(t *testing.T) {
	var buf bytes.Buffer
	baseLogger := slog.New(slog.NewTextHandler(&buf, &slog.HandlerOptions{
		Level: slog.LevelDebug,
	}))

	// Simulate middleware adding request context
	requestID := "req-123"
	requestLogger := baseLogger.With("request_id", requestID)
	ctx := WithLogger(context.Background(), requestLogger)

	// Simulate handler adding handler context
	handlerLogger := FromContext(ctx).With("component", "handler")
	ctx = WithLogger(ctx, handlerLogger)

	// Simulate service adding service context
	serviceLogger := FromContext(ctx).With("component", "service")

	// Log from service
	serviceLogger.Info("processing", "user_id", "user-456")

	// Verify log contains all context
	output := buf.String()
	assert.Contains(t, output, "request_id=req-123")
	assert.Contains(t, output, "user_id=user-456")
	assert.Contains(t, output, "processing")
}

// TestLoggerWithFields verifies adding fields to existing logger
func TestLoggerWithFields(t *testing.T) {
	var buf bytes.Buffer
	logger := slog.New(slog.NewTextHandler(&buf, nil))

	// Add base field
	logger = logger.With("service", "test-service")

	// Add more fields
	logger = logger.With("version", "1.0.0")

	// Log a message
	logger.Info("started")

	output := buf.String()
	assert.Contains(t, output, "service=test-service")
	assert.Contains(t, output, "version=1.0.0")
	assert.Contains(t, output, "started")
}

// TestLogLevels verifies log level behavior
func TestLogLevels(t *testing.T) {
	tests := []struct {
		name          string
		level         slog.Level
		shouldLog     []slog.Level
		shouldNotLog  []slog.Level
	}{
		{
			name:          "debug level logs all",
			level:         slog.LevelDebug,
			shouldLog:     []slog.Level{slog.LevelDebug, slog.LevelInfo, slog.LevelWarn, slog.LevelError},
			shouldNotLog:  []slog.Level{},
		},
		{
			name:          "info level skips debug",
			level:         slog.LevelInfo,
			shouldLog:     []slog.Level{slog.LevelInfo, slog.LevelWarn, slog.LevelError},
			shouldNotLog:  []slog.Level{slog.LevelDebug},
		},
		{
			name:          "warn level skips debug and info",
			level:         slog.LevelWarn,
			shouldLog:     []slog.Level{slog.LevelWarn, slog.LevelError},
			shouldNotLog:  []slog.Level{slog.LevelDebug, slog.LevelInfo},
		},
		{
			name:          "error level only logs errors",
			level:         slog.LevelError,
			shouldLog:     []slog.Level{slog.LevelError},
			shouldNotLog:  []slog.Level{slog.LevelDebug, slog.LevelInfo, slog.LevelWarn},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var buf bytes.Buffer
			logger := slog.New(slog.NewTextHandler(&buf, &slog.HandlerOptions{
				Level: tt.level,
			}))

			// Test levels that should log
			for _, level := range tt.shouldLog {
				buf.Reset()
				logger.Log(context.Background(), level, "test message")
				assert.NotEmpty(t, buf.String(), "Level %v should be logged when configured level is %v", level, tt.level)
			}

			// Test levels that should not log
			for _, level := range tt.shouldNotLog {
				buf.Reset()
				logger.Log(context.Background(), level, "test message")
				assert.Empty(t, buf.String(), "Level %v should NOT be logged when configured level is %v", level, tt.level)
			}
		})
	}
}

// TestStructuredLogOutput verifies structured output format
func TestStructuredLogOutput(t *testing.T) {
	var buf bytes.Buffer
	logger := slog.New(slog.NewTextHandler(&buf, nil))

	logger.Info("user action",
		"user_id", "user-123",
		"action", "login",
		"ip_address", "192.168.1.1",
	)

	output := buf.String()

	// Verify all fields are present
	assert.Contains(t, output, "user_id=user-123")
	assert.Contains(t, output, "action=login")
	assert.Contains(t, output, "ip_address=192.168.1.1")
	assert.Contains(t, output, "user action")
}
