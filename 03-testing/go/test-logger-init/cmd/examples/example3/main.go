// Example 3: Logger Configuration
//
// This example demonstrates logging configuration for tests.
// See tests/example3_test.go for the actual test implementation.
//
// Run with: go test -v -run TestExample3 ./tests/...
package main

import "fmt"

func main() {
	fmt.Println("Example 3: Logger Configuration")
	fmt.Println("===============================")
	fmt.Println()
	fmt.Println("This example demonstrates test logging patterns.")
	fmt.Println("Run the tests to see logging in action:")
	fmt.Println()
	fmt.Println("  go test -v -run TestExample3 ./tests/...")
	fmt.Println()
	fmt.Println("Key concepts demonstrated:")
	fmt.Println("  - Discarding logs in tests")
	fmt.Println("  - Capturing logs for assertions")
	fmt.Println("  - Test-aware logger with t.Log")
	fmt.Println("  - Log level configuration")
}
