// Example 2: Test Suites
//
// This file demonstrates testify suite package for organizing tests.
// See tests/example2_test.go for the actual test suite implementation.
//
// Run with: go test -v -run TestExample2 ./tests/...
package main

import "fmt"

// InMemoryUserStore is a simple in-memory user storage
type InMemoryUserStore struct {
	users map[int64]*User
	nextID int64
}

type User struct {
	ID    int64
	Name  string
	Email string
}

func NewInMemoryUserStore() *InMemoryUserStore {
	return &InMemoryUserStore{
		users:  make(map[int64]*User),
		nextID: 1,
	}
}

func (s *InMemoryUserStore) Create(user *User) error {
	user.ID = s.nextID
	s.nextID++
	s.users[user.ID] = user
	return nil
}

func (s *InMemoryUserStore) Get(id int64) (*User, error) {
	user, ok := s.users[id]
	if !ok {
		return nil, fmt.Errorf("user not found")
	}
	return user, nil
}

func (s *InMemoryUserStore) Update(user *User) error {
	if _, ok := s.users[user.ID]; !ok {
		return fmt.Errorf("user not found")
	}
	s.users[user.ID] = user
	return nil
}

func (s *InMemoryUserStore) Delete(id int64) error {
	if _, ok := s.users[id]; !ok {
		return fmt.Errorf("user not found")
	}
	delete(s.users, id)
	return nil
}

func (s *InMemoryUserStore) List() []*User {
	users := make([]*User, 0, len(s.users))
	for _, user := range s.users {
		users = append(users, user)
	}
	return users
}

func (s *InMemoryUserStore) Clear() {
	s.users = make(map[int64]*User)
	s.nextID = 1
}

func main() {
	fmt.Println("Example 2: Test Suites")
	fmt.Println("======================")
	fmt.Println()
	fmt.Println("This example demonstrates testify suite package.")
	fmt.Println("Run the tests to see suites in action:")
	fmt.Println()
	fmt.Println("  go test -v -run TestExample2 ./tests/...")
	fmt.Println()
	fmt.Println("Key concepts demonstrated:")
	fmt.Println("  - suite.Suite embedding")
	fmt.Println("  - SetupSuite / TearDownSuite (once per suite)")
	fmt.Println("  - SetupTest / TearDownTest (per test)")
	fmt.Println("  - Suite assertion methods (s.Equal, s.NoError)")
	fmt.Println("  - s.Require() for stopping assertions")
	fmt.Println("  - Shared state between tests")
}
