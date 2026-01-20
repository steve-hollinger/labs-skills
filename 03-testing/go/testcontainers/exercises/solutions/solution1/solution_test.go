//go:build integration

// Solution for Exercise 1: PostgreSQL Repository Testing
package solution1

import (
	"context"
	"database/sql"
	"testing"
	"time"

	_ "github.com/lib/pq"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/wait"
)

// Domain types
type Product struct {
	ID        int64
	Name      string
	Price     float64
	Quantity  int
	CreatedAt time.Time
}

// Repository - SOLUTION
type ProductRepository struct {
	db *sql.DB
}

func NewProductRepository(db *sql.DB) *ProductRepository {
	return &ProductRepository{db: db}
}

func (r *ProductRepository) CreateTable() error {
	_, err := r.db.Exec(`
		CREATE TABLE IF NOT EXISTS products (
			id SERIAL PRIMARY KEY,
			name VARCHAR(255) NOT NULL,
			price DECIMAL(10,2) NOT NULL,
			quantity INTEGER DEFAULT 0,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
	`)
	return err
}

func (r *ProductRepository) Create(product *Product) error {
	return r.db.QueryRow(
		"INSERT INTO products (name, price, quantity) VALUES ($1, $2, $3) RETURNING id, created_at",
		product.Name, product.Price, product.Quantity,
	).Scan(&product.ID, &product.CreatedAt)
}

func (r *ProductRepository) FindByID(id int64) (*Product, error) {
	product := &Product{}
	err := r.db.QueryRow(
		"SELECT id, name, price, quantity, created_at FROM products WHERE id = $1",
		id,
	).Scan(&product.ID, &product.Name, &product.Price, &product.Quantity, &product.CreatedAt)
	if err != nil {
		return nil, err
	}
	return product, nil
}

func (r *ProductRepository) UpdateQuantity(id int64, quantity int) error {
	_, err := r.db.Exec("UPDATE products SET quantity = $1 WHERE id = $2", quantity, id)
	return err
}

// setupPostgres - SOLUTION
func setupPostgres(ctx context.Context) (testcontainers.Container, *sql.DB, error) {
	container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: testcontainers.ContainerRequest{
			Image:        "postgres:15-alpine",
			ExposedPorts: []string{"5432/tcp"},
			Env: map[string]string{
				"POSTGRES_USER":     "test",
				"POSTGRES_PASSWORD": "test",
				"POSTGRES_DB":       "testdb",
			},
			WaitingFor: wait.ForLog("database system is ready to accept connections").
				WithOccurrence(2).
				WithStartupTimeout(60 * time.Second),
		},
		Started: true,
	})
	if err != nil {
		return nil, nil, err
	}

	host, err := container.Host(ctx)
	if err != nil {
		container.Terminate(ctx)
		return nil, nil, err
	}

	port, err := container.MappedPort(ctx, "5432")
	if err != nil {
		container.Terminate(ctx)
		return nil, nil, err
	}

	dsn := "postgres://test:test@" + host + ":" + port.Port() + "/testdb?sslmode=disable"
	db, err := sql.Open("postgres", dsn)
	if err != nil {
		container.Terminate(ctx)
		return nil, nil, err
	}

	// Wait for connection
	for i := 0; i < 30; i++ {
		if err := db.Ping(); err == nil {
			break
		}
		time.Sleep(time.Second)
	}

	return container, db, nil
}

// Tests - SOLUTION
func TestProductRepository_Create(t *testing.T) {
	ctx := context.Background()

	container, db, err := setupPostgres(ctx)
	require.NoError(t, err)
	defer container.Terminate(ctx)
	defer db.Close()

	repo := NewProductRepository(db)
	err = repo.CreateTable()
	require.NoError(t, err)

	product := &Product{
		Name:     "Widget",
		Price:    9.99,
		Quantity: 100,
	}

	err = repo.Create(product)
	require.NoError(t, err)
	assert.NotZero(t, product.ID)
	assert.NotZero(t, product.CreatedAt)
}

func TestProductRepository_FindByID(t *testing.T) {
	ctx := context.Background()

	container, db, err := setupPostgres(ctx)
	require.NoError(t, err)
	defer container.Terminate(ctx)
	defer db.Close()

	repo := NewProductRepository(db)
	repo.CreateTable()

	// Create a product
	product := &Product{Name: "Gadget", Price: 19.99, Quantity: 50}
	repo.Create(product)

	// Find it
	found, err := repo.FindByID(product.ID)
	require.NoError(t, err)
	assert.Equal(t, product.Name, found.Name)
	assert.Equal(t, product.Price, found.Price)
}

func TestProductRepository_UpdateQuantity(t *testing.T) {
	ctx := context.Background()

	container, db, err := setupPostgres(ctx)
	require.NoError(t, err)
	defer container.Terminate(ctx)
	defer db.Close()

	repo := NewProductRepository(db)
	repo.CreateTable()

	// Create a product
	product := &Product{Name: "Item", Price: 5.00, Quantity: 10}
	repo.Create(product)

	// Update quantity
	err = repo.UpdateQuantity(product.ID, 25)
	require.NoError(t, err)

	// Verify update
	found, err := repo.FindByID(product.ID)
	require.NoError(t, err)
	assert.Equal(t, 25, found.Quantity)
}
