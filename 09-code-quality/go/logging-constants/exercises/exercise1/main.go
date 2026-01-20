// Exercise 1: Define Logging Constants
//
// This file shows how the logging constants should be used.
// Your task is to create the logkey and logmsg packages.
package main

import (
	"fmt"
	"log/slog"
	"os"
	"time"

	// TODO: Create these packages
	// "exercise1/logkey"
	// "exercise1/logmsg"
)

// TODO: Remove these placeholders once you create the packages
// These are here so the code compiles before you start
const (
	// logkey placeholders - move to logkey/keys.go
	KeyOrderID       = "order_id"
	KeyCustomerID    = "customer_id"
	KeyPaymentID     = "payment_id"
	KeyProductID     = "product_id"
	KeyQuantity      = "quantity"
	KeyAmount        = "amount"
	KeyStatus        = "status"
	KeyDuration      = "duration_ms"
	KeyError         = "error"

	// logmsg placeholders - move to logmsg/messages.go
	MsgOrderCreated      = "order created"
	MsgOrderCompleted    = "order completed"
	MsgPaymentStarted    = "payment processing started"
	MsgPaymentCompleted  = "payment completed"
	MsgInventoryReserved = "inventory reserved"
)

func main() {
	fmt.Println("Exercise 1: E-Commerce Order Service Logging")
	fmt.Println("==============================================")
	fmt.Println()

	logger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelDebug,
	}))

	// Simulate order processing
	processOrder(logger, "ord-12345", "cust-789")
}

func processOrder(logger *slog.Logger, orderID, customerID string) {
	start := time.Now()

	// Create order
	logger.Info(MsgOrderCreated,
		KeyOrderID, orderID,
		KeyCustomerID, customerID,
		KeyStatus, "pending",
	)

	// Reserve inventory
	logger.Info(MsgInventoryReserved,
		KeyOrderID, orderID,
		KeyProductID, "prod-001",
		KeyQuantity, 2,
	)

	// Process payment
	logger.Info(MsgPaymentStarted,
		KeyOrderID, orderID,
		KeyPaymentID, "pay-abc123",
		KeyAmount, 99.99,
	)

	time.Sleep(50 * time.Millisecond) // Simulate processing

	logger.Info(MsgPaymentCompleted,
		KeyOrderID, orderID,
		KeyPaymentID, "pay-abc123",
		KeyStatus, "success",
	)

	// Complete order
	logger.Info(MsgOrderCompleted,
		KeyOrderID, orderID,
		KeyCustomerID, customerID,
		KeyDuration, time.Since(start).Milliseconds(),
	)
}
