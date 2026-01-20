// Example 3: Kafka Container
//
// This example demonstrates Kafka container for message queue testing.
// See tests/example3_test.go for the actual test implementation.
//
// Run with: go test -v -tags=integration -run TestExample3 ./tests/...
package main

import "fmt"

func main() {
	fmt.Println("Example 3: Kafka Container")
	fmt.Println("==========================")
	fmt.Println()
	fmt.Println("This example demonstrates Kafka integration testing.")
	fmt.Println("Run the tests to see Testcontainers in action:")
	fmt.Println()
	fmt.Println("  go test -v -tags=integration -run TestExample3 ./tests/...")
	fmt.Println()
	fmt.Println("Requirements:")
	fmt.Println("  - Docker must be running")
	fmt.Println()
	fmt.Println("Key concepts demonstrated:")
	fmt.Println("  - Starting Kafka container")
	fmt.Println("  - Creating topics")
	fmt.Println("  - Producing messages")
	fmt.Println("  - Consuming messages")
	fmt.Println("  - Testing event-driven systems")
}
