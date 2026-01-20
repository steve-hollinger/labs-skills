# CLAUDE.md - Testify Framework

This skill teaches effective Go testing using the Testify testing toolkit.

## Key Concepts

- **assert**: Assertion functions that continue on failure
- **require**: Assertion functions that stop test on failure
- **suite**: Test suites with setup/teardown lifecycle
- **mock**: Mocking framework for dependency injection

## Common Commands

```bash
make setup          # Download dependencies
make examples       # Run all examples
make example-1      # Run basic assertions example
make example-2      # Run test suites example
make example-3      # Run mocking example
make test           # Run go test
make test-verbose   # Run tests with verbose output
make test-race      # Run tests with race detector
make lint           # Run golangci-lint
make clean          # Remove build artifacts
```

## Project Structure

```
testify-framework/
├── cmd/examples/
│   ├── example1/main.go    # Basic assertions
│   ├── example2/main.go    # Test suites
│   └── example3/main.go    # Mocking
├── internal/
│   ├── assertions/         # Assertion examples
│   ├── mocks/              # Mock implementations
│   └── suites/             # Suite examples
├── exercises/
│   ├── exercise1/          # Assert/require practice
│   ├── exercise2/          # Suite practice
│   ├── exercise3/          # Mocking practice
│   └── solutions/
├── tests/
│   └── *_test.go           # Comprehensive tests
└── docs/
    ├── concepts.md         # Deep dive on testify
    └── patterns.md         # Testing patterns
```

## Code Patterns

### Pattern 1: Assert vs Require Decision
```go
func TestWithProperPreconditions(t *testing.T) {
    // Use require for preconditions that would cause panics
    result, err := GetData()
    require.NoError(t, err)           // Stop if error
    require.NotNil(t, result)         // Stop if nil

    // Use assert for actual test assertions
    assert.Equal(t, "expected", result.Value)
    assert.Greater(t, result.Count, 0)
}
```

### Pattern 2: Table-Driven Tests with Testify
```go
func TestCalculator(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
        wantErr  bool
    }{
        {"add positive", 2, 3, 5, false},
        {"add negative", -1, 1, 0, false},
        {"divide by zero", 1, 0, 0, true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result, err := Calculate(tt.a, tt.b)
            if tt.wantErr {
                require.Error(t, err)
                return
            }
            require.NoError(t, err)
            assert.Equal(t, tt.expected, result)
        })
    }
}
```

### Pattern 3: Suite with Database
```go
type DatabaseSuite struct {
    suite.Suite
    db   *sql.DB
    repo *UserRepository
}

func (s *DatabaseSuite) SetupSuite() {
    var err error
    s.db, err = sql.Open("postgres", testDSN)
    s.Require().NoError(err)
    s.repo = NewUserRepository(s.db)
}

func (s *DatabaseSuite) TearDownSuite() {
    s.db.Close()
}

func (s *DatabaseSuite) SetupTest() {
    _, err := s.db.Exec("DELETE FROM users")
    s.Require().NoError(err)
}

func (s *DatabaseSuite) TestCreateUser() {
    user := &User{Name: "Alice"}
    err := s.repo.Create(user)
    s.NoError(err)
    s.NotZero(user.ID)
}
```

### Pattern 4: Mock with Flexible Matching
```go
func TestWithMock(t *testing.T) {
    mockRepo := new(MockUserRepository)

    // Exact match
    mockRepo.On("GetUser", 1).Return(&User{ID: 1}, nil)

    // Any argument
    mockRepo.On("GetUser", mock.Anything).Return(nil, ErrNotFound)

    // Custom matcher
    mockRepo.On("SaveUser", mock.MatchedBy(func(u *User) bool {
        return u.Name != ""
    })).Return(nil)

    // Verify specific number of calls
    mockRepo.AssertNumberOfCalls(t, "GetUser", 2)
}
```

## Common Mistakes

1. **Wrong assertion order**
   - Why it happens: Forgetting that order is (expected, actual)
   - How to fix: Always use `assert.Equal(t, expected, actual)`

2. **Using assert when require is needed**
   - Why it happens: Not thinking about nil panics
   - How to fix: Use require for error checks and nil checks before accessing

3. **Forgetting mock.AssertExpectations**
   - Why it happens: Test passes even if mock wasn't called
   - How to fix: Always call `mockObj.AssertExpectations(t)` at end

4. **Suite method not starting with Test**
   - Why it happens: Methods must start with Test to be run
   - How to fix: Name like `TestSomething`, not `Something`

## When Users Ask About...

### "Which should I use, assert or require?"
- Use `require` when failure would cause panic (nil checks, error checks)
- Use `assert` for actual test validations
- Rule: If the test can't continue meaningfully, use require

### "How do I mock an interface?"
1. Create a struct embedding `mock.Mock`
2. Implement all interface methods
3. Use `m.Called()` to record calls and return values
4. Set expectations with `On()` and `Return()`
5. Verify with `AssertExpectations(t)`

### "Why isn't my suite test running?"
Check:
1. Test method starts with `Test` (e.g., `TestCreate` not `Create`)
2. There's a `func TestXxxSuite(t *testing.T)` that calls `suite.Run()`
3. Suite struct embeds `suite.Suite`

### "How do I test async code?"
Use `assert.Eventually`:
```go
assert.Eventually(t, func() bool {
    return condition()
}, 5*time.Second, 100*time.Millisecond)
```

## Testing Notes

- Run tests with `-v` for verbose output
- Use `-run TestName` to run specific tests
- Use `t.Parallel()` for concurrent test execution
- Suite tests can use `s.T()` to get the testing.T

## Dependencies

Key dependencies in go.mod:
- github.com/stretchr/testify v1.9.0: Core testify packages
  - assert: Assertion functions
  - require: Assertion functions that stop on failure
  - suite: Test suite framework
  - mock: Mocking framework
