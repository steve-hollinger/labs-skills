// Exercise 3: Mocking Practice
//
// In this exercise, you will create mocks for the PaymentGateway and
// NotificationService interfaces, then test the CheckoutService.
//
// Instructions:
// 1. Complete the mock implementations
// 2. Write tests using the mocks
// 3. Verify mock expectations are met
// 4. Run with: go test -v ./exercises/exercise3/...
//
// Expected: All tests should pass when completed correctly
package exercise3

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/mock"
)

// ============================================================================
// Interfaces to mock
// ============================================================================

type PaymentGateway interface {
	Charge(customerID string, amount float64) (transactionID string, err error)
	Refund(transactionID string) error
	GetBalance(customerID string) (float64, error)
}

type NotificationService interface {
	SendOrderConfirmation(email string, orderID int64) error
	SendPaymentReceipt(email string, transactionID string, amount float64) error
	SendRefundNotification(email string, transactionID string) error
}

// ============================================================================
// Service to test
// ============================================================================

type CheckoutService struct {
	payment      PaymentGateway
	notification NotificationService
}

func NewCheckoutService(payment PaymentGateway, notification NotificationService) *CheckoutService {
	return &CheckoutService{
		payment:      payment,
		notification: notification,
	}
}

type CheckoutRequest struct {
	CustomerID    string
	CustomerEmail string
	OrderID       int64
	Amount        float64
}

type CheckoutResult struct {
	TransactionID string
	Success       bool
}

func (s *CheckoutService) ProcessCheckout(req CheckoutRequest) (*CheckoutResult, error) {
	// Charge the customer
	txnID, err := s.payment.Charge(req.CustomerID, req.Amount)
	if err != nil {
		return nil, errors.New("payment failed: " + err.Error())
	}

	// Send notifications (don't fail checkout if notifications fail)
	_ = s.notification.SendOrderConfirmation(req.CustomerEmail, req.OrderID)
	_ = s.notification.SendPaymentReceipt(req.CustomerEmail, txnID, req.Amount)

	return &CheckoutResult{
		TransactionID: txnID,
		Success:       true,
	}, nil
}

func (s *CheckoutService) RefundOrder(customerEmail string, transactionID string) error {
	// Process refund
	if err := s.payment.Refund(transactionID); err != nil {
		return errors.New("refund failed: " + err.Error())
	}

	// Send notification
	if err := s.notification.SendRefundNotification(customerEmail, transactionID); err != nil {
		// Log but don't fail
		return nil
	}

	return nil
}

func (s *CheckoutService) CanAfford(customerID string, amount float64) (bool, error) {
	balance, err := s.payment.GetBalance(customerID)
	if err != nil {
		return false, err
	}
	return balance >= amount, nil
}

// ============================================================================
// Mock Implementations - TODO: Complete these
// ============================================================================

// MockPaymentGateway implements PaymentGateway
type MockPaymentGateway struct {
	mock.Mock
}

// TODO: Implement Charge method
// Hint: Use m.Called(customerID, amount) and return args.String(0), args.Error(1)
func (m *MockPaymentGateway) Charge(customerID string, amount float64) (string, error) {
	// Your code here:
	return "", nil
}

// TODO: Implement Refund method
func (m *MockPaymentGateway) Refund(transactionID string) error {
	// Your code here:
	return nil
}

// TODO: Implement GetBalance method
func (m *MockPaymentGateway) GetBalance(customerID string) (float64, error) {
	// Your code here:
	return 0, nil
}

// MockNotificationService implements NotificationService
type MockNotificationService struct {
	mock.Mock
}

// TODO: Implement SendOrderConfirmation method
func (m *MockNotificationService) SendOrderConfirmation(email string, orderID int64) error {
	// Your code here:
	return nil
}

// TODO: Implement SendPaymentReceipt method
func (m *MockNotificationService) SendPaymentReceipt(email string, transactionID string, amount float64) error {
	// Your code here:
	return nil
}

// TODO: Implement SendRefundNotification method
func (m *MockNotificationService) SendRefundNotification(email string, transactionID string) error {
	// Your code here:
	return nil
}

// ============================================================================
// Tests - TODO: Complete these
// ============================================================================

func TestProcessCheckout_Success(t *testing.T) {
	// TODO:
	// 1. Create mock instances
	// 2. Set up expectations:
	//    - payment.Charge should return "txn_123" and nil
	//    - notification.SendOrderConfirmation should return nil
	//    - notification.SendPaymentReceipt should return nil
	// 3. Create CheckoutService with mocks
	// 4. Call ProcessCheckout with a valid request
	// 5. Assert no error and result contains "txn_123"
	// 6. Assert all expectations were met

	// Your code here:
}

func TestProcessCheckout_PaymentFailed(t *testing.T) {
	// TODO:
	// 1. Set up payment.Charge to return an error
	// 2. Verify ProcessCheckout returns an error
	// 3. Verify notification methods were NOT called (payment failed first)
	// 4. Use mockNotification.AssertNotCalled()

	// Your code here:
}

func TestProcessCheckout_NotificationFails(t *testing.T) {
	// TODO:
	// 1. Set up payment.Charge to succeed
	// 2. Set up notifications to fail
	// 3. Verify ProcessCheckout STILL succeeds (notifications are non-critical)
	// 4. Verify all methods were still called

	// Your code here:
}

func TestRefundOrder_Success(t *testing.T) {
	// TODO:
	// 1. Set up payment.Refund to succeed
	// 2. Set up notification.SendRefundNotification to succeed
	// 3. Verify RefundOrder returns no error
	// 4. Verify both methods were called with correct arguments

	// Your code here:
}

func TestRefundOrder_RefundFailed(t *testing.T) {
	// TODO:
	// 1. Set up payment.Refund to return an error
	// 2. Verify RefundOrder returns an error
	// 3. Verify notification was NOT called

	// Your code here:
}

func TestCanAfford_HasBalance(t *testing.T) {
	// TODO:
	// 1. Set up payment.GetBalance to return 100.00
	// 2. Check if customer can afford 50.00
	// 3. Verify result is true

	// Your code here:
}

func TestCanAfford_InsufficientBalance(t *testing.T) {
	// TODO:
	// 1. Set up payment.GetBalance to return 30.00
	// 2. Check if customer can afford 50.00
	// 3. Verify result is false

	// Your code here:
}

func TestCanAfford_BalanceError(t *testing.T) {
	// TODO:
	// 1. Set up payment.GetBalance to return an error
	// 2. Verify CanAfford returns the error

	// Your code here:
}

// Bonus: Table-driven test with mocks
func TestProcessCheckout_TableDriven(t *testing.T) {
	// TODO: Create a table-driven test that covers:
	// - Successful checkout
	// - Payment declined
	// - Insufficient funds error

	// Your code here:
}
