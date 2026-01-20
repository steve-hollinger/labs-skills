// Package logger provides logging utilities with context support.
package logger

import (
	"context"
	"log/slog"
	"os"
)

// ContextKey is the type for context keys
type ContextKey string

// LoggerKey is the context key for storing the logger
const LoggerKey ContextKey = "logger"

// Config holds logger configuration
type Config struct {
	Level       slog.Level
	Format      string // "text" or "json"
	ServiceName string
}

// DefaultConfig returns a default configuration
func DefaultConfig() Config {
	return Config{
		Level:       slog.LevelInfo,
		Format:      "text",
		ServiceName: "unknown",
	}
}

// New creates a new configured logger
func New(cfg Config) *slog.Logger {
	var handler slog.Handler

	opts := &slog.HandlerOptions{
		Level: cfg.Level,
	}

	switch cfg.Format {
	case "json":
		handler = slog.NewJSONHandler(os.Stdout, opts)
	default:
		handler = slog.NewTextHandler(os.Stdout, opts)
	}

	logger := slog.New(handler)

	if cfg.ServiceName != "" {
		logger = logger.With("service", cfg.ServiceName)
	}

	return logger
}

// WithContext adds a logger to the context
func WithContext(ctx context.Context, logger *slog.Logger) context.Context {
	return context.WithValue(ctx, LoggerKey, logger)
}

// FromContext retrieves a logger from the context
// Returns slog.Default() if no logger is found
func FromContext(ctx context.Context) *slog.Logger {
	if logger, ok := ctx.Value(LoggerKey).(*slog.Logger); ok {
		return logger
	}
	return slog.Default()
}

// WithFields returns a new logger with additional fields
func WithFields(logger *slog.Logger, args ...any) *slog.Logger {
	return logger.With(args...)
}

// WithRequestID adds a request ID to the logger
func WithRequestID(logger *slog.Logger, requestID string) *slog.Logger {
	return logger.With("request_id", requestID)
}

// WithUserID adds a user ID to the logger
func WithUserID(logger *slog.Logger, userID string) *slog.Logger {
	return logger.With("user_id", userID)
}

// WithComponent adds a component name to the logger
func WithComponent(logger *slog.Logger, component string) *slog.Logger {
	return logger.With("component", component)
}

// WithOperation adds an operation name to the logger
func WithOperation(logger *slog.Logger, operation string) *slog.Logger {
	return logger.With("operation", operation)
}

// LevelFromString converts a string level to slog.Level
func LevelFromString(level string) slog.Level {
	switch level {
	case "debug", "DEBUG":
		return slog.LevelDebug
	case "info", "INFO":
		return slog.LevelInfo
	case "warn", "WARN", "warning", "WARNING":
		return slog.LevelWarn
	case "error", "ERROR":
		return slog.LevelError
	default:
		return slog.LevelInfo
	}
}
