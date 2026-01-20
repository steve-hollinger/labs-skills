// Example 1: Basic Assertions
//
// This file demonstrates the testify assert and require packages.
// Since these are testing functions, see tests/example1_test.go for the actual tests.
//
// Run with: go test -v -run TestExample1 ./tests/...
package main

import "fmt"

// User represents a user in the system
type User struct {
	ID        int64
	Name      string
	Email     string
	Active    bool
	Tags      []string
	Metadata  map[string]string
}

// NewUser creates a new user
func NewUser(name, email string) (*User, error) {
	if name == "" {
		return nil, fmt.Errorf("name is required")
	}
	if email == "" {
		return nil, fmt.Errorf("email is required")
	}
	return &User{
		ID:       1,
		Name:     name,
		Email:    email,
		Active:   true,
		Tags:     []string{"new"},
		Metadata: map[string]string{"source": "api"},
	}, nil
}

// Calculator performs basic math operations
type Calculator struct{}

func (c *Calculator) Add(a, b int) int {
	return a + b
}

func (c *Calculator) Divide(a, b int) (int, error) {
	if b == 0 {
		return 0, fmt.Errorf("division by zero")
	}
	return a / b, nil
}

// StringProcessor processes strings
type StringProcessor struct{}

func (p *StringProcessor) Reverse(s string) string {
	runes := []rune(s)
	for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
		runes[i], runes[j] = runes[j], runes[i]
	}
	return string(runes)
}

func (p *StringProcessor) Contains(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}

func main() {
	fmt.Println("Example 1: Basic Assertions")
	fmt.Println("===========================")
	fmt.Println()
	fmt.Println("This example demonstrates testify assert and require packages.")
	fmt.Println("Run the tests to see assertions in action:")
	fmt.Println()
	fmt.Println("  go test -v -run TestExample1 ./tests/...")
	fmt.Println()
	fmt.Println("Key concepts demonstrated:")
	fmt.Println("  - assert.Equal, assert.NotEqual")
	fmt.Println("  - assert.Nil, assert.NotNil")
	fmt.Println("  - assert.True, assert.False")
	fmt.Println("  - assert.Contains, assert.Len")
	fmt.Println("  - assert.Error, assert.NoError")
	fmt.Println("  - require vs assert (stopping vs continuing)")
}
