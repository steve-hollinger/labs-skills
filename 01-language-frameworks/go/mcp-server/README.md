# MCP Server in Go

Learn to build Model Context Protocol (MCP) servers in Go. This skill teaches how to create MCP servers that expose tools, resources, and prompts to AI applications like Claude Desktop and other MCP clients.

## Learning Objectives

After completing this skill, you will be able to:
- Understand the MCP protocol and its components
- Build MCP servers using the mcp-go library
- Define and implement tools with input validation
- Expose resources and resource templates
- Handle MCP protocol messages correctly
- Test and debug MCP servers

## Prerequisites

- Go 1.22+
- Basic understanding of Go interfaces and error handling
- Familiarity with JSON and HTTP concepts
- Understanding of client-server architecture

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Concepts

### MCP Protocol Overview

The Model Context Protocol (MCP) is a standardized way for AI applications to interact with external tools and data sources. It defines three main primitives:

1. **Tools**: Functions the AI can invoke to perform actions
2. **Resources**: Data sources the AI can read from
3. **Prompts**: Pre-defined prompt templates

```go
// Basic MCP server structure
import "github.com/mark3labs/mcp-go/server"

func main() {
    s := server.NewMCPServer(
        "my-server",
        "1.0.0",
        server.WithToolCapabilities(true),
        server.WithResourceCapabilities(true, false),
    )

    // Add tools and resources...

    s.ServeStdio()
}
```

### Tool Definition

Tools are defined with a name, description, input schema, and handler function. The AI can discover and invoke these tools.

```go
import (
    "github.com/mark3labs/mcp-go/mcp"
    "github.com/mark3labs/mcp-go/server"
)

// Define a tool
searchTool := mcp.NewTool("search",
    mcp.WithDescription("Search for documents"),
    mcp.WithString("query",
        mcp.Required(),
        mcp.Description("Search query"),
    ),
    mcp.WithNumber("limit",
        mcp.Description("Max results"),
        mcp.DefaultNumber(10),
    ),
)

// Add handler
s.AddTool(searchTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
    query := request.Params.Arguments["query"].(string)
    limit := int(request.Params.Arguments["limit"].(float64))

    results := performSearch(query, limit)

    return mcp.NewToolResultText(results), nil
})
```

### Resource Definition

Resources expose data that the AI can read. They can be static URIs or templates with parameters.

```go
// Static resource
s.AddResource(mcp.NewResource(
    "config://app/settings",
    "Application settings",
    mcp.WithMIMEType("application/json"),
), func(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
    return []mcp.ResourceContents{
        mcp.TextResourceContents(request.Params.URI, loadSettings(), "application/json"),
    }, nil
})

// Resource template
s.AddResourceTemplate(mcp.NewResourceTemplate(
    "user://{id}/profile",
    "User profile by ID",
), func(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
    // Extract ID from URI and return user profile
})
```

## Examples

### Example 1: Basic Tool Server

A minimal MCP server with a simple tool.

```bash
make example-1
```

### Example 2: Resources and Templates

Exposing resources with static and dynamic URIs.

```bash
make example-2
```

### Example 3: Full-Featured Server

A complete MCP server with tools, resources, and error handling.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Create a calculator tool with multiple operations
2. **Exercise 2**: Build a file browser with resource templates
3. **Exercise 3**: Implement a database query tool with validation

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Missing Required Fields
Always check for required fields and handle missing values:
```go
query, ok := request.Params.Arguments["query"].(string)
if !ok || query == "" {
    return nil, fmt.Errorf("query is required")
}
```

### Improper Error Handling
Return errors properly so the AI can understand what went wrong:
```go
result, err := doSomething()
if err != nil {
    return mcp.NewToolResultError(fmt.Sprintf("Operation failed: %v", err)), nil
}
```

### Not Validating Input Types
JSON numbers come as float64, strings may need trimming:
```go
// Handle number conversion
limit := 10 // default
if val, ok := args["limit"].(float64); ok {
    limit = int(val)
}
```

## Further Reading

- [MCP Specification](https://modelcontextprotocol.io/specification)
- [mcp-go Documentation](https://github.com/mark3labs/mcp-go)
- Related skills in this repository:
  - [Tool Registry](../../../02-architecture-design/tool-registry/) - Tool management patterns
  - [Go Race Detector](../../../03-testing/go/race-detector/) - Testing concurrent Go code
