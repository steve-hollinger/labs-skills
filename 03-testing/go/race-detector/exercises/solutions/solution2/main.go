// Solution for Exercise 2: Fix the Map Race
//
// This solution uses sync.RWMutex to protect the map with optimized read access.
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

// UserCache stores users by ID - now thread-safe with RWMutex
type UserCache struct {
	mu    sync.RWMutex   // RWMutex for optimized read/write locking
	users map[int]*User
}

// NewUserCache creates a new cache
func NewUserCache() *UserCache {
	return &UserCache{
		users: make(map[int]*User),
	}
}

// Get retrieves a user by ID - uses RLock for read-only access
func (c *UserCache) Get(id int) (*User, bool) {
	c.mu.RLock()         // Read lock - multiple readers allowed
	defer c.mu.RUnlock()
	user, ok := c.users[id]
	return user, ok
}

// Set stores a user - uses Lock for exclusive write access
func (c *UserCache) Set(user *User) {
	c.mu.Lock()         // Write lock - exclusive access
	defer c.mu.Unlock()
	c.users[user.ID] = user
}

// Count returns the number of users - uses RLock for read-only access
func (c *UserCache) Count() int {
	c.mu.RLock()
	defer c.mu.RUnlock()
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

/*
Key Changes:
1. Added sync.RWMutex field to UserCache struct
2. Used RLock/RUnlock for read operations (Get, Count)
3. Used Lock/Unlock for write operations (Set)
4. Used defer for all Unlock calls

Why RWMutex instead of Mutex?
- RWMutex allows multiple concurrent readers
- Only blocks when a writer needs access
- Better performance when reads are more frequent than writes

Alternative Solution using sync.Map:

type UserCache struct {
    users sync.Map
}

func (c *UserCache) Get(id int) (*User, bool) {
    v, ok := c.users.Load(id)
    if !ok {
        return nil, false
    }
    return v.(*User), true
}

func (c *UserCache) Set(user *User) {
    c.users.Store(user.ID, user)
}

func (c *UserCache) Count() int {
    count := 0
    c.users.Range(func(_, _ interface{}) bool {
        count++
        return true
    })
    return count
}

sync.Map is simpler but has trade-offs:
- No type safety (uses interface{})
- Count() is expensive (must iterate)
- Best for "mostly read" or disjoint write patterns
*/
