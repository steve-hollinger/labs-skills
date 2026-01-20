//go:build integration

// Exercise 1: PostgreSQL Repository Testing
//
// In this exercise, you will test a product repository using PostgreSQL.
//
// Instructions:
// 1. Complete the setupPostgres function to start a container
// 2. Implement the ProductRepository methods
// 3. Write tests using the container
// 4. Run with: go test -v -tags=integration ./exercises/exercise1/...
//
// Requirements:
// - Docker must be running
//
// Expected: All tests should pass when completed correctly
package exercise1

import (
	"context"
	"database/sql"
	"testing"
	"time"

	_ "github.com/lib/pq"
	"github.com/testcontainers/testcontainers-go"
)

// ============================================================================
// Domain types
// ============================================================================

type Product struct {
	ID        int64
	Name      string
	Price     float64
	Quantity  int
	CreatedAt time.Time
}

// ============================================================================
// Repository to implement
// ============================================================================

type ProductRepository struct {
	db *sql.DB
}

func NewProductRepository(db *sql.DB) *ProductRepository {
	return &ProductRepository{db: db}
}

// CreateTable creates the products table
// TODO: Implement this
func (r *ProductRepository) CreateTable() error {
	// Create a products table with:
	// - id: SERIAL PRIMARY KEY
	// - name: VARCHAR(255) NOT NULL
	// - price: DECIMAL(10,2) NOT NULL
	// - quantity: INTEGER DEFAULT 0
	// - created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	return nil
}

// Create inserts a new product
// TODO: Implement this
func (r *ProductRepository) Create(product *Product) error {
	// Insert the product and set the ID and CreatedAt fields
	return nil
}

// FindByID retrieves a product by ID
// TODO: Implement this
func (r *ProductRepository) FindByID(id int64) (*Product, error) {
	// Query the product by ID
	return nil, nil
}

// UpdateQuantity updates product quantity
// TODO: Implement this
func (r *ProductRepository) UpdateQuantity(id int64, quantity int) error {
	// Update the quantity for the given product ID
	return nil
}

// ============================================================================
// Test setup - TODO: Complete this
// ============================================================================

// setupPostgres starts a PostgreSQL container and returns a connection
// TODO: Implement this function
func setupPostgres(ctx context.Context) (testcontainers.Container, *sql.DB, error) {
	// 1. Create a container request for postgres:15-alpine
	// 2. Set environment variables for POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
	// 3. Expose port 5432
	// 4. Use wait.ForLog to wait for "database system is ready to accept connections"
	// 5. Start the container
	// 6. Get the host and mapped port
	// 7. Create connection string and open database connection
	// 8. Return container and db

	return nil, nil, nil
}

// ============================================================================
// Tests - TODO: Uncomment and complete after implementing above
// ============================================================================

func TestProductRepository_Create(t *testing.T) {
	// TODO: Uncomment after implementing setupPostgres
	//
	// ctx := context.Background()
	//
	// container, db, err := setupPostgres(ctx)
	// require.NoError(t, err)
	// defer container.Terminate(ctx)
	// defer db.Close()
	//
	// repo := NewProductRepository(db)
	// err = repo.CreateTable()
	// require.NoError(t, err)
	//
	// product := &Product{
	//     Name:     "Widget",
	//     Price:    9.99,
	//     Quantity: 100,
	// }
	//
	// err = repo.Create(product)
	// require.NoError(t, err)
	// assert.NotZero(t, product.ID)
	// assert.NotZero(t, product.CreatedAt)
}

func TestProductRepository_FindByID(t *testing.T) {
	// TODO: Uncomment after implementing
	//
	// ctx := context.Background()
	//
	// container, db, err := setupPostgres(ctx)
	// require.NoError(t, err)
	// defer container.Terminate(ctx)
	// defer db.Close()
	//
	// repo := NewProductRepository(db)
	// repo.CreateTable()
	//
	// // Create a product
	// product := &Product{Name: "Gadget", Price: 19.99, Quantity: 50}
	// repo.Create(product)
	//
	// // Find it
	// found, err := repo.FindByID(product.ID)
	// require.NoError(t, err)
	// assert.Equal(t, product.Name, found.Name)
	// assert.Equal(t, product.Price, found.Price)
}

func TestProductRepository_UpdateQuantity(t *testing.T) {
	// TODO: Uncomment after implementing
	//
	// ctx := context.Background()
	//
	// container, db, err := setupPostgres(ctx)
	// require.NoError(t, err)
	// defer container.Terminate(ctx)
	// defer db.Close()
	//
	// repo := NewProductRepository(db)
	// repo.CreateTable()
	//
	// // Create a product
	// product := &Product{Name: "Item", Price: 5.00, Quantity: 10}
	// repo.Create(product)
	//
	// // Update quantity
	// err = repo.UpdateQuantity(product.ID, 25)
	// require.NoError(t, err)
	//
	// // Verify update
	// found, err := repo.FindByID(product.ID)
	// require.NoError(t, err)
	// assert.Equal(t, 25, found.Quantity)
}
