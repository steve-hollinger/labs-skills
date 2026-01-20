# Test Logger Init

Learn test initialization patterns in Go including TestMain, fixtures, helpers, and logger configuration.

## Learning Objectives

After completing this skill, you will be able to:
- Use TestMain for package-level setup and teardown
- Create reusable test fixtures and helpers
- Configure logging for tests
- Organize test code effectively
- Share state safely between tests

## Prerequisites

- Go 1.22+
- Basic Go testing knowledge
- Understanding of package structure

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test

# Run tests with verbose logging
make test-verbose
```

## Concepts

### TestMain

`TestMain` is a special function that controls test execution for a package:

```go
func TestMain(m *testing.M) {
    // Setup before all tests
    setup()

    // Run tests
    code := m.Run()

    // Teardown after all tests
    teardown()

    // Exit with test result code
    os.Exit(code)
}

func setup() {
    // Initialize database, start services, etc.
}

func teardown() {
    // Clean up resources
}
```

### Test Fixtures

Test fixtures provide consistent test data:

```go
// fixtures.go
type TestFixtures struct {
    DB        *sql.DB
    TestUser  *User
    TestAdmin *User
}

func NewTestFixtures(db *sql.DB) *TestFixtures {
    return &TestFixtures{
        DB: db,
        TestUser: &User{
            ID:    1,
            Name:  "Test User",
            Email: "test@example.com",
            Role:  "user",
        },
        TestAdmin: &User{
            ID:    2,
            Name:  "Test Admin",
            Email: "admin@example.com",
            Role:  "admin",
        },
    }
}

func (f *TestFixtures) LoadUsers() error {
    for _, user := range []*User{f.TestUser, f.TestAdmin} {
        if err := f.DB.Create(user); err != nil {
            return err
        }
    }
    return nil
}
```

### Test Helpers

Test helpers reduce boilerplate and improve readability:

```go
// helpers.go
func RequireUser(t *testing.T, repo UserRepository, id int64) *User {
    t.Helper() // Mark as helper for better error reporting
    user, err := repo.GetUser(id)
    require.NoError(t, err)
    require.NotNil(t, user)
    return user
}

func AssertUserEquals(t *testing.T, expected, actual *User) {
    t.Helper()
    assert.Equal(t, expected.Name, actual.Name)
    assert.Equal(t, expected.Email, actual.Email)
    assert.Equal(t, expected.Role, actual.Role)
}
```

### Logger Configuration for Tests

Configure logging to work well in test environments:

```go
// logger.go
var testLogger *slog.Logger

func InitTestLogger() {
    // Option 1: Discard logs in tests
    testLogger = slog.New(slog.NewTextHandler(io.Discard, nil))

    // Option 2: Write to test output
    testLogger = slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
        Level: slog.LevelDebug,
    }))

    // Option 3: Buffer for assertions
    var buf bytes.Buffer
    testLogger = slog.New(slog.NewTextHandler(&buf, nil))
}

func GetTestLogger() *slog.Logger {
    return testLogger
}
```

## Examples

### Example 1: TestMain Basics

Demonstrates TestMain for package-level setup.

```bash
make example-1
```

### Example 2: Test Fixtures

Shows how to create and use test fixtures.

```bash
make example-2
```

### Example 3: Logger Configuration

Demonstrates logging configuration for tests.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Implement TestMain with database setup
2. **Exercise 2**: Create test fixtures for an e-commerce domain
3. **Exercise 3**: Configure structured logging for tests

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Mistake 1: Forgetting os.Exit

```go
// Bad: test result code not returned
func TestMain(m *testing.M) {
    setup()
    m.Run() // Result ignored!
    teardown()
}

// Good: properly exit with test code
func TestMain(m *testing.M) {
    setup()
    code := m.Run()
    teardown()
    os.Exit(code)
}
```

### Mistake 2: Not Using t.Helper()

```go
// Bad: errors point to helper, not test
func assertValid(t *testing.T, user *User) {
    require.NotNil(t, user) // Error shows this line
}

// Good: errors point to calling test
func assertValid(t *testing.T, user *User) {
    t.Helper()
    require.NotNil(t, user) // Error shows test calling this
}
```

### Mistake 3: Shared Mutable State

```go
// Bad: tests affect each other
var globalCounter int

func TestA(t *testing.T) {
    globalCounter++ // Modifies global state
}

// Good: isolate per-test state
func TestA(t *testing.T) {
    counter := newCounter()
    counter.Inc()
}
```

## Best Practices

1. **Keep TestMain simple** - Only setup/teardown, no test logic
2. **Use t.Helper()** - For all helper functions
3. **Clean up in defer** - Ensure resources are released
4. **Parallel-safe fixtures** - Use t.Parallel() carefully
5. **Log levels** - Reduce noise in normal runs, verbose on demand

## Further Reading

- [Go Testing Documentation](https://golang.org/pkg/testing/)
- [TestMain Examples](https://golang.org/pkg/testing/#hdr-Main)
- Related skills in this repository:
  - [Testify Framework](../testify-framework/)
  - [Race Detector](../race-detector/)
  - [Testcontainers](../testcontainers/)
