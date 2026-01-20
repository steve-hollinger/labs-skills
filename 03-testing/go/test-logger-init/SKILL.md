---
name: initializing-test-loggers
description: This skill teaches test initialization patterns in Go including TestMain, fixtures, helpers, and logging. Use when building or deploying containerized applications.
---

# Test Logger Init

## Quick Start
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
    # ... see docs/patterns.md for more
```

## Commands
```bash
make setup          # Download dependencies
make examples       # Run all examples
make example-1      # Run TestMain basics example
make example-2      # Run test fixtures example
make example-3      # Run logger configuration example
make test           # Run go test
```

## Key Points
- TestMain
- Test Fixtures
- Test Helpers

## Common Mistakes
1. **Forgetting os.Exit in TestMain** - Always capture and os.Exit with m.Run() result
2. **Not using t.Helper()** - Add t.Helper() as first line of every helper
3. **Shared mutable state between tests** - Reset state in SetupTest or use per-test instances

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples