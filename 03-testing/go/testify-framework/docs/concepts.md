# Core Concepts - Testify Framework

## Overview

Testify is the most popular testing toolkit for Go, providing assertion functions, test suites, and mocking capabilities that make tests more expressive and maintainable.

## Concept 1: Assert Package

### What It Is

The `assert` package provides a collection of assertion functions that test conditions and report failures without stopping the test.

### Why It Matters

- More expressive than manual `if` checks
- Better error messages showing expected vs actual values
- Consistent assertion patterns across your codebase

### How It Works

```go
import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestAssertions(t *testing.T) {
    // Equality
    assert.Equal(t, 123, result, "optional message")
    assert.NotEqual(t, 0, result)

    // Nil checks
    assert.Nil(t, err)
    assert.NotNil(t, user)

    // Boolean
    assert.True(t, isValid)
    assert.False(t, hasError)

    // Collections
    assert.Contains(t, "hello world", "world")
    assert.Len(t, items, 3)
    assert.Empty(t, list)
    assert.ElementsMatch(t, []int{1, 2, 3}, []int{3, 2, 1})

    // Comparisons
    assert.Greater(t, 5, 3)
    assert.GreaterOrEqual(t, 5, 5)
    assert.Less(t, 3, 5)

    // Error handling
    assert.Error(t, err)
    assert.NoError(t, err)
    assert.ErrorIs(t, err, ErrNotFound)
    assert.ErrorContains(t, err, "not found")

    // Type assertions
    assert.IsType(t, &User{}, obj)
    assert.Implements(t, (*Repository)(nil), repo)

    // Panics
    assert.Panics(t, func() { panic("oh no") })
    assert.NotPanics(t, func() { /* safe code */ })
}
```

### Key Behaviors

- Returns `bool` indicating pass/fail (useful for conditional logic)
- Continues test execution on failure
- Prints helpful diff for complex objects

## Concept 2: Require Package

### What It Is

The `require` package has the same assertions as `assert`, but stops test execution immediately on failure.

### Why It Matters

- Prevents cascading failures when preconditions aren't met
- Avoids nil pointer panics in subsequent code
- Makes test intent clearer

### When to Use Require vs Assert

```go
func TestUserService(t *testing.T) {
    // REQUIRE for setup and preconditions
    user, err := service.CreateUser("Alice")
    require.NoError(t, err, "user creation must succeed")
    require.NotNil(t, user, "user must not be nil")

    // ASSERT for actual test validations
    assert.Equal(t, "Alice", user.Name)
    assert.NotZero(t, user.ID)
    assert.WithinDuration(t, time.Now(), user.CreatedAt, time.Second)
}
```

### Decision Guide

| Situation | Use |
|-----------|-----|
| Error from function call | require.NoError |
| Result must not be nil | require.NotNil |
| Setup/precondition | require |
| Actual test assertion | assert |
| Multiple independent checks | assert |

## Concept 3: Test Suites

### What It Is

The `suite` package provides struct-based test organization with lifecycle hooks.

### Why It Matters

- Centralize setup/teardown logic
- Share state between tests safely
- Group related tests logically

### Lifecycle Methods

```go
type MySuite struct {
    suite.Suite
    db     *sql.DB
    server *httptest.Server
}

// SetupSuite runs once before all tests
func (s *MySuite) SetupSuite() {
    s.db = connectDatabase()
}

// TearDownSuite runs once after all tests
func (s *MySuite) TearDownSuite() {
    s.db.Close()
}

// SetupTest runs before each test
func (s *MySuite) SetupTest() {
    s.db.Exec("DELETE FROM users")
}

// TearDownTest runs after each test
func (s *MySuite) TearDownTest() {
    // cleanup if needed
}

// BeforeTest runs before each test with suite/test names
func (s *MySuite) BeforeTest(suiteName, testName string) {
    log.Printf("Running %s.%s", suiteName, testName)
}

// AfterTest runs after each test with suite/test names
func (s *MySuite) AfterTest(suiteName, testName string) {
    log.Printf("Completed %s.%s", suiteName, testName)
}
```

### Using Suite Assertions

```go
func (s *MySuite) TestCreate() {
    // Suite provides assertion methods directly
    user, err := s.repo.Create(&User{Name: "Alice"})
    s.NoError(err)           // Same as assert.NoError(s.T(), err)
    s.NotNil(user)

    // For require behavior
    s.Require().NoError(err) // Same as require.NoError(s.T(), err)
}

// Entry point - required!
func TestMySuite(t *testing.T) {
    suite.Run(t, new(MySuite))
}
```

## Concept 4: Mock Package

### What It Is

The `mock` package provides a framework for creating mock objects that implement interfaces.

### Why It Matters

- Test components in isolation
- Control dependency behavior
- Verify interactions between components

### Creating Mocks

```go
// 1. Define the interface
type EmailSender interface {
    SendEmail(to, subject, body string) error
    SendBulk(emails []Email) (int, error)
}

// 2. Create mock struct
type MockEmailSender struct {
    mock.Mock
}

// 3. Implement interface methods
func (m *MockEmailSender) SendEmail(to, subject, body string) error {
    args := m.Called(to, subject, body)
    return args.Error(0)
}

func (m *MockEmailSender) SendBulk(emails []Email) (int, error) {
    args := m.Called(emails)
    return args.Int(0), args.Error(1)
}
```

### Setting Expectations

```go
func TestNotificationService(t *testing.T) {
    mockSender := new(MockEmailSender)

    // Basic expectation
    mockSender.On("SendEmail", "user@example.com", "Welcome", mock.Anything).
        Return(nil)

    // Expectation with specific call count
    mockSender.On("SendBulk", mock.Anything).
        Return(5, nil).
        Times(1)

    // Conditional return
    mockSender.On("SendEmail", mock.MatchedBy(func(to string) bool {
        return strings.HasSuffix(to, "@internal.com")
    }), mock.Anything, mock.Anything).
        Return(errors.New("internal only"))

    // Use the mock
    service := NewNotificationService(mockSender)
    err := service.NotifyUser("user@example.com")

    assert.NoError(t, err)
    mockSender.AssertExpectations(t)
}
```

### Mock Argument Matchers

```go
// Exact match
mockRepo.On("GetUser", 42).Return(&User{ID: 42}, nil)

// Any value
mockRepo.On("GetUser", mock.Anything).Return(nil, ErrNotFound)

// Custom matcher
mockRepo.On("SaveUser", mock.MatchedBy(func(u *User) bool {
    return u.Email != "" && u.Name != ""
})).Return(nil)

// Type matcher
mockRepo.On("Process", mock.AnythingOfType("*User")).Return(nil)
```

### Verifying Calls

```go
func TestVerification(t *testing.T) {
    mockRepo := new(MockUserRepository)
    mockRepo.On("GetUser", mock.Anything).Return(&User{}, nil)

    // ... use mock ...

    // Verify all expectations were met
    mockRepo.AssertExpectations(t)

    // Verify specific call was made
    mockRepo.AssertCalled(t, "GetUser", 1)

    // Verify call was NOT made
    mockRepo.AssertNotCalled(t, "DeleteUser", mock.Anything)

    // Verify number of calls
    mockRepo.AssertNumberOfCalls(t, "GetUser", 3)
}
```

## Concept 5: Table-Driven Tests

### What It Is

A testing pattern that combines test cases in a slice and runs them in a loop.

### Why It Matters

- Reduces code duplication
- Makes it easy to add new test cases
- Clearly shows all test scenarios

### Implementation with Testify

```go
func TestCalculator(t *testing.T) {
    tests := []struct {
        name      string
        operation string
        a, b      float64
        expected  float64
        wantErr   bool
        errMsg    string
    }{
        {
            name:      "addition",
            operation: "+",
            a:         5,
            b:         3,
            expected:  8,
        },
        {
            name:      "division",
            operation: "/",
            a:         10,
            b:         2,
            expected:  5,
        },
        {
            name:      "division by zero",
            operation: "/",
            a:         10,
            b:         0,
            wantErr:   true,
            errMsg:    "division by zero",
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result, err := Calculate(tt.operation, tt.a, tt.b)

            if tt.wantErr {
                require.Error(t, err)
                assert.Contains(t, err.Error(), tt.errMsg)
                return
            }

            require.NoError(t, err)
            assert.Equal(t, tt.expected, result)
        })
    }
}
```

## Summary

Key takeaways:
1. Use `assert` for general validations, `require` for preconditions
2. Test suites organize related tests and share setup logic
3. Mocks isolate components and verify interactions
4. Table-driven tests reduce duplication and clarify test cases
5. Always verify mock expectations with `AssertExpectations`
