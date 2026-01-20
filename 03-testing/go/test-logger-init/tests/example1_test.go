package tests

import (
	"os"
	"sync"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// ============================================================================
// Example 1: TestMain Basics
// ============================================================================

// Simulated in-memory database for demonstration
type InMemoryDB struct {
	mu   sync.RWMutex
	data map[string]interface{}
}

func NewInMemoryDB() *InMemoryDB {
	return &InMemoryDB{
		data: make(map[string]interface{}),
	}
}

func (db *InMemoryDB) Set(key string, value interface{}) {
	db.mu.Lock()
	defer db.mu.Unlock()
	db.data[key] = value
}

func (db *InMemoryDB) Get(key string) (interface{}, bool) {
	db.mu.RLock()
	defer db.mu.RUnlock()
	val, ok := db.data[key]
	return val, ok
}

func (db *InMemoryDB) Delete(key string) {
	db.mu.Lock()
	defer db.mu.Unlock()
	delete(db.data, key)
}

func (db *InMemoryDB) Clear() {
	db.mu.Lock()
	defer db.mu.Unlock()
	db.data = make(map[string]interface{})
}

func (db *InMemoryDB) Close() error {
	db.Clear()
	return nil
}

// Package-level test resources
var (
	testDB        *InMemoryDB
	setupComplete bool
)

// TestMain demonstrates package-level setup and teardown
func TestMain(m *testing.M) {
	// ============================================================
	// SETUP: Runs once before any tests in this package
	// ============================================================

	// Initialize test database
	testDB = NewInMemoryDB()
	setupComplete = true

	// Seed some initial data
	testDB.Set("config:version", "1.0.0")
	testDB.Set("config:environment", "test")

	// ============================================================
	// RUN TESTS
	// ============================================================
	code := m.Run()

	// ============================================================
	// TEARDOWN: Runs once after all tests complete
	// ============================================================

	// Clean up resources
	if testDB != nil {
		testDB.Close()
	}

	// ============================================================
	// EXIT with test result code
	// CRITICAL: Must call os.Exit with the code from m.Run()
	// ============================================================
	os.Exit(code)
}

// TestExample1_SetupVerification verifies TestMain ran setup
func TestExample1_SetupVerification(t *testing.T) {
	assert.True(t, setupComplete, "TestMain should have completed setup")
	require.NotNil(t, testDB, "testDB should be initialized")

	// Verify seeded data
	version, ok := testDB.Get("config:version")
	require.True(t, ok)
	assert.Equal(t, "1.0.0", version)
}

// TestExample1_SharedResource demonstrates using shared resources
func TestExample1_SharedResource(t *testing.T) {
	// Can use testDB from TestMain
	testDB.Set("test:key", "test:value")

	val, ok := testDB.Get("test:key")
	require.True(t, ok)
	assert.Equal(t, "test:value", val)

	// Clean up our test data
	t.Cleanup(func() {
		testDB.Delete("test:key")
	})
}

// TestExample1_IsolatedTest demonstrates test isolation
func TestExample1_IsolatedTest(t *testing.T) {
	// Each test should clean up after itself
	key := "isolated:key"

	t.Cleanup(func() {
		testDB.Delete(key)
	})

	testDB.Set(key, "isolated value")

	val, ok := testDB.Get(key)
	require.True(t, ok)
	assert.Equal(t, "isolated value", val)
}

// TestExample1_SubTests demonstrates subtests with shared setup
func TestExample1_SubTests(t *testing.T) {
	// Parent test can do setup
	parentKey := "parent:key"
	testDB.Set(parentKey, "parent value")

	t.Cleanup(func() {
		testDB.Delete(parentKey)
	})

	t.Run("subtest_read_parent", func(t *testing.T) {
		val, ok := testDB.Get(parentKey)
		require.True(t, ok)
		assert.Equal(t, "parent value", val)
	})

	t.Run("subtest_own_data", func(t *testing.T) {
		childKey := "child:key"
		testDB.Set(childKey, "child value")

		t.Cleanup(func() {
			testDB.Delete(childKey)
		})

		val, ok := testDB.Get(childKey)
		require.True(t, ok)
		assert.Equal(t, "child value", val)
	})
}
