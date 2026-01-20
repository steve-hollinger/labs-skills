# Core Concepts

## Overview

The Model Context Protocol (MCP) is a standardized protocol that allows AI applications to interact with external tools, data sources, and services. This skill covers building MCP servers in Go that expose tools and resources to AI clients.

## Concept 1: MCP Protocol Architecture

### What It Is

MCP defines a client-server architecture where:
- **Clients** (like Claude Desktop) connect to servers and invoke capabilities
- **Servers** expose tools, resources, and prompts to clients
- Communication happens over stdio, HTTP/SSE, or WebSocket

### Why It Matters

- **Standardization**: One protocol for all AI integrations
- **Discoverability**: Clients can list available capabilities
- **Type Safety**: Schemas define expected inputs/outputs
- **Extensibility**: Add new tools without changing the protocol

### How It Works

```go
// Server lifecycle
import "github.com/mark3labs/mcp-go/server"

// 1. Create server with capabilities
s := server.NewMCPServer(
    "my-server",     // Server name
    "1.0.0",         // Version
    server.WithToolCapabilities(true),      // Enable tools
    server.WithResourceCapabilities(true, false), // Enable resources
)

// 2. Register capabilities (tools, resources)
s.AddTool(myTool, myHandler)
s.AddResource(myResource, myResourceHandler)

// 3. Start serving
s.ServeStdio()  // Or ServeHTTP, etc.
```

## Concept 2: Tools

### What It Is

Tools are functions that AI can invoke to perform actions. Each tool has:
- A unique name
- A description (helps AI understand when to use it)
- An input schema (JSON Schema defining parameters)
- A handler function

### Why It Matters

- **Actions**: Let AI perform real-world operations
- **Validation**: Inputs are validated against schemas
- **Documentation**: Descriptions guide AI usage
- **Error Handling**: Structured error responses

### How It Works

```go
import "github.com/mark3labs/mcp-go/mcp"

// Define the tool
tool := mcp.NewTool("search",
    mcp.WithDescription("Search for documents by query"),
    mcp.WithString("query",
        mcp.Required(),
        mcp.Description("The search query"),
    ),
    mcp.WithNumber("limit",
        mcp.Description("Maximum results"),
        mcp.DefaultNumber(10),
    ),
)

// Add handler
s.AddTool(tool, func(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
    // Extract parameters
    query := req.Params.Arguments["query"].(string)
    limit := 10
    if l, ok := req.Params.Arguments["limit"].(float64); ok {
        limit = int(l)
    }

    // Perform operation
    results := performSearch(query, limit)

    // Return result
    return mcp.NewToolResultText(results), nil
})
```

### Parameter Types

```go
// String parameter
mcp.WithString("name", mcp.Required(), mcp.Description("User name"))

// Number parameter (always float64 in JSON)
mcp.WithNumber("count", mcp.DefaultNumber(10))

// Boolean parameter
mcp.WithBoolean("verbose", mcp.DefaultBool(false))

// Array parameter
mcp.WithArray("tags", mcp.Description("List of tags"))

// Object parameter
mcp.WithObject("config", mcp.Description("Configuration object"))
```

## Concept 3: Resources

### What It Is

Resources are data sources that AI can read. They're identified by URIs and can be:
- **Static**: Fixed URI like `config://settings`
- **Templates**: Dynamic URI like `user://{id}/profile`

### Why It Matters

- **Data Access**: AI can read files, configs, databases
- **Structured**: URI scheme provides organization
- **Typed**: MIME types indicate content format
- **Dynamic**: Templates allow parameterized access

### How It Works

```go
// Static resource
resource := mcp.NewResource(
    "config://app/settings",
    "Application configuration",
    mcp.WithMIMEType("application/json"),
)

s.AddResource(resource, func(ctx context.Context, req mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
    data, err := loadConfig()
    if err != nil {
        return nil, err
    }

    return []mcp.ResourceContents{
        mcp.TextResourceContents(
            req.Params.URI,
            data,
            "application/json",
        ),
    }, nil
})

// Resource template
template := mcp.NewResourceTemplate(
    "user://{id}/profile",
    "User profile by ID",
)

s.AddResourceTemplate(template, func(ctx context.Context, req mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
    // Extract ID from URI
    id := extractID(req.Params.URI)

    user, err := getUser(id)
    if err != nil {
        return nil, err
    }

    return []mcp.ResourceContents{
        mcp.TextResourceContents(req.Params.URI, user.JSON(), "application/json"),
    }, nil
})
```

## Concept 4: Error Handling

### What It Is

MCP distinguishes between:
- **Tool errors**: Expected errors shown to the AI (validation, business logic)
- **Protocol errors**: Unexpected errors (bugs, connection issues)

### Why It Matters

- **User Experience**: AI can explain tool errors to users
- **Debugging**: Protocol errors indicate implementation issues
- **Recovery**: AI can retry or try alternatives for tool errors

### How It Works

```go
func handler(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
    // Validation error (tool error - shown to AI)
    if req.Params.Arguments["query"] == nil {
        return mcp.NewToolResultError("query is required"), nil
    }

    // Business logic error (tool error)
    result, err := performOperation()
    if err != nil {
        return mcp.NewToolResultError(fmt.Sprintf("Operation failed: %v", err)), nil
    }

    // Protocol error (unexpected - should be rare)
    if result == nil {
        return nil, errors.New("unexpected nil result")
    }

    return mcp.NewToolResultText(result.String()), nil
}
```

### Error Response Types

```go
// Tool error (AI will see this message)
return mcp.NewToolResultError("Invalid input: query cannot be empty"), nil

// Tool result with isError flag
result := mcp.NewToolResultText("Partial results...")
result.IsError = true
return result, nil

// Protocol error (connection issue, bug)
return nil, fmt.Errorf("database connection failed: %w", err)
```

## Summary

Key takeaways:

1. **MCP Protocol**: Standardized way for AI to interact with external capabilities

2. **Tools**: Functions AI can invoke with typed parameters and structured responses

3. **Resources**: Data sources AI can read with URI-based addressing

4. **Error Handling**: Distinguish between tool errors (expected) and protocol errors (unexpected)

5. **Type Safety**: JSON Schema validates inputs, Go types ensure correct handling
