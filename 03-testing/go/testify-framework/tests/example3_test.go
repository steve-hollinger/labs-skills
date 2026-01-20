package tests

import (
	"errors"
	"fmt"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

// ============================================================================
// Example 3: Mocking with testify/mock
// ============================================================================

// Interfaces to mock
type UserRepository interface {
	GetUser(id int64) (*MockUser, error)
	SaveUser(user *MockUser) error
	DeleteUser(id int64) error
	ListUsers() ([]*MockUser, error)
}

type EmailService interface {
	SendWelcomeEmail(to, name string) error
	SendPasswordReset(to, token string) error
}

// Domain types
type MockUser struct {
	ID    int64
	Name  string
	Email string
}

// Service that uses the interfaces
type MockUserService struct {
	repo  UserRepository
	email EmailService
}

func NewMockUserService(repo UserRepository, email EmailService) *MockUserService {
	return &MockUserService{repo: repo, email: email}
}

func (s *MockUserService) CreateUser(name, email string) (*MockUser, error) {
	user := &MockUser{Name: name, Email: email}
	if err := s.repo.SaveUser(user); err != nil {
		return nil, fmt.Errorf("failed to save user: %w", err)
	}
	// Send welcome email (don't fail if email fails)
	s.email.SendWelcomeEmail(email, name)
	return user, nil
}

func (s *MockUserService) GetUser(id int64) (*MockUser, error) {
	return s.repo.GetUser(id)
}

func (s *MockUserService) DeleteUser(id int64) error {
	// Verify user exists
	_, err := s.repo.GetUser(id)
	if err != nil {
		return fmt.Errorf("user not found: %w", err)
	}
	return s.repo.DeleteUser(id)
}

func (s *MockUserService) ResetPassword(userID int64, token string) error {
	user, err := s.repo.GetUser(userID)
	if err != nil {
		return fmt.Errorf("user not found: %w", err)
	}
	return s.email.SendPasswordReset(user.Email, token)
}

// ============================================================================
// Mock Implementations
// ============================================================================

// MockUserRepository implements UserRepository
type MockUserRepository struct {
	mock.Mock
}

func (m *MockUserRepository) GetUser(id int64) (*MockUser, error) {
	args := m.Called(id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*MockUser), args.Error(1)
}

func (m *MockUserRepository) SaveUser(user *MockUser) error {
	args := m.Called(user)
	return args.Error(0)
}

func (m *MockUserRepository) DeleteUser(id int64) error {
	args := m.Called(id)
	return args.Error(0)
}

func (m *MockUserRepository) ListUsers() ([]*MockUser, error) {
	args := m.Called()
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]*MockUser), args.Error(1)
}

// MockEmailService implements EmailService
type MockEmailService struct {
	mock.Mock
}

func (m *MockEmailService) SendWelcomeEmail(to, name string) error {
	args := m.Called(to, name)
	return args.Error(0)
}

func (m *MockEmailService) SendPasswordReset(to, token string) error {
	args := m.Called(to, token)
	return args.Error(0)
}

// ============================================================================
// Tests
// ============================================================================

// TestExample3_BasicMocking demonstrates basic mock setup and verification
func TestExample3_BasicMocking(t *testing.T) {
	// Create mocks
	mockRepo := new(MockUserRepository)
	mockEmail := new(MockEmailService)

	// Set up expectations
	mockRepo.On("SaveUser", mock.Anything).Return(nil)
	mockEmail.On("SendWelcomeEmail", "alice@example.com", "Alice").Return(nil)

	// Create service with mocks
	service := NewMockUserService(mockRepo, mockEmail)

	// Call the method under test
	user, err := service.CreateUser("Alice", "alice@example.com")

	// Assertions
	require.NoError(t, err)
	assert.Equal(t, "Alice", user.Name)
	assert.Equal(t, "alice@example.com", user.Email)

	// Verify all expectations were met
	mockRepo.AssertExpectations(t)
	mockEmail.AssertExpectations(t)
}

// TestExample3_MockReturningError demonstrates mocking error scenarios
func TestExample3_MockReturningError(t *testing.T) {
	mockRepo := new(MockUserRepository)
	mockEmail := new(MockEmailService)

	// Set up mock to return an error
	mockRepo.On("SaveUser", mock.Anything).Return(errors.New("database error"))

	service := NewMockUserService(mockRepo, mockEmail)

	// Call should fail
	user, err := service.CreateUser("Alice", "alice@example.com")

	assert.Error(t, err)
	assert.Nil(t, user)
	assert.Contains(t, err.Error(), "failed to save user")

	mockRepo.AssertExpectations(t)
	// Email should NOT have been called
	mockEmail.AssertNotCalled(t, "SendWelcomeEmail", mock.Anything, mock.Anything)
}

// TestExample3_MockAnything demonstrates mock.Anything matcher
func TestExample3_MockAnything(t *testing.T) {
	mockRepo := new(MockUserRepository)
	mockEmail := new(MockEmailService)

	// mock.Anything matches any value
	mockRepo.On("SaveUser", mock.Anything).Return(nil)
	mockEmail.On("SendWelcomeEmail", mock.Anything, mock.Anything).Return(nil)

	service := NewMockUserService(mockRepo, mockEmail)

	// Any user creation should work
	_, err := service.CreateUser("Bob", "bob@example.com")
	assert.NoError(t, err)

	_, err = service.CreateUser("Charlie", "charlie@example.com")
	assert.NoError(t, err)

	mockRepo.AssertExpectations(t)
}

// TestExample3_MockMatchedBy demonstrates custom argument matchers
func TestExample3_MockMatchedBy(t *testing.T) {
	mockRepo := new(MockUserRepository)
	mockEmail := new(MockEmailService)

	// Custom matcher - only accept users with valid email
	mockRepo.On("SaveUser", mock.MatchedBy(func(u *MockUser) bool {
		return strings.Contains(u.Email, "@") && u.Name != ""
	})).Return(nil)

	mockEmail.On("SendWelcomeEmail", mock.Anything, mock.Anything).Return(nil)

	service := NewMockUserService(mockRepo, mockEmail)

	// Valid user
	user, err := service.CreateUser("Alice", "alice@example.com")
	assert.NoError(t, err)
	assert.NotNil(t, user)

	mockRepo.AssertExpectations(t)
}

// TestExample3_MockWithCallback demonstrates using Run() for callbacks
func TestExample3_MockWithCallback(t *testing.T) {
	mockRepo := new(MockUserRepository)
	mockEmail := new(MockEmailService)

	// Use Run() to modify arguments or perform side effects
	var savedUser *MockUser
	mockRepo.On("SaveUser", mock.Anything).
		Run(func(args mock.Arguments) {
			// Capture the saved user
			savedUser = args.Get(0).(*MockUser)
			// Simulate ID assignment by database
			savedUser.ID = 42
		}).
		Return(nil)

	mockEmail.On("SendWelcomeEmail", mock.Anything, mock.Anything).Return(nil)

	service := NewMockUserService(mockRepo, mockEmail)

	user, err := service.CreateUser("Alice", "alice@example.com")

	require.NoError(t, err)
	assert.Equal(t, int64(42), user.ID) // ID was set by callback
	assert.NotNil(t, savedUser)
	assert.Equal(t, "Alice", savedUser.Name)
}

// TestExample3_MockSpecificCalls demonstrates different returns for different arguments
func TestExample3_MockSpecificCalls(t *testing.T) {
	mockRepo := new(MockUserRepository)

	// Different returns for different IDs
	mockRepo.On("GetUser", int64(1)).Return(&MockUser{ID: 1, Name: "Alice"}, nil)
	mockRepo.On("GetUser", int64(2)).Return(&MockUser{ID: 2, Name: "Bob"}, nil)
	mockRepo.On("GetUser", int64(999)).Return(nil, errors.New("not found"))

	// Test each case
	user1, err := mockRepo.GetUser(1)
	require.NoError(t, err)
	assert.Equal(t, "Alice", user1.Name)

	user2, err := mockRepo.GetUser(2)
	require.NoError(t, err)
	assert.Equal(t, "Bob", user2.Name)

	_, err = mockRepo.GetUser(999)
	assert.Error(t, err)

	mockRepo.AssertExpectations(t)
}

// TestExample3_MockAssertCalled demonstrates verifying specific calls
func TestExample3_MockAssertCalled(t *testing.T) {
	mockRepo := new(MockUserRepository)
	mockEmail := new(MockEmailService)

	mockRepo.On("GetUser", mock.Anything).Return(&MockUser{ID: 1, Name: "Alice", Email: "alice@example.com"}, nil)
	mockRepo.On("DeleteUser", mock.Anything).Return(nil)

	service := NewMockUserService(mockRepo, mockEmail)

	err := service.DeleteUser(1)
	require.NoError(t, err)

	// Verify specific calls were made
	mockRepo.AssertCalled(t, "GetUser", int64(1))
	mockRepo.AssertCalled(t, "DeleteUser", int64(1))

	// Verify number of calls
	mockRepo.AssertNumberOfCalls(t, "GetUser", 1)
	mockRepo.AssertNumberOfCalls(t, "DeleteUser", 1)

	// Verify call was NOT made
	mockEmail.AssertNotCalled(t, "SendWelcomeEmail", mock.Anything, mock.Anything)
}

// TestExample3_MockTimes demonstrates limiting call counts
func TestExample3_MockTimes(t *testing.T) {
	mockRepo := new(MockUserRepository)

	// Allow exactly 2 calls
	mockRepo.On("GetUser", mock.Anything).Return(&MockUser{ID: 1, Name: "Alice"}, nil).Times(2)

	// First two calls work
	_, err := mockRepo.GetUser(1)
	assert.NoError(t, err)

	_, err = mockRepo.GetUser(1)
	assert.NoError(t, err)

	mockRepo.AssertExpectations(t)
}

// TestExample3_MockOnce demonstrates single-use expectations
func TestExample3_MockOnce(t *testing.T) {
	mockRepo := new(MockUserRepository)

	// Once() is shorthand for Times(1)
	mockRepo.On("GetUser", int64(1)).Return(&MockUser{ID: 1, Name: "Alice"}, nil).Once()
	mockRepo.On("GetUser", int64(2)).Return(&MockUser{ID: 2, Name: "Bob"}, nil).Once()

	_, _ = mockRepo.GetUser(1)
	_, _ = mockRepo.GetUser(2)

	mockRepo.AssertExpectations(t)
}

// TestExample3_TableDrivenWithMocks demonstrates table-driven tests with mocks
func TestExample3_TableDrivenWithMocks(t *testing.T) {
	tests := []struct {
		name        string
		userID      int64
		setupMock   func(*MockUserRepository, *MockEmailService)
		wantErr     bool
		errContains string
	}{
		{
			name:   "successful password reset",
			userID: 1,
			setupMock: func(repo *MockUserRepository, email *MockEmailService) {
				repo.On("GetUser", int64(1)).Return(&MockUser{ID: 1, Email: "alice@example.com"}, nil)
				email.On("SendPasswordReset", "alice@example.com", "token123").Return(nil)
			},
			wantErr: false,
		},
		{
			name:   "user not found",
			userID: 999,
			setupMock: func(repo *MockUserRepository, email *MockEmailService) {
				repo.On("GetUser", int64(999)).Return(nil, errors.New("not found"))
			},
			wantErr:     true,
			errContains: "user not found",
		},
		{
			name:   "email service error",
			userID: 1,
			setupMock: func(repo *MockUserRepository, email *MockEmailService) {
				repo.On("GetUser", int64(1)).Return(&MockUser{ID: 1, Email: "alice@example.com"}, nil)
				email.On("SendPasswordReset", mock.Anything, mock.Anything).Return(errors.New("smtp error"))
			},
			wantErr:     true,
			errContains: "smtp error",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mockRepo := new(MockUserRepository)
			mockEmail := new(MockEmailService)
			tt.setupMock(mockRepo, mockEmail)

			service := NewMockUserService(mockRepo, mockEmail)
			err := service.ResetPassword(tt.userID, "token123")

			if tt.wantErr {
				require.Error(t, err)
				assert.Contains(t, err.Error(), tt.errContains)
			} else {
				require.NoError(t, err)
			}

			mockRepo.AssertExpectations(t)
			mockEmail.AssertExpectations(t)
		})
	}
}
