// Example 1: Basic Linting Setup
//
// This example demonstrates the fundamental usage of golangci-lint,
// showing how to identify and understand common linting issues.
package main

import (
	"fmt"
	"os"
)

func main() {
	fmt.Println("Example 1: Basic Linting Setup")
	fmt.Println("========================================")
	fmt.Println()

	// Demonstrate code that passes linting
	demonstrateGoodCode()

	// Show common issues that linters catch
	demonstrateLintingIssues()

	fmt.Println("\nExample completed successfully!")
}

// demonstrateGoodCode shows properly written Go code
func demonstrateGoodCode() {
	fmt.Println("=== Good Code Examples ===")
	fmt.Println()

	// Good: Always handle errors
	file, err := os.Open("example.txt")
	if err != nil {
		fmt.Printf("  Error opening file (expected): %v\n", err)
	} else {
		// Good: Always close resources
		defer func() {
			if err := file.Close(); err != nil {
				fmt.Printf("  Error closing file: %v\n", err)
			}
		}()
		fmt.Println("  File opened successfully")
	}

	// Good: Use meaningful variable names
	userCount := 42
	fmt.Printf("  User count: %d\n", userCount)

	// Good: Check type assertions
	var data interface{} = "hello"
	str, ok := data.(string)
	if ok {
		fmt.Printf("  Type assertion succeeded: %s\n", str)
	}
}

// demonstrateLintingIssues shows code patterns that linters catch
// Note: These are EXAMPLES of issues - actual code should not have these!
func demonstrateLintingIssues() {
	fmt.Println()
	fmt.Println("=== Common Linting Issues (Explained) ===")
	fmt.Println()

	// Issue 1: Unchecked errors (caught by errcheck)
	fmt.Println("1. ERRCHECK: Unchecked error returns")
	fmt.Println("   Bad:  os.Remove(\"file.txt\")")
	fmt.Println("   Good: err := os.Remove(\"file.txt\")")
	fmt.Println("         if err != nil { /* handle */ }")
	fmt.Println()

	// Issue 2: Shadow variables (caught by govet with shadow check)
	fmt.Println("2. GOVET SHADOW: Variable shadowing")
	fmt.Println("   Bad:  err := foo()")
	fmt.Println("         if condition {")
	fmt.Println("             err := bar() // shadows outer err!")
	fmt.Println("         }")
	fmt.Println("   Good: Use = instead of := for existing variables")
	fmt.Println()

	// Issue 3: Ineffectual assignment (caught by ineffassign)
	fmt.Println("3. INEFFASSIGN: Ineffectual assignment")
	fmt.Println("   Bad:  x := 5")
	fmt.Println("         x = 10 // previous value never used")
	fmt.Println("   Good: Only assign when value will be used")
	fmt.Println()

	// Issue 4: Unused code (caught by unused/deadcode)
	fmt.Println("4. UNUSED: Unused variables/functions")
	fmt.Println("   Bad:  func unusedHelper() { /* never called */ }")
	fmt.Println("   Good: Remove unused code or mark with _ prefix")
	fmt.Println()

	// Issue 5: Simplification opportunities (caught by gosimple)
	fmt.Println("5. GOSIMPLE: Code that can be simplified")
	fmt.Println("   Bad:  if x == true { ... }")
	fmt.Println("   Good: if x { ... }")
	fmt.Println()

	// Issue 6: Printf format issues (caught by govet)
	fmt.Println("6. GOVET PRINTF: Format string mismatches")
	fmt.Println("   Bad:  fmt.Printf(\"%d\", \"string\")")
	fmt.Println("   Good: fmt.Printf(\"%s\", \"string\")")
	fmt.Println()

	// Demonstrate running golangci-lint
	fmt.Println("=== How to Run golangci-lint ===")
	fmt.Println()
	fmt.Println("# Check current directory")
	fmt.Println("$ golangci-lint run")
	fmt.Println()
	fmt.Println("# Check specific files")
	fmt.Println("$ golangci-lint run ./path/to/file.go")
	fmt.Println()
	fmt.Println("# Show only specific linters")
	fmt.Println("$ golangci-lint run --enable=errcheck,govet")
	fmt.Println()
	fmt.Println("# Show available linters")
	fmt.Println("$ golangci-lint linters")
}
