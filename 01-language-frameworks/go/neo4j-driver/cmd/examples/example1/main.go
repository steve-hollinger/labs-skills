// Example 1: Basic CRUD Operations
//
// This example demonstrates fundamental Neo4j operations in Go:
// - Driver configuration and connection
// - Creating nodes with properties
// - Reading/querying nodes
// - Updating properties
// - Deleting nodes
//
// Prerequisites:
//   - Neo4j running at bolt://localhost:7687
//   - Run: make infra-up from repository root

package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

func getEnvOrDefault(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func main() {
	ctx := context.Background()

	// Get connection details from environment
	uri := getEnvOrDefault("NEO4J_URI", "bolt://localhost:7687")
	username := getEnvOrDefault("NEO4J_USER", "neo4j")
	password := getEnvOrDefault("NEO4J_PASSWORD", "password")

	fmt.Println("Neo4j Go Driver - Example 1: Basic CRUD Operations")
	fmt.Println("================================================")

	// 1. Create driver
	fmt.Println("\n1. Creating driver connection...")
	driver, err := neo4j.NewDriverWithContext(uri, neo4j.BasicAuth(username, password, ""))
	if err != nil {
		log.Fatalf("Failed to create driver: %v", err)
	}
	defer driver.Close(ctx)

	// Verify connectivity
	if err := driver.VerifyConnectivity(ctx); err != nil {
		log.Fatalf("Failed to verify connectivity: %v", err)
	}
	fmt.Println("   Connected to Neo4j!")

	// Cleanup before starting
	cleanup(ctx, driver)

	// 2. CREATE - Create nodes
	fmt.Println("\n2. CREATE - Creating nodes...")
	demoCreate(ctx, driver)

	// 3. READ - Query nodes
	fmt.Println("\n3. READ - Querying nodes...")
	demoRead(ctx, driver)

	// 4. UPDATE - Modify properties
	fmt.Println("\n4. UPDATE - Modifying properties...")
	demoUpdate(ctx, driver)

	// 5. DELETE - Remove nodes
	fmt.Println("\n5. DELETE - Removing nodes...")
	demoDelete(ctx, driver)

	// Cleanup
	cleanup(ctx, driver)

	fmt.Println("\n================================================")
	fmt.Println("Example completed successfully!")
}

func cleanup(ctx context.Context, driver neo4j.DriverWithContext) {
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	_, _ = session.Run(ctx, "MATCH (n:GoExample) DETACH DELETE n", nil)
}

func demoCreate(ctx context.Context, driver neo4j.DriverWithContext) {
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	// Create single node
	fmt.Println("   Creating single node with parameters...")
	result, err := session.Run(ctx, `
		CREATE (p:GoExample:Person {name: $name, age: $age, email: $email})
		RETURN p.name AS name
	`, map[string]any{
		"name":  "Alice",
		"age":   30,
		"email": "alice@example.com",
	})
	if err != nil {
		log.Fatalf("Create failed: %v", err)
	}

	record, err := result.Single(ctx)
	if err != nil {
		log.Fatalf("Single failed: %v", err)
	}
	name, _ := record.Get("name")
	fmt.Printf("   Created: %s\n", name)

	// Create multiple nodes
	fmt.Println("   Creating multiple nodes...")
	_, err = session.Run(ctx, `
		CREATE (:GoExample:Person {name: 'Bob', age: 25})
		CREATE (:GoExample:Person {name: 'Charlie', age: 35})
		CREATE (:GoExample:Person {name: 'Diana', age: 28})
	`, nil)
	if err != nil {
		log.Fatalf("Create multiple failed: %v", err)
	}
	fmt.Println("   Created Bob, Charlie, Diana")

	// Create with relationship
	fmt.Println("   Creating nodes with relationship...")
	_, err = session.Run(ctx, `
		MATCH (a:GoExample {name: 'Alice'}), (b:GoExample {name: 'Bob'})
		CREATE (a)-[:KNOWS {since: 2020}]->(b)
	`, nil)
	if err != nil {
		log.Fatalf("Create relationship failed: %v", err)
	}
	fmt.Println("   Created KNOWS relationship between Alice and Bob")
}

func demoRead(ctx context.Context, driver neo4j.DriverWithContext) {
	// Use read session for read-only operations
	session := driver.NewSession(ctx, neo4j.SessionConfig{
		AccessMode: neo4j.AccessModeRead,
	})
	defer session.Close(ctx)

	// Simple query
	fmt.Println("   Finding all people...")
	result, err := session.Run(ctx, `
		MATCH (p:GoExample:Person)
		RETURN p.name AS name, p.age AS age
		ORDER BY p.name
	`, nil)
	if err != nil {
		log.Fatalf("Query failed: %v", err)
	}

	fmt.Println("   People found:")
	for result.Next(ctx) {
		record := result.Record()
		name, _ := record.Get("name")
		age, _ := record.Get("age")
		fmt.Printf("     - %s (age %d)\n", name, age)
	}
	if err := result.Err(); err != nil {
		log.Fatalf("Result iteration failed: %v", err)
	}

	// Query with parameters
	fmt.Println("\n   Finding people over 27...")
	result, err = session.Run(ctx, `
		MATCH (p:GoExample:Person)
		WHERE p.age > $minAge
		RETURN p.name AS name, p.age AS age
		ORDER BY p.age DESC
	`, map[string]any{"minAge": 27})
	if err != nil {
		log.Fatalf("Query with params failed: %v", err)
	}

	for result.Next(ctx) {
		record := result.Record()
		name, _ := record.Get("name")
		age, _ := record.Get("age")
		fmt.Printf("     - %s (age %d)\n", name, age)
	}
	if err := result.Err(); err != nil {
		log.Fatalf("Result iteration failed: %v", err)
	}

	// Query relationships
	fmt.Println("\n   Finding who Alice knows...")
	result, err = session.Run(ctx, `
		MATCH (a:GoExample {name: 'Alice'})-[r:KNOWS]->(friend)
		RETURN friend.name AS friend, r.since AS since
	`, nil)
	if err != nil {
		log.Fatalf("Relationship query failed: %v", err)
	}

	for result.Next(ctx) {
		record := result.Record()
		friend, _ := record.Get("friend")
		since, _ := record.Get("since")
		fmt.Printf("     - Knows %s since %d\n", friend, since)
	}
	if err := result.Err(); err != nil {
		log.Fatalf("Result iteration failed: %v", err)
	}
}

func demoUpdate(ctx context.Context, driver neo4j.DriverWithContext) {
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	// Update single property
	fmt.Println("   Updating Alice's age...")
	result, err := session.Run(ctx, `
		MATCH (p:GoExample {name: 'Alice'})
		SET p.age = $newAge
		RETURN p.name AS name, p.age AS age
	`, map[string]any{"newAge": 31})
	if err != nil {
		log.Fatalf("Update failed: %v", err)
	}

	record, _ := result.Single(ctx)
	name, _ := record.Get("name")
	age, _ := record.Get("age")
	fmt.Printf("   Updated: %s is now %d\n", name, age)

	// Add new property
	fmt.Println("   Adding department to Bob...")
	result, err = session.Run(ctx, `
		MATCH (p:GoExample {name: 'Bob'})
		SET p.department = $dept
		RETURN p
	`, map[string]any{"dept": "Engineering"})
	if err != nil {
		log.Fatalf("Add property failed: %v", err)
	}

	record, _ = result.Single(ctx)
	node, _ := record.Get("p")
	neo4jNode := node.(neo4j.Node)
	fmt.Printf("   Bob's properties: %v\n", neo4jNode.Props)

	// Update with map merge
	fmt.Println("   Updating Charlie with multiple properties...")
	_, err = session.Run(ctx, `
		MATCH (p:GoExample {name: 'Charlie'})
		SET p += {city: 'NYC', role: 'Manager'}
	`, nil)
	if err != nil {
		log.Fatalf("Map merge failed: %v", err)
	}
	fmt.Println("   Added city and role to Charlie")
}

func demoDelete(ctx context.Context, driver neo4j.DriverWithContext) {
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	// Remove property
	fmt.Println("   Removing department from Bob...")
	_, err := session.Run(ctx, `
		MATCH (p:GoExample {name: 'Bob'})
		REMOVE p.department
	`, nil)
	if err != nil {
		log.Fatalf("Remove property failed: %v", err)
	}
	fmt.Println("   Removed department property")

	// Delete relationship
	fmt.Println("   Deleting KNOWS relationship...")
	result, err := session.Run(ctx, `
		MATCH (a:GoExample {name: 'Alice'})-[r:KNOWS]-(b)
		DELETE r
		RETURN count(r) AS deleted
	`, nil)
	if err != nil {
		log.Fatalf("Delete relationship failed: %v", err)
	}
	record, _ := result.Single(ctx)
	deleted, _ := record.Get("deleted")
	fmt.Printf("   Deleted %d relationship(s)\n", deleted)

	// Delete node
	fmt.Println("   Deleting Diana...")
	result, err = session.Run(ctx, `
		MATCH (p:GoExample {name: 'Diana'})
		DELETE p
		RETURN count(p) AS deleted
	`, nil)
	if err != nil {
		log.Fatalf("Delete node failed: %v", err)
	}
	record, _ = result.Single(ctx)
	deleted, _ = record.Get("deleted")
	fmt.Printf("   Deleted %d node(s)\n", deleted)
}
