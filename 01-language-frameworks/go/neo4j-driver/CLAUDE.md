# CLAUDE.md - Neo4j Go Driver

This skill teaches integration between Go applications and Neo4j graph database using the official neo4j-go-driver v5.

## Key Concepts

- **Driver**: Thread-safe connection pool, create once and reuse
- **Session**: Lightweight query execution context, close after use
- **Transaction**: Atomic unit of work with automatic retry support
- **ManagedTransaction**: Transaction function pattern for reliability
- **Result**: Lazy iterator over query results
- **Record**: Single row of query results

## Common Commands

```bash
make setup      # Download dependencies with go mod
make examples   # Run all examples
make example-1  # Run basic CRUD example
make example-2  # Run transaction patterns example
make example-3  # Run graph patterns example
make test       # Run go test
make test-race  # Run tests with race detector
make lint       # Run golangci-lint
make clean      # Remove build artifacts
```

## Project Structure

```
neo4j-driver/
├── cmd/examples/
│   ├── example1/main.go    # Basic CRUD operations
│   ├── example2/main.go    # Transaction patterns
│   └── example3/main.go    # Graph patterns
├── internal/
│   └── db/
│       └── neo4j.go        # Database helper functions
├── exercises/
│   ├── exercise1/main.go   # User management
│   ├── exercise2/main.go   # Social graph
│   ├── exercise3/main.go   # Repository pattern
│   └── solutions/
├── tests/
│   └── neo4j_test.go
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Driver Initialization

```go
package db

import (
    "context"
    "github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

type Neo4jClient struct {
    driver neo4j.DriverWithContext
}

func NewNeo4jClient(ctx context.Context, uri, username, password string) (*Neo4jClient, error) {
    driver, err := neo4j.NewDriverWithContext(uri, neo4j.BasicAuth(username, password, ""))
    if err != nil {
        return nil, fmt.Errorf("failed to create driver: %w", err)
    }

    if err := driver.VerifyConnectivity(ctx); err != nil {
        driver.Close(ctx)
        return nil, fmt.Errorf("failed to verify connectivity: %w", err)
    }

    return &Neo4jClient{driver: driver}, nil
}

func (c *Neo4jClient) Close(ctx context.Context) error {
    return c.driver.Close(ctx)
}
```

### Pattern 2: Transaction Function (Write)

```go
func (c *Neo4jClient) CreatePerson(ctx context.Context, name string, age int) (string, error) {
    session := c.driver.NewSession(ctx, neo4j.SessionConfig{})
    defer session.Close(ctx)

    result, err := session.ExecuteWrite(ctx,
        func(tx neo4j.ManagedTransaction) (any, error) {
            result, err := tx.Run(ctx, `
                CREATE (p:Person {name: $name, age: $age, created: datetime()})
                RETURN p.name AS name
            `, map[string]any{
                "name": name,
                "age":  age,
            })
            if err != nil {
                return nil, err
            }

            record, err := result.Single(ctx)
            if err != nil {
                return nil, err
            }

            name, _ := record.Get("name")
            return name.(string), nil
        },
    )

    if err != nil {
        return "", err
    }
    return result.(string), nil
}
```

### Pattern 3: Transaction Function (Read)

```go
func (c *Neo4jClient) FindPeople(ctx context.Context, minAge int) ([]Person, error) {
    session := c.driver.NewSession(ctx, neo4j.SessionConfig{
        AccessMode: neo4j.AccessModeRead,
    })
    defer session.Close(ctx)

    result, err := session.ExecuteRead(ctx,
        func(tx neo4j.ManagedTransaction) (any, error) {
            result, err := tx.Run(ctx, `
                MATCH (p:Person)
                WHERE p.age >= $minAge
                RETURN p.name AS name, p.age AS age
                ORDER BY p.name
            `, map[string]any{"minAge": minAge})
            if err != nil {
                return nil, err
            }

            var people []Person
            for result.Next(ctx) {
                record := result.Record()
                name, _ := record.Get("name")
                age, _ := record.Get("age")
                people = append(people, Person{
                    Name: name.(string),
                    Age:  int(age.(int64)),
                })
            }

            if err := result.Err(); err != nil {
                return nil, err
            }
            return people, nil
        },
    )

    if err != nil {
        return nil, err
    }
    return result.([]Person), nil
}
```

### Pattern 4: Handling Neo4j Types

```go
// Neo4j returns int64 for integers
age, _ := record.Get("age")
ageInt := int(age.(int64))

// Neo4j nodes can be accessed
node, _ := record.Get("person")
neo4jNode := node.(neo4j.Node)
name := neo4jNode.Props["name"].(string)
labels := neo4jNode.Labels // []string

// Relationships
rel, _ := record.Get("rel")
neo4jRel := rel.(neo4j.Relationship)
relType := neo4jRel.Type
props := neo4jRel.Props

// Dates/Times
date, _ := record.Get("date")
neo4jDate := date.(neo4j.Date)
goTime := neo4jDate.Time()

// Lists
names, _ := record.Get("names")
nameList := names.([]any)
for _, n := range nameList {
    name := n.(string)
}
```

## Common Mistakes

1. **Not closing sessions**
   - Sessions hold resources; always use `defer session.Close(ctx)`
   - Leaked sessions exhaust connection pool

2. **Not checking Result.Err()**
   - `result.Next()` returns false on error OR end of results
   - Always call `result.Err()` after iteration loop

3. **Creating driver per request**
   - Driver maintains connection pool, expensive to create
   - Create once at startup, reuse throughout application

4. **String interpolation in queries**
   - Security risk (injection) and performance issue (no plan caching)
   - Always use parameters with `$name` syntax

5. **Ignoring access mode**
   - `AccessModeRead` routes to read replicas in cluster
   - Use it for read-only queries to improve scalability

6. **Type assertion without checking**
   - Record values are `any`, need type assertion
   - Always handle type assertion failures

## When Users Ask About...

### "How do I connect to Neo4j?"
```go
driver, err := neo4j.NewDriverWithContext(
    "bolt://localhost:7687",
    neo4j.BasicAuth("neo4j", "password", ""),
)
defer driver.Close(ctx)
```

### "How do I run a query with parameters?"
```go
result, err := session.Run(ctx,
    "MATCH (p:Person {name: $name}) RETURN p",
    map[string]any{"name": "Alice"},
)
```

### "How do I handle transactions?"
Use `ExecuteWrite` or `ExecuteRead` for automatic retry:
```go
result, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
    // Your transactional code here
    return result, nil
})
```

### "How do I process multiple results?"
```go
for result.Next(ctx) {
    record := result.Record()
    // Process each record
}
if err := result.Err(); err != nil {
    return err  // Always check!
}
```

### "How do I get a single result?"
```go
record, err := result.Single(ctx)  // Fails if not exactly one result
// or
if result.Next(ctx) {
    record := result.Record()
    // Process single record
}
```

## Testing Notes

- Tests require Neo4j running (use `make infra-up` from repo root)
- Use transaction rollback for test isolation
- Mock the driver interface for unit tests
- Mark integration tests with `//go:build integration`
- Run with race detector: `make test-race`

## Dependencies

Key dependencies in go.mod:
- github.com/neo4j/neo4j-go-driver/v5: Official Neo4j driver
- github.com/stretchr/testify: Assertions and mocking
