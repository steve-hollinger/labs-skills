// Solution 2: Social Graph
//
// Complete implementation of the social graph exercise.

package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

type SocialGraph struct {
	driver neo4j.DriverWithContext
}

func NewSocialGraph(driver neo4j.DriverWithContext) *SocialGraph {
	return &SocialGraph{driver: driver}
}

func (s *SocialGraph) CreateUser(ctx context.Context, name, email string) (string, error) {
	session := s.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	result, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		result, err := tx.Run(ctx, `
			CREATE (u:SocialUser {name: $name, email: $email, created: datetime()})
			RETURN elementId(u) AS id
		`, map[string]any{"name": name, "email": email})
		if err != nil {
			return nil, err
		}

		record, err := result.Single(ctx)
		if err != nil {
			return nil, err
		}

		id, _ := record.Get("id")
		return id.(string), nil
	})

	if err != nil {
		return "", err
	}
	return result.(string), nil
}

func (s *SocialGraph) Follow(ctx context.Context, followerID, followeeID string) error {
	session := s.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	_, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		_, err := tx.Run(ctx, `
			MATCH (a:SocialUser), (b:SocialUser)
			WHERE elementId(a) = $follower AND elementId(b) = $followee
			MERGE (a)-[:FOLLOWS {since: datetime()}]->(b)
		`, map[string]any{
			"follower": followerID,
			"followee": followeeID,
		})
		return nil, err
	})

	return err
}

func (s *SocialGraph) GetFollowers(ctx context.Context, userID string) ([]string, error) {
	session := s.driver.NewSession(ctx, neo4j.SessionConfig{
		AccessMode: neo4j.AccessModeRead,
	})
	defer session.Close(ctx)

	result, err := session.ExecuteRead(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		result, err := tx.Run(ctx, `
			MATCH (follower:SocialUser)-[:FOLLOWS]->(user:SocialUser)
			WHERE elementId(user) = $id
			RETURN follower.name AS name
			ORDER BY name
		`, map[string]any{"id": userID})
		if err != nil {
			return nil, err
		}

		var followers []string
		for result.Next(ctx) {
			record := result.Record()
			name, _ := record.Get("name")
			followers = append(followers, name.(string))
		}

		return followers, result.Err()
	})

	if err != nil {
		return nil, err
	}
	return result.([]string), nil
}

func (s *SocialGraph) GetMutualFollows(ctx context.Context, userID string) ([]string, error) {
	session := s.driver.NewSession(ctx, neo4j.SessionConfig{
		AccessMode: neo4j.AccessModeRead,
	})
	defer session.Close(ctx)

	result, err := session.ExecuteRead(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		result, err := tx.Run(ctx, `
			MATCH (user:SocialUser)-[:FOLLOWS]->(other:SocialUser)-[:FOLLOWS]->(user)
			WHERE elementId(user) = $id
			RETURN DISTINCT other.name AS name
			ORDER BY name
		`, map[string]any{"id": userID})
		if err != nil {
			return nil, err
		}

		var mutual []string
		for result.Next(ctx) {
			record := result.Record()
			name, _ := record.Get("name")
			mutual = append(mutual, name.(string))
		}

		return mutual, result.Err()
	})

	if err != nil {
		return nil, err
	}
	return result.([]string), nil
}

func (s *SocialGraph) GetRecommendations(ctx context.Context, userID string) ([]string, error) {
	session := s.driver.NewSession(ctx, neo4j.SessionConfig{
		AccessMode: neo4j.AccessModeRead,
	})
	defer session.Close(ctx)

	result, err := session.ExecuteRead(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		result, err := tx.Run(ctx, `
			MATCH (user:SocialUser)-[:FOLLOWS]->(following:SocialUser)-[:FOLLOWS]->(rec:SocialUser)
			WHERE elementId(user) = $id
			  AND user <> rec
			  AND NOT (user)-[:FOLLOWS]->(rec)
			RETURN DISTINCT rec.name AS name, COUNT(following) AS mutualCount
			ORDER BY mutualCount DESC, name
		`, map[string]any{"id": userID})
		if err != nil {
			return nil, err
		}

		var recs []string
		for result.Next(ctx) {
			record := result.Record()
			name, _ := record.Get("name")
			recs = append(recs, name.(string))
		}

		return recs, result.Err()
	})

	if err != nil {
		return nil, err
	}
	return result.([]string), nil
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

	// Cleanup first
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	_, _ = session.Run(ctx, "MATCH (n:SocialUser) DETACH DELETE n", nil)
	session.Close(ctx)

	graph := NewSocialGraph(driver)

	fmt.Println("Solution 2: Social Graph")
	fmt.Println("========================")

	// Create users
	fmt.Println("\n1. Creating users...")
	alice, _ := graph.CreateUser(ctx, "Alice", "alice@example.com")
	bob, _ := graph.CreateUser(ctx, "Bob", "bob@example.com")
	charlie, _ := graph.CreateUser(ctx, "Charlie", "charlie@example.com")
	diana, _ := graph.CreateUser(ctx, "Diana", "diana@example.com")
	fmt.Printf("   Created: Alice, Bob, Charlie, Diana\n")

	// Create follow relationships
	fmt.Println("\n2. Creating follow relationships...")
	_ = graph.Follow(ctx, alice, bob)     // Alice -> Bob
	_ = graph.Follow(ctx, bob, alice)     // Bob -> Alice (mutual)
	_ = graph.Follow(ctx, alice, charlie) // Alice -> Charlie
	_ = graph.Follow(ctx, charlie, diana) // Charlie -> Diana
	_ = graph.Follow(ctx, bob, diana)     // Bob -> Diana
	fmt.Println("   Alice follows Bob (mutual)")
	fmt.Println("   Alice follows Charlie")
	fmt.Println("   Charlie follows Diana")
	fmt.Println("   Bob follows Diana")

	// Get followers
	fmt.Println("\n3. Alice's followers:")
	followers, _ := graph.GetFollowers(ctx, alice)
	fmt.Printf("   %v\n", followers)
	// Expected: [Bob] (Bob follows Alice)

	// Get mutual follows
	fmt.Println("\n4. Alice's mutual follows:")
	mutual, _ := graph.GetMutualFollows(ctx, alice)
	fmt.Printf("   %v\n", mutual)
	// Expected: [Bob] (Alice and Bob follow each other)

	// Get recommendations
	fmt.Println("\n5. Recommendations for Alice:")
	recs, _ := graph.GetRecommendations(ctx, alice)
	fmt.Printf("   %v\n", recs)
	// Expected: [Diana] (Bob and Charlie both follow Diana, Alice doesn't)

	// Cleanup
	session = driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)
	_, _ = session.Run(ctx, "MATCH (n:SocialUser) DETACH DELETE n", nil)

	fmt.Println("\n========================")
	fmt.Println("Solution completed successfully!")
}
