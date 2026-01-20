// Package logmsg provides standardized log message constants for an e-commerce service.
package logmsg

// Order lifecycle messages
const (
	// OrderCreated indicates a new order was created
	OrderCreated = "order created"

	// OrderUpdated indicates an order was updated
	OrderUpdated = "order updated"

	// OrderCompleted indicates an order was completed
	OrderCompleted = "order completed"

	// OrderCancelled indicates an order was cancelled
	OrderCancelled = "order cancelled"

	// OrderShipped indicates an order was shipped
	OrderShipped = "order shipped"

	// OrderDelivered indicates an order was delivered
	OrderDelivered = "order delivered"
)

// Payment messages
const (
	// PaymentStarted indicates payment processing has begun
	PaymentStarted = "payment processing started"

	// PaymentCompleted indicates payment was successful
	PaymentCompleted = "payment completed"

	// PaymentFailed indicates payment failed
	PaymentFailed = "payment failed"

	// PaymentRefunded indicates payment was refunded
	PaymentRefunded = "payment refunded"

	// PaymentPending indicates payment is pending
	PaymentPending = "payment pending"
)

// Inventory messages
const (
	// InventoryReserved indicates inventory was reserved for an order
	InventoryReserved = "inventory reserved"

	// InventoryReleased indicates reserved inventory was released
	InventoryReleased = "inventory released"

	// InventoryInsufficient indicates not enough inventory
	InventoryInsufficient = "insufficient inventory"

	// InventoryUpdated indicates inventory levels were updated
	InventoryUpdated = "inventory updated"

	// InventoryChecked indicates inventory was checked
	InventoryChecked = "inventory checked"
)

// General operation messages
const (
	// OperationStarted indicates an operation began
	OperationStarted = "operation started"

	// OperationCompleted indicates an operation completed
	OperationCompleted = "operation completed"

	// OperationFailed indicates an operation failed
	OperationFailed = "operation failed"

	// ValidationFailed indicates validation failed
	ValidationFailed = "validation failed"
)
