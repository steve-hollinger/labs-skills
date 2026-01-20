// Solution 2: Refactored User Service with Logging Constants
//
// This solution shows the code after refactoring to use constants.
package main

import (
	"context"
	"fmt"
	"log/slog"
	"os"
	"time"
)

// Log key constants - all keys are now defined once
const (
	KeyRequestID  = "request_id"
	KeyUserID     = "user_id"
	KeyError      = "error"
	KeyDuration   = "duration_ms"
	KeyStatus     = "status"
	KeyOperation  = "operation"
	KeyComponent  = "component"
)

// Log message constants - common messages defined once
const (
	MsgRequestStarted   = "request started"
	MsgRequestCompleted = "request completed"
	MsgRequestFailed    = "request failed"
	MsgUserFetched      = "user fetched"
	MsgUserUpdated      = "user updated"
	MsgFetchingUser     = "fetching user from database"
	MsgUpdatingUser     = "updating user"
)

func main() {
	fmt.Println("Solution 2: Refactored User Service")
	fmt.Println("=====================================")
	fmt.Println()

	logger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelDebug,
	}))

	ctx := context.Background()

	// Run the user service simulation
	svc := NewUserService(logger)
	svc.HandleUserRequest(ctx, "user-123", "req-abc")

	fmt.Println()
	fmt.Println("=== Changes Made ===")
	printChanges()
}

// UserService handles user operations
type UserService struct {
	logger *slog.Logger
}

// NewUserService creates a new user service
func NewUserService(logger *slog.Logger) *UserService {
	return &UserService{
		// FIXED: Using constant for component
		logger: logger.With(KeyComponent, "user_service"),
	}
}

// HandleUserRequest processes a user request
func (s *UserService) HandleUserRequest(ctx context.Context, userID, requestID string) {
	start := time.Now()

	// FIXED: Consistent key names using constants
	s.logger.Info(MsgRequestStarted,
		KeyRequestID, requestID,
		KeyUserID, userID,
	)

	// Get user
	user, err := s.getUser(ctx, userID, requestID)
	if err != nil {
		// FIXED: Consistent naming throughout
		s.logger.Error(MsgRequestFailed,
			KeyRequestID, requestID,
			KeyUserID, userID,
			KeyError, err.Error(),
		)
		return
	}

	// Update user
	if err := s.updateUser(ctx, user, requestID); err != nil {
		// FIXED: Same key names everywhere
		s.logger.Error(MsgRequestFailed,
			KeyRequestID, requestID,
			KeyUserID, userID,
			KeyError, err.Error(),
			KeyOperation, "update",
		)
		return
	}

	// FIXED: Using constants for all keys and messages
	s.logger.Info(MsgRequestCompleted,
		KeyRequestID, requestID,
		KeyUserID, userID,
		KeyDuration, time.Since(start).Milliseconds(),
		KeyStatus, "success",
	)
}

// User represents a user
type User struct {
	ID   string
	Name string
}

func (s *UserService) getUser(ctx context.Context, userID, requestID string) (*User, error) {
	// FIXED: Using message constants
	s.logger.Debug(MsgFetchingUser,
		KeyRequestID, requestID,
		KeyUserID, userID,
	)

	// Simulate DB lookup
	time.Sleep(10 * time.Millisecond)

	// FIXED: Using message constant
	s.logger.Info(MsgUserFetched,
		KeyRequestID, requestID,
		KeyUserID, userID,
	)

	return &User{ID: userID, Name: "John Doe"}, nil
}

func (s *UserService) updateUser(ctx context.Context, user *User, requestID string) error {
	// FIXED: Using constants
	s.logger.Debug(MsgUpdatingUser,
		KeyRequestID, requestID,
		KeyUserID, user.ID,
		KeyOperation, "update",
	)

	// Simulate update
	time.Sleep(5 * time.Millisecond)

	// FIXED: Using message constant
	s.logger.Info(MsgUserUpdated,
		KeyRequestID, requestID,
		KeyUserID, user.ID,
	)

	return nil
}

func printChanges() {
	changes := []struct {
		before string
		after  string
		issue  string
	}{
		{
			before: `"requestId", requestID`,
			after:  `KeyRequestID, requestID`,
			issue:  "Inconsistent naming (requestId vs request_id)",
		},
		{
			before: `"userId", userID`,
			after:  `KeyUserID, userID`,
			issue:  "Inconsistent naming (userId vs user_id)",
		},
		{
			before: `"UserID", userID`,
			after:  `KeyUserID, userID`,
			issue:  "Inconsistent naming (UserID vs user_id)",
		},
		{
			before: `"reqID", requestID`,
			after:  `KeyRequestID, requestID`,
			issue:  "Inconsistent naming (reqID vs request_id)",
		},
		{
			before: `"err", err.Error()`,
			after:  `KeyError, err.Error()`,
			issue:  "Inconsistent naming (err vs error)",
		},
		{
			before: `"request started"`,
			after:  `MsgRequestStarted`,
			issue:  "Magic string for message",
		},
		{
			before: `"user fetched"`,
			after:  `MsgUserFetched`,
			issue:  "Magic string for message",
		},
	}

	for _, c := range changes {
		fmt.Printf("Issue: %s\n", c.issue)
		fmt.Printf("  Before: %s\n", c.before)
		fmt.Printf("  After:  %s\n", c.after)
		fmt.Println()
	}

	fmt.Println("Benefits of these changes:")
	fmt.Println("  1. IDE autocomplete works for all keys and messages")
	fmt.Println("  2. Typos are caught at compile time")
	fmt.Println("  3. 'Find References' shows all uses of a key")
	fmt.Println("  4. Renaming a key updates all occurrences")
	fmt.Println("  5. Log aggregation tools can rely on consistent key names")
}
