// Exercise 2: Test Suites Practice
//
// In this exercise, you will create a test suite for the OrderService.
// The suite should use setup/teardown methods to manage test fixtures.
//
// Instructions:
// 1. Complete the OrderServiceSuite struct with necessary fields
// 2. Implement SetupSuite, TearDownSuite, SetupTest, TearDownTest
// 3. Write test methods that start with Test
// 4. Run with: go test -v ./exercises/exercise2/...
//
// Expected: All tests should pass when completed correctly
package exercise2

import (
	"errors"
	"testing"
	"time"

	"github.com/stretchr/testify/suite"
)

// ============================================================================
// Code to test
// ============================================================================

type Order struct {
	ID        int64
	UserID    int64
	Items     []OrderItem
	Status    string
	Total     float64
	CreatedAt time.Time
}

type OrderItem struct {
	ProductID int64
	Name      string
	Price     float64
	Quantity  int
}

type OrderStore struct {
	orders map[int64]*Order
	nextID int64
}

func NewOrderStore() *OrderStore {
	return &OrderStore{
		orders: make(map[int64]*Order),
		nextID: 1,
	}
}

func (s *OrderStore) Create(order *Order) error {
	if len(order.Items) == 0 {
		return errors.New("order must have at least one item")
	}
	order.ID = s.nextID
	s.nextID++
	order.Status = "pending"
	order.CreatedAt = time.Now()

	// Calculate total
	var total float64
	for _, item := range order.Items {
		total += item.Price * float64(item.Quantity)
	}
	order.Total = total

	s.orders[order.ID] = order
	return nil
}

func (s *OrderStore) Get(id int64) (*Order, error) {
	order, ok := s.orders[id]
	if !ok {
		return nil, errors.New("order not found")
	}
	return order, nil
}

func (s *OrderStore) UpdateStatus(id int64, status string) error {
	order, ok := s.orders[id]
	if !ok {
		return errors.New("order not found")
	}
	validStatuses := map[string]bool{
		"pending":   true,
		"confirmed": true,
		"shipped":   true,
		"delivered": true,
		"cancelled": true,
	}
	if !validStatuses[status] {
		return errors.New("invalid status")
	}
	order.Status = status
	return nil
}

func (s *OrderStore) ListByUser(userID int64) []*Order {
	var result []*Order
	for _, order := range s.orders {
		if order.UserID == userID {
			result = append(result, order)
		}
	}
	return result
}

func (s *OrderStore) Clear() {
	s.orders = make(map[int64]*Order)
	s.nextID = 1
}

// ============================================================================
// Test Suite to complete
// ============================================================================

type OrderServiceSuite struct {
	suite.Suite
	// TODO: Add fields:
	// - store: *OrderStore (the store we're testing)
	// - testOrder: *Order (a fixture order for tests)
	// - testUserID: int64 (a fixture user ID)
}

// SetupSuite runs once before all tests
func (s *OrderServiceSuite) SetupSuite() {
	// TODO: Initialize the store
	// This is where you'd set up expensive resources like database connections
	s.T().Log("SetupSuite: Initialize order store")
}

// TearDownSuite runs once after all tests
func (s *OrderServiceSuite) TearDownSuite() {
	// TODO: Clean up any resources
	s.T().Log("TearDownSuite: Cleanup")
}

// SetupTest runs before each test
func (s *OrderServiceSuite) SetupTest() {
	// TODO:
	// 1. Clear the store
	// 2. Set testUserID to a value like 100
	// 3. Create a testOrder with:
	//    - UserID: testUserID
	//    - Items: at least one item (e.g., ProductID: 1, Name: "Widget", Price: 10.00, Quantity: 2)
	// 4. Save the testOrder using s.store.Create()
	// 5. Use s.Require().NoError() to ensure setup succeeded
	s.T().Log("SetupTest: Create test fixtures")
}

// TearDownTest runs after each test
func (s *OrderServiceSuite) TearDownTest() {
	// Nothing to do here, but good to have
	s.T().Log("TearDownTest: Test completed")
}

// TestCreateOrder tests creating a new order
func (s *OrderServiceSuite) TestCreateOrder() {
	// TODO:
	// 1. Create a new order with different items
	// 2. Use s.NoError() to check creation succeeded
	// 3. Use s.NotZero() to check ID was assigned
	// 4. Use s.Equal() to check status is "pending"
	// 5. Use s.Greater() to check total is > 0
}

// TestCreateOrderNoItems tests that orders require items
func (s *OrderServiceSuite) TestCreateOrderNoItems() {
	// TODO:
	// 1. Try to create an order with empty Items
	// 2. Use s.Error() to check an error was returned
	// 3. Use s.ErrorContains() to verify the message
}

// TestGetOrder tests retrieving an existing order
func (s *OrderServiceSuite) TestGetOrder() {
	// TODO:
	// 1. Get the testOrder by its ID
	// 2. Use s.Require().NoError() for the error
	// 3. Use s.Equal() to compare with s.testOrder
}

// TestGetOrderNotFound tests retrieving a non-existent order
func (s *OrderServiceSuite) TestGetOrderNotFound() {
	// TODO:
	// 1. Try to get order ID 999
	// 2. Verify error is returned with "not found"
}

// TestUpdateStatus tests updating order status
func (s *OrderServiceSuite) TestUpdateStatus() {
	// TODO:
	// 1. Update testOrder status to "confirmed"
	// 2. Verify no error
	// 3. Get the order and verify status changed
}

// TestUpdateStatusInvalid tests invalid status
func (s *OrderServiceSuite) TestUpdateStatusInvalid() {
	// TODO:
	// 1. Try to update status to "invalid_status"
	// 2. Verify error contains "invalid"
}

// TestListByUser tests listing orders for a user
func (s *OrderServiceSuite) TestListByUser() {
	// TODO:
	// 1. Create 2 more orders for testUserID
	// 2. List orders by testUserID
	// 3. Use s.Len() to verify 3 orders (1 from SetupTest + 2 new)
}

// TestListByUserEmpty tests listing for user with no orders
func (s *OrderServiceSuite) TestListByUserEmpty() {
	// TODO:
	// 1. List orders for a different user (e.g., 999)
	// 2. Verify the list is empty
}

// TestOrderTotal tests that total is calculated correctly
func (s *OrderServiceSuite) TestOrderTotal() {
	// TODO:
	// 1. Create an order with known items:
	//    - Item 1: Price 10.00, Quantity 2 = 20.00
	//    - Item 2: Price 5.50, Quantity 3 = 16.50
	// 2. Verify total is 36.50
}

// Entry point for the suite - REQUIRED!
func TestOrderServiceSuite(t *testing.T) {
	suite.Run(t, new(OrderServiceSuite))
}
