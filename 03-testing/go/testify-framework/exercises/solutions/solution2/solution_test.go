// Solution for Exercise 2: Test Suites Practice
package solution2

import (
	"errors"
	"testing"
	"time"

	"github.com/stretchr/testify/suite"
)

// Code to test (same as exercise)
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

// Solution
type OrderServiceSuite struct {
	suite.Suite
	store      *OrderStore
	testOrder  *Order
	testUserID int64
}

func (s *OrderServiceSuite) SetupSuite() {
	s.T().Log("SetupSuite: Initialize order store")
	s.store = NewOrderStore()
}

func (s *OrderServiceSuite) TearDownSuite() {
	s.T().Log("TearDownSuite: Cleanup")
	s.store = nil
}

func (s *OrderServiceSuite) SetupTest() {
	s.T().Log("SetupTest: Create test fixtures")
	s.store.Clear()
	s.testUserID = 100

	s.testOrder = &Order{
		UserID: s.testUserID,
		Items: []OrderItem{
			{ProductID: 1, Name: "Widget", Price: 10.00, Quantity: 2},
		},
	}
	err := s.store.Create(s.testOrder)
	s.Require().NoError(err)
}

func (s *OrderServiceSuite) TearDownTest() {
	s.T().Log("TearDownTest: Test completed")
}

func (s *OrderServiceSuite) TestCreateOrder() {
	order := &Order{
		UserID: s.testUserID,
		Items: []OrderItem{
			{ProductID: 2, Name: "Gadget", Price: 25.00, Quantity: 1},
		},
	}

	err := s.store.Create(order)

	s.NoError(err)
	s.NotZero(order.ID)
	s.Equal("pending", order.Status)
	s.Greater(order.Total, 0.0)
	s.Equal(25.00, order.Total)
}

func (s *OrderServiceSuite) TestCreateOrderNoItems() {
	order := &Order{
		UserID: s.testUserID,
		Items:  []OrderItem{},
	}

	err := s.store.Create(order)

	s.Error(err)
	s.ErrorContains(err, "at least one item")
}

func (s *OrderServiceSuite) TestGetOrder() {
	order, err := s.store.Get(s.testOrder.ID)

	s.Require().NoError(err)
	s.Equal(s.testOrder.ID, order.ID)
	s.Equal(s.testOrder.UserID, order.UserID)
}

func (s *OrderServiceSuite) TestGetOrderNotFound() {
	_, err := s.store.Get(999)

	s.Error(err)
	s.ErrorContains(err, "not found")
}

func (s *OrderServiceSuite) TestUpdateStatus() {
	err := s.store.UpdateStatus(s.testOrder.ID, "confirmed")

	s.NoError(err)

	order, err := s.store.Get(s.testOrder.ID)
	s.Require().NoError(err)
	s.Equal("confirmed", order.Status)
}

func (s *OrderServiceSuite) TestUpdateStatusInvalid() {
	err := s.store.UpdateStatus(s.testOrder.ID, "invalid_status")

	s.Error(err)
	s.ErrorContains(err, "invalid")
}

func (s *OrderServiceSuite) TestListByUser() {
	// Create 2 more orders
	s.store.Create(&Order{
		UserID: s.testUserID,
		Items:  []OrderItem{{ProductID: 2, Name: "Item2", Price: 5.00, Quantity: 1}},
	})
	s.store.Create(&Order{
		UserID: s.testUserID,
		Items:  []OrderItem{{ProductID: 3, Name: "Item3", Price: 15.00, Quantity: 1}},
	})

	orders := s.store.ListByUser(s.testUserID)

	s.Len(orders, 3)
}

func (s *OrderServiceSuite) TestListByUserEmpty() {
	orders := s.store.ListByUser(999)

	s.Empty(orders)
}

func (s *OrderServiceSuite) TestOrderTotal() {
	order := &Order{
		UserID: s.testUserID,
		Items: []OrderItem{
			{ProductID: 1, Name: "Item1", Price: 10.00, Quantity: 2},  // 20.00
			{ProductID: 2, Name: "Item2", Price: 5.50, Quantity: 3},   // 16.50
		},
	}

	err := s.store.Create(order)

	s.Require().NoError(err)
	s.Equal(36.50, order.Total)
}

func TestOrderServiceSuite(t *testing.T) {
	suite.Run(t, new(OrderServiceSuite))
}
