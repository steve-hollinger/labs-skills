# Common Patterns

## Overview

This document covers common patterns for working with Neo4j in Go applications.

## Pattern 1: Repository Pattern

### When to Use

When building applications that need clean separation between database and business logic.

### Implementation

```go
// Repository interface
type PersonRepository interface {
    Create(ctx context.Context, person Person) (string, error)
    FindByID(ctx context.Context, id string) (*Person, error)
    FindByName(ctx context.Context, name string) ([]Person, error)
    Update(ctx context.Context, id string, updates map[string]any) error
    Delete(ctx context.Context, id string) error
}

// Neo4j implementation
type neo4jPersonRepo struct {
    driver neo4j.DriverWithContext
}

func NewPersonRepository(driver neo4j.DriverWithContext) PersonRepository {
    return &neo4jPersonRepo{driver: driver}
}

func (r *neo4jPersonRepo) Create(ctx context.Context, person Person) (string, error) {
    session := r.driver.NewSession(ctx, neo4j.SessionConfig{})
    defer session.Close(ctx)

    result, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
        result, err := tx.Run(ctx, `
            CREATE (p:Person {
                name: $name,
                email: $email,
                created: datetime()
            })
            RETURN elementId(p) AS id
        `, map[string]any{
            "name":  person.Name,
            "email": person.Email,
        })
        if err != nil {
            return nil, err
        }
        record, err := result.Single(ctx)
        if err != nil {
            return nil, err
        }
        id, _ := record.Get("id")
        return id.(string), nil
    })

    if err != nil {
        return "", err
    }
    return result.(string), nil
}

func (r *neo4jPersonRepo) FindByID(ctx context.Context, id string) (*Person, error) {
    session := r.driver.NewSession(ctx, neo4j.SessionConfig{
        AccessMode: neo4j.AccessModeRead,
    })
    defer session.Close(ctx)

    result, err := session.ExecuteRead(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
        result, err := tx.Run(ctx, `
            MATCH (p:Person)
            WHERE elementId(p) = $id
            RETURN p
        `, map[string]any{"id": id})
        if err != nil {
            return nil, err
        }

        record, err := result.Single(ctx)
        if err != nil {
            return nil, err // Not found or multiple results
        }

        node, _ := record.Get("p")
        return nodeToPersonn(node.(neo4j.Node)), nil
    })

    if err != nil {
        return nil, err
    }
    return result.(*Person), nil
}
```

### Pitfalls to Avoid

- Don't expose Neo4j types in the interface
- Handle "not found" cases explicitly
- Use transactions for operations that need atomicity

## Pattern 2: Batch Operations

### When to Use

When inserting or updating large amounts of data efficiently.

### Implementation

```go
func (r *neo4jPersonRepo) CreateBatch(ctx context.Context, people []Person) (int, error) {
    session := r.driver.NewSession(ctx, neo4j.SessionConfig{})
    defer session.Close(ctx)

    // Convert to maps for Neo4j
    batch := make([]map[string]any, len(people))
    for i, p := range people {
        batch[i] = map[string]any{
            "name":  p.Name,
            "email": p.Email,
        }
    }

    result, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
        result, err := tx.Run(ctx, `
            UNWIND $batch AS person
            CREATE (p:Person {
                name: person.name,
                email: person.email,
                created: datetime()
            })
            RETURN count(p) AS created
        `, map[string]any{"batch": batch})
        if err != nil {
            return nil, err
        }

        record, err := result.Single(ctx)
        if err != nil {
            return nil, err
        }

        count, _ := record.Get("created")
        return int(count.(int64)), nil
    })

    if err != nil {
        return 0, err
    }
    return result.(int), nil
}
```

### Pitfalls to Avoid

- Don't create too large batches (memory pressure)
- Consider chunking for very large datasets
- Use UNWIND for efficient batch operations

## Pattern 3: Error Handling

### When to Use

Always - proper error handling is essential.

### Implementation

```go
import (
    "errors"
    "github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

var (
    ErrNotFound     = errors.New("entity not found")
    ErrDuplicate    = errors.New("entity already exists")
    ErrInvalidInput = errors.New("invalid input")
)

func (r *neo4jPersonRepo) Create(ctx context.Context, person Person) (string, error) {
    session := r.driver.NewSession(ctx, neo4j.SessionConfig{})
    defer session.Close(ctx)

    result, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
        result, err := tx.Run(ctx, `
            MERGE (p:Person {email: $email})
            ON CREATE SET p.name = $name, p.created = datetime()
            ON MATCH SET p._matched = true
            RETURN elementId(p) AS id, p._matched AS existed
        `, map[string]any{
            "name":  person.Name,
            "email": person.Email,
        })
        if err != nil {
            return nil, err
        }

        record, err := result.Single(ctx)
        if err != nil {
            return nil, err
        }

        existed, _ := record.Get("existed")
        if existed != nil && existed.(bool) {
            return nil, ErrDuplicate
        }

        id, _ := record.Get("id")
        return id.(string), nil
    })

    if err != nil {
        // Check for specific Neo4j errors
        var neo4jErr *neo4j.Neo4jError
        if errors.As(err, &neo4jErr) {
            switch neo4jErr.Code {
            case "Neo.ClientError.Schema.ConstraintValidationFailed":
                return "", ErrDuplicate
            }
        }
        return "", err
    }
    return result.(string), nil
}
```

### Pitfalls to Avoid

- Don't swallow errors
- Wrap errors with context using `fmt.Errorf("context: %w", err)`
- Check for specific Neo4j error codes when needed

## Pattern 4: Relationship Handling

### When to Use

When working with graph relationships, which is most of the time in graph databases.

### Implementation

```go
// Create relationship between nodes
func (r *repo) CreateFriendship(ctx context.Context, person1ID, person2ID string) error {
    session := r.driver.NewSession(ctx, neo4j.SessionConfig{})
    defer session.Close(ctx)

    _, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
        result, err := tx.Run(ctx, `
            MATCH (a:Person), (b:Person)
            WHERE elementId(a) = $id1 AND elementId(b) = $id2
            MERGE (a)-[r:FRIENDS_WITH]->(b)
            ON CREATE SET r.since = date()
            RETURN r
        `, map[string]any{
            "id1": person1ID,
            "id2": person2ID,
        })
        if err != nil {
            return nil, err
        }

        _, err = result.Single(ctx)
        return nil, err
    })

    return err
}

// Query relationships
func (r *repo) GetFriends(ctx context.Context, personID string) ([]Person, error) {
    session := r.driver.NewSession(ctx, neo4j.SessionConfig{
        AccessMode: neo4j.AccessModeRead,
    })
    defer session.Close(ctx)

    result, err := session.ExecuteRead(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
        result, err := tx.Run(ctx, `
            MATCH (p:Person)-[:FRIENDS_WITH]-(friend:Person)
            WHERE elementId(p) = $id
            RETURN friend
        `, map[string]any{"id": personID})
        if err != nil {
            return nil, err
        }

        var friends []Person
        for result.Next(ctx) {
            record := result.Record()
            node, _ := record.Get("friend")
            friends = append(friends, nodeToPerson(node.(neo4j.Node)))
        }

        if err := result.Err(); err != nil {
            return nil, err
        }
        return friends, nil
    })

    if err != nil {
        return nil, err
    }
    return result.([]Person), nil
}
```

## Pattern 5: Testing with Neo4j

### When to Use

For integration tests that need a real database.

### Implementation

```go
// test_helpers.go
package db_test

import (
    "context"
    "os"
    "testing"

    "github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

func getTestDriver(t *testing.T) neo4j.DriverWithContext {
    t.Helper()

    uri := os.Getenv("NEO4J_URI")
    if uri == "" {
        uri = "bolt://localhost:7687"
    }

    driver, err := neo4j.NewDriverWithContext(
        uri,
        neo4j.BasicAuth(
            os.Getenv("NEO4J_USER"),
            os.Getenv("NEO4J_PASSWORD"),
            "",
        ),
    )
    if err != nil {
        t.Fatalf("Failed to create driver: %v", err)
    }

    ctx := context.Background()
    if err := driver.VerifyConnectivity(ctx); err != nil {
        t.Skipf("Neo4j not available: %v", err)
    }

    return driver
}

func cleanupTestData(t *testing.T, driver neo4j.DriverWithContext) {
    t.Helper()
    ctx := context.Background()
    session := driver.NewSession(ctx, neo4j.SessionConfig{})
    defer session.Close(ctx)

    _, err := session.Run(ctx, "MATCH (n:TestNode) DETACH DELETE n", nil)
    if err != nil {
        t.Logf("Cleanup warning: %v", err)
    }
}

// Usage in tests
func TestCreatePerson(t *testing.T) {
    driver := getTestDriver(t)
    defer driver.Close(context.Background())

    t.Cleanup(func() {
        cleanupTestData(t, driver)
    })

    repo := NewPersonRepository(driver)
    ctx := context.Background()

    id, err := repo.Create(ctx, Person{Name: "Test", Email: "test@example.com"})
    if err != nil {
        t.Fatalf("Create failed: %v", err)
    }

    if id == "" {
        t.Error("Expected non-empty ID")
    }
}
```

## Anti-Pattern 1: Driver Per Request

### What It Is

Creating a new driver for each request.

### Why It's Bad

```go
// BAD - Creates connection pool per request
func handleRequest(w http.ResponseWriter, r *http.Request) {
    driver, _ := neo4j.NewDriverWithContext(uri, auth)
    defer driver.Close(r.Context())
    // use driver
}
```

### Better Approach

```go
// GOOD - Reuse driver
type Server struct {
    driver neo4j.DriverWithContext
}

func NewServer(uri string, auth neo4j.AuthToken) (*Server, error) {
    driver, err := neo4j.NewDriverWithContext(uri, auth)
    if err != nil {
        return nil, err
    }
    return &Server{driver: driver}, nil
}

func (s *Server) handleRequest(w http.ResponseWriter, r *http.Request) {
    session := s.driver.NewSession(r.Context(), neo4j.SessionConfig{})
    defer session.Close(r.Context())
    // use session
}
```

## Anti-Pattern 2: Ignoring Result.Err()

### What It Is

Not checking for errors after iterating results.

### Why It's Bad

```go
// BAD - Errors during iteration are silently ignored
for result.Next(ctx) {
    record := result.Record()
    // process record
}
// What if there was a network error mid-iteration?
```

### Better Approach

```go
// GOOD - Always check Err() after iteration
for result.Next(ctx) {
    record := result.Record()
    // process record
}
if err := result.Err(); err != nil {
    return nil, fmt.Errorf("result iteration failed: %w", err)
}
```
