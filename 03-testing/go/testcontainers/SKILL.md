---
name: testing-with-containers
description: Integration testing with Testcontainers-Go for real service dependencies. Use when building or deploying containerized applications.
---

# Testcontainers

## Quick Start
```go
func SetupPostgres(ctx context.Context) (*postgres.PostgresContainer, error) {
    return postgres.RunContainer(ctx,
        testcontainers.WithImage("postgres:15-alpine"),
        postgres.WithDatabase("testdb"),
        postgres.WithUsername("test"),
        postgres.WithPassword("test"),
        testcontainers.WithWaitStrategy(
            wait.ForLog("database system is ready to accept connections").
                WithOccurrence(2).
                WithStartupTimeout(60*time.Second),
        ),
    )
}
```


## Key Points
- Testcontainers
- Wait Strategies
- Container Lifecycle

## Common Mistakes
1. **Not waiting for container ready** - Use appropriate WaitingFor strategy
2. **Hardcoding ports** - Use container.MappedPort() for dynamic ports
3. **Container leak** - Always defer container.Terminate(ctx)

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples