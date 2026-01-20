// Package logkey provides standardized log field key constants for an e-commerce service.
package logkey

// Order identification keys
const (
	// OrderID uniquely identifies an order
	OrderID = "order_id"

	// OrderStatus represents the current status of an order
	OrderStatus = "order_status"

	// OrderTotal represents the total amount of an order
	OrderTotal = "order_total"
)

// Customer identification keys
const (
	// CustomerID uniquely identifies a customer
	CustomerID = "customer_id"

	// CustomerEmail is the customer's email (use with caution - PII)
	CustomerEmail = "customer_email"
)

// Payment keys
const (
	// PaymentID uniquely identifies a payment
	PaymentID = "payment_id"

	// PaymentMethod indicates how payment was made (card, paypal, etc.)
	PaymentMethod = "payment_method"

	// PaymentAmount is the payment amount
	PaymentAmount = "payment_amount"

	// PaymentStatus is the status of the payment
	PaymentStatus = "payment_status"

	// Currency is the payment currency
	Currency = "currency"
)

// Inventory keys
const (
	// ProductID uniquely identifies a product
	ProductID = "product_id"

	// ProductName is the name of the product
	ProductName = "product_name"

	// Quantity is the quantity of items
	Quantity = "quantity"

	// WarehouseID identifies the warehouse
	WarehouseID = "warehouse_id"

	// SKU is the stock keeping unit
	SKU = "sku"

	// AvailableStock is the available stock count
	AvailableStock = "available_stock"
)

// Timing keys
const (
	// DurationMS is the duration in milliseconds
	DurationMS = "duration_ms"

	// Timestamp is a generic timestamp
	Timestamp = "timestamp"
)

// Error keys
const (
	// Error is the error message
	Error = "error"

	// ErrorCode is a machine-readable error code
	ErrorCode = "error_code"

	// ErrorType categorizes the error
	ErrorType = "error_type"
)

// Generic keys
const (
	// RequestID is the request identifier
	RequestID = "request_id"

	// Component identifies the service component
	Component = "component"

	// Operation identifies the operation being performed
	Operation = "operation"

	// Status is a generic status field
	Status = "status"
)
