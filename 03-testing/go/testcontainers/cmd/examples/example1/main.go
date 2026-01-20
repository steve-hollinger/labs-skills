// Example 1: PostgreSQL Container
//
// This example demonstrates PostgreSQL container setup for integration testing.
// See tests/example1_test.go for the actual test implementation.
//
// Run with: go test -v -tags=integration -run TestExample1 ./tests/...
package main

import "fmt"

func main() {
	fmt.Println("Example 1: PostgreSQL Container")
	fmt.Println("================================")
	fmt.Println()
	fmt.Println("This example demonstrates PostgreSQL integration testing.")
	fmt.Println("Run the tests to see Testcontainers in action:")
	fmt.Println()
	fmt.Println("  go test -v -tags=integration -run TestExample1 ./tests/...")
	fmt.Println()
	fmt.Println("Requirements:")
	fmt.Println("  - Docker must be running")
	fmt.Println()
	fmt.Println("Key concepts demonstrated:")
	fmt.Println("  - Starting PostgreSQL container")
	fmt.Println("  - Wait strategies for database readiness")
	fmt.Println("  - Getting connection strings")
	fmt.Println("  - Running SQL queries against container")
	fmt.Println("  - Proper container cleanup")
}
