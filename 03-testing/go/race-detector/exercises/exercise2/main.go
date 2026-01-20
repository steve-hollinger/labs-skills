// Exercise 2: Fix the Map Race
//
// This code has a race condition when accessing a map concurrently.
// Maps in Go are not safe for concurrent use.
//
// Instructions:
// 1. Run this code: go run main.go
// 2. Run with race detector: go run -race main.go
// 3. Notice the race condition (may panic: "concurrent map writes")
// 4. Fix the UserCache to be thread-safe
// 5. Verify with: go run -race main.go
//
// Expected Output (after fix):
// - All 100 users should be in the cache
// - No race detector warnings or panics
//
// Hints:
// - Use sync.RWMutex for better read performance
// - RLock/RUnlock for reads, Lock/Unlock for writes
// - Or use sync.Map for a simpler solution
package main

import (
	"fmt"
	"sync"
)

// User represents a cached user
type User struct {
	ID   int
	Name string
}

// UserCache stores users by ID - fix the race condition!
type UserCache struct {
	// TODO: Add synchronization
	users map[int]*User
}

// NewUserCache creates a new cache
func NewUserCache() *UserCache {
	return &UserCache{
		users: make(map[int]*User),
	}
}

// Get retrieves a user by ID - fix the race condition!
func (c *UserCache) Get(id int) (*User, bool) {
	// TODO: Add proper locking for reads
	user, ok := c.users[id]
	return user, ok
}

// Set stores a user - fix the race condition!
func (c *UserCache) Set(user *User) {
	// TODO: Add proper locking for writes
	c.users[user.ID] = user
}

// Count returns the number of users - fix the race condition!
func (c *UserCache) Count() int {
	// TODO: Add proper locking for reads
	return len(c.users)
}

func main() {
	cache := NewUserCache()
	var wg sync.WaitGroup

	// Concurrent writes
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			cache.Set(&User{ID: id, Name: fmt.Sprintf("User%d", id)})
		}(i)
	}

	// Concurrent reads while writes are happening
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			cache.Get(id)
		}(i)
	}

	wg.Wait()

	fmt.Printf("Expected users: 100\n")
	fmt.Printf("Actual users:   %d\n", cache.Count())

	if cache.Count() == 100 {
		fmt.Println("SUCCESS! All users in cache.")
	} else {
		fmt.Println("FAILED! Some users missing due to race condition.")
	}
}
