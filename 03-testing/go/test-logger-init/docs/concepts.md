# Core Concepts - Test Logger Init

## Overview

This document covers test initialization patterns in Go, including TestMain, fixtures, helpers, and logging configuration.

## Concept 1: TestMain

### What It Is

`TestMain` is a special function in Go that provides control over test execution for an entire package. When present, it's called instead of running tests directly.

### Why It Matters

- Enables one-time setup and teardown for all tests in a package
- Essential for expensive resources (databases, external services)
- Provides control over test execution flow
- Allows custom test output and reporting

### How It Works

```go
package mypackage

import (
    "os"
    "testing"
)

var testDB *Database

func TestMain(m *testing.M) {
    // Phase 1: Setup (runs once before any tests)
    var err error
    testDB, err = NewDatabase(":memory:")
    if err != nil {
        // Cannot use t.Fatal here - log and exit
        log.Fatalf("failed to create test database: %v", err)
    }

    // Phase 2: Run all tests
    code := m.Run()

    // Phase 3: Teardown (runs once after all tests)
    if testDB != nil {
        testDB.Close()
    }

    // Phase 4: Exit with test result code
    // CRITICAL: Must call os.Exit with the code from m.Run()
    os.Exit(code)
}
```

### Key Rules

1. Must be named exactly `TestMain`
2. Takes `*testing.M` as parameter
3. Must call `m.Run()` to execute tests
4. Must call `os.Exit()` with the result of `m.Run()`
5. Cannot use `t.Fatal()` or `t.Error()` - no *testing.T available

## Concept 2: Test Fixtures

### What It Is

Test fixtures are predefined test data and state that provide a consistent starting point for tests.

### Why It Matters

- Reduces code duplication across tests
- Ensures consistent test data
- Makes tests more readable
- Simplifies test maintenance

### Implementation Patterns

#### Simple Fixtures

```go
// fixtures.go
package fixtures

type UserFixtures struct {
    StandardUser *User
    AdminUser    *User
    InactiveUser *User
}

func NewUserFixtures() *UserFixtures {
    return &UserFixtures{
        StandardUser: &User{
            ID:     1,
            Name:   "Standard User",
            Email:  "user@example.com",
            Role:   "user",
            Active: true,
        },
        AdminUser: &User{
            ID:     2,
            Name:   "Admin User",
            Email:  "admin@example.com",
            Role:   "admin",
            Active: true,
        },
        InactiveUser: &User{
            ID:     3,
            Name:   "Inactive User",
            Email:  "inactive@example.com",
            Role:   "user",
            Active: false,
        },
    }
}
```

#### Builder Pattern Fixtures

```go
// builder.go
type UserBuilder struct {
    user User
}

func NewUserBuilder() *UserBuilder {
    return &UserBuilder{
        user: User{
            Name:   "Default Name",
            Email:  "default@example.com",
            Role:   "user",
            Active: true,
        },
    }
}

func (b *UserBuilder) WithID(id int64) *UserBuilder {
    b.user.ID = id
    return b
}

func (b *UserBuilder) WithName(name string) *UserBuilder {
    b.user.Name = name
    return b
}

func (b *UserBuilder) WithEmail(email string) *UserBuilder {
    b.user.Email = email
    return b
}

func (b *UserBuilder) WithRole(role string) *UserBuilder {
    b.user.Role = role
    return b
}

func (b *UserBuilder) AsInactive() *UserBuilder {
    b.user.Active = false
    return b
}

func (b *UserBuilder) Build() User {
    return b.user
}

// Usage
user := NewUserBuilder().
    WithName("Alice").
    WithEmail("alice@example.com").
    WithRole("admin").
    Build()
```

#### Database Fixtures

```go
// db_fixtures.go
type DBFixtures struct {
    DB    *sql.DB
    Users *UserFixtures
}

func NewDBFixtures(db *sql.DB) *DBFixtures {
    return &DBFixtures{
        DB:    db,
        Users: NewUserFixtures(),
    }
}

func (f *DBFixtures) Load() error {
    // Load users into database
    for _, user := range []*User{
        f.Users.StandardUser,
        f.Users.AdminUser,
        f.Users.InactiveUser,
    } {
        _, err := f.DB.Exec(
            "INSERT INTO users (id, name, email, role, active) VALUES (?, ?, ?, ?, ?)",
            user.ID, user.Name, user.Email, user.Role, user.Active,
        )
        if err != nil {
            return err
        }
    }
    return nil
}

func (f *DBFixtures) Clear() error {
    _, err := f.DB.Exec("DELETE FROM users")
    return err
}
```

## Concept 3: Test Helpers

### What It Is

Test helpers are reusable functions that encapsulate common test operations.

### Why It Matters

- Reduces test code duplication
- Improves test readability
- Centralizes assertion logic
- Makes tests easier to maintain

### The t.Helper() Function

```go
func assertEqual(t *testing.T, expected, actual interface{}) {
    t.Helper() // CRITICAL: Must be first line

    if expected != actual {
        t.Errorf("expected %v, got %v", expected, actual)
    }
}
```

Without `t.Helper()`:
```
--- FAIL: TestSomething (0.00s)
    helpers.go:10: expected 5, got 3  <-- Points to helper
```

With `t.Helper()`:
```
--- FAIL: TestSomething (0.00s)
    mytest_test.go:25: expected 5, got 3  <-- Points to test
```

### Common Helper Patterns

#### Assertion Helpers

```go
func AssertUserValid(t *testing.T, user *User) {
    t.Helper()
    require.NotNil(t, user, "user should not be nil")
    assert.NotZero(t, user.ID, "user should have ID")
    assert.NotEmpty(t, user.Name, "user should have name")
    assert.NotEmpty(t, user.Email, "user should have email")
}
```

#### Setup Helpers

```go
func SetupTestUser(t *testing.T, db *sql.DB) *User {
    t.Helper()

    user := &User{Name: "Test User", Email: "test@example.com"}
    result, err := db.Exec(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        user.Name, user.Email,
    )
    require.NoError(t, err)

    id, err := result.LastInsertId()
    require.NoError(t, err)
    user.ID = id

    // Cleanup when test completes
    t.Cleanup(func() {
        db.Exec("DELETE FROM users WHERE id = ?", user.ID)
    })

    return user
}
```

#### API Testing Helpers

```go
func MakeRequest(t *testing.T, handler http.Handler, method, path string, body io.Reader) *httptest.ResponseRecorder {
    t.Helper()

    req := httptest.NewRequest(method, path, body)
    req.Header.Set("Content-Type", "application/json")

    rec := httptest.NewRecorder()
    handler.ServeHTTP(rec, req)

    return rec
}

func AssertJSONResponse(t *testing.T, rec *httptest.ResponseRecorder, status int) map[string]interface{} {
    t.Helper()

    assert.Equal(t, status, rec.Code)
    assert.Contains(t, rec.Header().Get("Content-Type"), "application/json")

    var result map[string]interface{}
    err := json.Unmarshal(rec.Body.Bytes(), &result)
    require.NoError(t, err)

    return result
}
```

## Concept 4: Test Logging

### What It Is

Configuring logging behavior for test environments to aid debugging while reducing noise.

### Why It Matters

- Helps debug test failures
- Reduces noise during normal test runs
- Enables log assertions in tests
- Provides flexibility for different test scenarios

### Implementation Patterns

#### Discarding Logs

```go
import (
    "io"
    "log/slog"
)

func NewDiscardLogger() *slog.Logger {
    return slog.New(slog.NewTextHandler(io.Discard, nil))
}
```

#### Capturing Logs for Assertions

```go
type CaptureLogger struct {
    buf    bytes.Buffer
    Logger *slog.Logger
}

func NewCaptureLogger() *CaptureLogger {
    cl := &CaptureLogger{}
    cl.Logger = slog.New(slog.NewJSONHandler(&cl.buf, &slog.HandlerOptions{
        Level: slog.LevelDebug,
    }))
    return cl
}

func (cl *CaptureLogger) Contains(substr string) bool {
    return strings.Contains(cl.buf.String(), substr)
}

func (cl *CaptureLogger) Lines() []string {
    return strings.Split(strings.TrimSpace(cl.buf.String()), "\n")
}

func (cl *CaptureLogger) Clear() {
    cl.buf.Reset()
}

// Usage in test
func TestLogging(t *testing.T) {
    cl := NewCaptureLogger()
    service := NewService(cl.Logger)

    service.DoSomething()

    assert.True(t, cl.Contains("operation completed"))
}
```

#### Test-Aware Logging

```go
type TestLogger struct {
    t *testing.T
}

func NewTestLogger(t *testing.T) *slog.Logger {
    return slog.New(&TestLogHandler{t: t})
}

type TestLogHandler struct {
    t *testing.T
}

func (h *TestLogHandler) Enabled(ctx context.Context, level slog.Level) bool {
    return true
}

func (h *TestLogHandler) Handle(ctx context.Context, r slog.Record) error {
    h.t.Logf("[%s] %s", r.Level, r.Message)
    return nil
}

func (h *TestLogHandler) WithAttrs(attrs []slog.Attr) slog.Handler {
    return h
}

func (h *TestLogHandler) WithGroup(name string) slog.Handler {
    return h
}
```

## Summary

Key takeaways:
1. TestMain provides package-level setup/teardown
2. Always call os.Exit(m.Run()) in TestMain
3. Use fixtures for consistent test data
4. Mark helpers with t.Helper() for correct error reporting
5. Configure logging appropriately for test scenarios
