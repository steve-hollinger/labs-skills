# CLAUDE.md - Testcontainers

This skill teaches integration testing with Testcontainers-Go for real service dependencies.

## Key Concepts

- **Testcontainers**: Library for managing throwaway Docker containers in tests
- **Wait Strategies**: Methods to detect when a container is ready
- **Container Lifecycle**: Creating, starting, and terminating containers
- **Port Mapping**: Connecting to dynamically assigned container ports

## Common Commands

```bash
make setup            # Download dependencies
make examples         # Run all examples
make example-1        # Run PostgreSQL example
make example-2        # Run DynamoDB example
make example-3        # Run Kafka example
make test             # Run unit tests
make test-integration # Run integration tests (requires Docker)
make lint             # Run golangci-lint
make clean            # Remove build artifacts
```

## Project Structure

```
testcontainers/
├── cmd/examples/
│   ├── example1/main.go    # PostgreSQL container
│   ├── example2/main.go    # DynamoDB Local container
│   └── example3/main.go    # Kafka container
├── internal/
│   ├── containers/         # Container helper functions
│   ├── database/           # Database utilities
│   └── messaging/          # Messaging utilities
├── exercises/
│   ├── exercise1/          # PostgreSQL practice
│   ├── exercise2/          # Redis practice
│   ├── exercise3/          # Kafka practice
│   └── solutions/
├── tests/
│   └── *_test.go           # Integration tests
└── docs/
    ├── concepts.md         # Deep dive on concepts
    └── patterns.md         # Common patterns
```

## Code Patterns

### Pattern 1: PostgreSQL Container
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

### Pattern 2: Generic Container with Wait
```go
func SetupRedis(ctx context.Context) (testcontainers.Container, error) {
    return testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
        ContainerRequest: testcontainers.ContainerRequest{
            Image:        "redis:7-alpine",
            ExposedPorts: []string{"6379/tcp"},
            WaitingFor:   wait.ForLog("Ready to accept connections"),
        },
        Started: true,
    })
}
```

### Pattern 3: Shared Container in TestMain
```go
var pgContainer *postgres.PostgresContainer

func TestMain(m *testing.M) {
    ctx := context.Background()

    var err error
    pgContainer, err = SetupPostgres(ctx)
    if err != nil {
        log.Fatalf("failed to start postgres: %v", err)
    }

    code := m.Run()

    pgContainer.Terminate(ctx)
    os.Exit(code)
}

func TestSomething(t *testing.T) {
    connStr, _ := pgContainer.ConnectionString(context.Background())
    // Use connStr...
}
```

### Pattern 4: Container with Network
```go
func SetupKafkaWithNetwork(ctx context.Context) (testcontainers.Container, error) {
    network, _ := testcontainers.GenericNetwork(ctx, testcontainers.GenericNetworkRequest{
        NetworkRequest: testcontainers.NetworkRequest{Name: "kafka-net"},
    })

    return kafka.RunContainer(ctx,
        kafka.WithClusterID("test-cluster"),
        testcontainers.WithNetwork([]string{"kafka-net"}, network),
    )
}
```

## Common Mistakes

1. **Not waiting for container ready**
   - Why it happens: Container starts but service isn't ready
   - How to fix: Use appropriate WaitingFor strategy

2. **Hardcoding ports**
   - Why it happens: Assuming container uses host port
   - How to fix: Use container.MappedPort() for dynamic ports

3. **Container leak**
   - Why it happens: Forgetting to terminate
   - How to fix: Always defer container.Terminate(ctx)

4. **Starting container per test**
   - Why it happens: Isolation concerns
   - How to fix: Share container, isolate data with cleanup

## When Users Ask About...

### "Docker isn't available in CI"
Options:
1. Use GitHub Actions with `services:` for containers
2. Use Testcontainers Cloud
3. Skip integration tests with build tags: `//go:build integration`

### "Tests are slow"
1. Reuse containers across tests with TestMain
2. Use Alpine images for faster startup
3. Parallelize tests that don't share data
4. Use Ryuk (cleanup container) wisely

### "How do I run specific container versions?"
```go
postgres.RunContainer(ctx,
    testcontainers.WithImage("postgres:15.3-alpine"),
)
```

### "How do I initialize database schema?"
```go
postgres.RunContainer(ctx,
    postgres.WithInitScripts("init.sql"),
    // Or with inline SQL:
    postgres.WithDatabase("testdb"),
)

// Or after container starts:
db, _ := sql.Open("postgres", connStr)
db.Exec(schema)
```

## Testing Notes

- Requires Docker running locally
- Use build tags for integration tests: `//go:build integration`
- Set TESTCONTAINERS_RYUK_DISABLED=true to disable cleanup container
- Container logs available via container.Logs(ctx)

## Dependencies

Key dependencies in go.mod:
- github.com/testcontainers/testcontainers-go: Core library
- github.com/testcontainers/testcontainers-go/modules/postgres: PostgreSQL module
- github.com/testcontainers/testcontainers-go/modules/kafka: Kafka module
- github.com/stretchr/testify: Test assertions
- github.com/lib/pq: PostgreSQL driver
- github.com/aws/aws-sdk-go-v2: DynamoDB client

## Docker Requirements

Minimum Docker version: 20.10+
Required: Docker daemon running
Optional: Docker Compose for complex setups
