// Exercise 1: Assert and Require Practice
//
// In this exercise, you will write tests for the provided functions using
// testify's assert and require packages.
//
// Instructions:
// 1. Complete the TODO sections in each test function
// 2. Use require for preconditions that could cause panics
// 3. Use assert for actual test validations
// 4. Run with: go test -v ./exercises/exercise1/...
//
// Expected: All tests should pass when completed correctly
package exercise1

import (
	"errors"
	"testing"
)

// ============================================================================
// Code to test
// ============================================================================

type Product struct {
	ID       int64
	Name     string
	Price    float64
	Quantity int
	Tags     []string
}

func NewProduct(name string, price float64) (*Product, error) {
	if name == "" {
		return nil, errors.New("name is required")
	}
	if price < 0 {
		return nil, errors.New("price cannot be negative")
	}
	return &Product{
		ID:       1,
		Name:     name,
		Price:    price,
		Quantity: 0,
		Tags:     []string{},
	}, nil
}

func (p *Product) AddStock(quantity int) error {
	if quantity < 0 {
		return errors.New("quantity cannot be negative")
	}
	p.Quantity += quantity
	return nil
}

func (p *Product) RemoveStock(quantity int) error {
	if quantity < 0 {
		return errors.New("quantity cannot be negative")
	}
	if quantity > p.Quantity {
		return errors.New("insufficient stock")
	}
	p.Quantity -= quantity
	return nil
}

func (p *Product) AddTag(tag string) {
	if tag != "" {
		p.Tags = append(p.Tags, tag)
	}
}

func (p *Product) TotalValue() float64 {
	return p.Price * float64(p.Quantity)
}

// ============================================================================
// Tests to complete
// ============================================================================

func TestNewProduct_Success(t *testing.T) {
	// TODO: Create a product with name "Widget" and price 9.99
	// Use require for error check and nil check
	// Use assert to verify name and price
	// Use assert to verify quantity starts at 0
	// Use assert to verify tags starts empty

	// Your code here:
	// product, err := NewProduct(...)
	// require.NoError(...)
	// require.NotNil(...)
	// assert.Equal(...)
}

func TestNewProduct_MissingName(t *testing.T) {
	// TODO: Test that creating a product with empty name returns an error
	// Use assert to verify error is returned
	// Use assert to verify product is nil
	// Use assert to verify error message contains "name"

	// Your code here:
}

func TestNewProduct_NegativePrice(t *testing.T) {
	// TODO: Test that creating a product with negative price returns an error
	// Verify error contains "negative"

	// Your code here:
}

func TestAddStock(t *testing.T) {
	// TODO: Create a product, add stock of 10, verify quantity
	// Use require for initial product creation
	// Use assert for the addstock result and quantity check

	// Your code here:
}

func TestRemoveStock_Success(t *testing.T) {
	// TODO: Create a product, add 10 stock, remove 3, verify 7 remaining

	// Your code here:
}

func TestRemoveStock_InsufficientStock(t *testing.T) {
	// TODO: Create a product with 5 stock, try to remove 10
	// Verify error is returned with "insufficient" message
	// Verify quantity is unchanged (still 5)

	// Your code here:
}

func TestAddTag(t *testing.T) {
	// TODO: Create a product, add tags "sale" and "featured"
	// Use assert.Contains to verify each tag is present
	// Use assert.Len to verify count

	// Your code here:
}

func TestTotalValue(t *testing.T) {
	// TODO: Create product at $10.00, add 5 stock
	// Verify total value is 50.00
	// Use assert.Equal for float comparison

	// Your code here:
}

// Table-driven test
func TestProduct_TableDriven(t *testing.T) {
	// TODO: Complete the table-driven test for NewProduct
	tests := []struct {
		name      string
		prodName  string
		price     float64
		wantErr   bool
		errSubstr string
	}{
		// TODO: Add test cases:
		// 1. "valid product" - name "Widget", price 9.99, no error
		// 2. "empty name" - name "", price 9.99, error with "name"
		// 3. "negative price" - name "Widget", price -5.00, error with "negative"
		// 4. "zero price" - name "Widget", price 0, no error (free products allowed)
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// TODO: Implement the test logic
			// Call NewProduct with tt.prodName and tt.price
			// If tt.wantErr, use assert.Error and assert.Contains
			// If !tt.wantErr, use assert.NoError and verify the product

			_ = tt // Remove this when implementing
		})
	}
}
