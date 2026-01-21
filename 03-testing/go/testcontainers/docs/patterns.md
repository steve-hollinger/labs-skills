# Common Patterns - Testcontainers

## Overview

This document covers common patterns and best practices for using Testcontainers in Go integration tests.

## Pattern 1: Repository Testing with PostgreSQL

### When to Use

Testing data access layers with real SQL queries.

### Implementation

```go
//go:build integration

package repository_test

import (
    "context"
    "database/sql"
    "os"
    "testing"

    _ "github.com/lib/pq"
    "github.com/stretchr/testify/require"
    "github.com/testcontainers/testcontainers-go/modules/postgres"
)

var (
    testDB    *sql.DB
    testContainer *postgres.PostgresContainer
)

func TestMain(m *testing.M) {
    ctx := context.Background()

    // Start PostgreSQL container
    var err error
    testContainer, err = postgres.RunContainer(ctx,
        postgres.WithDatabase("testdb"),
        postgres.WithUsername("test"),
        postgres.WithPassword("test"),
    )
    if err != nil {
        panic(err)
    }

    // Get connection
    connStr, _ := testContainer.ConnectionString(ctx, "sslmode=disable")
    testDB, _ = sql.Open("postgres", connStr)

    // Run migrations
    runMigrations(testDB)

    // Run tests
    code := m.Run()

    // Cleanup
    testDB.Close()
    testContainer.Terminate(ctx)

    os.Exit(code)
}

// Helper to clean table before each test
func cleanTable(t *testing.T, table string) {
    t.Helper()
    _, err := testDB.Exec("DELETE FROM " + table)
    require.NoError(t, err)
}

func TestUserRepository_Create(t *testing.T) {
    cleanTable(t, "users")

    repo := NewUserRepository(testDB)
    user := &User{Name: "Alice", Email: "alice@example.com"}

    err := repo.Create(user)

    require.NoError(t, err)
    require.NotZero(t, user.ID)
}

func TestUserRepository_FindByEmail(t *testing.T) {
    cleanTable(t, "users")

    // Setup
    repo := NewUserRepository(testDB)
    repo.Create(&User{Name: "Alice", Email: "alice@example.com"})

    // Test
    user, err := repo.FindByEmail("alice@example.com")

    require.NoError(t, err)
    require.Equal(t, "Alice", user.Name)
}
```

## Pattern 2: Testing with DynamoDB Local

### When to Use

Testing AWS DynamoDB operations without AWS account.

### Implementation

```go
//go:build integration

package dynamodb_test

import (
    "context"
    "testing"

    "github.com/aws/aws-sdk-go-v2/aws"
    "github.com/aws/aws-sdk-go-v2/config"
    "github.com/aws/aws-sdk-go-v2/credentials"
    "github.com/aws/aws-sdk-go-v2/service/dynamodb"
    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/wait"
)

func setupDynamoDB(ctx context.Context) (testcontainers.Container, *dynamodb.Client, error) {
    // Start DynamoDB Local container
    container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
        ContainerRequest: testcontainers.ContainerRequest{
            Image:        "amazon/dynamodb-local:latest",
            ExposedPorts: []string{"8000/tcp"},
            WaitingFor:   wait.ForListeningPort("8000/tcp"),
        },
        Started: true,
    })
    if err != nil {
        return nil, nil, err
    }

    // Get endpoint
    host, _ := container.Host(ctx)
    port, _ := container.MappedPort(ctx, "8000")
    endpoint := fmt.Sprintf("http://%s:%s", host, port.Port())

    // Create client
    cfg, _ := config.LoadDefaultConfig(ctx,
        config.WithRegion("us-east-1"),
        config.WithCredentialsProvider(credentials.NewStaticCredentialsProvider("dummy", "dummy", "")),
    )

    client := dynamodb.NewFromConfig(cfg, func(o *dynamodb.Options) {
        o.BaseEndpoint = aws.String(endpoint)
    })

    return container, client, nil
}

func TestDynamoDB_PutGetItem(t *testing.T) {
    ctx := context.Background()

    container, client, err := setupDynamoDB(ctx)
    require.NoError(t, err)
    defer container.Terminate(ctx)

    // Create table
    createTable(t, client, "users")

    // Test put/get
    err = putItem(client, "users", map[string]string{"id": "1", "name": "Alice"})
    require.NoError(t, err)

    item, err := getItem(client, "users", "1")
    require.NoError(t, err)
    require.Equal(t, "Alice", item["name"])
}
```

## Pattern 3: Kafka Message Testing

### When to Use

Testing message producers and consumers with real Kafka.

### Implementation

```go
//go:build integration

package kafka_test

import (
    "context"
    "testing"
    "time"

    "github.com/segmentio/kafka-go"
    "github.com/testcontainers/testcontainers-go/modules/kafka"
)

func TestKafkaProducerConsumer(t *testing.T) {
    ctx := context.Background()

    // Start Kafka container
    kafkaContainer, err := kafka.RunContainer(ctx,
        kafka.WithClusterID("test-cluster"),
    )
    require.NoError(t, err)
    defer kafkaContainer.Terminate(ctx)

    // Get brokers
    brokers, err := kafkaContainer.Brokers(ctx)
    require.NoError(t, err)

    topic := "test-topic"

    // Create topic
    conn, _ := kafka.DialLeader(ctx, "tcp", brokers[0], topic, 0)
    conn.CreateTopics(kafka.TopicConfig{Topic: topic, NumPartitions: 1, ReplicationFactor: 1})
    conn.Close()

    // Write message
    writer := &kafka.Writer{
        Addr:  kafka.TCP(brokers...),
        Topic: topic,
    }
    defer writer.Close()

    err = writer.WriteMessages(ctx, kafka.Message{
        Key:   []byte("key-1"),
        Value: []byte("Hello Kafka!"),
    })
    require.NoError(t, err)

    // Read message
    reader := kafka.NewReader(kafka.ReaderConfig{
        Brokers: brokers,
        Topic:   topic,
        GroupID: "test-group",
    })
    defer reader.Close()

    ctx, cancel := context.WithTimeout(ctx, 10*time.Second)
    defer cancel()

    msg, err := reader.ReadMessage(ctx)
    require.NoError(t, err)
    require.Equal(t, "Hello Kafka!", string(msg.Value))
}
```

## Pattern 4: Multi-Container Setup

### When to Use

Testing services that depend on multiple external systems.

### Implementation

```go
//go:build integration

package integration_test

import (
    "context"
    "testing"

    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/modules/postgres"
    "github.com/testcontainers/testcontainers-go/modules/redis"
)

type TestEnvironment struct {
    Postgres    *postgres.PostgresContainer
    Redis       *redis.RedisContainer
    PostgresURL string
    RedisURL    string
}

func SetupTestEnvironment(ctx context.Context) (*TestEnvironment, error) {
    env := &TestEnvironment{}

    // Start PostgreSQL
    var err error
    env.Postgres, err = postgres.RunContainer(ctx,
        postgres.WithDatabase("testdb"),
        postgres.WithUsername("test"),
        postgres.WithPassword("test"),
    )
    if err != nil {
        return nil, err
    }
    env.PostgresURL, _ = env.Postgres.ConnectionString(ctx, "sslmode=disable")

    // Start Redis
    env.Redis, err = redis.RunContainer(ctx)
    if err != nil {
        env.Postgres.Terminate(ctx)
        return nil, err
    }
    env.RedisURL, _ = env.Redis.ConnectionString(ctx)

    return env, nil
}

func (e *TestEnvironment) Teardown(ctx context.Context) {
    if e.Redis != nil {
        e.Redis.Terminate(ctx)
    }
    if e.Postgres != nil {
        e.Postgres.Terminate(ctx)
    }
}

func TestServiceIntegration(t *testing.T) {
    ctx := context.Background()

    env, err := SetupTestEnvironment(ctx)
    require.NoError(t, err)
    defer env.Teardown(ctx)

    // Create service with real dependencies
    service := NewUserService(
        NewUserRepository(env.PostgresURL),
        NewCacheClient(env.RedisURL),
    )

    // Test service
    user, err := service.CreateUser("Alice", "alice@example.com")
    require.NoError(t, err)
    require.NotNil(t, user)
}
```

## Pattern 5: Container Reuse for Speed

### When to Use

When tests are slow due to container startup.

### Implementation

```go
//go:build integration

package fast_test

import (
    "context"
    "os"
    "testing"

    "github.com/testcontainers/testcontainers-go/modules/postgres"
)

var sharedContainer *postgres.PostgresContainer

func TestMain(m *testing.M) {
    ctx := context.Background()

    // Check if reusing existing container
    if os.Getenv("TESTCONTAINERS_REUSE") == "true" {
        // Try to connect to existing container
        // Implementation depends on your needs
    }

    // Start new container
    var err error
    sharedContainer, err = postgres.RunContainer(ctx,
        postgres.WithDatabase("testdb"),
        postgres.WithUsername("test"),
        postgres.WithPassword("test"),
    )
    if err != nil {
        panic(err)
    }

    code := m.Run()

    // Only terminate if not reusing
    if os.Getenv("TESTCONTAINERS_REUSE") != "true" {
        sharedContainer.Terminate(ctx)
    }

    os.Exit(code)
}

func cleanDatabase(t *testing.T) {
    t.Helper()
    ctx := context.Background()
    connStr, _ := sharedContainer.ConnectionString(ctx, "sslmode=disable")
    db, _ := sql.Open("postgres", connStr)
    defer db.Close()

    // Truncate all tables
    db.Exec("TRUNCATE users, orders CASCADE")
}

func TestA(t *testing.T) {
    cleanDatabase(t)
    // Test...
}

func TestB(t *testing.T) {
    cleanDatabase(t)
    // Test...
}
```

## Pattern 6: Build Tags for Integration Tests

### When to Use

To separate integration tests from unit tests.

### Implementation

```go
// user_repository_test.go (unit tests)
package repository

import (
    "testing"
    "github.com/stretchr/testify/mock"
)

func TestUserRepository_Mock(t *testing.T) {
    // Unit tests with mocks
}
```

```go
// user_repository_integration_test.go
//go:build integration

package repository_test

import (
    "testing"
)

func TestUserRepository_Integration(t *testing.T) {
    // Integration tests with real database
}
```

### Running Tests

```bash
# Unit tests only
go test ./...

# Integration tests only
go test -tags=integration ./...

# All tests
go test -tags=integration ./...
```

## Anti-Patterns

### Anti-Pattern 1: New Container Per Test

```go
// Bad: Slow, starts container for each test
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

// Good: Share container, isolate data
var container *postgres.PostgresContainer

func TestMain(m *testing.M) {
    container = startPostgres()
    code := m.Run()
    container.Terminate(ctx)
    os.Exit(code)
}
```

### Anti-Pattern 2: Ignoring Container Logs

```go
// Bad: No visibility into container issues
container, _ := testcontainers.GenericContainer(ctx, req)

// Good: Capture logs for debugging
container, _ := testcontainers.GenericContainer(ctx, req)
logs, _ := container.Logs(ctx)
defer logs.Close()
// On failure, logs help diagnose issues
```

### Anti-Pattern 3: Hardcoded Wait Times

```go
// Bad: Arbitrary sleep
container, _ := startContainer()
time.Sleep(10 * time.Second) // Might be too short or too long

// Good: Proper wait strategy
req := testcontainers.ContainerRequest{
    WaitingFor: wait.ForLog("ready").WithStartupTimeout(60 * time.Second),
}
```

## Best Practices Summary

1. **Use TestMain** for shared containers across tests
2. **Use build tags** to separate integration tests
3. **Use wait strategies** instead of sleeps
4. **Use modules** for common services
5. **Clean data between tests** instead of starting new containers
6. **Capture container logs** for debugging
7. **Use dynamic ports** from MappedPort()
8. **Always defer Terminate()** to avoid container leaks
