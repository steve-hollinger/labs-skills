// Exercise 2: Social Graph
//
// Build and query a social network graph.
//
// Tasks:
// 1. Create a social network with users and FOLLOWS relationships
// 2. Find all followers of a user
// 3. Find mutual followers (users who follow each other)
// 4. Find followers of followers (potential recommendations)
//
// Run with: go run ./exercises/exercise2/main.go
// Check solution: go run ./exercises/solutions/solution2/main.go

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

// TODO: Implement CreateUser
// Create a user node with name and email
func (s *SocialGraph) CreateUser(ctx context.Context, name, email string) (string, error) {
	// TODO: Implement
	return "", fmt.Errorf("not implemented")
}

// TODO: Implement Follow
// Create a FOLLOWS relationship between two users
func (s *SocialGraph) Follow(ctx context.Context, followerID, followeeID string) error {
	// TODO: Implement
	// Query: MATCH (a:SocialUser), (b:SocialUser) WHERE elementId(a) = $follower AND elementId(b) = $followee CREATE (a)-[:FOLLOWS]->(b)
	return fmt.Errorf("not implemented")
}

// TODO: Implement GetFollowers
// Return list of users who follow the given user
func (s *SocialGraph) GetFollowers(ctx context.Context, userID string) ([]string, error) {
	// TODO: Implement
	// Query: MATCH (follower:SocialUser)-[:FOLLOWS]->(user:SocialUser) WHERE elementId(user) = $id RETURN follower.name
	return nil, fmt.Errorf("not implemented")
}

// TODO: Implement GetMutualFollows
// Find users who have a mutual follow relationship with given user
func (s *SocialGraph) GetMutualFollows(ctx context.Context, userID string) ([]string, error) {
	// TODO: Implement
	// Query: MATCH (user:SocialUser)-[:FOLLOWS]->(other:SocialUser)-[:FOLLOWS]->(user) WHERE elementId(user) = $id RETURN other.name
	return nil, fmt.Errorf("not implemented")
}

// TODO: Implement GetRecommendations
// Find followers of followers who the user doesn't already follow
func (s *SocialGraph) GetRecommendations(ctx context.Context, userID string) ([]string, error) {
	// TODO: Implement
	// Query: MATCH (user)-[:FOLLOWS]->(following)-[:FOLLOWS]->(rec) WHERE elementId(user) = $id AND user <> rec AND NOT (user)-[:FOLLOWS]->(rec) RETURN DISTINCT rec.name
	return nil, fmt.Errorf("not implemented")
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

	graph := NewSocialGraph(driver)

	fmt.Println("Exercise 2: Social Graph")
	fmt.Println("========================")

	// Create users
	fmt.Println("\n1. Creating users...")
	alice, _ := graph.CreateUser(ctx, "Alice", "alice@example.com")
	bob, _ := graph.CreateUser(ctx, "Bob", "bob@example.com")
	charlie, _ := graph.CreateUser(ctx, "Charlie", "charlie@example.com")
	diana, _ := graph.CreateUser(ctx, "Diana", "diana@example.com")

	if alice == "" {
		fmt.Println("   CreateUser not implemented yet")
	} else {
		fmt.Printf("   Created Alice: %s\n", alice)
	}

	// Create follow relationships
	fmt.Println("\n2. Creating follow relationships...")
	_ = graph.Follow(ctx, alice, bob)     // Alice follows Bob
	_ = graph.Follow(ctx, bob, alice)     // Bob follows Alice (mutual)
	_ = graph.Follow(ctx, alice, charlie) // Alice follows Charlie
	_ = graph.Follow(ctx, charlie, diana) // Charlie follows Diana
	_ = graph.Follow(ctx, bob, diana)     // Bob follows Diana

	// Get followers
	fmt.Println("\n3. Getting Alice's followers...")
	followers, err := graph.GetFollowers(ctx, alice)
	if err != nil {
		fmt.Printf("   Error: %v\n", err)
	} else {
		fmt.Printf("   Followers: %v\n", followers)
	}

	// Get mutual follows
	fmt.Println("\n4. Getting Alice's mutual follows...")
	mutual, err := graph.GetMutualFollows(ctx, alice)
	if err != nil {
		fmt.Printf("   Error: %v\n", err)
	} else {
		fmt.Printf("   Mutual: %v\n", mutual)
	}

	// Get recommendations
	fmt.Println("\n5. Getting recommendations for Alice...")
	recs, err := graph.GetRecommendations(ctx, alice)
	if err != nil {
		fmt.Printf("   Error: %v\n", err)
	} else {
		fmt.Printf("   Recommendations: %v\n", recs)
	}

	// Cleanup
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)
	_, _ = session.Run(ctx, "MATCH (n:SocialUser) DETACH DELETE n", nil)

	fmt.Println("\nExercise complete!")
}
