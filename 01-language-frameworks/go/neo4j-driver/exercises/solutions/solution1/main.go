// Solution 1: User Management
//
// Complete implementation of the user management exercise.

package main

import (
	"context"
	"errors"
	"fmt"
	"log"
	"os"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

// ErrNotFound is returned when an entity is not found
var ErrNotFound = errors.New("entity not found")

// User represents a user entity
type User struct {
	ID    string
	Name  string
	Email string
	Age   int
}

// Neo4jUserRepository implements UserRepository using Neo4j
type Neo4jUserRepository struct {
	driver neo4j.DriverWithContext
}

func NewNeo4jUserRepository(driver neo4j.DriverWithContext) *Neo4jUserRepository {
	return &Neo4jUserRepository{driver: driver}
}

// CreateUser creates a new user and returns the element ID
func (r *Neo4jUserRepository) CreateUser(ctx context.Context, user User) (string, error) {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	result, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		result, err := tx.Run(ctx, `
			CREATE (u:User {
				name: $name,
				email: $email,
				age: $age,
				created: datetime()
			})
			RETURN elementId(u) AS id
		`, map[string]any{
			"name":  user.Name,
			"email": user.Email,
			"age":   user.Age,
		})
		if err != nil {
			return nil, fmt.Errorf("create user failed: %w", err)
		}

		record, err := result.Single(ctx)
		if err != nil {
			return nil, fmt.Errorf("get result failed: %w", err)
		}

		id, _ := record.Get("id")
		return id.(string), nil
	})

	if err != nil {
		return "", err
	}
	return result.(string), nil
}

// GetUserByEmail finds a user by email address
func (r *Neo4jUserRepository) GetUserByEmail(ctx context.Context, email string) (*User, error) {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{
		AccessMode: neo4j.AccessModeRead,
	})
	defer session.Close(ctx)

	result, err := session.ExecuteRead(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		result, err := tx.Run(ctx, `
			MATCH (u:User {email: $email})
			RETURN u, elementId(u) AS id
		`, map[string]any{"email": email})
		if err != nil {
			return nil, fmt.Errorf("query failed: %w", err)
		}

		if !result.Next(ctx) {
			return nil, ErrNotFound
		}

		record := result.Record()
		nodeVal, _ := record.Get("u")
		idVal, _ := record.Get("id")

		node := nodeVal.(neo4j.Node)
		return &User{
			ID:    idVal.(string),
			Name:  node.Props["name"].(string),
			Email: node.Props["email"].(string),
			Age:   int(node.Props["age"].(int64)),
		}, nil
	})

	if err != nil {
		if errors.Is(err, ErrNotFound) {
			return nil, nil
		}
		return nil, err
	}
	return result.(*User), nil
}

// UpdateUser updates user properties by ID
func (r *Neo4jUserRepository) UpdateUser(ctx context.Context, id string, updates map[string]any) error {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	_, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		result, err := tx.Run(ctx, `
			MATCH (u:User)
			WHERE elementId(u) = $id
			SET u += $updates, u.updated = datetime()
			RETURN u
		`, map[string]any{
			"id":      id,
			"updates": updates,
		})
		if err != nil {
			return nil, fmt.Errorf("update failed: %w", err)
		}

		// Check if we actually updated something
		if !result.Next(ctx) {
			return nil, ErrNotFound
		}

		return nil, result.Err()
	})

	return err
}

// DeleteUser deletes a user by ID
func (r *Neo4jUserRepository) DeleteUser(ctx context.Context, id string) error {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	_, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		result, err := tx.Run(ctx, `
			MATCH (u:User)
			WHERE elementId(u) = $id
			DELETE u
			RETURN count(*) AS deleted
		`, map[string]any{"id": id})
		if err != nil {
			return nil, fmt.Errorf("delete failed: %w", err)
		}

		record, err := result.Single(ctx)
		if err != nil {
			return nil, err
		}

		deleted, _ := record.Get("deleted")
		if deleted.(int64) == 0 {
			return nil, ErrNotFound
		}

		return nil, nil
	})

	return err
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

	fmt.Println("Solution 1: User Management")
	fmt.Println("===========================")

	// Clean up first
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	_, _ = session.Run(ctx, "MATCH (n:User) DELETE n", nil)
	session.Close(ctx)

	// Test CreateUser
	fmt.Println("\n1. Creating user...")
	user := User{Name: "Alice", Email: "alice@example.com", Age: 30}
	id, err := repo.CreateUser(ctx, user)
	if err != nil {
		log.Fatalf("CreateUser failed: %v", err)
	}
	fmt.Printf("   Created user with ID: %s\n", id)

	// Test GetUserByEmail
	fmt.Println("\n2. Finding user by email...")
	found, err := repo.GetUserByEmail(ctx, "alice@example.com")
	if err != nil {
		log.Fatalf("GetUserByEmail failed: %v", err)
	}
	if found != nil {
		fmt.Printf("   Found: %+v\n", found)
	}

	// Test GetUserByEmail - not found case
	fmt.Println("\n3. Finding non-existent user...")
	notFound, err := repo.GetUserByEmail(ctx, "nobody@example.com")
	if err != nil {
		log.Fatalf("GetUserByEmail failed: %v", err)
	}
	if notFound == nil {
		fmt.Println("   Correctly returned nil for non-existent user")
	}

	// Test UpdateUser
	fmt.Println("\n4. Updating user...")
	err = repo.UpdateUser(ctx, id, map[string]any{"age": 31, "city": "NYC"})
	if err != nil {
		log.Fatalf("UpdateUser failed: %v", err)
	}
	fmt.Println("   Updated successfully")

	// Verify update
	updated, _ := repo.GetUserByEmail(ctx, "alice@example.com")
	fmt.Printf("   Verified: Age is now %d\n", updated.Age)

	// Test DeleteUser
	fmt.Println("\n5. Deleting user...")
	err = repo.DeleteUser(ctx, id)
	if err != nil {
		log.Fatalf("DeleteUser failed: %v", err)
	}
	fmt.Println("   Deleted successfully")

	// Verify deletion
	deleted, _ := repo.GetUserByEmail(ctx, "alice@example.com")
	if deleted == nil {
		fmt.Println("   Verified: User no longer exists")
	}

	fmt.Println("\n===========================")
	fmt.Println("Solution completed successfully!")
}
