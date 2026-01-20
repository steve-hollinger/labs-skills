// Exercise 1: Implement TestMain
//
// In this exercise, you will implement TestMain for a package that tests
// a key-value store.
//
// Instructions:
// 1. Implement TestMain with proper setup and teardown
// 2. Initialize the testStore in setup
// 3. Clean up resources in teardown
// 4. Implement the helper functions
// 5. Run with: go test -v ./exercises/exercise1/...
//
// Expected: All tests should pass when completed correctly
package exercise1

import (
	"os"
	"testing"
)

// ============================================================================
// Key-Value Store to test
// ============================================================================

type KVStore struct {
	data map[string]string
}

func NewKVStore() *KVStore {
	return &KVStore{data: make(map[string]string)}
}

func (s *KVStore) Set(key, value string) {
	s.data[key] = value
}

func (s *KVStore) Get(key string) (string, bool) {
	val, ok := s.data[key]
	return val, ok
}

func (s *KVStore) Delete(key string) {
	delete(s.data, key)
}

func (s *KVStore) Clear() {
	s.data = make(map[string]string)
}

func (s *KVStore) Close() {
	s.Clear()
}

// ============================================================================
// Package-level test resources - TODO: Initialize in TestMain
// ============================================================================

var testStore *KVStore

// ============================================================================
// TestMain - TODO: Implement this
// ============================================================================

func TestMain(m *testing.M) {
	// TODO: Implement TestMain
	//
	// 1. SETUP: Initialize testStore
	//    - Create a new KVStore
	//    - Seed it with config data: "version" -> "1.0.0"
	//
	// 2. RUN: Execute tests with m.Run()
	//    - Capture the return code
	//
	// 3. TEARDOWN: Clean up resources
	//    - Close the testStore if it's not nil
	//
	// 4. EXIT: Call os.Exit with the test result code
	//    - CRITICAL: Don't forget this!

	// Your code here:

	// Placeholder - replace with proper implementation
	os.Exit(m.Run())
}

// ============================================================================
// Helper functions - TODO: Implement these
// ============================================================================

// clearStore clears the test store for test isolation
// TODO: Add t.Helper() and implement
func clearStore(t *testing.T) {
	// Your code here:
}

// setTestData sets up test data and registers cleanup
// TODO: Add t.Helper(), set the data, and register cleanup with t.Cleanup
func setTestData(t *testing.T, key, value string) {
	// Your code here:
}

// requireValue gets a value and fails if not found
// TODO: Add t.Helper() and implement with proper assertions
func requireValue(t *testing.T, key string) string {
	// Your code here:
	return ""
}

// ============================================================================
// Tests - These should pass when TestMain and helpers are implemented
// ============================================================================

func TestSetupVerification(t *testing.T) {
	// TODO: Uncomment and fix after implementing TestMain
	// if testStore == nil {
	// 	t.Fatal("testStore should be initialized by TestMain")
	// }
	//
	// version, ok := testStore.Get("version")
	// if !ok || version != "1.0.0" {
	// 	t.Fatal("testStore should have seeded config data")
	// }
}

func TestSetAndGet(t *testing.T) {
	// TODO: Uncomment after implementing helpers
	// clearStore(t)
	// setTestData(t, "test:key", "test:value")
	//
	// value := requireValue(t, "test:key")
	// if value != "test:value" {
	// 	t.Errorf("expected test:value, got %s", value)
	// }
}

func TestIsolation(t *testing.T) {
	// TODO: Uncomment after implementing helpers
	// clearStore(t)
	//
	// // This test should not see data from other tests
	// _, ok := testStore.Get("other:test:key")
	// if ok {
	// 	t.Error("test isolation failed - saw data from other test")
	// }
}

func TestCleanup(t *testing.T) {
	// TODO: Uncomment after implementing helpers
	// clearStore(t)
	// setTestData(t, "cleanup:key", "cleanup:value")
	//
	// // Verify data exists
	// _ = requireValue(t, "cleanup:key")
	//
	// // After test completes, cleanup should delete the key
	// // (This is verified by the test framework)
}
