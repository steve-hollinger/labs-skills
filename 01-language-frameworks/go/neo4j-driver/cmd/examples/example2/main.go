// Example 2: Transaction Patterns
//
// This example demonstrates transaction handling in Go:
// - Transaction functions (ExecuteWrite/ExecuteRead)
// - Automatic retry on transient failures
// - Error handling within transactions
// - Explicit transactions when needed
//
// Prerequisites:
//   - Neo4j running at bolt://localhost:7687
//   - Run: make infra-up from repository root

package main

import (
	"context"
	"errors"
	"fmt"
	"log"
	"os"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

// Person represents a person entity
type Person struct {
	Name  string
	Age   int
	Email string
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

	fmt.Println("Neo4j Go Driver - Example 2: Transaction Patterns")
	fmt.Println("================================================")

	driver, err := neo4j.NewDriverWithContext(uri, neo4j.BasicAuth(username, password, ""))
	if err != nil {
		log.Fatalf("Failed to create driver: %v", err)
	}
	defer driver.Close(ctx)

	if err := driver.VerifyConnectivity(ctx); err != nil {
		log.Fatalf("Failed to verify connectivity: %v", err)
	}
	fmt.Println("Connected to Neo4j!")

	// Cleanup
	cleanup(ctx, driver)

	// Demonstrate different transaction patterns
	fmt.Println("\n1. Transaction Function - Write")
	demoWriteTransaction(ctx, driver)

	fmt.Println("\n2. Transaction Function - Read")
	demoReadTransaction(ctx, driver)

	fmt.Println("\n3. Transaction with Error Handling")
	demoTransactionWithErrors(ctx, driver)

	fmt.Println("\n4. Multiple Operations in One Transaction")
	demoMultipleOperations(ctx, driver)

	fmt.Println("\n5. Explicit Transaction (Manual Control)")
	demoExplicitTransaction(ctx, driver)

	// Cleanup
	cleanup(ctx, driver)

	fmt.Println("\n================================================")
	fmt.Println("Example completed successfully!")
}

func cleanup(ctx context.Context, driver neo4j.DriverWithContext) {
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)
	_, _ = session.Run(ctx, "MATCH (n:TxExample) DETACH DELETE n", nil)
}

func demoWriteTransaction(ctx context.Context, driver neo4j.DriverWithContext) {
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	fmt.Println("   Using ExecuteWrite for write operations...")

	// ExecuteWrite automatically retries on transient failures
	result, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		result, err := tx.Run(ctx, `
			CREATE (p:TxExample:Person {
				name: $name,
				age: $age,
				created: datetime()
			})
			RETURN p.name AS name, p.age AS age
		`, map[string]any{
			"name": "Alice",
			"age":  30,
		})
		if err != nil {
			return nil, fmt.Errorf("create failed: %w", err)
		}

		record, err := result.Single(ctx)
		if err != nil {
			return nil, fmt.Errorf("single failed: %w", err)
		}

		name, _ := record.Get("name")
		age, _ := record.Get("age")
		return Person{Name: name.(string), Age: int(age.(int64))}, nil
	})

	if err != nil {
		log.Fatalf("Write transaction failed: %v", err)
	}

	person := result.(Person)
	fmt.Printf("   Created: %s (age %d)\n", person.Name, person.Age)
}

func demoReadTransaction(ctx context.Context, driver neo4j.DriverWithContext) {
	// Create some test data first
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	_, _ = session.Run(ctx, `
		CREATE (:TxExample:Person {name: 'Bob', age: 25})
		CREATE (:TxExample:Person {name: 'Charlie', age: 35})
	`, nil)
	session.Close(ctx)

	// Use AccessModeRead for read-only sessions (enables routing to read replicas)
	readSession := driver.NewSession(ctx, neo4j.SessionConfig{
		AccessMode: neo4j.AccessModeRead,
	})
	defer readSession.Close(ctx)

	fmt.Println("   Using ExecuteRead with AccessModeRead...")

	result, err := readSession.ExecuteRead(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		result, err := tx.Run(ctx, `
			MATCH (p:TxExample:Person)
			RETURN p.name AS name, p.age AS age
			ORDER BY p.age DESC
		`, nil)
		if err != nil {
			return nil, err
		}

		var people []Person
		for result.Next(ctx) {
			record := result.Record()
			name, _ := record.Get("name")
			age, _ := record.Get("age")
			people = append(people, Person{
				Name: name.(string),
				Age:  int(age.(int64)),
			})
		}

		if err := result.Err(); err != nil {
			return nil, err
		}

		return people, nil
	})

	if err != nil {
		log.Fatalf("Read transaction failed: %v", err)
	}

	people := result.([]Person)
	fmt.Println("   Found people:")
	for _, p := range people {
		fmt.Printf("     - %s (age %d)\n", p.Name, p.Age)
	}
}

// ErrNotFound is returned when an entity is not found
var ErrNotFound = errors.New("entity not found")

func demoTransactionWithErrors(ctx context.Context, driver neo4j.DriverWithContext) {
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	fmt.Println("   Handling errors within transactions...")

	// Try to find a non-existent person
	_, err := session.ExecuteRead(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		result, err := tx.Run(ctx, `
			MATCH (p:TxExample:Person {name: $name})
			RETURN p
		`, map[string]any{"name": "NonExistent"})
		if err != nil {
			return nil, err
		}

		// Check if we got any results
		if !result.Next(ctx) {
			return nil, ErrNotFound
		}

		return result.Record(), nil
	})

	if errors.Is(err, ErrNotFound) {
		fmt.Println("   Correctly handled: Person not found")
	} else if err != nil {
		log.Fatalf("Unexpected error: %v", err)
	}

	// Demonstrate handling constraint violations
	fmt.Println("   Handling constraint violations...")

	// First create with unique email
	_, _ = session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		_, err := tx.Run(ctx, `
			CREATE (p:TxExample:Person {name: 'Unique', email: 'unique@example.com'})
		`, nil)
		return nil, err
	})

	// Try to create duplicate (if constraint exists, this would fail)
	result, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		result, err := tx.Run(ctx, `
			MERGE (p:TxExample:Person {email: $email})
			ON CREATE SET p.name = $name, p.isNew = true
			ON MATCH SET p.isNew = false
			RETURN p.isNew AS isNew
		`, map[string]any{
			"email": "unique@example.com",
			"name":  "Another",
		})
		if err != nil {
			return nil, err
		}
		record, err := result.Single(ctx)
		if err != nil {
			return nil, err
		}
		isNew, _ := record.Get("isNew")
		return isNew.(bool), nil
	})

	if err != nil {
		log.Fatalf("Merge failed: %v", err)
	}

	if !result.(bool) {
		fmt.Println("   Handled: Person already existed, not created again")
	}
}

func demoMultipleOperations(ctx context.Context, driver neo4j.DriverWithContext) {
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	fmt.Println("   Running multiple operations in one transaction...")

	result, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		// Operation 1: Create a company
		_, err := tx.Run(ctx, `
			CREATE (c:TxExample:Company {name: 'TechCorp', industry: 'Technology'})
		`, nil)
		if err != nil {
			return nil, fmt.Errorf("create company failed: %w", err)
		}

		// Operation 2: Create employees
		_, err = tx.Run(ctx, `
			CREATE (:TxExample:Employee {name: 'Eve', role: 'Engineer'})
			CREATE (:TxExample:Employee {name: 'Frank', role: 'Manager'})
		`, nil)
		if err != nil {
			return nil, fmt.Errorf("create employees failed: %w", err)
		}

		// Operation 3: Create relationships
		result, err := tx.Run(ctx, `
			MATCH (c:TxExample:Company {name: 'TechCorp'})
			MATCH (e:TxExample:Employee)
			CREATE (e)-[:WORKS_AT {since: date()}]->(c)
			RETURN count(*) AS relationships
		`, nil)
		if err != nil {
			return nil, fmt.Errorf("create relationships failed: %w", err)
		}

		record, err := result.Single(ctx)
		if err != nil {
			return nil, err
		}

		count, _ := record.Get("relationships")
		return int(count.(int64)), nil
	})

	if err != nil {
		log.Fatalf("Multi-operation transaction failed: %v", err)
	}

	fmt.Printf("   Created company with %d employees linked\n", result.(int))
}

func demoExplicitTransaction(ctx context.Context, driver neo4j.DriverWithContext) {
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	fmt.Println("   Using explicit transaction with manual commit/rollback...")

	// Begin explicit transaction
	tx, err := session.BeginTransaction(ctx)
	if err != nil {
		log.Fatalf("Begin transaction failed: %v", err)
	}

	// Ensure transaction is closed (rollback if not committed)
	defer func() {
		if tx != nil {
			_ = tx.Close(ctx)
		}
	}()

	// Run queries
	result, err := tx.Run(ctx, `
		CREATE (p:TxExample:Person {name: 'Grace', age: 28})
		RETURN p.name AS name
	`, nil)
	if err != nil {
		_ = tx.Rollback(ctx)
		log.Fatalf("Create in explicit tx failed: %v", err)
	}

	record, err := result.Single(ctx)
	if err != nil {
		_ = tx.Rollback(ctx)
		log.Fatalf("Get result failed: %v", err)
	}

	name, _ := record.Get("name")
	fmt.Printf("   Created %s in explicit transaction\n", name)

	// Commit the transaction
	if err := tx.Commit(ctx); err != nil {
		log.Fatalf("Commit failed: %v", err)
	}

	fmt.Println("   Transaction committed successfully")

	// Note: Explicit transactions don't have automatic retry!
	// Use transaction functions (ExecuteWrite/ExecuteRead) when possible
	fmt.Println("   Note: Use transaction functions for automatic retry capability")
}
