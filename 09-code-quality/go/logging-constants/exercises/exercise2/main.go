// Exercise 2: Refactor to Use Logging Constants
//
// This file contains magic strings in log calls.
// Your task is to refactor it to use constants.
package main

import (
	"context"
	"fmt"
	"log/slog"
	"os"
	"time"
)

// TODO: Define your constants here or in separate files

func main() {
	fmt.Println("Exercise 2: Refactor Magic Strings")
	fmt.Println("====================================")
	fmt.Println()

	logger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelDebug,
	}))

	ctx := context.Background()

	// Run the user service simulation
	svc := NewUserService(logger)
	svc.HandleUserRequest(ctx, "user-123", "req-abc")
}

// UserService handles user operations
type UserService struct {
	logger *slog.Logger
}

// NewUserService creates a new user service
func NewUserService(logger *slog.Logger) *UserService {
	return &UserService{
		// PROBLEM: Magic string "user_service"
		logger: logger.With("component", "user_service"),
	}
}

// HandleUserRequest processes a user request
func (s *UserService) HandleUserRequest(ctx context.Context, userID, requestID string) {
	start := time.Now()

	// PROBLEM: Inconsistent key names
	// PROBLEM: Magic strings for both keys and messages
	s.logger.Info("request started",
		"requestId", requestID,  // Should be request_id
		"userId", userID,        // Should be user_id
	)

	// Get user
	user, err := s.getUser(ctx, userID, requestID)
	if err != nil {
		// PROBLEM: More inconsistent naming
		s.logger.Error("failed to get user",
			"request_id", requestID,
			"UserID", userID,  // Different from above!
			"error", err.Error(),
		)
		return
	}

	// Update user
	if err := s.updateUser(ctx, user, requestID); err != nil {
		// PROBLEM: Yet another variation
		s.logger.Error("update failed",
			"reqID", requestID,  // Yet another variation!
			"user", userID,
			"err", err.Error(),  // Different from "error" above
		)
		return
	}

	// PROBLEM: Magic strings for duration
	s.logger.Info("request completed",
		"request_id", requestID,
		"user_id", userID,
		"duration_ms", time.Since(start).Milliseconds(),
		"status", "success",
	)
}

// User represents a user
type User struct {
	ID   string
	Name string
}

func (s *UserService) getUser(ctx context.Context, userID, requestID string) (*User, error) {
	// PROBLEM: Magic strings
	s.logger.Debug("fetching user from database",
		"request_id", requestID,
		"user_id", userID,
	)

	// Simulate DB lookup
	time.Sleep(10 * time.Millisecond)

	// PROBLEM: Magic message string
	s.logger.Info("user fetched",
		"request_id", requestID,
		"user_id", userID,
	)

	return &User{ID: userID, Name: "John Doe"}, nil
}

func (s *UserService) updateUser(ctx context.Context, user *User, requestID string) error {
	// PROBLEM: Magic strings
	s.logger.Debug("updating user",
		"request_id", requestID,
		"user_id", user.ID,
		"operation", "update",
	)

	// Simulate update
	time.Sleep(5 * time.Millisecond)

	// PROBLEM: Magic message string
	s.logger.Info("user updated",
		"request_id", requestID,
		"user_id", user.ID,
	)

	return nil
}

/*
EXERCISE TASKS:

1. Create constants for all log keys:
   - request_id
   - user_id
   - error
   - duration_ms
   - status
   - operation
   - component

2. Create constants for log messages:
   - "request started"
   - "request completed"
   - "user fetched"
   - "user updated"
   - etc.

3. Replace ALL magic strings with constants

4. Fix the inconsistent naming (requestId -> request_id, etc.)

5. Verify the output is the same after refactoring
*/
