// Exercise 1: Create a Calculator Tool with Multiple Operations
//
// Build an MCP server with a calculator tool that supports:
// - Basic operations: add, subtract, multiply, divide
// - Advanced operations: power, sqrt, modulo
// - A history feature that tracks recent calculations
//
// Instructions:
// 1. Complete the calculator tool handler
// 2. Add proper input validation
// 3. Handle edge cases (division by zero, negative sqrt, etc.)
// 4. Implement the get_history tool to retrieve recent calculations
//
// Expected behavior:
// - calculate(operation: "add", a: 5, b: 3) -> "5 + 3 = 8"
// - calculate(operation: "sqrt", a: 16) -> "sqrt(16) = 4"
// - get_history() -> list of recent calculations
//
// Hints:
// - Use math.Sqrt and math.Pow from the math package
// - Store calculations in a slice with a max size
// - Remember that JSON numbers are float64

package main

import (
	"context"
	"fmt"
	"log"
	"math"
	"os"
	"sync"

	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
)

// Calculation represents a single calculation
type Calculation struct {
	Operation string
	A         float64
	B         float64
	Result    float64
}

// History stores recent calculations
type History struct {
	mu           sync.Mutex
	calculations []Calculation
	maxSize      int
}

func NewHistory(maxSize int) *History {
	return &History{
		calculations: make([]Calculation, 0),
		maxSize:      maxSize,
	}
}

func (h *History) Add(calc Calculation) {
	h.mu.Lock()
	defer h.mu.Unlock()

	h.calculations = append(h.calculations, calc)
	if len(h.calculations) > h.maxSize {
		h.calculations = h.calculations[1:]
	}
}

func (h *History) GetAll() []Calculation {
	h.mu.Lock()
	defer h.mu.Unlock()

	result := make([]Calculation, len(h.calculations))
	copy(result, h.calculations)
	return result
}

var history = NewHistory(10)

func main() {
	s := server.NewMCPServer(
		"calculator-server",
		"1.0.0",
		server.WithToolCapabilities(true),
	)

	// Add the calculate tool
	addCalculateTool(s)

	// Add the get_history tool
	addGetHistoryTool(s)

	fmt.Fprintln(os.Stderr, "Calculator Server starting...")
	fmt.Fprintln(os.Stderr, "Tools: calculate, get_history")

	if err := s.ServeStdio(); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}

func addCalculateTool(s *server.MCPServer) {
	tool := mcp.NewTool("calculate",
		mcp.WithDescription("Perform a calculation"),
		mcp.WithString("operation",
			mcp.Required(),
			mcp.Description("Operation: add, subtract, multiply, divide, power, sqrt, modulo"),
		),
		mcp.WithNumber("a",
			mcp.Required(),
			mcp.Description("First operand (or only operand for sqrt)"),
		),
		mcp.WithNumber("b",
			mcp.Description("Second operand (not needed for sqrt)"),
		),
	)

	s.AddTool(tool, func(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		// TODO: Implement the calculator handler
		// 1. Extract operation, a, and b from request arguments
		// 2. Validate inputs (check required fields, handle missing b for some ops)
		// 3. Perform the calculation
		// 4. Handle errors (division by zero, negative sqrt, etc.)
		// 5. Add to history
		// 6. Return formatted result

		operation, ok := req.Params.Arguments["operation"].(string)
		if !ok {
			return mcp.NewToolResultError("operation is required"), nil
		}

		a, ok := req.Params.Arguments["a"].(float64)
		if !ok {
			return mcp.NewToolResultError("a is required and must be a number"), nil
		}

		// TODO: Handle b (some operations need it, some don't)
		var b float64
		if bVal, ok := req.Params.Arguments["b"].(float64); ok {
			b = bVal
		}

		// TODO: Implement the operations
		var result float64
		var resultStr string

		switch operation {
		case "add":
			// TODO: Implement
			result = 0
			resultStr = fmt.Sprintf("%.2f + %.2f = %.2f", a, b, result)
		case "subtract":
			// TODO: Implement
			result = 0
			resultStr = fmt.Sprintf("%.2f - %.2f = %.2f", a, b, result)
		case "multiply":
			// TODO: Implement
			result = 0
			resultStr = fmt.Sprintf("%.2f * %.2f = %.2f", a, b, result)
		case "divide":
			// TODO: Implement (handle division by zero!)
			result = 0
			resultStr = fmt.Sprintf("%.2f / %.2f = %.2f", a, b, result)
		case "power":
			// TODO: Implement using math.Pow
			result = 0
			resultStr = fmt.Sprintf("%.2f ^ %.2f = %.2f", a, b, result)
		case "sqrt":
			// TODO: Implement using math.Sqrt (handle negative numbers!)
			result = 0
			resultStr = fmt.Sprintf("sqrt(%.2f) = %.2f", a, result)
		case "modulo":
			// TODO: Implement (handle division by zero!)
			result = 0
			resultStr = fmt.Sprintf("%.2f mod %.2f = %.2f", a, b, result)
		default:
			return mcp.NewToolResultError(fmt.Sprintf("unknown operation: %s", operation)), nil
		}

		// Add to history
		history.Add(Calculation{
			Operation: operation,
			A:         a,
			B:         b,
			Result:    result,
		})

		return mcp.NewToolResultText(resultStr), nil
	})
}

func addGetHistoryTool(s *server.MCPServer) {
	tool := mcp.NewTool("get_history",
		mcp.WithDescription("Get the history of recent calculations"),
	)

	s.AddTool(tool, func(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		// TODO: Implement get_history
		// Return a formatted list of recent calculations

		calculations := history.GetAll()
		if len(calculations) == 0 {
			return mcp.NewToolResultText("No calculations in history."), nil
		}

		// TODO: Format the calculations as a nice string
		result := "History of calculations:\n"
		for i, calc := range calculations {
			_ = i
			_ = calc
			// TODO: Format each calculation
		}

		return mcp.NewToolResultText(result), nil
	})
}

// Helper function to check if b is required for an operation
func needsSecondOperand(operation string) bool {
	return operation != "sqrt"
}
