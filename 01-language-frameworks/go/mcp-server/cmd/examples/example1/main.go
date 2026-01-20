// Example 1: Basic Tool Server
//
// This example demonstrates creating a minimal MCP server with simple tools.
// The server exposes two tools: a greeting tool and a calculator tool.
//
// Key concepts:
// - Creating an MCP server with tool capabilities
// - Defining tools with typed parameters
// - Implementing tool handlers
// - Running the server over stdio
package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
)

func main() {
	// Check if running in demo mode (for non-interactive testing)
	if len(os.Args) > 1 && os.Args[1] == "--demo" {
		runDemo()
		return
	}

	// Create a new MCP server with tool capabilities
	s := server.NewMCPServer(
		"basic-tool-server",
		"1.0.0",
		server.WithToolCapabilities(true),
	)

	// Add the greeting tool
	addGreetingTool(s)

	// Add the calculator tool
	addCalculatorTool(s)

	// Add a string utility tool
	addStringTool(s)

	fmt.Fprintln(os.Stderr, "Basic Tool Server starting...")
	fmt.Fprintln(os.Stderr, "Available tools: greet, calculate, string_util")
	fmt.Fprintln(os.Stderr, "Listening on stdio...")

	// Serve over stdio (standard way for MCP servers)
	if err := s.ServeStdio(); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}

// addGreetingTool adds a simple greeting tool to the server
func addGreetingTool(s *server.MCPServer) {
	// Define the tool with its schema
	greetTool := mcp.NewTool("greet",
		mcp.WithDescription("Greet someone by name"),
		mcp.WithString("name",
			mcp.Required(),
			mcp.Description("The name of the person to greet"),
		),
		mcp.WithString("style",
			mcp.Description("Greeting style: formal, casual, or enthusiastic"),
			mcp.DefaultString("casual"),
		),
	)

	// Add the tool with its handler
	s.AddTool(greetTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		// Extract parameters with type checking
		name, ok := request.Params.Arguments["name"].(string)
		if !ok || name == "" {
			return mcp.NewToolResultError("name is required and must be a string"), nil
		}

		style := "casual"
		if s, ok := request.Params.Arguments["style"].(string); ok {
			style = s
		}

		// Generate greeting based on style
		var greeting string
		switch style {
		case "formal":
			greeting = fmt.Sprintf("Good day, %s. It is a pleasure to make your acquaintance.", name)
		case "enthusiastic":
			greeting = fmt.Sprintf("Hey %s! So awesome to meet you! 🎉", name)
		default:
			greeting = fmt.Sprintf("Hello, %s! Nice to meet you.", name)
		}

		return mcp.NewToolResultText(greeting), nil
	})
}

// addCalculatorTool adds a calculator tool to the server
func addCalculatorTool(s *server.MCPServer) {
	calcTool := mcp.NewTool("calculate",
		mcp.WithDescription("Perform arithmetic calculations"),
		mcp.WithString("operation",
			mcp.Required(),
			mcp.Description("The operation to perform: add, subtract, multiply, divide"),
		),
		mcp.WithNumber("a",
			mcp.Required(),
			mcp.Description("First operand"),
		),
		mcp.WithNumber("b",
			mcp.Required(),
			mcp.Description("Second operand"),
		),
	)

	s.AddTool(calcTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		// Extract parameters
		operation, ok := request.Params.Arguments["operation"].(string)
		if !ok {
			return mcp.NewToolResultError("operation is required"), nil
		}

		a, ok := request.Params.Arguments["a"].(float64)
		if !ok {
			return mcp.NewToolResultError("a must be a number"), nil
		}

		b, ok := request.Params.Arguments["b"].(float64)
		if !ok {
			return mcp.NewToolResultError("b must be a number"), nil
		}

		// Perform calculation
		var result float64
		var opSymbol string

		switch operation {
		case "add":
			result = a + b
			opSymbol = "+"
		case "subtract":
			result = a - b
			opSymbol = "-"
		case "multiply":
			result = a * b
			opSymbol = "*"
		case "divide":
			if b == 0 {
				return mcp.NewToolResultError("division by zero"), nil
			}
			result = a / b
			opSymbol = "/"
		default:
			return mcp.NewToolResultError(
				fmt.Sprintf("unknown operation: %s. Use: add, subtract, multiply, divide", operation),
			), nil
		}

		response := fmt.Sprintf("%.2f %s %.2f = %.2f", a, opSymbol, b, result)
		return mcp.NewToolResultText(response), nil
	})
}

// addStringTool adds a string utility tool
func addStringTool(s *server.MCPServer) {
	stringTool := mcp.NewTool("string_util",
		mcp.WithDescription("Perform string operations"),
		mcp.WithString("text",
			mcp.Required(),
			mcp.Description("The text to process"),
		),
		mcp.WithString("operation",
			mcp.Required(),
			mcp.Description("Operation: uppercase, lowercase, reverse, length"),
		),
	)

	s.AddTool(stringTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		text, ok := request.Params.Arguments["text"].(string)
		if !ok {
			return mcp.NewToolResultError("text is required"), nil
		}

		operation, ok := request.Params.Arguments["operation"].(string)
		if !ok {
			return mcp.NewToolResultError("operation is required"), nil
		}

		var result string
		switch operation {
		case "uppercase":
			result = strings.ToUpper(text)
		case "lowercase":
			result = strings.ToLower(text)
		case "reverse":
			runes := []rune(text)
			for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
				runes[i], runes[j] = runes[j], runes[i]
			}
			result = string(runes)
		case "length":
			result = fmt.Sprintf("Length: %d characters", len(text))
		default:
			return mcp.NewToolResultError(
				fmt.Sprintf("unknown operation: %s. Use: uppercase, lowercase, reverse, length", operation),
			), nil
		}

		return mcp.NewToolResultText(result), nil
	})
}

// runDemo runs a demonstration of the server functionality
func runDemo() {
	fmt.Println("Example 1: Basic Tool Server")
	fmt.Println("=" + strings.Repeat("=", 49))
	fmt.Println()
	fmt.Println("This example demonstrates a basic MCP server with three tools:")
	fmt.Println()
	fmt.Println("1. greet - Greet someone with different styles")
	fmt.Println("   Parameters:")
	fmt.Println("   - name (required): The person's name")
	fmt.Println("   - style (optional): formal, casual, or enthusiastic")
	fmt.Println()
	fmt.Println("2. calculate - Perform arithmetic operations")
	fmt.Println("   Parameters:")
	fmt.Println("   - operation (required): add, subtract, multiply, divide")
	fmt.Println("   - a (required): First number")
	fmt.Println("   - b (required): Second number")
	fmt.Println()
	fmt.Println("3. string_util - String manipulation")
	fmt.Println("   Parameters:")
	fmt.Println("   - text (required): Text to process")
	fmt.Println("   - operation (required): uppercase, lowercase, reverse, length")
	fmt.Println()
	fmt.Println("To use this server with Claude Desktop, add to your config:")
	fmt.Println(`{
  "mcpServers": {
    "basic-tools": {
      "command": "go",
      "args": ["run", "./cmd/examples/example1/main.go"]
    }
  }
}`)
	fmt.Println()
	fmt.Println("Run without --demo flag to start the actual server.")
}
