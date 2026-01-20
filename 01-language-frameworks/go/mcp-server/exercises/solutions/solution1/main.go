// Solution for Exercise 1: Calculator Tool with Multiple Operations
//
// This solution implements a full-featured calculator MCP server.

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

type Calculation struct {
	Operation string
	A         float64
	B         float64
	Result    float64
}

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

	addCalculateTool(s)
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
		// Extract operation
		operation, ok := req.Params.Arguments["operation"].(string)
		if !ok {
			return mcp.NewToolResultError("operation is required"), nil
		}

		// Extract first operand
		a, ok := req.Params.Arguments["a"].(float64)
		if !ok {
			return mcp.NewToolResultError("a is required and must be a number"), nil
		}

		// Extract second operand (may not be present for sqrt)
		var b float64
		if bVal, ok := req.Params.Arguments["b"].(float64); ok {
			b = bVal
		} else if needsSecondOperand(operation) {
			return mcp.NewToolResultError(fmt.Sprintf("operation '%s' requires parameter b", operation)), nil
		}

		// Perform calculation
		var result float64
		var resultStr string

		switch operation {
		case "add":
			result = a + b
			resultStr = fmt.Sprintf("%.4g + %.4g = %.4g", a, b, result)

		case "subtract":
			result = a - b
			resultStr = fmt.Sprintf("%.4g - %.4g = %.4g", a, b, result)

		case "multiply":
			result = a * b
			resultStr = fmt.Sprintf("%.4g * %.4g = %.4g", a, b, result)

		case "divide":
			if b == 0 {
				return mcp.NewToolResultError("cannot divide by zero"), nil
			}
			result = a / b
			resultStr = fmt.Sprintf("%.4g / %.4g = %.4g", a, b, result)

		case "power":
			result = math.Pow(a, b)
			if math.IsInf(result, 0) || math.IsNaN(result) {
				return mcp.NewToolResultError("result is too large or undefined"), nil
			}
			resultStr = fmt.Sprintf("%.4g ^ %.4g = %.4g", a, b, result)

		case "sqrt":
			if a < 0 {
				return mcp.NewToolResultError("cannot compute square root of negative number"), nil
			}
			result = math.Sqrt(a)
			resultStr = fmt.Sprintf("sqrt(%.4g) = %.4g", a, result)

		case "modulo":
			if b == 0 {
				return mcp.NewToolResultError("cannot compute modulo with zero"), nil
			}
			result = math.Mod(a, b)
			resultStr = fmt.Sprintf("%.4g mod %.4g = %.4g", a, b, result)

		default:
			return mcp.NewToolResultError(
				fmt.Sprintf("unknown operation: %s. Supported: add, subtract, multiply, divide, power, sqrt, modulo", operation),
			), nil
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
		calculations := history.GetAll()

		if len(calculations) == 0 {
			return mcp.NewToolResultText("No calculations in history."), nil
		}

		result := fmt.Sprintf("History (%d calculations):\n", len(calculations))
		result += "─────────────────────────────────\n"

		for i, calc := range calculations {
			var line string
			if calc.Operation == "sqrt" {
				line = fmt.Sprintf("%d. sqrt(%.4g) = %.4g", i+1, calc.A, calc.Result)
			} else {
				opSymbol := operationSymbol(calc.Operation)
				line = fmt.Sprintf("%d. %.4g %s %.4g = %.4g", i+1, calc.A, opSymbol, calc.B, calc.Result)
			}
			result += line + "\n"
		}

		return mcp.NewToolResultText(result), nil
	})
}

func needsSecondOperand(operation string) bool {
	return operation != "sqrt"
}

func operationSymbol(operation string) string {
	switch operation {
	case "add":
		return "+"
	case "subtract":
		return "-"
	case "multiply":
		return "*"
	case "divide":
		return "/"
	case "power":
		return "^"
	case "modulo":
		return "mod"
	default:
		return "?"
	}
}
