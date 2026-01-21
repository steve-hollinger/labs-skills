# Core Concepts - Testcontainers

## Overview

Testcontainers is a testing library that provides lightweight, throwaway instances of databases, message brokers, or any service that can run in a Docker container.

## Concept 1: Why Testcontainers?

### The Problem with Mocks

Traditional unit testing often uses mocks for external dependencies:

```go
// Mock approach
type MockDatabase struct {
    mock.Mock
}

func (m *MockDatabase) Save(user *User) error {
    args := m.Called(user)
    return args.Error(0)
}
```

Problems with mocks:
- Don't test real behavior
- Can drift from actual implementation
- Miss edge cases in real systems
- Don't test SQL queries

### The Testcontainers Solution

```go
// Real database approach
func TestUserRepository(t *testing.T) {
    ctx := context.Background()

    // Start real PostgreSQL
    pgContainer, _ := postgres.RunContainer(ctx)
    defer pgContainer.Terminate(ctx)

    // Get connection
    connStr, _ := pgContainer.ConnectionString(ctx)
    db, _ := sql.Open("postgres", connStr)

    // Test with real database
    repo := NewUserRepository(db)
    err := repo.Save(&User{Name: "Alice"})
    assert.NoError(t, err)
}
```

Benefits:
- Tests real database behavior
- Catches SQL syntax errors
- Tests migrations
- Validates constraints

## Concept 2: Container Lifecycle

### Basic Lifecycle

```go
func TestBasicLifecycle(t *testing.T) {
    ctx := context.Background()

    // 1. CREATE: Define container configuration
    req := testcontainers.ContainerRequest{
        Image:        "postgres:15",
        ExposedPorts: []string{"5432/tcp"},
        Env: map[string]string{
            "POSTGRES_PASSWORD": "test",
        },
        WaitingFor: wait.ForLog("ready to accept connections"),
    }

    // 2. START: Create and start container
    container, err := testcontainers.GenericContainer(ctx,
        testcontainers.GenericContainerRequest{
            ContainerRequest: req,
            Started:          true,
        })
    require.NoError(t, err)

    // 3. USE: Get connection info and use container
    host, _ := container.Host(ctx)
    port, _ := container.MappedPort(ctx, "5432")
    // Connect and test...

    // 4. TERMINATE: Clean up container
    defer container.Terminate(ctx)
}
```

### Lifecycle with TestMain

For sharing containers across tests:

```go
var pgContainer *postgres.PostgresContainer

func TestMain(m *testing.M) {
    ctx := context.Background()

    // Setup: Start container once
    var err error
    pgContainer, err = postgres.RunContainer(ctx)
    if err != nil {
        log.Fatalf("failed to start container: %v", err)
    }

    // Run all tests
    code := m.Run()

    // Teardown: Stop container
    if err := pgContainer.Terminate(ctx); err != nil {
        log.Printf("failed to terminate container: %v", err)
    }

    os.Exit(code)
}

func TestA(t *testing.T) {
    // Uses shared pgContainer
}

func TestB(t *testing.T) {
    // Uses shared pgContainer
}
```

## Concept 3: Wait Strategies

### Why Wait?

Containers start quickly, but services inside may take time to initialize.

```go
// Without waiting - may fail!
container, _ := testcontainers.GenericContainer(ctx, req)
db, _ := sql.Open("postgres", connStr) // Service not ready!
```

### Wait Strategy Types

#### Log-based Wait

```go
WaitingFor: wait.ForLog("database system is ready to accept connections").
    WithOccurrence(2).
    WithStartupTimeout(60 * time.Second)
```

#### Port-based Wait

```go
WaitingFor: wait.ForListeningPort("5432/tcp").
    WithStartupTimeout(30 * time.Second)
```

#### HTTP Wait

```go
WaitingFor: wait.ForHTTP("/health").
    WithPort("8080/tcp").
    WithStatusCodeMatcher(func(status int) bool {
        return status == 200
    }).
    WithStartupTimeout(30 * time.Second)
```

#### SQL Wait

```go
WaitingFor: wait.ForSQL("5432/tcp", "postgres", func(host string, port nat.Port) string {
    return fmt.Sprintf("postgres://user:pass@%s:%s/db?sslmode=disable", host, port.Port())
})
```

#### Combined Wait

```go
WaitingFor: wait.ForAll(
    wait.ForLog("Ready"),
    wait.ForListeningPort("8080/tcp"),
)
```

## Concept 4: Port Mapping

### Dynamic Port Allocation

Containers expose ports, but Docker maps them to random host ports:

```
Container:  postgres:5432
Host:       localhost:55432 (random)
```

### Getting Mapped Ports

```go
// Get host
host, err := container.Host(ctx)

// Get mapped port
port, err := container.MappedPort(ctx, "5432/tcp")

// Build connection string
connStr := fmt.Sprintf("postgres://user:pass@%s:%s/db", host, port.Port())
```

### Module Shortcuts

Pre-built modules often provide helper methods:

```go
// PostgreSQL module
connStr, err := pgContainer.ConnectionString(ctx, "sslmode=disable")

// Redis module
addr, err := redisContainer.ConnectionString(ctx)
```

## Concept 5: Container Configuration

### Environment Variables

```go
ContainerRequest{
    Image: "postgres:15",
    Env: map[string]string{
        "POSTGRES_USER":     "testuser",
        "POSTGRES_PASSWORD": "testpass",
        "POSTGRES_DB":       "testdb",
    },
}
```

### Volume Mounts

```go
ContainerRequest{
    Image: "postgres:15",
    Mounts: testcontainers.Mounts(
        testcontainers.BindMount("/path/on/host", "/path/in/container"),
    ),
}
```

### Init Scripts

```go
// PostgreSQL module
postgres.RunContainer(ctx,
    postgres.WithInitScripts("schema.sql", "data.sql"),
)
```

### Custom Commands

```go
ContainerRequest{
    Image: "redis:7",
    Cmd:   []string{"redis-server", "--requirepass", "secret"},
}
```

### Networks

```go
// Create network
network, _ := testcontainers.GenericNetwork(ctx, testcontainers.GenericNetworkRequest{
    NetworkRequest: testcontainers.NetworkRequest{
        Name: "test-network",
    },
})

// Add container to network
ContainerRequest{
    Networks: []string{"test-network"},
}
```

## Concept 6: Module-Based Containers

### Available Modules

Testcontainers provides pre-configured modules:

```go
import (
    "github.com/testcontainers/testcontainers-go/modules/postgres"
    "github.com/testcontainers/testcontainers-go/modules/kafka"
    "github.com/testcontainers/testcontainers-go/modules/redis"
    "github.com/testcontainers/testcontainers-go/modules/localstack"
)
```

### Using Modules

```go
// PostgreSQL
pgContainer, _ := postgres.RunContainer(ctx,
    testcontainers.WithImage("postgres:15"),
    postgres.WithDatabase("testdb"),
    postgres.WithUsername("test"),
    postgres.WithPassword("test"),
)

// Kafka
kafkaContainer, _ := kafka.RunContainer(ctx,
    kafka.WithClusterID("test-cluster"),
)

// Redis
redisContainer, _ := redis.RunContainer(ctx,
    testcontainers.WithImage("redis:7"),
)
```

## Summary

Key takeaways:
1. Testcontainers tests against real services, not mocks
2. Use wait strategies to ensure containers are ready
3. Get mapped ports dynamically, don't hardcode
4. Share containers across tests with TestMain
5. Use modules for common services
6. Always terminate containers (use defer)
