package tests

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/suite"
)

// ============================================================================
// Example 2: Test Suites
// ============================================================================

// InMemoryUserStore is a simple in-memory user storage for testing
type InMemoryUserStore struct {
	users  map[int64]*StoreUser
	nextID int64
}

type StoreUser struct {
	ID    int64
	Name  string
	Email string
}

func NewInMemoryUserStore() *InMemoryUserStore {
	return &InMemoryUserStore{
		users:  make(map[int64]*StoreUser),
		nextID: 1,
	}
}

func (s *InMemoryUserStore) Create(user *StoreUser) error {
	user.ID = s.nextID
	s.nextID++
	s.users[user.ID] = user
	return nil
}

func (s *InMemoryUserStore) Get(id int64) (*StoreUser, error) {
	user, ok := s.users[id]
	if !ok {
		return nil, fmt.Errorf("user not found")
	}
	return user, nil
}

func (s *InMemoryUserStore) Update(user *StoreUser) error {
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

func (s *InMemoryUserStore) List() []*StoreUser {
	users := make([]*StoreUser, 0, len(s.users))
	for _, user := range s.users {
		users = append(users, user)
	}
	return users
}

func (s *InMemoryUserStore) Clear() {
	s.users = make(map[int64]*StoreUser)
	s.nextID = 1
}

// ============================================================================
// UserStoreSuite - Test suite for InMemoryUserStore
// ============================================================================

type UserStoreSuite struct {
	suite.Suite
	store    *InMemoryUserStore
	testUser *StoreUser
}

// SetupSuite runs once before all tests in the suite
func (s *UserStoreSuite) SetupSuite() {
	s.T().Log("SetupSuite: Creating user store")
	s.store = NewInMemoryUserStore()
}

// TearDownSuite runs once after all tests in the suite
func (s *UserStoreSuite) TearDownSuite() {
	s.T().Log("TearDownSuite: Cleaning up")
	s.store = nil
}

// SetupTest runs before each test
func (s *UserStoreSuite) SetupTest() {
	s.T().Log("SetupTest: Clearing store and creating test user")
	s.store.Clear()

	// Create a standard test fixture
	s.testUser = &StoreUser{
		Name:  "Test User",
		Email: "test@example.com",
	}
	err := s.store.Create(s.testUser)
	s.Require().NoError(err)
}

// TearDownTest runs after each test
func (s *UserStoreSuite) TearDownTest() {
	s.T().Log("TearDownTest: Test completed")
}

// TestExample2_CreateUser tests creating a new user
func (s *UserStoreSuite) TestExample2_CreateUser() {
	user := &StoreUser{
		Name:  "Alice",
		Email: "alice@example.com",
	}

	err := s.store.Create(user)

	s.NoError(err)
	s.NotZero(user.ID)
	s.Equal("Alice", user.Name)
}

// TestExample2_GetUser tests retrieving an existing user
func (s *UserStoreSuite) TestExample2_GetUser() {
	user, err := s.store.Get(s.testUser.ID)

	s.NoError(err)
	s.NotNil(user)
	s.Equal(s.testUser.Name, user.Name)
	s.Equal(s.testUser.Email, user.Email)
}

// TestExample2_GetUserNotFound tests retrieving a non-existent user
func (s *UserStoreSuite) TestExample2_GetUserNotFound() {
	_, err := s.store.Get(999)

	s.Error(err)
	s.ErrorContains(err, "not found")
}

// TestExample2_UpdateUser tests updating an existing user
func (s *UserStoreSuite) TestExample2_UpdateUser() {
	s.testUser.Name = "Updated Name"
	s.testUser.Email = "updated@example.com"

	err := s.store.Update(s.testUser)

	s.NoError(err)

	// Verify the update
	user, err := s.store.Get(s.testUser.ID)
	s.Require().NoError(err)
	s.Equal("Updated Name", user.Name)
	s.Equal("updated@example.com", user.Email)
}

// TestExample2_UpdateUserNotFound tests updating a non-existent user
func (s *UserStoreSuite) TestExample2_UpdateUserNotFound() {
	user := &StoreUser{ID: 999, Name: "Ghost"}

	err := s.store.Update(user)

	s.Error(err)
	s.ErrorContains(err, "not found")
}

// TestExample2_DeleteUser tests deleting a user
func (s *UserStoreSuite) TestExample2_DeleteUser() {
	err := s.store.Delete(s.testUser.ID)

	s.NoError(err)

	// Verify user is gone
	_, err = s.store.Get(s.testUser.ID)
	s.Error(err)
}

// TestExample2_DeleteUserNotFound tests deleting a non-existent user
func (s *UserStoreSuite) TestExample2_DeleteUserNotFound() {
	err := s.store.Delete(999)

	s.Error(err)
	s.ErrorContains(err, "not found")
}

// TestExample2_ListUsers tests listing all users
func (s *UserStoreSuite) TestExample2_ListUsers() {
	// Create additional users
	s.store.Create(&StoreUser{Name: "Alice", Email: "alice@example.com"})
	s.store.Create(&StoreUser{Name: "Bob", Email: "bob@example.com"})

	users := s.store.List()

	s.Len(users, 3) // testUser + 2 new users
}

// TestExample2_ClearStore tests clearing all users
func (s *UserStoreSuite) TestExample2_ClearStore() {
	s.store.Create(&StoreUser{Name: "Alice", Email: "alice@example.com"})
	s.store.Create(&StoreUser{Name: "Bob", Email: "bob@example.com"})

	s.store.Clear()

	s.Len(s.store.List(), 0)
}

// TestExample2Suite is the entry point for the suite - REQUIRED!
func TestExample2Suite(t *testing.T) {
	suite.Run(t, new(UserStoreSuite))
}

// ============================================================================
// CalculatorSuite - Another example suite
// ============================================================================

type CalculatorSuite struct {
	suite.Suite
	calc *SuiteCalculator
}

type SuiteCalculator struct{}

func (c *SuiteCalculator) Add(a, b int) int      { return a + b }
func (c *SuiteCalculator) Subtract(a, b int) int { return a - b }
func (c *SuiteCalculator) Multiply(a, b int) int { return a * b }
func (c *SuiteCalculator) Divide(a, b int) (int, error) {
	if b == 0 {
		return 0, fmt.Errorf("division by zero")
	}
	return a / b, nil
}

func (s *CalculatorSuite) SetupSuite() {
	s.calc = &SuiteCalculator{}
}

func (s *CalculatorSuite) TestExample2_Addition() {
	result := s.calc.Add(2, 3)
	s.Equal(5, result)
}

func (s *CalculatorSuite) TestExample2_Subtraction() {
	result := s.calc.Subtract(5, 3)
	s.Equal(2, result)
}

func (s *CalculatorSuite) TestExample2_Multiplication() {
	result := s.calc.Multiply(4, 3)
	s.Equal(12, result)
}

func (s *CalculatorSuite) TestExample2_Division() {
	result, err := s.calc.Divide(10, 2)
	s.Require().NoError(err)
	s.Equal(5, result)
}

func (s *CalculatorSuite) TestExample2_DivisionByZero() {
	_, err := s.calc.Divide(10, 0)
	s.Error(err)
	s.ErrorContains(err, "division by zero")
}

func TestCalculatorSuite(t *testing.T) {
	suite.Run(t, new(CalculatorSuite))
}
