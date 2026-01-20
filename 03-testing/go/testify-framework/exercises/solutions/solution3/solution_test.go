// Solution for Exercise 3: Mocking Practice
package solution3

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

// Interfaces (same as exercise)
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

// Service (same as exercise)
type CheckoutService struct {
	payment      PaymentGateway
	notification NotificationService
}

func NewCheckoutService(payment PaymentGateway, notification NotificationService) *CheckoutService {
	return &CheckoutService{payment: payment, notification: notification}
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
	txnID, err := s.payment.Charge(req.CustomerID, req.Amount)
	if err != nil {
		return nil, errors.New("payment failed: " + err.Error())
	}
	_ = s.notification.SendOrderConfirmation(req.CustomerEmail, req.OrderID)
	_ = s.notification.SendPaymentReceipt(req.CustomerEmail, txnID, req.Amount)
	return &CheckoutResult{TransactionID: txnID, Success: true}, nil
}

func (s *CheckoutService) RefundOrder(customerEmail string, transactionID string) error {
	if err := s.payment.Refund(transactionID); err != nil {
		return errors.New("refund failed: " + err.Error())
	}
	_ = s.notification.SendRefundNotification(customerEmail, transactionID)
	return nil
}

func (s *CheckoutService) CanAfford(customerID string, amount float64) (bool, error) {
	balance, err := s.payment.GetBalance(customerID)
	if err != nil {
		return false, err
	}
	return balance >= amount, nil
}

// Mock Implementations - SOLUTION
type MockPaymentGateway struct {
	mock.Mock
}

func (m *MockPaymentGateway) Charge(customerID string, amount float64) (string, error) {
	args := m.Called(customerID, amount)
	return args.String(0), args.Error(1)
}

func (m *MockPaymentGateway) Refund(transactionID string) error {
	args := m.Called(transactionID)
	return args.Error(0)
}

func (m *MockPaymentGateway) GetBalance(customerID string) (float64, error) {
	args := m.Called(customerID)
	return args.Get(0).(float64), args.Error(1)
}

type MockNotificationService struct {
	mock.Mock
}

func (m *MockNotificationService) SendOrderConfirmation(email string, orderID int64) error {
	args := m.Called(email, orderID)
	return args.Error(0)
}

func (m *MockNotificationService) SendPaymentReceipt(email string, transactionID string, amount float64) error {
	args := m.Called(email, transactionID, amount)
	return args.Error(0)
}

func (m *MockNotificationService) SendRefundNotification(email string, transactionID string) error {
	args := m.Called(email, transactionID)
	return args.Error(0)
}

// Tests - SOLUTION
func TestProcessCheckout_Success(t *testing.T) {
	mockPayment := new(MockPaymentGateway)
	mockNotification := new(MockNotificationService)

	mockPayment.On("Charge", "cust_123", 99.99).Return("txn_123", nil)
	mockNotification.On("SendOrderConfirmation", "test@example.com", int64(1)).Return(nil)
	mockNotification.On("SendPaymentReceipt", "test@example.com", "txn_123", 99.99).Return(nil)

	service := NewCheckoutService(mockPayment, mockNotification)

	result, err := service.ProcessCheckout(CheckoutRequest{
		CustomerID:    "cust_123",
		CustomerEmail: "test@example.com",
		OrderID:       1,
		Amount:        99.99,
	})

	require.NoError(t, err)
	assert.Equal(t, "txn_123", result.TransactionID)
	assert.True(t, result.Success)

	mockPayment.AssertExpectations(t)
	mockNotification.AssertExpectations(t)
}

func TestProcessCheckout_PaymentFailed(t *testing.T) {
	mockPayment := new(MockPaymentGateway)
	mockNotification := new(MockNotificationService)

	mockPayment.On("Charge", mock.Anything, mock.Anything).Return("", errors.New("card declined"))

	service := NewCheckoutService(mockPayment, mockNotification)

	result, err := service.ProcessCheckout(CheckoutRequest{
		CustomerID:    "cust_123",
		CustomerEmail: "test@example.com",
		OrderID:       1,
		Amount:        99.99,
	})

	require.Error(t, err)
	assert.Nil(t, result)
	assert.Contains(t, err.Error(), "payment failed")

	mockPayment.AssertExpectations(t)
	mockNotification.AssertNotCalled(t, "SendOrderConfirmation", mock.Anything, mock.Anything)
	mockNotification.AssertNotCalled(t, "SendPaymentReceipt", mock.Anything, mock.Anything, mock.Anything)
}

func TestProcessCheckout_NotificationFails(t *testing.T) {
	mockPayment := new(MockPaymentGateway)
	mockNotification := new(MockNotificationService)

	mockPayment.On("Charge", mock.Anything, mock.Anything).Return("txn_123", nil)
	mockNotification.On("SendOrderConfirmation", mock.Anything, mock.Anything).Return(errors.New("email failed"))
	mockNotification.On("SendPaymentReceipt", mock.Anything, mock.Anything, mock.Anything).Return(errors.New("email failed"))

	service := NewCheckoutService(mockPayment, mockNotification)

	result, err := service.ProcessCheckout(CheckoutRequest{
		CustomerID:    "cust_123",
		CustomerEmail: "test@example.com",
		OrderID:       1,
		Amount:        99.99,
	})

	// Checkout should STILL succeed even if notifications fail
	require.NoError(t, err)
	assert.True(t, result.Success)

	mockPayment.AssertExpectations(t)
	mockNotification.AssertExpectations(t)
}

func TestRefundOrder_Success(t *testing.T) {
	mockPayment := new(MockPaymentGateway)
	mockNotification := new(MockNotificationService)

	mockPayment.On("Refund", "txn_123").Return(nil)
	mockNotification.On("SendRefundNotification", "test@example.com", "txn_123").Return(nil)

	service := NewCheckoutService(mockPayment, mockNotification)

	err := service.RefundOrder("test@example.com", "txn_123")

	require.NoError(t, err)
	mockPayment.AssertCalled(t, "Refund", "txn_123")
	mockNotification.AssertCalled(t, "SendRefundNotification", "test@example.com", "txn_123")
}

func TestRefundOrder_RefundFailed(t *testing.T) {
	mockPayment := new(MockPaymentGateway)
	mockNotification := new(MockNotificationService)

	mockPayment.On("Refund", "txn_123").Return(errors.New("refund not allowed"))

	service := NewCheckoutService(mockPayment, mockNotification)

	err := service.RefundOrder("test@example.com", "txn_123")

	require.Error(t, err)
	assert.Contains(t, err.Error(), "refund failed")
	mockNotification.AssertNotCalled(t, "SendRefundNotification", mock.Anything, mock.Anything)
}

func TestCanAfford_HasBalance(t *testing.T) {
	mockPayment := new(MockPaymentGateway)
	mockNotification := new(MockNotificationService)

	mockPayment.On("GetBalance", "cust_123").Return(100.00, nil)

	service := NewCheckoutService(mockPayment, mockNotification)

	canAfford, err := service.CanAfford("cust_123", 50.00)

	require.NoError(t, err)
	assert.True(t, canAfford)
}

func TestCanAfford_InsufficientBalance(t *testing.T) {
	mockPayment := new(MockPaymentGateway)
	mockNotification := new(MockNotificationService)

	mockPayment.On("GetBalance", "cust_123").Return(30.00, nil)

	service := NewCheckoutService(mockPayment, mockNotification)

	canAfford, err := service.CanAfford("cust_123", 50.00)

	require.NoError(t, err)
	assert.False(t, canAfford)
}

func TestCanAfford_BalanceError(t *testing.T) {
	mockPayment := new(MockPaymentGateway)
	mockNotification := new(MockNotificationService)

	mockPayment.On("GetBalance", "cust_123").Return(0.0, errors.New("service unavailable"))

	service := NewCheckoutService(mockPayment, mockNotification)

	_, err := service.CanAfford("cust_123", 50.00)

	require.Error(t, err)
}

func TestProcessCheckout_TableDriven(t *testing.T) {
	tests := []struct {
		name          string
		request       CheckoutRequest
		setupMocks    func(*MockPaymentGateway, *MockNotificationService)
		wantErr       bool
		wantTxnID     string
	}{
		{
			name: "successful checkout",
			request: CheckoutRequest{
				CustomerID:    "cust_1",
				CustomerEmail: "test@example.com",
				OrderID:       1,
				Amount:        50.00,
			},
			setupMocks: func(p *MockPaymentGateway, n *MockNotificationService) {
				p.On("Charge", "cust_1", 50.00).Return("txn_success", nil)
				n.On("SendOrderConfirmation", mock.Anything, mock.Anything).Return(nil)
				n.On("SendPaymentReceipt", mock.Anything, mock.Anything, mock.Anything).Return(nil)
			},
			wantErr:   false,
			wantTxnID: "txn_success",
		},
		{
			name: "payment declined",
			request: CheckoutRequest{
				CustomerID:    "cust_bad",
				CustomerEmail: "bad@example.com",
				OrderID:       2,
				Amount:        100.00,
			},
			setupMocks: func(p *MockPaymentGateway, n *MockNotificationService) {
				p.On("Charge", mock.Anything, mock.Anything).Return("", errors.New("card declined"))
			},
			wantErr: true,
		},
		{
			name: "insufficient funds",
			request: CheckoutRequest{
				CustomerID:    "cust_poor",
				CustomerEmail: "poor@example.com",
				OrderID:       3,
				Amount:        1000.00,
			},
			setupMocks: func(p *MockPaymentGateway, n *MockNotificationService) {
				p.On("Charge", mock.Anything, mock.Anything).Return("", errors.New("insufficient funds"))
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mockPayment := new(MockPaymentGateway)
			mockNotification := new(MockNotificationService)
			tt.setupMocks(mockPayment, mockNotification)

			service := NewCheckoutService(mockPayment, mockNotification)
			result, err := service.ProcessCheckout(tt.request)

			if tt.wantErr {
				require.Error(t, err)
				assert.Nil(t, result)
			} else {
				require.NoError(t, err)
				assert.Equal(t, tt.wantTxnID, result.TransactionID)
			}

			mockPayment.AssertExpectations(t)
			mockNotification.AssertExpectations(t)
		})
	}
}
