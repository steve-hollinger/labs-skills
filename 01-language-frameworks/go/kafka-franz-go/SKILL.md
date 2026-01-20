---
name: streaming-with-franz-go
description: This skill teaches high-performance Kafka integration in Go using the franz-go library. Use when writing or improving tests.
---

# Kafka Franz Go

## Quick Start
```go
package main

import (
    "context"
    "github.com/twmb/franz-go/pkg/kgo"
)

func main() {
    client, err := kgo.NewClient(
        kgo.SeedBrokers("localhost:9092"),
    )
    if err != nil {
        panic(err)
    }
    defer client.Close()
    # ... see docs/patterns.md for more
```

## Commands
```bash
make setup      # Download dependencies
make examples   # Run all examples
make example-1  # Run specific example
make test       # Run go test
make test-race  # Run tests with race detector
make lint       # Run golangci-lint
```

## Key Points
- franz-go Client
- Producing
- Consuming

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples