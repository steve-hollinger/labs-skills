# CLAUDE.md - MCP Server in Go

This skill teaches building Model Context Protocol (MCP) servers in Go using the mcp-go library. MCP servers expose tools and resources to AI applications.

## Key Concepts

- **MCP Protocol**: Standardized protocol for AI-tool interaction
- **Tools**: Functions the AI can invoke with typed parameters
- **Resources**: Data sources the AI can read (files, APIs, etc.)
- **Resource Templates**: Dynamic resource URIs with parameters
- **Server Capabilities**: Declare what the server supports

## Common Commands

```bash
make setup      # Download dependencies
make examples   # Run all examples
make example-1  # Run specific example
make test       # Run go test
make test-race  # Run tests with race detector
make lint       # Run golangci-lint
make clean      # Remove build artifacts
```

## Project Structure

```
mcp-server/
├── cmd/examples/
│   ├── example1/main.go  # Basic tool server
│   ├── example2/main.go  # Resources
│   └── example3/main.go  # Full-featured
├── internal/
│   └── handlers/         # Shared handlers
├── pkg/
│   └── mcputil/         # Utility functions
├── exercises/
│   ├── exercise1/
│   └── solutions/
├── tests/
│   └── server_test.go
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic Server Setup
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

    if err := s.ServeStdio(); err != nil {
        log.Fatal(err)
    }
}
```

### Pattern 2: Tool with Handler
```go
tool := mcp.NewTool("greet",
    mcp.WithDescription("Greet someone"),
    mcp.WithString("name", mcp.Required()),
)

s.AddTool(tool, func(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
    name := req.Params.Arguments["name"].(string)
    return mcp.NewToolResultText(fmt.Sprintf("Hello, %s!", name)), nil
})
```

### Pattern 3: Resource Handler
```go
resource := mcp.NewResource(
    "file://config.json",
    "Configuration file",
    mcp.WithMIMEType("application/json"),
)

s.AddResource(resource, func(ctx context.Context, req mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
    data, err := os.ReadFile("config.json")
    if err != nil {
        return nil, err
    }
    return []mcp.ResourceContents{
        mcp.TextResourceContents(req.Params.URI, string(data), "application/json"),
    }, nil
})
```

## Common Mistakes

1. **Type assertions without checks**
   - JSON numbers are float64
   - Always check type assertion success
   ```go
   // Bad
   name := req.Params.Arguments["name"].(string)

   // Good
   name, ok := req.Params.Arguments["name"].(string)
   if !ok {
       return nil, errors.New("name must be a string")
   }
   ```

2. **Forgetting capabilities**
   - Server must declare capabilities
   - Tools need `WithToolCapabilities(true)`
   - Resources need `WithResourceCapabilities(true, subscribe)`

3. **Not handling context cancellation**
   - Long operations should check `ctx.Done()`
   - Return early if context is cancelled

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make example-1` and the basic server pattern above.

### "How do I test my MCP server?"
Show how to use the MCP Inspector or create test clients. See tests/ for examples.

### "How do I handle errors?"
Use `mcp.NewToolResultError()` for tool errors that should be shown to the AI. Return Go errors for protocol-level failures.

### "How do I add authentication?"
MCP doesn't define auth - implement it at the transport level or in middleware.

## Testing Notes

- Use table-driven tests for tool handlers
- Mock external services
- Test error cases thoroughly
- Run with race detector: `go test -race`

## Dependencies

Key dependencies in go.mod:
- github.com/mark3labs/mcp-go: MCP server library
- github.com/stretchr/testify: Test assertions

## MCP Protocol Reference

### Tool Response Types
- `mcp.NewToolResultText(text)`: Plain text result
- `mcp.NewToolResultImage(data, mimeType)`: Image result
- `mcp.NewToolResultError(message)`: Error result

### Resource Contents
- `mcp.TextResourceContents(uri, text, mimeType)`: Text content
- `mcp.BlobResourceContents(uri, base64Data, mimeType)`: Binary content

### Input Schema Types
- `mcp.WithString(name, opts...)`: String parameter
- `mcp.WithNumber(name, opts...)`: Number parameter
- `mcp.WithBoolean(name, opts...)`: Boolean parameter
- `mcp.WithObject(name, opts...)`: Object parameter
- `mcp.WithArray(name, opts...)`: Array parameter
