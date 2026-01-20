// Example 3: Mocking
//
// This file demonstrates testify mock package for mocking dependencies.
// See tests/example3_test.go for the actual mock tests.
//
// Run with: go test -v -run TestExample3 ./tests/...
package main

import "fmt"

// UserRepository defines the interface for user data access
type UserRepository interface {
	GetUser(id int64) (*User, error)
	SaveUser(user *User) error
	DeleteUser(id int64) error
	ListUsers() ([]*User, error)
}

// EmailService defines the interface for sending emails
type EmailService interface {
	SendWelcomeEmail(to, name string) error
	SendPasswordReset(to, token string) error
}

// User represents a user entity
type User struct {
	ID    int64
	Name  string
	Email string
}

// UserService is a service that depends on repository and email service
type UserService struct {
	repo  UserRepository
	email EmailService
}

func NewUserService(repo UserRepository, email EmailService) *UserService {
	return &UserService{repo: repo, email: email}
}

func (s *UserService) CreateUser(name, email string) (*User, error) {
	user := &User{Name: name, Email: email}
	if err := s.repo.SaveUser(user); err != nil {
		return nil, fmt.Errorf("failed to save user: %w", err)
	}

	if err := s.email.SendWelcomeEmail(email, name); err != nil {
		// Log but don't fail - email is not critical
		fmt.Printf("Warning: failed to send welcome email: %v\n", err)
	}

	return user, nil
}

func (s *UserService) GetUser(id int64) (*User, error) {
	user, err := s.repo.GetUser(id)
	if err != nil {
		return nil, fmt.Errorf("failed to get user: %w", err)
	}
	return user, nil
}

func (s *UserService) DeleteUser(id int64) error {
	// First get the user to verify it exists
	_, err := s.repo.GetUser(id)
	if err != nil {
		return fmt.Errorf("user not found: %w", err)
	}

	if err := s.repo.DeleteUser(id); err != nil {
		return fmt.Errorf("failed to delete user: %w", err)
	}

	return nil
}

func (s *UserService) ResetPassword(userID int64, token string) error {
	user, err := s.repo.GetUser(userID)
	if err != nil {
		return fmt.Errorf("user not found: %w", err)
	}

	if err := s.email.SendPasswordReset(user.Email, token); err != nil {
		return fmt.Errorf("failed to send password reset email: %w", err)
	}

	return nil
}

func main() {
	fmt.Println("Example 3: Mocking")
	fmt.Println("==================")
	fmt.Println()
	fmt.Println("This example demonstrates testify mock package.")
	fmt.Println("Run the tests to see mocking in action:")
	fmt.Println()
	fmt.Println("  go test -v -run TestExample3 ./tests/...")
	fmt.Println()
	fmt.Println("Key concepts demonstrated:")
	fmt.Println("  - Creating mock structs with mock.Mock")
	fmt.Println("  - Setting expectations with On() and Return()")
	fmt.Println("  - Using mock.Anything and mock.MatchedBy")
	fmt.Println("  - Verifying calls with AssertExpectations")
	fmt.Println("  - Verifying specific calls with AssertCalled")
	fmt.Println("  - Using Run() for callbacks")
}
