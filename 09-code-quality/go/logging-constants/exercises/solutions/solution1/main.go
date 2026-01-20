// Solution 1: E-Commerce Order Service Logging
//
// This solution demonstrates proper use of logging constants.
package main

import (
	"fmt"
	"log/slog"
	"os"
	"time"
)

// Import our logging packages (in practice, these would be separate files)
// For this solution, constants are defined inline to keep it self-contained

// Log key constants
const (
	KeyOrderID       = "order_id"
	KeyCustomerID    = "customer_id"
	KeyPaymentID     = "payment_id"
	KeyPaymentMethod = "payment_method"
	KeyProductID     = "product_id"
	KeyQuantity      = "quantity"
	KeyAmount        = "amount"
	KeyStatus        = "status"
	KeyDuration      = "duration_ms"
	KeyError         = "error"
	KeyComponent     = "component"
	KeyOperation     = "operation"
	KeyWarehouseID   = "warehouse_id"
)

// Log message constants
const (
	MsgOrderCreated       = "order created"
	MsgOrderCompleted     = "order completed"
	MsgPaymentStarted     = "payment processing started"
	MsgPaymentCompleted   = "payment completed"
	MsgInventoryReserved  = "inventory reserved"
	MsgInventoryChecked   = "inventory checked"
)

func main() {
	fmt.Println("Solution 1: E-Commerce Order Service Logging")
	fmt.Println("==============================================")
	fmt.Println()

	logger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelDebug,
	}))

	// Simulate order processing
	processOrder(logger, "ord-12345", "cust-789")

	fmt.Println()
	fmt.Println("=== Key Points ===")
	fmt.Println("1. All log keys use constants (KeyOrderID, KeyCustomerID, etc.)")
	fmt.Println("2. All log messages use constants (MsgOrderCreated, etc.)")
	fmt.Println("3. Consistent snake_case naming throughout")
	fmt.Println("4. Easy to search for all uses of a key in the codebase")
}

func processOrder(logger *slog.Logger, orderID, customerID string) {
	// Add order context to all logs
	orderLogger := logger.With(
		KeyComponent, "order_processor",
		KeyOrderID, orderID,
		KeyCustomerID, customerID,
	)

	start := time.Now()

	// Create order
	orderLogger.Info(MsgOrderCreated,
		KeyStatus, "pending",
	)

	// Check inventory
	checkInventory(orderLogger, "prod-001", 2)

	// Reserve inventory
	reserveInventory(orderLogger, "prod-001", 2, "warehouse-east")

	// Process payment
	processPayment(orderLogger, "pay-abc123", 99.99)

	// Complete order
	orderLogger.Info(MsgOrderCompleted,
		KeyDuration, time.Since(start).Milliseconds(),
		KeyStatus, "completed",
	)
}

func checkInventory(logger *slog.Logger, productID string, quantity int) {
	invLogger := logger.With(
		KeyOperation, "check_inventory",
	)

	invLogger.Debug(MsgInventoryChecked,
		KeyProductID, productID,
		KeyQuantity, quantity,
	)
}

func reserveInventory(logger *slog.Logger, productID string, quantity int, warehouseID string) {
	invLogger := logger.With(
		KeyOperation, "reserve_inventory",
	)

	time.Sleep(10 * time.Millisecond) // Simulate work

	invLogger.Info(MsgInventoryReserved,
		KeyProductID, productID,
		KeyQuantity, quantity,
		KeyWarehouseID, warehouseID,
	)
}

func processPayment(logger *slog.Logger, paymentID string, amount float64) {
	payLogger := logger.With(
		KeyOperation, "process_payment",
		KeyPaymentID, paymentID,
	)

	payLogger.Info(MsgPaymentStarted,
		KeyAmount, amount,
		KeyPaymentMethod, "credit_card",
	)

	time.Sleep(50 * time.Millisecond) // Simulate processing

	payLogger.Info(MsgPaymentCompleted,
		KeyAmount, amount,
		KeyStatus, "success",
	)
}
