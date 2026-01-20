// Exercise 1: User Management
//
// Implement a simple user management system using Neo4j.
//
// Tasks:
// 1. Implement CreateUser to add a new user
// 2. Implement GetUserByEmail to find a user by email
// 3. Implement UpdateUser to modify user properties
// 4. Implement DeleteUser to remove a user
//
// Run with: go run ./exercises/exercise1/main.go
// Check solution: go run ./exercises/solutions/solution1/main.go

package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

// User represents a user entity
type User struct {
	ID    string
	Name  string
	Email string
	Age   int
}

// UserRepository defines the interface for user operations
type UserRepository interface {
	CreateUser(ctx context.Context, user User) (string, error)
	GetUserByEmail(ctx context.Context, email string) (*User, error)
	UpdateUser(ctx context.Context, id string, updates map[string]any) error
	DeleteUser(ctx context.Context, id string) error
}

// Neo4jUserRepository implements UserRepository using Neo4j
type Neo4jUserRepository struct {
	driver neo4j.DriverWithContext
}

func NewNeo4jUserRepository(driver neo4j.DriverWithContext) *Neo4jUserRepository {
	return &Neo4jUserRepository{driver: driver}
}

// TODO: Implement CreateUser
// - Create a new User node with name, email, and age properties
// - Return the element ID of the created node
// - Use ExecuteWrite for the transaction
func (r *Neo4jUserRepository) CreateUser(ctx context.Context, user User) (string, error) {
	// TODO: Implement this method
	// Hint: Use session.ExecuteWrite and tx.Run
	// Query should be: CREATE (u:User {name: $name, email: $email, age: $age}) RETURN elementId(u) AS id

	return "", fmt.Errorf("not implemented")
}

// TODO: Implement GetUserByEmail
// - Find a user by their email address
// - Return nil if not found
// - Use ExecuteRead for the transaction
func (r *Neo4jUserRepository) GetUserByEmail(ctx context.Context, email string) (*User, error) {
	// TODO: Implement this method
	// Hint: Use session.ExecuteRead and tx.Run
	// Query should be: MATCH (u:User {email: $email}) RETURN u, elementId(u) AS id

	return nil, fmt.Errorf("not implemented")
}

// TODO: Implement UpdateUser
// - Update user properties by ID
// - The updates map contains property names and their new values
// - Use ExecuteWrite for the transaction
func (r *Neo4jUserRepository) UpdateUser(ctx context.Context, id string, updates map[string]any) error {
	// TODO: Implement this method
	// Hint: Use SET u += $updates syntax
	// Query should be: MATCH (u:User) WHERE elementId(u) = $id SET u += $updates

	return fmt.Errorf("not implemented")
}

// TODO: Implement DeleteUser
// - Delete a user by ID
// - Use ExecuteWrite for the transaction
func (r *Neo4jUserRepository) DeleteUser(ctx context.Context, id string) error {
	// TODO: Implement this method
	// Hint: Use MATCH and DELETE
	// Query should be: MATCH (u:User) WHERE elementId(u) = $id DELETE u

	return fmt.Errorf("not implemented")
}

func getEnvOrDefault(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func main() {
	ctx := context.Background()

	uri := getEnvOrDefault("NEO4J_URI", "bolt://localhost:7687")
	username := getEnvOrDefault("NEO4J_USER", "neo4j")
	password := getEnvOrDefault("NEO4J_PASSWORD", "password")

	driver, err := neo4j.NewDriverWithContext(uri, neo4j.BasicAuth(username, password, ""))
	if err != nil {
		log.Fatalf("Failed to create driver: %v", err)
	}
	defer driver.Close(ctx)

	repo := NewNeo4jUserRepository(driver)

	fmt.Println("Exercise 1: User Management")
	fmt.Println("===========================")

	// Test CreateUser
	fmt.Println("\n1. Creating user...")
	user := User{Name: "Alice", Email: "alice@example.com", Age: 30}
	id, err := repo.CreateUser(ctx, user)
	if err != nil {
		fmt.Printf("   Error: %v\n", err)
	} else {
		fmt.Printf("   Created user with ID: %s\n", id)
	}

	// Test GetUserByEmail
	fmt.Println("\n2. Finding user by email...")
	found, err := repo.GetUserByEmail(ctx, "alice@example.com")
	if err != nil {
		fmt.Printf("   Error: %v\n", err)
	} else if found != nil {
		fmt.Printf("   Found: %+v\n", found)
	}

	// Test UpdateUser
	fmt.Println("\n3. Updating user...")
	if id != "" {
		err = repo.UpdateUser(ctx, id, map[string]any{"age": 31})
		if err != nil {
			fmt.Printf("   Error: %v\n", err)
		} else {
			fmt.Println("   Updated successfully")
		}
	}

	// Test DeleteUser
	fmt.Println("\n4. Deleting user...")
	if id != "" {
		err = repo.DeleteUser(ctx, id)
		if err != nil {
			fmt.Printf("   Error: %v\n", err)
		} else {
			fmt.Println("   Deleted successfully")
		}
	}

	// Cleanup
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)
	_, _ = session.Run(ctx, "MATCH (n:User) DELETE n", nil)

	fmt.Println("\nExercise complete! Check your implementation.")
}
