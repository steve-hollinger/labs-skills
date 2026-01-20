# Testcontainers

Learn integration testing with Testcontainers-Go for database, message queue, and service container management.

## Learning Objectives

After completing this skill, you will be able to:
- Use Testcontainers for integration testing
- Create and manage database containers (PostgreSQL, DynamoDB)
- Set up message queue containers (Kafka)
- Manage container lifecycle in tests
- Write reliable integration tests with real dependencies

## Prerequisites

- Go 1.22+
- Docker installed and running
- Basic understanding of Go testing
- Familiarity with databases and message queues

## Quick Start

```bash
# Install dependencies
make setup

# Start Docker if not running
docker info

# Run examples
make examples

# Run integration tests
make test-integration
```

## Concepts

### What is Testcontainers?

Testcontainers is a library that provides throwaway, lightweight instances of databases, message brokers, or any Docker container. Tests run against real services instead of mocks.

### Why Use Testcontainers?

- **Real dependencies**: Test against actual databases, not mocks
- **Isolation**: Each test can have its own container
- **Reproducibility**: Same environment everywhere
- **CI/CD friendly**: Works in any environment with Docker

### Basic Container Usage

```go
import (
    "context"
    "testing"

    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/wait"
)

func TestWithPostgres(t *testing.T) {
    ctx := context.Background()

    // Create container
    container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
        ContainerRequest: testcontainers.ContainerRequest{
            Image:        "postgres:15",
            ExposedPorts: []string{"5432/tcp"},
            Env: map[string]string{
                "POSTGRES_USER":     "test",
                "POSTGRES_PASSWORD": "test",
                "POSTGRES_DB":       "testdb",
            },
            WaitingFor: wait.ForLog("database system is ready"),
        },
        Started: true,
    })
    require.NoError(t, err)
    defer container.Terminate(ctx)

    // Get connection info
    host, _ := container.Host(ctx)
    port, _ := container.MappedPort(ctx, "5432")

    // Connect and test
    dsn := fmt.Sprintf("postgres://test:test@%s:%s/testdb?sslmode=disable", host, port.Port())
    // Use dsn to connect...
}
```

### Module-Based Containers

Testcontainers provides pre-configured modules for common services:

```go
import (
    "github.com/testcontainers/testcontainers-go/modules/postgres"
)

func TestWithPostgresModule(t *testing.T) {
    ctx := context.Background()

    pgContainer, err := postgres.RunContainer(ctx,
        testcontainers.WithImage("postgres:15"),
        postgres.WithDatabase("testdb"),
        postgres.WithUsername("test"),
        postgres.WithPassword("test"),
    )
    require.NoError(t, err)
    defer pgContainer.Terminate(ctx)

    // Get connection string directly
    connStr, err := pgContainer.ConnectionString(ctx, "sslmode=disable")
    require.NoError(t, err)

    // Use connStr to connect...
}
```

## Examples

### Example 1: PostgreSQL Container

Demonstrates PostgreSQL container setup and database testing.

```bash
make example-1
```

### Example 2: DynamoDB Local

Shows DynamoDB Local container for AWS service testing.

```bash
make example-2
```

### Example 3: Kafka Container

Demonstrates Kafka container for message queue testing.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Test a user repository with PostgreSQL
2. **Exercise 2**: Test a cache service with Redis
3. **Exercise 3**: Test an event processor with Kafka

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Mistake 1: Not Waiting for Container Ready

```go
// Bad: container may not be ready
container, _ := testcontainers.GenericContainer(ctx, req)
// Immediately try to connect - may fail!

// Good: wait for container to be ready
req := testcontainers.ContainerRequest{
    Image:      "postgres:15",
    WaitingFor: wait.ForLog("database system is ready").WithStartupTimeout(60*time.Second),
}
```

### Mistake 2: Hardcoding Ports

```go
// Bad: hardcoded port may conflict
dsn := "postgres://localhost:5432/testdb"

// Good: use mapped port
port, _ := container.MappedPort(ctx, "5432")
dsn := fmt.Sprintf("postgres://localhost:%s/testdb", port.Port())
```

### Mistake 3: Not Terminating Containers

```go
// Bad: container leaks
container, _ := testcontainers.GenericContainer(ctx, req)
// No cleanup!

// Good: always terminate
container, _ := testcontainers.GenericContainer(ctx, req)
defer container.Terminate(ctx)

// Or use t.Cleanup
t.Cleanup(func() {
    container.Terminate(ctx)
})
```

### Mistake 4: Starting Fresh Containers Per Test

```go
// Bad: slow - new container for each test
func TestA(t *testing.T) {
    container := startPostgres()
    defer container.Terminate(ctx)
    // test
}

func TestB(t *testing.T) {
    container := startPostgres()
    defer container.Terminate(ctx)
    // test
}

// Good: share container, isolate data
var testContainer *postgres.PostgresContainer

func TestMain(m *testing.M) {
    testContainer = startPostgres()
    code := m.Run()
    testContainer.Terminate(context.Background())
    os.Exit(code)
}

func TestA(t *testing.T) {
    cleanupTable(t, "users")
    // test
}
```

## Wait Strategies

Different services need different wait strategies:

| Service | Wait Strategy |
|---------|---------------|
| PostgreSQL | `wait.ForLog("database system is ready")` |
| MySQL | `wait.ForLog("ready for connections")` |
| Redis | `wait.ForLog("Ready to accept connections")` |
| Kafka | `wait.ForListeningPort("9092/tcp")` |
| HTTP services | `wait.ForHTTP("/health")` |
| Generic | `wait.ForListeningPort("8080/tcp")` |

## Further Reading

- [Testcontainers-Go Documentation](https://golang.testcontainers.org/)
- [Testcontainers Modules](https://golang.testcontainers.org/modules/)
- Related skills in this repository:
  - [Testify Framework](../testify-framework/)
  - [Test Logger Init](../test-logger-init/)
  - [Race Detector](../race-detector/)
