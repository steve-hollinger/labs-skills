---
name: using-neo4j-go-driver
description: This skill teaches integration between Go applications and Neo4j graph database using the official neo4j-go-driver v5. Use when implementing authentication or verifying tokens.
---

# Neo4J Driver

## Quick Start
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
    # ... see docs/patterns.md for more
```

## Commands
```bash
make setup      # Download dependencies with go mod
make examples   # Run all examples
make example-1  # Run basic CRUD example
make example-2  # Run transaction patterns example
make example-3  # Run graph patterns example
make test       # Run go test
```

## Key Points
- Driver
- Session
- Transaction

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples