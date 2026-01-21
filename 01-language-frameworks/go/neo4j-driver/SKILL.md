---
name: using-neo4j-go-driver
description: Integration between Go applications and Neo4j graph database using the official neo4j-go-driver v5. Use when implementing authentication or verifying tokens.
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


## Key Points
- Driver
- Session
- Transaction

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples