// Example 1: TestMain Basics
//
// This example demonstrates TestMain for package-level setup and teardown.
// See tests/example1_test.go for the actual test implementation.
//
// Run with: go test -v -run TestExample1 ./tests/...
package main

import "fmt"

func main() {
	fmt.Println("Example 1: TestMain Basics")
	fmt.Println("==========================")
	fmt.Println()
	fmt.Println("This example demonstrates TestMain for setup/teardown.")
	fmt.Println("Run the tests to see TestMain in action:")
	fmt.Println()
	fmt.Println("  go test -v -run TestExample1 ./tests/...")
	fmt.Println()
	fmt.Println("Key concepts demonstrated:")
	fmt.Println("  - TestMain function signature")
	fmt.Println("  - Setup before all tests")
	fmt.Println("  - Teardown after all tests")
	fmt.Println("  - Proper use of os.Exit(m.Run())")
	fmt.Println("  - Package-level test resources")
}
