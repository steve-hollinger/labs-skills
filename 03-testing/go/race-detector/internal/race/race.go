// Package race provides utilities for demonstrating and testing race conditions.
package race

import (
	"sync"
	"sync/atomic"
)

// UnsafeCounter demonstrates a counter with race conditions.
// DO NOT use in production - this is for educational purposes only.
type UnsafeCounter struct {
	value int
}

// Inc increments the counter (NOT thread-safe).
func (c *UnsafeCounter) Inc() {
	c.value++
}

// Value returns the current value (NOT thread-safe).
func (c *UnsafeCounter) Value() int {
	return c.value
}

// SafeCounter is a thread-safe counter using mutex.
type SafeCounter struct {
	mu    sync.Mutex
	value int
}

// Inc increments the counter safely.
func (c *SafeCounter) Inc() {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.value++
}

// Value returns the current value safely.
func (c *SafeCounter) Value() int {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.value
}

// AtomicCounter is a thread-safe counter using atomic operations.
type AtomicCounter struct {
	value int64
}

// Inc increments the counter atomically.
func (c *AtomicCounter) Inc() {
	atomic.AddInt64(&c.value, 1)
}

// Value returns the current value atomically.
func (c *AtomicCounter) Value() int64 {
	return atomic.LoadInt64(&c.value)
}

// UnsafeCache demonstrates a cache with race conditions.
// DO NOT use in production - this is for educational purposes only.
type UnsafeCache struct {
	Data map[string]interface{}
}

// NewUnsafeCache creates a new unsafe cache.
func NewUnsafeCache() *UnsafeCache {
	return &UnsafeCache{Data: make(map[string]interface{})}
}

// Get retrieves a value (NOT thread-safe).
func (c *UnsafeCache) Get(key string) (interface{}, bool) {
	v, ok := c.Data[key]
	return v, ok
}

// Set stores a value (NOT thread-safe).
func (c *UnsafeCache) Set(key string, value interface{}) {
	c.Data[key] = value
}

// SafeCache is a thread-safe cache using RWMutex.
type SafeCache struct {
	mu   sync.RWMutex
	data map[string]interface{}
}

// NewSafeCache creates a new safe cache.
func NewSafeCache() *SafeCache {
	return &SafeCache{data: make(map[string]interface{})}
}

// Get retrieves a value safely.
func (c *SafeCache) Get(key string) (interface{}, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()
	v, ok := c.data[key]
	return v, ok
}

// Set stores a value safely.
func (c *SafeCache) Set(key string, value interface{}) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.data[key] = value
}

// Delete removes a value safely.
func (c *SafeCache) Delete(key string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	delete(c.data, key)
}

// Len returns the number of items safely.
func (c *SafeCache) Len() int {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return len(c.data)
}
