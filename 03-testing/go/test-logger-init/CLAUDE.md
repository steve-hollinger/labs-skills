# CLAUDE.md - Test Logger Init

This skill teaches test initialization patterns in Go including TestMain, fixtures, helpers, and logging.

## Key Concepts

- **TestMain**: Package-level setup/teardown for tests
- **Test Fixtures**: Predefined test data and state
- **Test Helpers**: Reusable functions with t.Helper()
- **Test Logger**: Logging configuration for test environments

## Common Commands

```bash
make setup          # Download dependencies
make examples       # Run all examples
make example-1      # Run TestMain basics example
make example-2      # Run test fixtures example
make example-3      # Run logger configuration example
make test           # Run go test
make test-verbose   # Run tests with verbose output
make test-race      # Run tests with race detector
make lint           # Run golangci-lint
make clean          # Remove build artifacts
```

## Project Structure

```
test-logger-init/
├── cmd/examples/
│   ├── example1/main.go    # TestMain basics
│   ├── example2/main.go    # Test fixtures
│   └── example3/main.go    # Logger configuration
├── internal/
│   ├── fixtures/           # Test fixture implementations
│   ├── logger/             # Test logger utilities
│   └── testhelpers/        # Reusable test helpers
├── exercises/
│   ├── exercise1/          # TestMain practice
│   ├── exercise2/          # Fixtures practice
│   ├── exercise3/          # Logger practice
│   └── solutions/
├── tests/
│   └── *_test.go           # Comprehensive tests
└── docs/
    ├── concepts.md         # Deep dive on concepts
    └── patterns.md         # Common patterns
```

## Code Patterns

### Pattern 1: TestMain Template
```go
var testDB *sql.DB

func TestMain(m *testing.M) {
    // Setup
    var err error
    testDB, err = setupDatabase()
    if err != nil {
        log.Fatalf("failed to setup database: %v", err)
    }

    // Run tests
    code := m.Run()

    // Teardown
    if testDB != nil {
        testDB.Close()
    }

    os.Exit(code)
}
```

### Pattern 2: Test Helper with t.Helper()
```go
func requireUser(t *testing.T, repo *UserRepo, id int64) *User {
    t.Helper() // IMPORTANT: marks this as helper
    user, err := repo.Get(id)
    require.NoError(t, err)
    require.NotNil(t, user)
    return user
}
```

### Pattern 3: Test Logger with Buffer
```go
type TestLogger struct {
    buf    bytes.Buffer
    logger *slog.Logger
}

func NewTestLogger() *TestLogger {
    tl := &TestLogger{}
    tl.logger = slog.New(slog.NewJSONHandler(&tl.buf, nil))
    return tl
}

func (tl *TestLogger) AssertContains(t *testing.T, msg string) {
    t.Helper()
    assert.Contains(t, tl.buf.String(), msg)
}
```

### Pattern 4: Fixture Builder
```go
type UserBuilder struct {
    user *User
}

func NewUserBuilder() *UserBuilder {
    return &UserBuilder{
        user: &User{
            Name:  "Default User",
            Email: "default@example.com",
            Role:  "user",
        },
    }
}

func (b *UserBuilder) WithName(name string) *UserBuilder {
    b.user.Name = name
    return b
}

func (b *UserBuilder) WithRole(role string) *UserBuilder {
    b.user.Role = role
    return b
}

func (b *UserBuilder) Build() *User {
    return b.user
}
```

## Common Mistakes

1. **Forgetting os.Exit in TestMain**
   - Why it happens: Test code in m.Run() doesn't propagate exit code
   - How to fix: Always capture and os.Exit with m.Run() result

2. **Not using t.Helper()**
   - Why it happens: Oversight when writing helpers
   - How to fix: Add t.Helper() as first line of every helper

3. **Shared mutable state between tests**
   - Why it happens: Global variables modified by tests
   - How to fix: Reset state in SetupTest or use per-test instances

4. **Teardown not running on panic**
   - Why it happens: Panic in setup prevents cleanup
   - How to fix: Use defer before any code that might panic

## When Users Ask About...

### "When should I use TestMain?"
Use TestMain when you need:
- Expensive one-time setup (database connections, docker containers)
- Global state initialization
- Resource cleanup after all tests
- Custom test output handling

### "How do I share setup between tests?"
Options:
1. TestMain for package-level setup
2. Suite.SetupTest for per-test setup with testify
3. Helper functions that run setup
4. Fixtures loaded in TestMain

### "Why isn't my helper showing the right line?"
Ensure t.Helper() is the first line of your helper function:
```go
func myHelper(t *testing.T, ...) {
    t.Helper() // Must be first
    // ... rest of helper
}
```

### "How do I test log output?"
1. Inject logger as dependency
2. Use bytes.Buffer as log output
3. Assert on buffer contents after test

## Testing Notes

- TestMain runs once per package
- Use -v flag for verbose test output
- Use -count=1 to disable test caching
- Helper functions should accept *testing.T first

## Dependencies

Key dependencies in go.mod:
- github.com/stretchr/testify v1.9.0: Test assertions
- log/slog: Structured logging (Go 1.21+)
