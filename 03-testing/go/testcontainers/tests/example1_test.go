//go:build integration

package tests

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

// ============================================================================
// Example 1: PostgreSQL Container
// ============================================================================

// User represents a user in the database
type User struct {
	ID        int64
	Name      string
	Email     string
	CreatedAt time.Time
}

// UserRepository handles user data access
type UserRepository struct {
	db *sql.DB
}

func NewUserRepository(db *sql.DB) *UserRepository {
	return &UserRepository{db: db}
}

func (r *UserRepository) CreateTable() error {
	_, err := r.db.Exec(`
		CREATE TABLE IF NOT EXISTS users (
			id SERIAL PRIMARY KEY,
			name VARCHAR(255) NOT NULL,
			email VARCHAR(255) UNIQUE NOT NULL,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
	`)
	return err
}

func (r *UserRepository) Create(user *User) error {
	return r.db.QueryRow(
		"INSERT INTO users (name, email) VALUES ($1, $2) RETURNING id, created_at",
		user.Name, user.Email,
	).Scan(&user.ID, &user.CreatedAt)
}

func (r *UserRepository) FindByEmail(email string) (*User, error) {
	user := &User{}
	err := r.db.QueryRow(
		"SELECT id, name, email, created_at FROM users WHERE email = $1",
		email,
	).Scan(&user.ID, &user.Name, &user.Email, &user.CreatedAt)
	if err != nil {
		return nil, err
	}
	return user, nil
}

func (r *UserRepository) FindAll() ([]*User, error) {
	rows, err := r.db.Query("SELECT id, name, email, created_at FROM users")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var users []*User
	for rows.Next() {
		user := &User{}
		if err := rows.Scan(&user.ID, &user.Name, &user.Email, &user.CreatedAt); err != nil {
			return nil, err
		}
		users = append(users, user)
	}
	return users, nil
}

func (r *UserRepository) Delete(id int64) error {
	_, err := r.db.Exec("DELETE FROM users WHERE id = $1", id)
	return err
}

func (r *UserRepository) Truncate() error {
	_, err := r.db.Exec("TRUNCATE users RESTART IDENTITY CASCADE")
	return err
}

// ============================================================================
// Integration Tests
// ============================================================================

func TestExample1_PostgresBasic(t *testing.T) {
	ctx := context.Background()

	// Start PostgreSQL container
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
	require.NoError(t, err)
	defer container.Terminate(ctx)

	// Get connection info
	host, err := container.Host(ctx)
	require.NoError(t, err)

	port, err := container.MappedPort(ctx, "5432")
	require.NoError(t, err)

	// Connect to database
	dsn := "postgres://test:test@" + host + ":" + port.Port() + "/testdb?sslmode=disable"
	db, err := sql.Open("postgres", dsn)
	require.NoError(t, err)
	defer db.Close()

	// Test connection
	err = db.Ping()
	require.NoError(t, err)

	t.Log("PostgreSQL container started successfully!")
}

func TestExample1_UserRepository(t *testing.T) {
	ctx := context.Background()

	// Start PostgreSQL container
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
	require.NoError(t, err)
	defer container.Terminate(ctx)

	// Get connection
	host, _ := container.Host(ctx)
	port, _ := container.MappedPort(ctx, "5432")
	dsn := "postgres://test:test@" + host + ":" + port.Port() + "/testdb?sslmode=disable"

	db, err := sql.Open("postgres", dsn)
	require.NoError(t, err)
	defer db.Close()

	// Create repository and table
	repo := NewUserRepository(db)
	err = repo.CreateTable()
	require.NoError(t, err)

	t.Run("Create user", func(t *testing.T) {
		user := &User{Name: "Alice", Email: "alice@example.com"}
		err := repo.Create(user)

		require.NoError(t, err)
		assert.NotZero(t, user.ID)
		assert.NotZero(t, user.CreatedAt)
	})

	t.Run("Find by email", func(t *testing.T) {
		user, err := repo.FindByEmail("alice@example.com")

		require.NoError(t, err)
		assert.Equal(t, "Alice", user.Name)
	})

	t.Run("Create another user", func(t *testing.T) {
		user := &User{Name: "Bob", Email: "bob@example.com"}
		err := repo.Create(user)

		require.NoError(t, err)
		assert.NotZero(t, user.ID)
	})

	t.Run("Find all users", func(t *testing.T) {
		users, err := repo.FindAll()

		require.NoError(t, err)
		assert.Len(t, users, 2)
	})

	t.Run("Delete user", func(t *testing.T) {
		user, _ := repo.FindByEmail("alice@example.com")
		err := repo.Delete(user.ID)

		require.NoError(t, err)

		_, err = repo.FindByEmail("alice@example.com")
		assert.Error(t, err) // Should not find
	})
}

func TestExample1_Transactions(t *testing.T) {
	ctx := context.Background()

	// Start PostgreSQL container
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
	require.NoError(t, err)
	defer container.Terminate(ctx)

	// Get connection
	host, _ := container.Host(ctx)
	port, _ := container.MappedPort(ctx, "5432")
	dsn := "postgres://test:test@" + host + ":" + port.Port() + "/testdb?sslmode=disable"

	db, err := sql.Open("postgres", dsn)
	require.NoError(t, err)
	defer db.Close()

	// Setup
	repo := NewUserRepository(db)
	repo.CreateTable()

	t.Run("Transaction commit", func(t *testing.T) {
		tx, err := db.Begin()
		require.NoError(t, err)

		_, err = tx.Exec("INSERT INTO users (name, email) VALUES ($1, $2)", "Charlie", "charlie@example.com")
		require.NoError(t, err)

		err = tx.Commit()
		require.NoError(t, err)

		// Should find the user
		user, err := repo.FindByEmail("charlie@example.com")
		require.NoError(t, err)
		assert.Equal(t, "Charlie", user.Name)
	})

	t.Run("Transaction rollback", func(t *testing.T) {
		tx, err := db.Begin()
		require.NoError(t, err)

		_, err = tx.Exec("INSERT INTO users (name, email) VALUES ($1, $2)", "David", "david@example.com")
		require.NoError(t, err)

		err = tx.Rollback()
		require.NoError(t, err)

		// Should NOT find the user
		_, err = repo.FindByEmail("david@example.com")
		assert.Error(t, err)
	})
}
