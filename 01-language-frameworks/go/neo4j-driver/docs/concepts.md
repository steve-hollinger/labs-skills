# Core Concepts

## Overview

The neo4j-go-driver is the official Go driver for Neo4j, providing a robust and efficient way to connect Go applications to Neo4j graph databases.

## Concept 1: Driver Architecture

### What It Is

The driver follows a layered architecture:
- **Driver**: Connection pool manager, thread-safe, long-lived
- **Session**: Query execution context, short-lived
- **Transaction**: Atomic unit of work
- **Result**: Lazy iterator over query results

### Why It Matters

Understanding this architecture helps you:
- Manage resources efficiently (don't create drivers per request)
- Handle errors appropriately at each layer
- Write concurrent code safely

### How It Works

```go
// Driver layer - create once, reuse
driver, err := neo4j.NewDriverWithContext(uri, auth)
defer driver.Close(ctx)

// Session layer - create per unit of work
session := driver.NewSession(ctx, neo4j.SessionConfig{})
defer session.Close(ctx)

// Transaction layer - for atomic operations
result, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
    // Query execution
    result, err := tx.Run(ctx, query, params)
    // Process results
    return data, err
})
```

## Concept 2: Connection Management

### What It Is

The driver maintains a connection pool that handles:
- Connection lifecycle
- Load balancing across cluster members
- Automatic reconnection on failures

### Why It Matters

- Drivers are expensive to create (connection setup, auth)
- Connection pooling improves performance
- Cluster awareness enables high availability

### How It Works

```go
// Create driver with custom configuration
driver, err := neo4j.NewDriverWithContext(
    "neo4j://localhost:7687",  // Use neo4j:// for cluster routing
    neo4j.BasicAuth("neo4j", "password", ""),
    func(config *neo4j.Config) {
        config.MaxConnectionPoolSize = 100
        config.ConnectionAcquisitionTimeout = 60 * time.Second
        config.MaxTransactionRetryTime = 30 * time.Second
    },
)

// Verify connectivity before use
if err := driver.VerifyConnectivity(ctx); err != nil {
    return fmt.Errorf("neo4j unreachable: %w", err)
}
```

URI schemes:
- `bolt://` - Direct connection to single instance
- `neo4j://` - Cluster routing (recommended)
- `bolt+s://`, `neo4j+s://` - With TLS encryption

## Concept 3: Session Management

### What It Is

Sessions provide the context for query execution. They're lightweight and should be short-lived.

### Why It Matters

- Sessions are NOT thread-safe
- Sessions handle transaction state
- Access mode affects routing in clusters

### How It Works

```go
// Default session
session := driver.NewSession(ctx, neo4j.SessionConfig{})
defer session.Close(ctx)

// Session with specific database
session := driver.NewSession(ctx, neo4j.SessionConfig{
    DatabaseName: "mydb",
})

// Read-only session (routes to read replicas)
session := driver.NewSession(ctx, neo4j.SessionConfig{
    AccessMode: neo4j.AccessModeRead,
})

// Session with bookmarks for causal consistency
session := driver.NewSession(ctx, neo4j.SessionConfig{
    Bookmarks: neo4j.BookmarksFromRawValues([]string{"..."})
})
```

## Concept 4: Transaction Patterns

### What It Is

Neo4j Go driver supports three transaction patterns:
1. **Auto-commit transactions**: Simple, single query
2. **Transaction functions**: Automatic retry, recommended
3. **Explicit transactions**: Manual control

### Why It Matters

- Transaction functions handle retries automatically
- Proper transaction use ensures data consistency
- Wrong pattern can cause data loss or poor performance

### How It Works

```go
// Auto-commit (implicit transaction)
result, err := session.Run(ctx, "CREATE (n:Node) RETURN n", nil)

// Transaction function (RECOMMENDED)
result, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
    // All operations in this function are in one transaction
    // Automatically retried on transient failures
    result, err := tx.Run(ctx, "CREATE (n:Node) RETURN n", nil)
    if err != nil {
        return nil, err
    }
    return result.Single(ctx)
})

// Explicit transaction (manual control)
tx, err := session.BeginTransaction(ctx)
if err != nil {
    return err
}
defer tx.Close(ctx)

result, err := tx.Run(ctx, "CREATE (n:Node) RETURN n", nil)
if err != nil {
    tx.Rollback(ctx)
    return err
}
tx.Commit(ctx)
```

## Concept 5: Result Processing

### What It Is

Results are lazy iterators over query output. Records are not fetched until you iterate.

### Why It Matters

- Memory efficient for large result sets
- Errors can occur during iteration
- Results must be consumed before transaction closes

### How It Works

```go
// Iterate over results
result, err := tx.Run(ctx, "MATCH (n) RETURN n.name AS name", nil)
if err != nil {
    return err
}

for result.Next(ctx) {
    record := result.Record()
    name, ok := record.Get("name")
    if !ok {
        continue
    }
    fmt.Println(name.(string))
}

// CRITICAL: Check for errors after iteration
if err := result.Err(); err != nil {
    return err
}

// Get single result (fails if not exactly one)
record, err := result.Single(ctx)

// Collect all results
records, err := result.Collect(ctx)

// Peek at next record without consuming
record := result.Peek(ctx)
```

## Concept 6: Type Mapping

### What It Is

Neo4j types map to Go types with some specific conversions.

### Why It Matters

- Incorrect type handling causes runtime panics
- Some types require explicit conversion
- Complex types (nodes, relationships) have special handling

### How It Works

```go
// Primitive types
intVal := record.Values[0].(int64)        // Neo4j integers are int64
floatVal := record.Values[1].(float64)    // Neo4j floats are float64
stringVal := record.Values[2].(string)
boolVal := record.Values[3].(bool)

// Collections
listVal := record.Values[4].([]any)
mapVal := record.Values[5].(map[string]any)

// Graph types
node := record.Values[6].(neo4j.Node)
rel := record.Values[7].(neo4j.Relationship)
path := record.Values[8].(neo4j.Path)

// Accessing node properties
node.Labels       // []string
node.Props        // map[string]any
node.ElementId    // string (unique identifier)

// Accessing relationship properties
rel.Type          // string
rel.Props         // map[string]any
rel.StartElementId
rel.EndElementId

// Temporal types
date := record.Values[9].(neo4j.Date)
dateTime := record.Values[10].(neo4j.DateTime)
goTime := dateTime.Time()  // Convert to time.Time
```

## Summary

Key takeaways:

1. **Driver**: Create once, reuse (thread-safe, handles connection pooling)
2. **Session**: Short-lived, NOT thread-safe, always defer Close()
3. **Transaction Functions**: Use `ExecuteWrite`/`ExecuteRead` for automatic retry
4. **Parameters**: Always use `$param` syntax, never string interpolation
5. **Results**: Lazy iteration, always check `result.Err()` after loop
6. **Types**: Neo4j integers are int64, handle type assertions carefully
