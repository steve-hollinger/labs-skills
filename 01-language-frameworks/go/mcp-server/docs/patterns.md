# Common Patterns

## Overview

This document covers common patterns and best practices for building MCP servers in Go.

## Pattern 1: Safe Parameter Extraction

### When to Use

Always when extracting parameters from tool requests. JSON unmarshaling produces specific Go types that need careful handling.

### Implementation

```go
// Create a helper function for safe extraction
func getString(args map[string]interface{}, key string) (string, bool) {
    val, ok := args[key].(string)
    return val, ok && val != ""
}

func getNumber(args map[string]interface{}, key string, defaultVal float64) float64 {
    if val, ok := args[key].(float64); ok {
        return val
    }
    return defaultVal
}

func getBool(args map[string]interface{}, key string, defaultVal bool) bool {
    if val, ok := args[key].(bool); ok {
        return val
    }
    return defaultVal
}

func getStringSlice(args map[string]interface{}, key string) []string {
    raw, ok := args[key].([]interface{})
    if !ok {
        return nil
    }
    result := make([]string, 0, len(raw))
    for _, v := range raw {
        if s, ok := v.(string); ok {
            result = append(result, s)
        }
    }
    return result
}
```

### Example

```go
s.AddTool(tool, func(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
    args := req.Params.Arguments

    // Required string
    query, ok := getString(args, "query")
    if !ok {
        return mcp.NewToolResultError("query is required"), nil
    }

    // Optional number with default
    limit := getNumber(args, "limit", 10)

    // Optional boolean
    includeMetadata := getBool(args, "include_metadata", false)

    // Optional string array
    tags := getStringSlice(args, "tags")

    // Use the values...
    return mcp.NewToolResultText("OK"), nil
})
```

### Pitfalls to Avoid

- Don't assume types match - always use type assertions with checks
- JSON numbers are always float64, convert explicitly to int
- Empty strings should often be treated as missing

## Pattern 2: Structured Tool Responses

### When to Use

When tool results need to be parsed by AI or contain multiple pieces of information.

### Implementation

```go
import "encoding/json"

type SearchResult struct {
    Query   string  `json:"query"`
    Total   int     `json:"total"`
    Results []Item  `json:"results"`
}

func searchHandler(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
    query := req.Params.Arguments["query"].(string)

    results := performSearch(query)

    response := SearchResult{
        Query:   query,
        Total:   len(results),
        Results: results,
    }

    // Serialize to JSON
    data, err := json.MarshalIndent(response, "", "  ")
    if err != nil {
        return nil, fmt.Errorf("failed to serialize response: %w", err)
    }

    return mcp.NewToolResultText(string(data)), nil
}
```

### Example

```go
// For simple results, plain text is fine
return mcp.NewToolResultText("User created successfully"), nil

// For complex results, use JSON
result := map[string]interface{}{
    "status":  "success",
    "user_id": newUserID,
    "message": "User created",
}
data, _ := json.MarshalIndent(result, "", "  ")
return mcp.NewToolResultText(string(data)), nil
```

### Pitfalls to Avoid

- Don't return raw Go struct representations (use JSON)
- Include enough context for AI to understand the result
- Consider the AI's ability to parse the response

## Pattern 3: Context-Aware Handlers

### When to Use

When handlers need to respect cancellation or have timeout requirements.

### Implementation

```go
func longRunningHandler(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
    // Create a channel for results
    resultCh := make(chan string, 1)
    errCh := make(chan error, 1)

    go func() {
        result, err := performLongOperation()
        if err != nil {
            errCh <- err
            return
        }
        resultCh <- result
    }()

    // Wait with context awareness
    select {
    case <-ctx.Done():
        return mcp.NewToolResultError("operation cancelled"), nil
    case err := <-errCh:
        return mcp.NewToolResultError(err.Error()), nil
    case result := <-resultCh:
        return mcp.NewToolResultText(result), nil
    }
}
```

### Example

```go
// Simple context check for batch operations
func processBatchHandler(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
    items := getItems(req)
    results := make([]string, 0, len(items))

    for _, item := range items {
        // Check context before each item
        select {
        case <-ctx.Done():
            return mcp.NewToolResultError(
                fmt.Sprintf("cancelled after processing %d/%d items", len(results), len(items)),
            ), nil
        default:
        }

        result := processItem(item)
        results = append(results, result)
    }

    return mcp.NewToolResultText(fmt.Sprintf("Processed %d items", len(results))), nil
}
```

### Pitfalls to Avoid

- Don't ignore context.Done() in long operations
- Return partial results when cancelled if meaningful
- Set reasonable timeouts for external calls

## Pattern 4: Resource URI Parsing

### When to Use

When implementing resource templates that need to extract parameters from URIs.

### Implementation

```go
import (
    "net/url"
    "strings"
)

// ParseResourceURI extracts components from a resource URI
// URI format: scheme://path/to/resource
func ParseResourceURI(uri string) (scheme, path string, err error) {
    parts := strings.SplitN(uri, "://", 2)
    if len(parts) != 2 {
        return "", "", fmt.Errorf("invalid URI format: %s", uri)
    }
    return parts[0], parts[1], nil
}

// For template URIs like user://{id}/profile
func ExtractTemplateParams(uri, template string) (map[string]string, error) {
    // Simple implementation for single parameter
    _, uriPath, err := ParseResourceURI(uri)
    if err != nil {
        return nil, err
    }

    _, templatePath, err := ParseResourceURI(template)
    if err != nil {
        return nil, err
    }

    // Match path segments
    uriParts := strings.Split(uriPath, "/")
    templateParts := strings.Split(templatePath, "/")

    if len(uriParts) != len(templateParts) {
        return nil, fmt.Errorf("path mismatch")
    }

    params := make(map[string]string)
    for i, tp := range templateParts {
        if strings.HasPrefix(tp, "{") && strings.HasSuffix(tp, "}") {
            key := tp[1 : len(tp)-1]
            params[key] = uriParts[i]
        }
    }

    return params, nil
}
```

### Example

```go
s.AddResourceTemplate(template, func(ctx context.Context, req mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
    params, err := ExtractTemplateParams(req.Params.URI, "user://{id}/profile")
    if err != nil {
        return nil, err
    }

    userID := params["id"]
    user, err := getUser(userID)
    if err != nil {
        return nil, fmt.Errorf("user not found: %s", userID)
    }

    return []mcp.ResourceContents{
        mcp.TextResourceContents(req.Params.URI, user.JSON(), "application/json"),
    }, nil
})
```

## Pattern 5: Stateful Server with Concurrency

### When to Use

When your server maintains state (like the notes example) and needs thread safety.

### Implementation

```go
import "sync"

type DataStore struct {
    mu   sync.RWMutex
    data map[string]Item
}

func NewDataStore() *DataStore {
    return &DataStore{
        data: make(map[string]Item),
    }
}

// Read operation - use RLock for concurrent reads
func (s *DataStore) Get(id string) (Item, bool) {
    s.mu.RLock()
    defer s.mu.RUnlock()
    item, ok := s.data[id]
    return item, ok
}

// Write operation - use Lock for exclusive access
func (s *DataStore) Set(id string, item Item) {
    s.mu.Lock()
    defer s.mu.Unlock()
    s.data[id] = item
}

// List operation - return copy to avoid holding lock
func (s *DataStore) List() []Item {
    s.mu.RLock()
    defer s.mu.RUnlock()

    items := make([]Item, 0, len(s.data))
    for _, item := range s.data {
        items = append(items, item)
    }
    return items
}
```

### Pitfalls to Avoid

- Don't hold locks while doing I/O
- Return copies of data, not references
- Use RWMutex when reads outnumber writes

## Anti-Patterns

### Anti-Pattern 1: Panicking on Bad Input

```go
// Bad - panics on missing or wrong type
func handler(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
    name := req.Params.Arguments["name"].(string)  // Panics if nil or wrong type!
    ...
}
```

### Better Approach

```go
// Good - safe extraction with error handling
func handler(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
    name, ok := req.Params.Arguments["name"].(string)
    if !ok || name == "" {
        return mcp.NewToolResultError("name is required"), nil
    }
    ...
}
```

### Anti-Pattern 2: Ignoring Context

```go
// Bad - ignores context, can't be cancelled
func handler(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
    result := verySlowOperation()  // No way to cancel
    return mcp.NewToolResultText(result), nil
}
```

### Better Approach

```go
// Good - respects context
func handler(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
    result, err := verySlowOperationWithContext(ctx)
    if err != nil {
        if ctx.Err() != nil {
            return mcp.NewToolResultError("operation cancelled"), nil
        }
        return mcp.NewToolResultError(err.Error()), nil
    }
    return mcp.NewToolResultText(result), nil
}
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Parameter extraction | Safe Parameter Extraction |
| Complex responses | Structured Tool Responses |
| Long operations | Context-Aware Handlers |
| Resource templates | Resource URI Parsing |
| Stateful servers | Stateful Server with Concurrency |
