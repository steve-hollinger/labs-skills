// Example 1: Basic Logging Constants
//
// This example demonstrates the fundamental usage of logging key constants
// and how they improve log consistency and maintainability.
package main

import (
	"fmt"
	"log/slog"
	"os"
	"time"
)

// Log key constants - defined once, used everywhere
const (
	KeyUserID    = "user_id"
	KeyRequestID = "request_id"
	KeyOperation = "operation"
	KeyDuration  = "duration_ms"
	KeyStatus    = "status"
	KeyError     = "error"
)

// Log message constants - for searchable, consistent messages
const (
	MsgUserCreated    = "user created"
	MsgUserUpdated    = "user updated"
	MsgOperationStart = "operation started"
	MsgOperationEnd   = "operation completed"
)

func main() {
	fmt.Println("Example 1: Basic Logging Constants")
	fmt.Println("========================================")
	fmt.Println()

	// Create a structured logger
	logger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelDebug,
	}))

	// Demonstrate the problem with magic strings
	demonstrateBadPractice(logger)

	fmt.Println()
	fmt.Println("--- Using Constants (Good Practice) ---")
	fmt.Println()

	// Demonstrate the solution with constants
	demonstrateGoodPractice(logger)

	fmt.Println()
	fmt.Println("=== Benefits Summary ===")
	printBenefits()

	fmt.Println("\nExample completed successfully!")
}

func demonstrateBadPractice(logger *slog.Logger) {
	fmt.Println("--- Without Constants (Bad Practice) ---")
	fmt.Println()
	fmt.Println("Problem: Inconsistent key names across the codebase")
	fmt.Println()

	// These look similar but are inconsistent - hard to search for!
	fmt.Println("Code example (don't do this):")
	fmt.Println(`  logger.Info("user created", "userId", "123")`)
	fmt.Println(`  logger.Info("user created", "user_id", "123")`)
	fmt.Println(`  logger.Info("user created", "UserID", "123")`)
	fmt.Println()
	fmt.Println("Issues:")
	fmt.Println("  - Can't search for all 'user_id' logs reliably")
	fmt.Println("  - Typos go unnoticed until production")
	fmt.Println("  - No IDE autocomplete support")
}

func demonstrateGoodPractice(logger *slog.Logger) {
	// Simulate a user creation operation
	userID := "user-123"
	requestID := "req-abc-456"

	// Log operation start with constants
	logger.Info(MsgOperationStart,
		KeyRequestID, requestID,
		KeyOperation, "create_user",
	)

	// Simulate some work
	start := time.Now()
	time.Sleep(50 * time.Millisecond)

	// Log the operation result
	logger.Info(MsgUserCreated,
		KeyRequestID, requestID,
		KeyUserID, userID,
		KeyDuration, time.Since(start).Milliseconds(),
		KeyStatus, "success",
	)

	// Demonstrate error logging with constants
	logger.Error("database connection failed",
		KeyRequestID, requestID,
		KeyOperation, "create_user",
		KeyError, "connection timeout",
	)

	fmt.Println()
	fmt.Println("Notice how the key names are consistent:")
	fmt.Println("  - Always 'user_id', never 'userId' or 'UserID'")
	fmt.Println("  - Always 'request_id', never 'requestId'")
	fmt.Println("  - Messages are searchable constants")
}

func printBenefits() {
	benefits := []struct {
		title       string
		description string
	}{
		{
			title:       "1. Consistency",
			description: "Same key names across all services and packages",
		},
		{
			title:       "2. Searchability",
			description: "Find all uses with IDE 'Find References' on constants",
		},
		{
			title:       "3. Refactoring",
			description: "Change a key name once, update everywhere automatically",
		},
		{
			title:       "4. IDE Support",
			description: "Autocomplete shows available log keys",
		},
		{
			title:       "5. Documentation",
			description: "Constants serve as documentation of available keys",
		},
		{
			title:       "6. Compile-Time Safety",
			description: "Typos caught at compile time, not in production",
		},
	}

	for _, b := range benefits {
		fmt.Printf("%s\n", b.title)
		fmt.Printf("   %s\n", b.description)
	}
}
