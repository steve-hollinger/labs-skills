// Solution for Exercise 1: Assert and Require Practice
package solution1

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Code to test (same as exercise)
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

// Solutions
func TestNewProduct_Success(t *testing.T) {
	product, err := NewProduct("Widget", 9.99)

	// Use require for preconditions
	require.NoError(t, err, "product creation should succeed")
	require.NotNil(t, product, "product should not be nil")

	// Use assert for validations
	assert.Equal(t, "Widget", product.Name, "name should match")
	assert.Equal(t, 9.99, product.Price, "price should match")
	assert.Equal(t, 0, product.Quantity, "quantity should start at 0")
	assert.Empty(t, product.Tags, "tags should start empty")
}

func TestNewProduct_MissingName(t *testing.T) {
	product, err := NewProduct("", 9.99)

	assert.Error(t, err, "should return error for empty name")
	assert.Nil(t, product, "product should be nil on error")
	assert.Contains(t, err.Error(), "name", "error should mention name")
}

func TestNewProduct_NegativePrice(t *testing.T) {
	product, err := NewProduct("Widget", -5.00)

	assert.Error(t, err)
	assert.Nil(t, product)
	assert.Contains(t, err.Error(), "negative")
}

func TestAddStock(t *testing.T) {
	product, err := NewProduct("Widget", 9.99)
	require.NoError(t, err)

	err = product.AddStock(10)

	assert.NoError(t, err)
	assert.Equal(t, 10, product.Quantity)
}

func TestRemoveStock_Success(t *testing.T) {
	product, err := NewProduct("Widget", 9.99)
	require.NoError(t, err)
	require.NoError(t, product.AddStock(10))

	err = product.RemoveStock(3)

	assert.NoError(t, err)
	assert.Equal(t, 7, product.Quantity)
}

func TestRemoveStock_InsufficientStock(t *testing.T) {
	product, err := NewProduct("Widget", 9.99)
	require.NoError(t, err)
	require.NoError(t, product.AddStock(5))

	err = product.RemoveStock(10)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "insufficient")
	assert.Equal(t, 5, product.Quantity, "quantity should be unchanged")
}

func TestAddTag(t *testing.T) {
	product, err := NewProduct("Widget", 9.99)
	require.NoError(t, err)

	product.AddTag("sale")
	product.AddTag("featured")

	assert.Contains(t, product.Tags, "sale")
	assert.Contains(t, product.Tags, "featured")
	assert.Len(t, product.Tags, 2)
}

func TestTotalValue(t *testing.T) {
	product, err := NewProduct("Widget", 10.00)
	require.NoError(t, err)
	require.NoError(t, product.AddStock(5))

	total := product.TotalValue()

	assert.Equal(t, 50.00, total)
}

func TestProduct_TableDriven(t *testing.T) {
	tests := []struct {
		name      string
		prodName  string
		price     float64
		wantErr   bool
		errSubstr string
	}{
		{
			name:     "valid product",
			prodName: "Widget",
			price:    9.99,
			wantErr:  false,
		},
		{
			name:      "empty name",
			prodName:  "",
			price:     9.99,
			wantErr:   true,
			errSubstr: "name",
		},
		{
			name:      "negative price",
			prodName:  "Widget",
			price:     -5.00,
			wantErr:   true,
			errSubstr: "negative",
		},
		{
			name:     "zero price (free product)",
			prodName: "Widget",
			price:    0,
			wantErr:  false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			product, err := NewProduct(tt.prodName, tt.price)

			if tt.wantErr {
				require.Error(t, err)
				assert.Contains(t, err.Error(), tt.errSubstr)
				assert.Nil(t, product)
			} else {
				require.NoError(t, err)
				require.NotNil(t, product)
				assert.Equal(t, tt.prodName, product.Name)
				assert.Equal(t, tt.price, product.Price)
			}
		})
	}
}
