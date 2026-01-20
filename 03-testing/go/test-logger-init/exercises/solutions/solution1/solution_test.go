// Solution for Exercise 1: Implement TestMain
package solution1

import (
	"os"
	"testing"

	"github.com/stretchr/testify/require"
)

// Key-Value Store (same as exercise)
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

// Package-level test resources
var testStore *KVStore

// TestMain - SOLUTION
func TestMain(m *testing.M) {
	// 1. SETUP
	testStore = NewKVStore()
	testStore.Set("version", "1.0.0")

	// 2. RUN TESTS
	code := m.Run()

	// 3. TEARDOWN
	if testStore != nil {
		testStore.Close()
	}

	// 4. EXIT with test result code
	os.Exit(code)
}

// Helper functions - SOLUTION

func clearStore(t *testing.T) {
	t.Helper()
	testStore.Clear()
	// Re-seed config after clear
	testStore.Set("version", "1.0.0")
}

func setTestData(t *testing.T, key, value string) {
	t.Helper()
	testStore.Set(key, value)

	// Register cleanup to delete the key when test completes
	t.Cleanup(func() {
		testStore.Delete(key)
	})
}

func requireValue(t *testing.T, key string) string {
	t.Helper()
	value, ok := testStore.Get(key)
	require.True(t, ok, "key %s should exist", key)
	return value
}

// Tests - SOLUTION

func TestSetupVerification(t *testing.T) {
	require.NotNil(t, testStore, "testStore should be initialized by TestMain")

	version, ok := testStore.Get("version")
	require.True(t, ok, "version should exist")
	require.Equal(t, "1.0.0", version)
}

func TestSetAndGet(t *testing.T) {
	clearStore(t)
	setTestData(t, "test:key", "test:value")

	value := requireValue(t, "test:key")
	require.Equal(t, "test:value", value)
}

func TestIsolation(t *testing.T) {
	clearStore(t)

	// This test should not see data from other tests
	_, ok := testStore.Get("other:test:key")
	require.False(t, ok, "test isolation failed")
}

func TestCleanup(t *testing.T) {
	clearStore(t)
	setTestData(t, "cleanup:key", "cleanup:value")

	// Verify data exists during test
	value := requireValue(t, "cleanup:key")
	require.Equal(t, "cleanup:value", value)

	// Cleanup registered by setTestData will delete the key
}
