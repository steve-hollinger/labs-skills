// Example 2: Resources and Templates
//
// This example demonstrates exposing resources through an MCP server.
// Resources allow AI applications to read data from various sources.
//
// Key concepts:
// - Defining static resources with fixed URIs
// - Creating resource templates with dynamic parameters
// - Listing and reading resources
// - Different MIME types for resources
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
)

// Simulated data stores
var (
	users = map[string]User{
		"1": {ID: "1", Name: "Alice", Email: "alice@example.com", Role: "admin"},
		"2": {ID: "2", Name: "Bob", Email: "bob@example.com", Role: "user"},
		"3": {ID: "3", Name: "Charlie", Email: "charlie@example.com", Role: "user"},
	}

	config = map[string]interface{}{
		"app_name":    "MCP Demo",
		"version":     "1.0.0",
		"environment": "development",
		"features": map[string]bool{
			"dark_mode":   true,
			"beta_access": false,
		},
	}
)

type User struct {
	ID    string `json:"id"`
	Name  string `json:"name"`
	Email string `json:"email"`
	Role  string `json:"role"`
}

func main() {
	// Check if running in demo mode
	if len(os.Args) > 1 && os.Args[1] == "--demo" {
		runDemo()
		return
	}

	// Create server with resource capabilities
	// Second parameter enables resource subscription (we disable it here)
	s := server.NewMCPServer(
		"resource-server",
		"1.0.0",
		server.WithResourceCapabilities(true, false),
	)

	// Add static resources
	addConfigResource(s)
	addSystemInfoResource(s)

	// Add resource templates for dynamic data
	addUserResourceTemplate(s)
	addUserListResource(s)

	fmt.Fprintln(os.Stderr, "Resource Server starting...")
	fmt.Fprintln(os.Stderr, "Available resources:")
	fmt.Fprintln(os.Stderr, "  - config://app/settings")
	fmt.Fprintln(os.Stderr, "  - system://info")
	fmt.Fprintln(os.Stderr, "  - user://list")
	fmt.Fprintln(os.Stderr, "  - user://{id}/profile (template)")
	fmt.Fprintln(os.Stderr, "Listening on stdio...")

	if err := s.ServeStdio(); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}

// addConfigResource adds a static configuration resource
func addConfigResource(s *server.MCPServer) {
	resource := mcp.NewResource(
		"config://app/settings",
		"Application configuration settings",
		mcp.WithResourceDescription("Read-only application configuration"),
		mcp.WithMIMEType("application/json"),
	)

	s.AddResource(resource, func(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
		// Serialize config to JSON
		data, err := json.MarshalIndent(config, "", "  ")
		if err != nil {
			return nil, fmt.Errorf("failed to serialize config: %w", err)
		}

		return []mcp.ResourceContents{
			mcp.TextResourceContents(
				request.Params.URI,
				string(data),
				"application/json",
			),
		}, nil
	})
}

// addSystemInfoResource adds a dynamic system information resource
func addSystemInfoResource(s *server.MCPServer) {
	resource := mcp.NewResource(
		"system://info",
		"Current system information",
		mcp.WithResourceDescription("Real-time system status and information"),
		mcp.WithMIMEType("application/json"),
	)

	s.AddResource(resource, func(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
		info := map[string]interface{}{
			"timestamp":  time.Now().Format(time.RFC3339),
			"go_version": "go1.22",
			"server":     "mcp-server-example",
			"status":     "healthy",
			"uptime":     "running",
			"resources": map[string]int{
				"users":   len(users),
				"configs": 1,
			},
		}

		data, err := json.MarshalIndent(info, "", "  ")
		if err != nil {
			return nil, fmt.Errorf("failed to serialize system info: %w", err)
		}

		return []mcp.ResourceContents{
			mcp.TextResourceContents(
				request.Params.URI,
				string(data),
				"application/json",
			),
		}, nil
	})
}

// addUserResourceTemplate adds a template for accessing individual user profiles
func addUserResourceTemplate(s *server.MCPServer) {
	template := mcp.NewResourceTemplate(
		"user://{id}/profile",
		"User profile by ID",
		mcp.WithTemplateDescription("Retrieve a user's profile by their unique ID"),
		mcp.WithTemplateMIMEType("application/json"),
	)

	s.AddResourceTemplate(template, func(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
		// Extract user ID from URI
		// URI format: user://123/profile
		uri := request.Params.URI
		parts := strings.Split(uri, "://")
		if len(parts) != 2 {
			return nil, fmt.Errorf("invalid URI format: %s", uri)
		}

		pathParts := strings.Split(parts[1], "/")
		if len(pathParts) < 1 {
			return nil, fmt.Errorf("missing user ID in URI: %s", uri)
		}

		userID := pathParts[0]

		// Look up user
		user, exists := users[userID]
		if !exists {
			return nil, fmt.Errorf("user not found: %s", userID)
		}

		// Serialize user to JSON
		data, err := json.MarshalIndent(user, "", "  ")
		if err != nil {
			return nil, fmt.Errorf("failed to serialize user: %w", err)
		}

		return []mcp.ResourceContents{
			mcp.TextResourceContents(
				request.Params.URI,
				string(data),
				"application/json",
			),
		}, nil
	})
}

// addUserListResource adds a resource that lists all users
func addUserListResource(s *server.MCPServer) {
	resource := mcp.NewResource(
		"user://list",
		"List of all users",
		mcp.WithResourceDescription("Get a list of all users in the system"),
		mcp.WithMIMEType("application/json"),
	)

	s.AddResource(resource, func(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
		// Convert map to slice
		userList := make([]User, 0, len(users))
		for _, u := range users {
			userList = append(userList, u)
		}

		// Create response
		response := map[string]interface{}{
			"total": len(userList),
			"users": userList,
		}

		data, err := json.MarshalIndent(response, "", "  ")
		if err != nil {
			return nil, fmt.Errorf("failed to serialize user list: %w", err)
		}

		return []mcp.ResourceContents{
			mcp.TextResourceContents(
				request.Params.URI,
				string(data),
				"application/json",
			),
		}, nil
	})
}

func runDemo() {
	fmt.Println("Example 2: Resources and Templates")
	fmt.Println("=" + strings.Repeat("=", 49))
	fmt.Println()
	fmt.Println("This example demonstrates MCP resources - data that AI can read.")
	fmt.Println()
	fmt.Println("Static Resources:")
	fmt.Println("-----------------")
	fmt.Println("1. config://app/settings")
	fmt.Println("   Application configuration as JSON")
	fmt.Println()
	fmt.Println("2. system://info")
	fmt.Println("   Real-time system information")
	fmt.Println()
	fmt.Println("3. user://list")
	fmt.Println("   List of all users")
	fmt.Println()
	fmt.Println("Resource Templates:")
	fmt.Println("-------------------")
	fmt.Println("1. user://{id}/profile")
	fmt.Println("   Get a specific user's profile by ID")
	fmt.Println("   Example: user://1/profile, user://2/profile")
	fmt.Println()
	fmt.Println("Sample User Data:")
	for id, user := range users {
		fmt.Printf("   user://%s/profile -> %s (%s)\n", id, user.Name, user.Email)
	}
	fmt.Println()
	fmt.Println("Run without --demo flag to start the actual server.")
}
