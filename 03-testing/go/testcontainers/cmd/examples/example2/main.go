// Example 2: DynamoDB Local Container
//
// This example demonstrates DynamoDB Local container for AWS testing.
// See tests/example2_test.go for the actual test implementation.
//
// Run with: go test -v -tags=integration -run TestExample2 ./tests/...
package main

import "fmt"

func main() {
	fmt.Println("Example 2: DynamoDB Local Container")
	fmt.Println("====================================")
	fmt.Println()
	fmt.Println("This example demonstrates DynamoDB Local integration testing.")
	fmt.Println("Run the tests to see Testcontainers in action:")
	fmt.Println()
	fmt.Println("  go test -v -tags=integration -run TestExample2 ./tests/...")
	fmt.Println()
	fmt.Println("Requirements:")
	fmt.Println("  - Docker must be running")
	fmt.Println()
	fmt.Println("Key concepts demonstrated:")
	fmt.Println("  - Starting DynamoDB Local container")
	fmt.Println("  - Configuring AWS SDK for local endpoint")
	fmt.Println("  - Creating tables and items")
	fmt.Println("  - Querying DynamoDB")
}
