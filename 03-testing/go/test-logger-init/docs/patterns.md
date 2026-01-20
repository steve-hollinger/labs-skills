# Common Patterns - Test Logger Init

## Overview

This document covers common patterns for test initialization, fixtures, helpers, and logging.

## Pattern 1: Database TestMain

### When to Use

When tests require a database connection that's expensive to create.

### Implementation

```go
package repo_test

import (
    "database/sql"
    "log"
    "os"
    "testing"

    _ "github.com/lib/pq"
)

var testDB *sql.DB

func TestMain(m *testing.M) {
    // Setup
    dsn := os.Getenv("TEST_DATABASE_URL")
    if dsn == "" {
        dsn = "postgres://localhost/testdb?sslmode=disable"
    }

    var err error
    testDB, err = sql.Open("postgres", dsn)
    if err != nil {
        log.Fatalf("failed to connect to test database: %v", err)
    }

    if err := testDB.Ping(); err != nil {
        log.Fatalf("failed to ping test database: %v", err)
    }

    // Run migrations
    if err := runMigrations(testDB); err != nil {
        log.Fatalf("failed to run migrations: %v", err)
    }

    // Run tests
    code := m.Run()

    // Teardown
    testDB.Close()

    os.Exit(code)
}

// Helper to get clean table for each test
func cleanTable(t *testing.T, table string) {
    t.Helper()
    _, err := testDB.Exec("DELETE FROM " + table)
    require.NoError(t, err)
}
```

## Pattern 2: Fixture Factory

### When to Use

When you need to create many similar test objects with variations.

### Implementation

```go
package fixtures

type OrderFactory struct {
    sequence int64
}

func NewOrderFactory() *OrderFactory {
    return &OrderFactory{}
}

func (f *OrderFactory) nextID() int64 {
    f.sequence++
    return f.sequence
}

func (f *OrderFactory) Create(opts ...OrderOption) *Order {
    order := &Order{
        ID:        f.nextID(),
        UserID:    1,
        Status:    "pending",
        Items:     []OrderItem{},
        Total:     0,
        CreatedAt: time.Now(),
    }

    for _, opt := range opts {
        opt(order)
    }

    return order
}

type OrderOption func(*Order)

func WithUserID(id int64) OrderOption {
    return func(o *Order) {
        o.UserID = id
    }
}

func WithStatus(status string) OrderOption {
    return func(o *Order) {
        o.Status = status
    }
}

func WithItems(items ...OrderItem) OrderOption {
    return func(o *Order) {
        o.Items = items
        var total float64
        for _, item := range items {
            total += item.Price * float64(item.Quantity)
        }
        o.Total = total
    }
}

// Usage
factory := NewOrderFactory()
pendingOrder := factory.Create(WithUserID(42), WithStatus("pending"))
shippedOrder := factory.Create(
    WithUserID(42),
    WithStatus("shipped"),
    WithItems(OrderItem{Price: 10.00, Quantity: 2}),
)
```

## Pattern 3: Test Context with Cleanup

### When to Use

When tests need multiple resources with automatic cleanup.

### Implementation

```go
package testutil

type TestContext struct {
    t        *testing.T
    cleanups []func()
    DB       *sql.DB
    Logger   *slog.Logger
    Cache    *Redis
}

func NewTestContext(t *testing.T) *TestContext {
    tc := &TestContext{t: t}

    // Register cleanup
    t.Cleanup(func() {
        tc.cleanup()
    })

    return tc
}

func (tc *TestContext) cleanup() {
    // Run cleanups in reverse order
    for i := len(tc.cleanups) - 1; i >= 0; i-- {
        tc.cleanups[i]()
    }
}

func (tc *TestContext) OnCleanup(fn func()) {
    tc.cleanups = append(tc.cleanups, fn)
}

func (tc *TestContext) WithDB(db *sql.DB) *TestContext {
    tc.DB = db
    return tc
}

func (tc *TestContext) WithLogger(logger *slog.Logger) *TestContext {
    tc.Logger = logger
    return tc
}

func (tc *TestContext) CreateUser(name, email string) *User {
    tc.t.Helper()

    user := &User{Name: name, Email: email}
    result, err := tc.DB.Exec(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        name, email,
    )
    require.NoError(tc.t, err)

    id, _ := result.LastInsertId()
    user.ID = id

    // Register cleanup
    tc.OnCleanup(func() {
        tc.DB.Exec("DELETE FROM users WHERE id = ?", id)
    })

    return user
}

// Usage
func TestUserService(t *testing.T) {
    ctx := NewTestContext(t).
        WithDB(testDB).
        WithLogger(NewDiscardLogger())

    user := ctx.CreateUser("Alice", "alice@example.com")
    // User will be deleted when test completes
}
```

## Pattern 4: Golden File Testing

### When to Use

When testing output that's complex to assert inline.

### Implementation

```go
package golden

import (
    "os"
    "path/filepath"
    "testing"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

var update = flag.Bool("update", false, "update golden files")

func AssertGolden(t *testing.T, name string, actual []byte) {
    t.Helper()

    goldenFile := filepath.Join("testdata", name+".golden")

    if *update {
        err := os.MkdirAll("testdata", 0755)
        require.NoError(t, err)
        err = os.WriteFile(goldenFile, actual, 0644)
        require.NoError(t, err)
        return
    }

    expected, err := os.ReadFile(goldenFile)
    require.NoError(t, err, "golden file not found, run with -update flag")

    assert.Equal(t, string(expected), string(actual))
}

// Usage
func TestJSONOutput(t *testing.T) {
    result := generateJSON()
    AssertGolden(t, "expected_output", result)
}

// Update golden files: go test -update ./...
```

## Pattern 5: Test Logger with Assertions

### When to Use

When you need to verify that specific logs are written.

### Implementation

```go
package testlog

type AssertableLogger struct {
    entries []LogEntry
    mu      sync.Mutex
}

type LogEntry struct {
    Level   string
    Message string
    Attrs   map[string]interface{}
}

func NewAssertableLogger() (*AssertableLogger, *slog.Logger) {
    al := &AssertableLogger{
        entries: make([]LogEntry, 0),
    }

    logger := slog.New(&assertableHandler{al: al})
    return al, logger
}

func (al *AssertableLogger) AssertLogged(t *testing.T, level, message string) {
    t.Helper()
    al.mu.Lock()
    defer al.mu.Unlock()

    for _, entry := range al.entries {
        if entry.Level == level && strings.Contains(entry.Message, message) {
            return
        }
    }

    t.Errorf("expected log entry with level=%s message containing %q, got: %v",
        level, message, al.entries)
}

func (al *AssertableLogger) AssertNotLogged(t *testing.T, level, message string) {
    t.Helper()
    al.mu.Lock()
    defer al.mu.Unlock()

    for _, entry := range al.entries {
        if entry.Level == level && strings.Contains(entry.Message, message) {
            t.Errorf("unexpected log entry: %v", entry)
            return
        }
    }
}

func (al *AssertableLogger) Clear() {
    al.mu.Lock()
    defer al.mu.Unlock()
    al.entries = al.entries[:0]
}

// Usage
func TestServiceLogging(t *testing.T) {
    assertLog, logger := NewAssertableLogger()
    service := NewService(logger)

    service.Process()

    assertLog.AssertLogged(t, "INFO", "processing started")
    assertLog.AssertLogged(t, "INFO", "processing completed")
    assertLog.AssertNotLogged(t, "ERROR", "")
}
```

## Pattern 6: Parallel-Safe Fixtures

### When to Use

When using t.Parallel() with shared fixtures.

### Implementation

```go
package fixtures

type ParallelFixtures struct {
    db       *sql.DB
    mu       sync.Mutex
    sequence int64
}

func NewParallelFixtures(db *sql.DB) *ParallelFixtures {
    return &ParallelFixtures{db: db}
}

func (f *ParallelFixtures) nextID() int64 {
    f.mu.Lock()
    defer f.mu.Unlock()
    f.sequence++
    return f.sequence
}

func (f *ParallelFixtures) CreateUser(t *testing.T) *User {
    t.Helper()

    // Use unique ID to avoid conflicts
    id := f.nextID()
    user := &User{
        ID:    id,
        Name:  fmt.Sprintf("User_%d", id),
        Email: fmt.Sprintf("user%d@example.com", id),
    }

    _, err := f.db.Exec(
        "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
        user.ID, user.Name, user.Email,
    )
    require.NoError(t, err)

    t.Cleanup(func() {
        f.db.Exec("DELETE FROM users WHERE id = ?", id)
    })

    return user
}

// Usage
func TestParallel(t *testing.T) {
    fixtures := NewParallelFixtures(testDB)

    t.Run("test1", func(t *testing.T) {
        t.Parallel()
        user := fixtures.CreateUser(t)
        // Test with unique user
    })

    t.Run("test2", func(t *testing.T) {
        t.Parallel()
        user := fixtures.CreateUser(t)
        // Test with different unique user
    })
}
```

## Anti-Patterns

### Anti-Pattern 1: Not Using t.Helper()

```go
// Bad: errors point to helper
func assertUser(t *testing.T, user *User) {
    require.NotNil(t, user)
}

// Good: errors point to test
func assertUser(t *testing.T, user *User) {
    t.Helper()
    require.NotNil(t, user)
}
```

### Anti-Pattern 2: Forgetting os.Exit

```go
// Bad: test failures not propagated
func TestMain(m *testing.M) {
    setup()
    m.Run() // Result ignored!
    teardown()
}

// Good: properly exit
func TestMain(m *testing.M) {
    setup()
    code := m.Run()
    teardown()
    os.Exit(code)
}
```

### Anti-Pattern 3: Shared Mutable State

```go
// Bad: tests affect each other
var users = make(map[int64]*User)

func TestA(t *testing.T) {
    users[1] = &User{ID: 1}
}

func TestB(t *testing.T) {
    // May or may not see user from TestA!
}

// Good: per-test state
func TestA(t *testing.T) {
    users := make(map[int64]*User)
    users[1] = &User{ID: 1}
}
```

### Anti-Pattern 4: Cleanup in Wrong Order

```go
// Bad: dependent cleanup fails
func TestWithDB(t *testing.T) {
    db := setupDB()
    defer db.Close()

    conn := db.GetConn()
    defer conn.Close() // Runs BEFORE db.Close - might fail

    // Test
}

// Good: cleanup order matches setup
func TestWithDB(t *testing.T) {
    db := setupDB()
    conn := db.GetConn()

    t.Cleanup(func() {
        conn.Close() // Runs first
        db.Close()   // Runs second
    })

    // Test
}
```

## Best Practices Summary

1. Always use `t.Helper()` in helper functions
2. Always `os.Exit(m.Run())` in TestMain
3. Use `t.Cleanup()` for automatic resource cleanup
4. Create unique data for parallel tests
5. Capture logs in buffer for assertions
6. Use builder pattern for flexible fixtures
7. Keep TestMain simple - only setup/teardown
