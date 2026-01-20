---
name: building-mcp-servers
description: This skill teaches building Model Context Protocol (MCP) servers in Go using the mcp-go library. MCP servers expose tools and resources to AI applications. Use when implementing authentication or verifying tokens.
---

# Mcp Server

## Quick Start
```go
package main

import (
    "github.com/mark3labs/mcp-go/mcp"
    "github.com/mark3labs/mcp-go/server"
)

func main() {
    s := server.NewMCPServer(
        "my-server",
        "1.0.0",
        server.WithToolCapabilities(true),
    )

    // Add tools...
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
- MCP Protocol
- Tools
- Resources

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples