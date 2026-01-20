// Example 2: Log Level Management
//
// This example demonstrates proper log level selection and configuration
// for different environments and scenarios.
package main

import (
	"fmt"
	"log/slog"
	"os"
	"time"
)

// Log keys
const (
	KeyUserID      = "user_id"
	KeyRequestID   = "request_id"
	KeyOperation   = "operation"
	KeyDuration    = "duration_ms"
	KeyError       = "error"
	KeyErrorCode   = "error_code"
	KeyRetryCount  = "retry_count"
	KeyMaxRetries  = "max_retries"
	KeyComponent   = "component"
	KeyCacheHit    = "cache_hit"
	KeyQueryTime   = "query_time_ms"
)

// Log messages
const (
	MsgRequestStarted   = "request started"
	MsgRequestCompleted = "request completed"
	MsgCacheHit         = "cache hit"
	MsgCacheMiss        = "cache miss"
	MsgRetrying         = "retrying operation"
	MsgUserNotFound     = "user not found"
	MsgDatabaseError    = "database error"
)

// LogLevel represents configurable log levels
type LogLevel string

const (
	LevelDebug LogLevel = "debug"
	LevelInfo  LogLevel = "info"
	LevelWarn  LogLevel = "warn"
	LevelError LogLevel = "error"
)

func main() {
	fmt.Println("Example 2: Log Level Management")
	fmt.Println("========================================")
	fmt.Println()

	// Demonstrate different log levels
	demonstrateLogLevels()

	// Show environment-based configuration
	fmt.Println("\n=== Environment-Based Configuration ===")
	demonstrateEnvironmentConfig()

	// Show level selection guidelines
	fmt.Println("\n=== Log Level Selection Guidelines ===")
	printLevelGuidelines()

	fmt.Println("\nExample completed successfully!")
}

func demonstrateLogLevels() {
	fmt.Println("=== Log Level Demonstrations ===")
	fmt.Println()

	// Create logger at DEBUG level to show all
	logger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelDebug,
	}))

	requestID := "req-123"
	userID := "user-456"

	fmt.Println("--- DEBUG Level ---")
	fmt.Println("Use for: Development details, variable values, flow tracing")
	logger.Debug("checking cache for user",
		KeyRequestID, requestID,
		KeyUserID, userID,
		KeyComponent, "user_cache",
	)
	fmt.Println()

	fmt.Println("--- INFO Level ---")
	fmt.Println("Use for: Normal operations, business events, request lifecycle")
	logger.Info(MsgRequestStarted,
		KeyRequestID, requestID,
		KeyOperation, "get_user",
	)
	logger.Info(MsgCacheHit,
		KeyRequestID, requestID,
		KeyCacheHit, true,
	)
	fmt.Println()

	fmt.Println("--- WARN Level ---")
	fmt.Println("Use for: Concerning situations that are handled, retries, deprecation")
	logger.Warn(MsgRetrying,
		KeyRequestID, requestID,
		KeyOperation, "external_api_call",
		KeyRetryCount, 2,
		KeyMaxRetries, 3,
		KeyError, "timeout",
	)
	fmt.Println()

	fmt.Println("--- ERROR Level ---")
	fmt.Println("Use for: Failures that need attention, unrecoverable errors")
	logger.Error(MsgDatabaseError,
		KeyRequestID, requestID,
		KeyOperation, "save_user",
		KeyError, "connection refused",
		KeyErrorCode, "DB_CONN_REFUSED",
	)
}

func demonstrateEnvironmentConfig() {
	environments := []struct {
		name          string
		level         slog.Level
		description   string
	}{
		{
			name:          "Development",
			level:         slog.LevelDebug,
			description:   "All logs visible for debugging",
		},
		{
			name:          "Staging",
			level:         slog.LevelInfo,
			description:   "INFO and above, no DEBUG noise",
		},
		{
			name:          "Production",
			level:         slog.LevelInfo,
			description:   "INFO and above, focused on operations",
		},
		{
			name:          "Production (Reduced)",
			level:         slog.LevelWarn,
			description:   "Only warnings and errors (cost savings)",
		},
	}

	for _, env := range environments {
		fmt.Printf("\n%s Environment:\n", env.name)
		fmt.Printf("  Level: %s\n", env.level)
		fmt.Printf("  Purpose: %s\n", env.description)

		// Show what would be logged
		logger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
			Level: env.level,
		}))

		// These may or may not show depending on level
		logger.Debug("debug message", KeyComponent, "demo")
		logger.Info("info message", KeyComponent, "demo")
		logger.Warn("warn message", KeyComponent, "demo")
	}

	fmt.Println("\n\nConfiguration example:")
	fmt.Println(`
func NewLogger(env string) *slog.Logger {
    var level slog.Level
    switch env {
    case "development":
        level = slog.LevelDebug
    case "staging", "production":
        level = slog.LevelInfo
    default:
        level = slog.LevelInfo
    }

    return slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
        Level: level,
    }))
}`)
}

func printLevelGuidelines() {
	guidelines := []struct {
		level    string
		useFor   []string
		examples []string
	}{
		{
			level: "DEBUG",
			useFor: []string{
				"Variable values during debugging",
				"Detailed flow tracing",
				"Cache key lookups",
				"Loop iterations",
			},
			examples: []string{
				`logger.Debug("processing item", "index", i, "value", v)`,
				`logger.Debug("cache lookup", KeyCacheKey, key)`,
			},
		},
		{
			level: "INFO",
			useFor: []string{
				"Request start/completion",
				"Business events (user created, order placed)",
				"Service lifecycle (started, stopped)",
				"Configuration loaded",
			},
			examples: []string{
				`logger.Info(MsgRequestCompleted, KeyDuration, elapsed)`,
				`logger.Info(MsgUserCreated, KeyUserID, id)`,
			},
		},
		{
			level: "WARN",
			useFor: []string{
				"Retry attempts",
				"Fallback to default behavior",
				"Deprecated feature usage",
				"Resource usage approaching limits",
			},
			examples: []string{
				`logger.Warn(MsgRetrying, KeyAttempt, 2)`,
				`logger.Warn("using deprecated endpoint", "endpoint", path)`,
			},
		},
		{
			level: "ERROR",
			useFor: []string{
				"Database failures",
				"External service failures",
				"Unhandled errors",
				"Security violations",
			},
			examples: []string{
				`logger.Error(MsgDatabaseError, KeyError, err)`,
				`logger.Error("authentication failed", KeyUserID, id)`,
			},
		},
	}

	for _, g := range guidelines {
		fmt.Printf("\n%s Level:\n", g.level)
		fmt.Println("  Use for:")
		for _, use := range g.useFor {
			fmt.Printf("    - %s\n", use)
		}
		fmt.Println("  Examples:")
		for _, ex := range g.examples {
			fmt.Printf("    %s\n", ex)
		}
	}

	fmt.Println("\n=== Common Mistakes ===")
	mistakes := []struct {
		bad  string
		good string
		why  string
	}{
		{
			bad:  `logger.Error("user not found")  // for expected case`,
			good: `logger.Info("user not found")   // expected, not an error`,
			why:  "User not found is often expected behavior",
		},
		{
			bad:  `logger.Debug("processing payment") // won't see in prod`,
			good: `logger.Info("processing payment")  // visible in prod`,
			why:  "Important operations should be visible in production",
		},
		{
			bad:  `logger.Info("retry failed")       // sounds alarming`,
			good: `logger.Warn("retry failed")       // appropriate level`,
			why:  "Failures warrant WARN level for visibility",
		},
	}

	for _, m := range mistakes {
		fmt.Printf("\nBad:  %s\n", m.bad)
		fmt.Printf("Good: %s\n", m.good)
		fmt.Printf("Why:  %s\n", m.why)
	}
}

// simulateOperation simulates an operation with timing
func simulateOperation(name string, duration time.Duration) {
	time.Sleep(duration)
}
