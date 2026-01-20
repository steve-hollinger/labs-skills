// Example 3: Graph Patterns
//
// This example demonstrates common graph database patterns:
// - Building a social network graph
// - Finding paths and connections
// - Aggregations and recommendations
// - Working with Neo4j types (nodes, relationships, paths)
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

	uri := getEnvOrDefault("NEO4J_URI", "bolt://localhost:7687")
	username := getEnvOrDefault("NEO4J_USER", "neo4j")
	password := getEnvOrDefault("NEO4J_PASSWORD", "password")

	fmt.Println("Neo4j Go Driver - Example 3: Graph Patterns")
	fmt.Println("==========================================")

	driver, err := neo4j.NewDriverWithContext(uri, neo4j.BasicAuth(username, password, ""))
	if err != nil {
		log.Fatalf("Failed to create driver: %v", err)
	}
	defer driver.Close(ctx)

	if err := driver.VerifyConnectivity(ctx); err != nil {
		log.Fatalf("Failed to verify connectivity: %v", err)
	}
	fmt.Println("Connected to Neo4j!")

	// Cleanup and setup
	cleanup(ctx, driver)
	setupSocialNetwork(ctx, driver)

	// Demonstrate graph patterns
	fmt.Println("\n1. Working with Neo4j Node Type")
	demoNodeType(ctx, driver)

	fmt.Println("\n2. Working with Relationships")
	demoRelationships(ctx, driver)

	fmt.Println("\n3. Finding Paths")
	demoPaths(ctx, driver)

	fmt.Println("\n4. Aggregations")
	demoAggregations(ctx, driver)

	fmt.Println("\n5. Friend Recommendations")
	demoRecommendations(ctx, driver)

	fmt.Println("\n6. Batch Processing")
	demoBatchProcessing(ctx, driver)

	// Cleanup
	cleanup(ctx, driver)

	fmt.Println("\n==========================================")
	fmt.Println("Example completed successfully!")
}

func cleanup(ctx context.Context, driver neo4j.DriverWithContext) {
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)
	_, _ = session.Run(ctx, "MATCH (n:GraphExample) DETACH DELETE n", nil)
}

func setupSocialNetwork(ctx context.Context, driver neo4j.DriverWithContext) {
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	fmt.Println("\nSetting up social network...")

	// Create people
	_, err := session.Run(ctx, `
		CREATE (alice:GraphExample:Person {name: 'Alice', age: 30, city: 'NYC'})
		CREATE (bob:GraphExample:Person {name: 'Bob', age: 25, city: 'NYC'})
		CREATE (charlie:GraphExample:Person {name: 'Charlie', age: 35, city: 'LA'})
		CREATE (diana:GraphExample:Person {name: 'Diana', age: 28, city: 'NYC'})
		CREATE (eve:GraphExample:Person {name: 'Eve', age: 32, city: 'LA'})
		CREATE (frank:GraphExample:Person {name: 'Frank', age: 40, city: 'Chicago'})

		CREATE (alice)-[:KNOWS {since: 2018}]->(bob)
		CREATE (alice)-[:KNOWS {since: 2020}]->(charlie)
		CREATE (bob)-[:KNOWS {since: 2019}]->(diana)
		CREATE (charlie)-[:KNOWS {since: 2017}]->(eve)
		CREATE (diana)-[:KNOWS {since: 2021}]->(eve)
		CREATE (eve)-[:KNOWS {since: 2016}]->(frank)
	`, nil)

	if err != nil {
		log.Fatalf("Setup failed: %v", err)
	}
	fmt.Println("Created social network with 6 people and relationships")
}

func demoNodeType(ctx context.Context, driver neo4j.DriverWithContext) {
	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)

	fmt.Println("   Accessing Neo4j Node properties...")

	result, err := session.Run(ctx, `
		MATCH (p:GraphExample:Person {name: 'Alice'})
		RETURN p
	`, nil)
	if err != nil {
		log.Fatalf("Query failed: %v", err)
	}

	record, _ := result.Single(ctx)
	nodeVal, _ := record.Get("p")

	// Type assertion to neo4j.Node
	node := nodeVal.(neo4j.Node)

	fmt.Printf("   Element ID: %s\n", node.ElementId)
	fmt.Printf("   Labels: %v\n", node.Labels)
	fmt.Printf("   Properties:\n")
	for key, value := range node.Props {
		fmt.Printf("     - %s: %v\n", key, value)
	}

	// Access individual properties with type assertion
	name := node.Props["name"].(string)
	age := node.Props["age"].(int64)
	fmt.Printf("   Direct access: %s is %d years old\n", name, age)
}

func demoRelationships(ctx context.Context, driver neo4j.DriverWithContext) {
	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)

	fmt.Println("   Working with Neo4j Relationship type...")

	result, err := session.Run(ctx, `
		MATCH (a:GraphExample:Person)-[r:KNOWS]->(b:GraphExample:Person)
		RETURN a.name AS from, r, b.name AS to
		LIMIT 3
	`, nil)
	if err != nil {
		log.Fatalf("Query failed: %v", err)
	}

	for result.Next(ctx) {
		record := result.Record()
		from, _ := record.Get("from")
		to, _ := record.Get("to")
		relVal, _ := record.Get("r")

		rel := relVal.(neo4j.Relationship)

		fmt.Printf("   %s -[%s]-> %s\n", from, rel.Type, to)
		fmt.Printf("     Relationship ID: %s\n", rel.ElementId)
		fmt.Printf("     Properties: %v\n", rel.Props)
	}

	if err := result.Err(); err != nil {
		log.Fatalf("Iteration failed: %v", err)
	}
}

func demoPaths(ctx context.Context, driver neo4j.DriverWithContext) {
	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)

	fmt.Println("   Finding shortest path between Alice and Frank...")

	result, err := session.Run(ctx, `
		MATCH path = shortestPath(
			(a:GraphExample:Person {name: 'Alice'})-[:KNOWS*]-(b:GraphExample:Person {name: 'Frank'})
		)
		RETURN path, length(path) AS hops
	`, nil)
	if err != nil {
		log.Fatalf("Path query failed: %v", err)
	}

	if result.Next(ctx) {
		record := result.Record()
		pathVal, _ := record.Get("path")
		hops, _ := record.Get("hops")

		path := pathVal.(neo4j.Path)

		fmt.Printf("   Path length: %d hops\n", hops)
		fmt.Printf("   Path nodes:\n")
		for _, node := range path.Nodes {
			name := node.Props["name"].(string)
			fmt.Printf("     -> %s\n", name)
		}

		fmt.Printf("   Path relationships:\n")
		for _, rel := range path.Relationships {
			since := rel.Props["since"].(int64)
			fmt.Printf("     -[KNOWS since %d]-\n", since)
		}
	}

	if err := result.Err(); err != nil {
		log.Fatalf("Result error: %v", err)
	}

	// Find all paths up to 3 hops
	fmt.Println("\n   Finding all paths from Alice (up to 3 hops)...")

	result, err = session.Run(ctx, `
		MATCH path = (a:GraphExample:Person {name: 'Alice'})-[:KNOWS*1..3]->(end:GraphExample:Person)
		WHERE a <> end
		RETURN [n IN nodes(path) | n.name] AS names, length(path) AS hops
		ORDER BY hops
	`, nil)
	if err != nil {
		log.Fatalf("Multi-path query failed: %v", err)
	}

	for result.Next(ctx) {
		record := result.Record()
		names, _ := record.Get("names")
		hops, _ := record.Get("hops")

		// Convert to string slice
		var nameStrs []string
		for _, n := range names.([]any) {
			nameStrs = append(nameStrs, n.(string))
		}

		fmt.Printf("   %d hops: %v\n", hops, nameStrs)
	}
}

func demoAggregations(ctx context.Context, driver neo4j.DriverWithContext) {
	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)

	fmt.Println("   Counting connections per person...")

	result, err := session.Run(ctx, `
		MATCH (p:GraphExample:Person)
		OPTIONAL MATCH (p)-[r:KNOWS]-()
		RETURN p.name AS name, COUNT(r) AS connections
		ORDER BY connections DESC
	`, nil)
	if err != nil {
		log.Fatalf("Aggregation query failed: %v", err)
	}

	for result.Next(ctx) {
		record := result.Record()
		name, _ := record.Get("name")
		connections, _ := record.Get("connections")
		fmt.Printf("   %s: %d connections\n", name, connections)
	}

	fmt.Println("\n   People by city...")

	result, err = session.Run(ctx, `
		MATCH (p:GraphExample:Person)
		RETURN p.city AS city, COLLECT(p.name) AS people, COUNT(p) AS count
		ORDER BY count DESC
	`, nil)
	if err != nil {
		log.Fatalf("City aggregation failed: %v", err)
	}

	for result.Next(ctx) {
		record := result.Record()
		city, _ := record.Get("city")
		count, _ := record.Get("count")
		peopleVal, _ := record.Get("people")

		var names []string
		for _, n := range peopleVal.([]any) {
			names = append(names, n.(string))
		}

		fmt.Printf("   %s (%d): %v\n", city, count, names)
	}
}

func demoRecommendations(ctx context.Context, driver neo4j.DriverWithContext) {
	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)

	fmt.Println("   Friend recommendations for Alice (friends of friends)...")

	result, err := session.Run(ctx, `
		MATCH (person:GraphExample:Person {name: 'Alice'})-[:KNOWS]->(friend)-[:KNOWS]->(fof)
		WHERE person <> fof
		  AND NOT (person)-[:KNOWS]-(fof)
		RETURN fof.name AS recommendation,
		       COLLECT(DISTINCT friend.name) AS through,
		       COUNT(DISTINCT friend) AS mutualFriends
		ORDER BY mutualFriends DESC
	`, nil)
	if err != nil {
		log.Fatalf("Recommendation query failed: %v", err)
	}

	for result.Next(ctx) {
		record := result.Record()
		rec, _ := record.Get("recommendation")
		throughVal, _ := record.Get("through")
		mutual, _ := record.Get("mutualFriends")

		var through []string
		for _, t := range throughVal.([]any) {
			through = append(through, t.(string))
		}

		fmt.Printf("   Recommend: %s (through %v, %d mutual)\n", rec, through, mutual)
	}
}

func demoBatchProcessing(ctx context.Context, driver neo4j.DriverWithContext) {
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	fmt.Println("   Batch creating nodes with UNWIND...")

	// Prepare batch data
	people := []map[string]any{
		{"name": "Grace", "age": 27, "city": "Boston"},
		{"name": "Henry", "age": 45, "city": "Boston"},
		{"name": "Ivy", "age": 33, "city": "Seattle"},
	}

	result, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		result, err := tx.Run(ctx, `
			UNWIND $batch AS person
			CREATE (p:GraphExample:Person {
				name: person.name,
				age: person.age,
				city: person.city
			})
			RETURN COUNT(p) AS created
		`, map[string]any{"batch": people})
		if err != nil {
			return nil, err
		}

		record, err := result.Single(ctx)
		if err != nil {
			return nil, err
		}

		count, _ := record.Get("created")
		return int(count.(int64)), nil
	})

	if err != nil {
		log.Fatalf("Batch create failed: %v", err)
	}

	fmt.Printf("   Created %d people in batch\n", result.(int))

	// Verify
	verifyResult, _ := session.Run(ctx, `
		MATCH (p:GraphExample:Person)
		RETURN COUNT(p) AS total
	`, nil)
	record, _ := verifyResult.Single(ctx)
	total, _ := record.Get("total")
	fmt.Printf("   Total people in graph: %d\n", total)
}
