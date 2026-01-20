// Package tests contains integration tests for the Neo4j Go driver skill.
//
// Run with: go test -v ./tests/
// These tests require Neo4j to be running.
package tests

import (
	"context"
	"os"
	"testing"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func getTestDriver(t *testing.T) neo4j.DriverWithContext {
	t.Helper()

	uri := os.Getenv("NEO4J_URI")
	if uri == "" {
		uri = "bolt://localhost:7687"
	}
	user := os.Getenv("NEO4J_USER")
	if user == "" {
		user = "neo4j"
	}
	password := os.Getenv("NEO4J_PASSWORD")
	if password == "" {
		password = "password"
	}

	driver, err := neo4j.NewDriverWithContext(uri, neo4j.BasicAuth(user, password, ""))
	require.NoError(t, err, "Failed to create driver")

	ctx := context.Background()
	err = driver.VerifyConnectivity(ctx)
	if err != nil {
		t.Skipf("Neo4j not available: %v", err)
	}

	return driver
}

func cleanupTestData(t *testing.T, driver neo4j.DriverWithContext, label string) {
	t.Helper()
	ctx := context.Background()
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	_, err := session.Run(ctx, "MATCH (n:"+label+") DETACH DELETE n", nil)
	if err != nil {
		t.Logf("Cleanup warning: %v", err)
	}
}

func TestDriverConnection(t *testing.T) {
	driver := getTestDriver(t)
	defer driver.Close(context.Background())

	ctx := context.Background()
	err := driver.VerifyConnectivity(ctx)
	assert.NoError(t, err)
}

func TestCreateNode(t *testing.T) {
	driver := getTestDriver(t)
	ctx := context.Background()
	defer driver.Close(ctx)

	t.Cleanup(func() {
		cleanupTestData(t, driver, "TestNode")
	})

	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	result, err := session.Run(ctx, `
		CREATE (n:TestNode {name: $name, value: $value})
		RETURN n.name AS name, n.value AS value
	`, map[string]any{
		"name":  "test",
		"value": 42,
	})
	require.NoError(t, err)

	record, err := result.Single(ctx)
	require.NoError(t, err)

	name, ok := record.Get("name")
	assert.True(t, ok)
	assert.Equal(t, "test", name)

	value, ok := record.Get("value")
	assert.True(t, ok)
	assert.Equal(t, int64(42), value)
}

func TestTransactionFunction(t *testing.T) {
	driver := getTestDriver(t)
	ctx := context.Background()
	defer driver.Close(ctx)

	t.Cleanup(func() {
		cleanupTestData(t, driver, "TxTestNode")
	})

	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	// Test ExecuteWrite
	result, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		result, err := tx.Run(ctx, `
			CREATE (n:TxTestNode {name: $name})
			RETURN n.name AS name
		`, map[string]any{"name": "txtest"})
		if err != nil {
			return nil, err
		}

		record, err := result.Single(ctx)
		if err != nil {
			return nil, err
		}

		name, _ := record.Get("name")
		return name.(string), nil
	})

	require.NoError(t, err)
	assert.Equal(t, "txtest", result.(string))

	// Test ExecuteRead
	readResult, err := session.ExecuteRead(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		result, err := tx.Run(ctx, `
			MATCH (n:TxTestNode {name: $name})
			RETURN n.name AS name
		`, map[string]any{"name": "txtest"})
		if err != nil {
			return nil, err
		}

		record, err := result.Single(ctx)
		if err != nil {
			return nil, err
		}

		name, _ := record.Get("name")
		return name.(string), nil
	})

	require.NoError(t, err)
	assert.Equal(t, "txtest", readResult.(string))
}

func TestResultIteration(t *testing.T) {
	driver := getTestDriver(t)
	ctx := context.Background()
	defer driver.Close(ctx)

	t.Cleanup(func() {
		cleanupTestData(t, driver, "IterTestNode")
	})

	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	// Create test data
	_, err := session.Run(ctx, `
		CREATE (:IterTestNode {name: 'A', value: 1})
		CREATE (:IterTestNode {name: 'B', value: 2})
		CREATE (:IterTestNode {name: 'C', value: 3})
	`, nil)
	require.NoError(t, err)

	// Iterate results
	result, err := session.Run(ctx, `
		MATCH (n:IterTestNode)
		RETURN n.name AS name, n.value AS value
		ORDER BY n.name
	`, nil)
	require.NoError(t, err)

	var names []string
	var values []int64
	for result.Next(ctx) {
		record := result.Record()
		name, _ := record.Get("name")
		value, _ := record.Get("value")
		names = append(names, name.(string))
		values = append(values, value.(int64))
	}

	require.NoError(t, result.Err())
	assert.Equal(t, []string{"A", "B", "C"}, names)
	assert.Equal(t, []int64{1, 2, 3}, values)
}

func TestNodeType(t *testing.T) {
	driver := getTestDriver(t)
	ctx := context.Background()
	defer driver.Close(ctx)

	t.Cleanup(func() {
		cleanupTestData(t, driver, "NodeTypeTest")
	})

	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	// Create and retrieve node
	result, err := session.Run(ctx, `
		CREATE (n:NodeTypeTest:Person {name: 'Alice', age: 30})
		RETURN n
	`, nil)
	require.NoError(t, err)

	record, err := result.Single(ctx)
	require.NoError(t, err)

	nodeVal, ok := record.Get("n")
	require.True(t, ok)

	node := nodeVal.(neo4j.Node)
	assert.Contains(t, node.Labels, "NodeTypeTest")
	assert.Contains(t, node.Labels, "Person")
	assert.Equal(t, "Alice", node.Props["name"])
	assert.Equal(t, int64(30), node.Props["age"])
}

func TestRelationshipType(t *testing.T) {
	driver := getTestDriver(t)
	ctx := context.Background()
	defer driver.Close(ctx)

	t.Cleanup(func() {
		cleanupTestData(t, driver, "RelTestNode")
	})

	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	// Create nodes with relationship
	result, err := session.Run(ctx, `
		CREATE (a:RelTestNode {name: 'A'})-[r:CONNECTS_TO {weight: 5}]->(b:RelTestNode {name: 'B'})
		RETURN r
	`, nil)
	require.NoError(t, err)

	record, err := result.Single(ctx)
	require.NoError(t, err)

	relVal, ok := record.Get("r")
	require.True(t, ok)

	rel := relVal.(neo4j.Relationship)
	assert.Equal(t, "CONNECTS_TO", rel.Type)
	assert.Equal(t, int64(5), rel.Props["weight"])
}

func TestParameters(t *testing.T) {
	driver := getTestDriver(t)
	ctx := context.Background()
	defer driver.Close(ctx)

	t.Cleanup(func() {
		cleanupTestData(t, driver, "ParamTestNode")
	})

	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	// Create with parameters
	_, err := session.Run(ctx, `
		CREATE (n:ParamTestNode {name: $name, age: $age, active: $active})
	`, map[string]any{
		"name":   "Test",
		"age":    25,
		"active": true,
	})
	require.NoError(t, err)

	// Query with parameters
	result, err := session.Run(ctx, `
		MATCH (n:ParamTestNode {name: $name})
		WHERE n.age >= $minAge AND n.active = $active
		RETURN n.name AS name
	`, map[string]any{
		"name":   "Test",
		"minAge": 20,
		"active": true,
	})
	require.NoError(t, err)

	record, err := result.Single(ctx)
	require.NoError(t, err)

	name, _ := record.Get("name")
	assert.Equal(t, "Test", name)
}

func TestCollectResults(t *testing.T) {
	driver := getTestDriver(t)
	ctx := context.Background()
	defer driver.Close(ctx)

	t.Cleanup(func() {
		cleanupTestData(t, driver, "CollectTestNode")
	})

	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	// Create test data
	_, err := session.Run(ctx, `
		CREATE (:CollectTestNode {value: 1})
		CREATE (:CollectTestNode {value: 2})
		CREATE (:CollectTestNode {value: 3})
	`, nil)
	require.NoError(t, err)

	// Use Collect to get all results at once
	result, err := session.Run(ctx, `
		MATCH (n:CollectTestNode)
		RETURN n.value AS value
		ORDER BY value
	`, nil)
	require.NoError(t, err)

	records, err := result.Collect(ctx)
	require.NoError(t, err)
	assert.Len(t, records, 3)

	for i, record := range records {
		value, _ := record.Get("value")
		assert.Equal(t, int64(i+1), value)
	}
}
