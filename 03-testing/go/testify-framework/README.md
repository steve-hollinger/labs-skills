# Testify Framework

Learn to write expressive, maintainable Go tests using the Testify testing toolkit.

## Learning Objectives

After completing this skill, you will be able to:
- Write clear assertions using `assert` and `require`
- Create test suites with setup/teardown using `suite`
- Mock dependencies effectively using `mock`
- Implement table-driven tests with Testify
- Structure tests for readability and maintainability

## Prerequisites

- Go 1.22+
- Basic understanding of Go testing (`go test`)
- Familiarity with interfaces

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test

# Run tests with verbose output
make test-verbose
```

## Concepts

### Why Testify?

The standard library's `testing` package is powerful but verbose. Testify provides:
- Expressive assertion functions
- Better failure messages
- Test suites with setup/teardown
- Mocking framework
- HTTP testing utilities

### Assert vs Require

```go
import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func TestExample(t *testing.T) {
    // assert: continues test on failure
    assert.Equal(t, expected, actual, "values should match")
    assert.NoError(t, err)
    assert.True(t, condition)

    // require: stops test immediately on failure
    require.NotNil(t, obj, "object must exist")
    require.NoError(t, err, "must not error")

    // Use require for preconditions that would cause panics
    require.NotNil(t, config)
    assert.Equal(t, "value", config.Setting)
}
```

### Test Suites

```go
import (
    "testing"
    "github.com/stretchr/testify/suite"
)

type MyTestSuite struct {
    suite.Suite
    db *Database
}

func (s *MyTestSuite) SetupSuite() {
    // Runs once before all tests
    s.db = ConnectDatabase()
}

func (s *MyTestSuite) TearDownSuite() {
    // Runs once after all tests
    s.db.Close()
}

func (s *MyTestSuite) SetupTest() {
    // Runs before each test
    s.db.Truncate()
}

func (s *MyTestSuite) TestSomething() {
    s.Equal(expected, actual)
    s.NoError(err)
}

func TestMyTestSuite(t *testing.T) {
    suite.Run(t, new(MyTestSuite))
}
```

### Mocking

```go
import (
    "github.com/stretchr/testify/mock"
)

// Define interface
type UserRepository interface {
    GetUser(id int) (*User, error)
    SaveUser(user *User) error
}

// Create mock
type MockUserRepository struct {
    mock.Mock
}

func (m *MockUserRepository) GetUser(id int) (*User, error) {
    args := m.Called(id)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*User), args.Error(1)
}

func (m *MockUserRepository) SaveUser(user *User) error {
    args := m.Called(user)
    return args.Error(0)
}

// Use in tests
func TestService(t *testing.T) {
    mockRepo := new(MockUserRepository)
    mockRepo.On("GetUser", 1).Return(&User{ID: 1, Name: "Alice"}, nil)

    service := NewService(mockRepo)
    user, err := service.GetUser(1)

    require.NoError(t, err)
    assert.Equal(t, "Alice", user.Name)
    mockRepo.AssertExpectations(t)
}
```

## Examples

### Example 1: Basic Assertions

Demonstrates assert and require packages with common assertion types.

```bash
make example-1
```

### Example 2: Test Suites

Shows how to create test suites with setup/teardown lifecycle.

```bash
make example-2
```

### Example 3: Mocking

Demonstrates dependency mocking for unit testing.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Write tests with proper assert/require usage
2. **Exercise 2**: Create a test suite for a user service
3. **Exercise 3**: Mock an external API client

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Mistake 1: Using Assert When Require is Needed

```go
// Bad: continues after nil, causes panic
func TestBad(t *testing.T) {
    user, err := getUser()
    assert.NoError(t, err)
    assert.Equal(t, "Alice", user.Name) // PANIC if user is nil!
}

// Good: stops on precondition failure
func TestGood(t *testing.T) {
    user, err := getUser()
    require.NoError(t, err)
    require.NotNil(t, user)
    assert.Equal(t, "Alice", user.Name)
}
```

### Mistake 2: Not Asserting Mock Expectations

```go
// Bad: mock calls not verified
func TestBad(t *testing.T) {
    mockRepo := new(MockUserRepository)
    mockRepo.On("GetUser", 1).Return(&User{}, nil)

    service := NewService(mockRepo)
    service.Process()
    // Forgot to verify mock was called!
}

// Good: verify expectations
func TestGood(t *testing.T) {
    mockRepo := new(MockUserRepository)
    mockRepo.On("GetUser", 1).Return(&User{}, nil)

    service := NewService(mockRepo)
    service.Process()

    mockRepo.AssertExpectations(t)
}
```

### Mistake 3: Inconsistent Assertion Order

```go
// Bad: actual/expected swapped
assert.Equal(t, result, 42) // Wrong order!

// Good: expected, actual
assert.Equal(t, 42, result)
```

## Assertion Reference

### Common Assertions

| Assertion | Description |
|-----------|-------------|
| `Equal(expected, actual)` | Deep equality check |
| `NotEqual(a, b)` | Values are different |
| `Nil(obj)` / `NotNil(obj)` | Nil checks |
| `True(val)` / `False(val)` | Boolean checks |
| `Error(err)` / `NoError(err)` | Error checks |
| `Contains(s, substr)` | String/slice contains |
| `Len(obj, length)` | Check length |
| `Empty(obj)` / `NotEmpty(obj)` | Empty checks |
| `Greater(a, b)` / `Less(a, b)` | Numeric comparisons |
| `Panics(fn)` / `NotPanics(fn)` | Panic checks |
| `Eventually(fn, wait, tick)` | Async condition |
| `ElementsMatch(a, b)` | Same elements, any order |

## Further Reading

- [Testify Documentation](https://github.com/stretchr/testify)
- [Go Testing Best Practices](https://go.dev/doc/tutorial/add-a-test)
- Related skills in this repository:
  - [Race Detector](../race-detector/)
  - [Test Logger Init](../test-logger-init/)
  - [Testcontainers](../testcontainers/)
