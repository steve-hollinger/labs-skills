// Tests for Kafka franz-go examples
//
// These tests verify the basic functionality works correctly.
// Integration tests require a running Kafka instance.

package tests

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Event represents a test event
type Event struct {
	ID        string    `json:"id"`
	Type      string    `json:"type"`
	Data      string    `json:"data"`
	Timestamp time.Time `json:"timestamp"`
}

// Order represents a test order
type Order struct {
	OrderID    string    `json:"order_id"`
	CustomerID string    `json:"customer_id"`
	Amount     float64   `json:"amount"`
	Items      int       `json:"items"`
	CreatedAt  time.Time `json:"created_at"`
}

func TestEventSerialization(t *testing.T) {
	event := Event{
		ID:        "evt-001",
		Type:      "user.login",
		Data:      "User logged in",
		Timestamp: time.Now(),
	}

	// Serialize
	data, err := json.Marshal(event)
	require.NoError(t, err)
	assert.NotEmpty(t, data)

	// Deserialize
	var decoded Event
	err = json.Unmarshal(data, &decoded)
	require.NoError(t, err)

	assert.Equal(t, event.ID, decoded.ID)
	assert.Equal(t, event.Type, decoded.Type)
	assert.Equal(t, event.Data, decoded.Data)
}

func TestOrderSerialization(t *testing.T) {
	order := Order{
		OrderID:    "ord-001",
		CustomerID: "cust-001",
		Amount:     99.99,
		Items:      3,
		CreatedAt:  time.Now(),
	}

	// Serialize
	data, err := json.Marshal(order)
	require.NoError(t, err)
	assert.NotEmpty(t, data)

	// Deserialize
	var decoded Order
	err = json.Unmarshal(data, &decoded)
	require.NoError(t, err)

	assert.Equal(t, order.OrderID, decoded.OrderID)
	assert.Equal(t, order.CustomerID, decoded.CustomerID)
	assert.InDelta(t, order.Amount, decoded.Amount, 0.001)
	assert.Equal(t, order.Items, decoded.Items)
}

func TestEventRouting(t *testing.T) {
	testCases := []struct {
		eventType string
		expected  string
	}{
		{"user.created", "user-events"},
		{"user.updated", "user-events"},
		{"order.placed", "order-events"},
		{"order.shipped", "order-events"},
		{"payment.completed", "payment-events"},
		{"payment.failed", "payment-events"},
		{"unknown.event", "unknown-events"},
		{"something.else", "unknown-events"},
	}

	for _, tc := range testCases {
		t.Run(tc.eventType, func(t *testing.T) {
			result := routeEvent(tc.eventType)
			assert.Equal(t, tc.expected, result)
		})
	}
}

// routeEvent simulates the routing logic from exercise 1
func routeEvent(eventType string) string {
	prefix := ""
	for i, c := range eventType {
		if c == '.' {
			prefix = eventType[:i]
			break
		}
	}

	switch prefix {
	case "user":
		return "user-events"
	case "order":
		return "order-events"
	case "payment":
		return "payment-events"
	default:
		return "unknown-events"
	}
}

func TestBatchProcessing(t *testing.T) {
	// Test batch processing logic
	orders := make([]Order, 100)
	for i := 0; i < 100; i++ {
		orders[i] = Order{
			OrderID:    "ord-" + string(rune('0'+i%10)),
			CustomerID: "cust-" + string(rune('0'+i%5)),
			Amount:     float64(i) + 0.99,
			Items:      i%5 + 1,
		}
	}

	// Calculate totals
	var totalAmount float64
	var totalItems int
	for _, order := range orders {
		totalAmount += order.Amount
		totalItems += order.Items
	}

	assert.Greater(t, totalAmount, 0.0)
	assert.Equal(t, 300, totalItems) // Sum of (i%5+1) for i=0..99
}

// Integration tests would go here, marked with build tags or skipped
// func TestKafkaIntegration(t *testing.T) {
//     t.Skip("Requires running Kafka instance")
// }
