// Example 2: Test Fixtures
//
// This example demonstrates creating and using test fixtures.
// See tests/example2_test.go for the actual test implementation.
//
// Run with: go test -v -run TestExample2 ./tests/...
package main

import "fmt"

func main() {
	fmt.Println("Example 2: Test Fixtures")
	fmt.Println("========================")
	fmt.Println()
	fmt.Println("This example demonstrates test fixture patterns.")
	fmt.Println("Run the tests to see fixtures in action:")
	fmt.Println()
	fmt.Println("  go test -v -run TestExample2 ./tests/...")
	fmt.Println()
	fmt.Println("Key concepts demonstrated:")
	fmt.Println("  - Simple fixture structs")
	fmt.Println("  - Builder pattern for fixtures")
	fmt.Println("  - Fixture factory pattern")
	fmt.Println("  - Database fixtures with cleanup")
}
