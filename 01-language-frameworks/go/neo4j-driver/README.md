# Neo4j Go Driver

Learn how to integrate Neo4j graph database with Go applications using the official neo4j-go-driver. Master connection management, transactions, and query patterns.

## Learning Objectives

After completing this skill, you will be able to:
- Configure and manage Neo4j driver connections in Go
- Execute Cypher queries with proper parameter handling
- Use session and transaction management patterns
- Handle results, records, and type mapping
- Implement common graph database patterns in Go
- Write robust, production-ready Neo4j integration code

## Prerequisites

- Go 1.22+
- [Neo4j Cypher](../../../05-data-databases/neo4j-cypher/) skill completed
- Docker (for running Neo4j locally)
- Neo4j shared infrastructure: `make infra-up` from repository root

## Quick Start

```bash
# Ensure Neo4j is running (from repository root)
cd /path/to/labs-skills
make infra-up

# Install dependencies
cd 01-language-frameworks/go/neo4j-driver
make setup

# Run examples
make examples

# Run tests
make test
```

## Neo4j Connection Details

When using the shared infrastructure:
- **Bolt URL**: bolt://localhost:7687
- **Username**: neo4j
- **Password**: password

## Concepts

### Driver Configuration

The driver is the main entry point for Neo4j connections.

```go
import (
    "context"
    "github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

// Create driver with basic auth
driver, err := neo4j.NewDriverWithContext(
    "bolt://localhost:7687",
    neo4j.BasicAuth("neo4j", "password", ""),
)
if err != nil {
    log.Fatal(err)
}
defer driver.Close(ctx)

// Verify connectivity
if err := driver.VerifyConnectivity(ctx); err != nil {
    log.Fatal(err)
}
```

### Session Management

Sessions are used to execute queries. They are lightweight and should be closed after use.

```go
// Create a session for the default database
session := driver.NewSession(ctx, neo4j.SessionConfig{
    DatabaseName: "neo4j",
})
defer session.Close(ctx)

// Session with access mode (read replica routing)
readSession := driver.NewSession(ctx, neo4j.SessionConfig{
    AccessMode: neo4j.AccessModeRead,
})
```

### Executing Queries

Use `session.Run()` for simple queries or transaction functions for atomic operations.

```go
// Simple query execution
result, err := session.Run(ctx,
    "MATCH (p:Person {name: $name}) RETURN p",
    map[string]any{"name": "Alice"},
)

// Process results
for result.Next(ctx) {
    record := result.Record()
    person, _ := record.Get("p")
    fmt.Printf("Found: %v\n", person)
}

// Check for errors after iteration
if err := result.Err(); err != nil {
    log.Fatal(err)
}
```

### Transaction Functions

Transaction functions provide automatic retry on transient failures.

```go
// Write transaction with automatic retry
result, err := session.ExecuteWrite(ctx,
    func(tx neo4j.ManagedTransaction) (any, error) {
        result, err := tx.Run(ctx,
            "CREATE (p:Person {name: $name}) RETURN p",
            map[string]any{"name": "Alice"},
        )
        if err != nil {
            return nil, err
        }
        record, err := result.Single(ctx)
        if err != nil {
            return nil, err
        }
        return record.Get("p")
    },
)

// Read transaction (routes to read replicas in cluster)
result, err := session.ExecuteRead(ctx,
    func(tx neo4j.ManagedTransaction) (any, error) {
        // Read-only query
        result, err := tx.Run(ctx,
            "MATCH (p:Person) RETURN p LIMIT 10",
            nil,
        )
        // ...
    },
)
```

## Examples

### Example 1: Basic CRUD Operations

Learn driver setup, basic queries, and result handling.

```bash
make example-1
```

### Example 2: Transaction Patterns

Master transaction functions and error handling.

```bash
make example-2
```

### Example 3: Graph Patterns

Implement common graph database patterns and queries.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: User Management - CRUD operations for user entities
2. **Exercise 2**: Social Graph - Build and query a social network
3. **Exercise 3**: Repository Pattern - Implement a clean repository interface

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Not Closing Sessions

```go
// BAD - Session leak
session := driver.NewSession(ctx, neo4j.SessionConfig{})
result, _ := session.Run(ctx, "MATCH (n) RETURN n", nil)
// Session never closed!

// GOOD - Always use defer
session := driver.NewSession(ctx, neo4j.SessionConfig{})
defer session.Close(ctx)
```

### Not Checking Result.Err()

```go
// BAD - Errors during iteration are missed
for result.Next(ctx) {
    // process record
}
// What if there was an error?

// GOOD - Always check Err() after iteration
for result.Next(ctx) {
    // process record
}
if err := result.Err(); err != nil {
    return err
}
```

### Using String Interpolation in Queries

```go
// BAD - SQL/Cypher injection risk, no query plan caching
name := "Alice"
query := fmt.Sprintf("MATCH (p:Person {name: '%s'}) RETURN p", name)

// GOOD - Use parameters
query := "MATCH (p:Person {name: $name}) RETURN p"
params := map[string]any{"name": "Alice"}
result, _ := session.Run(ctx, query, params)
```

### Creating Driver Per Request

```go
// BAD - Expensive to create drivers
func handleRequest() {
    driver, _ := neo4j.NewDriverWithContext(...)
    // use driver
    driver.Close(ctx)
}

// GOOD - Reuse driver (it's thread-safe)
var driver neo4j.DriverWithContext // package-level or in struct

func init() {
    driver, _ = neo4j.NewDriverWithContext(...)
}
```

## Further Reading

- [Neo4j Go Driver Documentation](https://neo4j.com/docs/go-manual/current/)
- [neo4j-go-driver GitHub](https://github.com/neo4j/neo4j-go-driver)
- Related skills in this repository:
  - [Neo4j Cypher](../../../05-data-databases/neo4j-cypher/)
  - [Neo4j DATE vs DATETIME](../../../05-data-databases/neo4j-date-datetime/)
  - [Go HTTP Services](../http-services/)
