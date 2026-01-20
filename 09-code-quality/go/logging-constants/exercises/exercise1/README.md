# Exercise 1: Define Logging Constants

## Objective

Create a complete set of logging constants for an e-commerce order service.

## Instructions

1. Create a `logkey` package with key constants
2. Create a `logmsg` package with message constants
3. Organize constants by domain (order, payment, inventory)
4. Add documentation comments for each constant

## Requirements

### Key Constants (logkey/keys.go)

Define constants for:
- Order identification (order_id, order_status)
- Customer identification (customer_id)
- Payment information (payment_id, payment_method, amount)
- Inventory (product_id, quantity, warehouse_id)
- Timing (duration_ms)
- Errors (error, error_code)

### Message Constants (logmsg/messages.go)

Define constants for:
- Order lifecycle (created, updated, completed, cancelled)
- Payment processing (started, completed, failed)
- Inventory operations (reserved, released, insufficient)

## Starting Point

The `main.go` file shows how the constants should be used.

## Expected Output

When running the program, you should see consistent, well-structured log output.

## Hints

- Use snake_case for all key names (order_id, not orderId)
- Group related constants together
- Add Go doc comments for IDE support
- Keep message constants concise but descriptive

## Verification

```bash
# Run the program
go run main.go

# Check that all logs use constants (no magic strings)
# The output should be consistent and readable
```
