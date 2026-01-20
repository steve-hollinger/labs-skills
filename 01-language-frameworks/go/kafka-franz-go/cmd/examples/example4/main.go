// Example 4: Event-Driven Service
//
// This example demonstrates a complete event-driven service with
// graceful shutdown, error handling, and structured logging.
//
// Learning objectives:
// - Build a production-ready Kafka service
// - Implement graceful shutdown with signals
// - Handle errors and retries appropriately
// - Use structured patterns for event processing
//
// Prerequisites:
// - Kafka running on localhost:9092
// - Start with: make infra-up (from repository root)

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"

	"github.com/twmb/franz-go/pkg/kgo"
)

const (
	bootstrapServers = "localhost:9092"
	inputTopic       = "orders-input"
	outputTopic      = "orders-processed"
)

// Order represents an incoming order
type Order struct {
	OrderID    string    `json:"order_id"`
	CustomerID string    `json:"customer_id"`
	Items      []Item    `json:"items"`
	CreatedAt  time.Time `json:"created_at"`
}

// Item represents an order item
type Item struct {
	ProductID string  `json:"product_id"`
	Quantity  int     `json:"quantity"`
	Price     float64 `json:"price"`
}

// ProcessedOrder represents the output after processing
type ProcessedOrder struct {
	OrderID     string    `json:"order_id"`
	CustomerID  string    `json:"customer_id"`
	TotalAmount float64   `json:"total_amount"`
	ItemCount   int       `json:"item_count"`
	ProcessedAt time.Time `json:"processed_at"`
	Status      string    `json:"status"`
}

// OrderProcessor handles order processing
type OrderProcessor struct {
	client    *kgo.Client
	processed int
	errors    int
	mu        sync.Mutex
}

func NewOrderProcessor() (*OrderProcessor, error) {
	client, err := kgo.NewClient(
		kgo.SeedBrokers(bootstrapServers),
		kgo.ConsumerGroup("order-processor-service"),
		kgo.ConsumeTopics(inputTopic),
		kgo.ConsumeResetOffset(kgo.NewOffset().AtStart()),

		// Production-ready settings
		kgo.RequiredAcks(kgo.AllISRAcks()),
		kgo.ProducerLinger(5*time.Millisecond),
		kgo.SessionTimeout(10*time.Second),

		// Rebalance callbacks
		kgo.OnPartitionsAssigned(func(ctx context.Context, c *kgo.Client, assigned map[string][]int32) {
			for topic, partitions := range assigned {
				fmt.Printf("[INFO] Assigned %s: %v\n", topic, partitions)
			}
		}),
		kgo.OnPartitionsRevoked(func(ctx context.Context, c *kgo.Client, revoked map[string][]int32) {
			c.CommitUncommittedOffsets(ctx)
			for topic, partitions := range revoked {
				fmt.Printf("[INFO] Revoked %s: %v\n", topic, partitions)
			}
		}),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create client: %w", err)
	}

	return &OrderProcessor{
		client: client,
	}, nil
}

func (p *OrderProcessor) ProcessOrder(order *Order) (*ProcessedOrder, error) {
	// Calculate totals
	var totalAmount float64
	var itemCount int

	for _, item := range order.Items {
		totalAmount += item.Price * float64(item.Quantity)
		itemCount += item.Quantity
	}

	// Simulate some processing
	time.Sleep(10 * time.Millisecond)

	return &ProcessedOrder{
		OrderID:     order.OrderID,
		CustomerID:  order.CustomerID,
		TotalAmount: totalAmount,
		ItemCount:   itemCount,
		ProcessedAt: time.Now(),
		Status:      "completed",
	}, nil
}

func (p *OrderProcessor) Run(ctx context.Context) error {
	fmt.Println("[INFO] Order processor starting...")

	for {
		fetches := p.client.PollFetches(ctx)

		// Check for shutdown
		if ctx.Err() != nil {
			fmt.Println("[INFO] Context cancelled, shutting down...")
			break
		}

		// Handle fetch errors
		if errs := fetches.Errors(); len(errs) > 0 {
			for _, fetchErr := range errs {
				fmt.Printf("[ERROR] Fetch: %v\n", fetchErr.Err)
			}
			continue
		}

		// Process records
		fetches.EachRecord(func(r *kgo.Record) {
			p.processRecord(ctx, r)
		})

		// Commit after processing
		if err := p.client.CommitUncommittedOffsets(ctx); err != nil {
			fmt.Printf("[ERROR] Commit: %v\n", err)
		}
	}

	return nil
}

func (p *OrderProcessor) processRecord(ctx context.Context, r *kgo.Record) {
	// Parse order
	var order Order
	if err := json.Unmarshal(r.Value, &order); err != nil {
		fmt.Printf("[ERROR] Parse order: %v\n", err)
		p.mu.Lock()
		p.errors++
		p.mu.Unlock()
		return
	}

	// Process order
	processed, err := p.ProcessOrder(&order)
	if err != nil {
		fmt.Printf("[ERROR] Process order %s: %v\n", order.OrderID, err)
		p.mu.Lock()
		p.errors++
		p.mu.Unlock()
		return
	}

	// Produce result
	value, _ := json.Marshal(processed)
	p.client.Produce(ctx, &kgo.Record{
		Topic: outputTopic,
		Key:   []byte(processed.OrderID),
		Value: value,
	}, func(r *kgo.Record, err error) {
		if err != nil {
			fmt.Printf("[ERROR] Produce result: %v\n", err)
		}
	})

	p.mu.Lock()
	p.processed++
	if p.processed%10 == 0 || p.processed <= 5 {
		fmt.Printf("[INFO] Processed order %s (total: %d)\n", order.OrderID, p.processed)
	}
	p.mu.Unlock()
}

func (p *OrderProcessor) Stats() (int, int) {
	p.mu.Lock()
	defer p.mu.Unlock()
	return p.processed, p.errors
}

func (p *OrderProcessor) Close() {
	p.client.Flush(context.Background())
	p.client.Close()
}

func produceTestOrders(count int) error {
	client, err := kgo.NewClient(kgo.SeedBrokers(bootstrapServers))
	if err != nil {
		return err
	}
	defer client.Close()

	ctx := context.Background()

	for i := 0; i < count; i++ {
		order := Order{
			OrderID:    fmt.Sprintf("ord-%05d", i),
			CustomerID: fmt.Sprintf("cust-%03d", i%50),
			Items: []Item{
				{ProductID: "prod-001", Quantity: 1 + i%3, Price: 29.99},
				{ProductID: "prod-002", Quantity: 1, Price: 49.99},
			},
			CreatedAt: time.Now(),
		}

		value, _ := json.Marshal(order)
		client.Produce(ctx, &kgo.Record{
			Topic: inputTopic,
			Key:   []byte(order.CustomerID),
			Value: value,
		}, nil)
	}

	return client.Flush(ctx)
}

func main() {
	fmt.Println("============================================================")
	fmt.Println("Example 4: Event-Driven Order Processing Service")
	fmt.Println("============================================================")

	// Produce test orders
	fmt.Println("\n[INFO] Producing test orders...")
	if err := produceTestOrders(100); err != nil {
		fmt.Printf("[ERROR] Failed to produce orders: %v\n", err)
		fmt.Println("\nMake sure Kafka is running:")
		fmt.Println("  cd ../../../.. && make infra-up")
		return
	}
	fmt.Println("[INFO] Produced 100 test orders")

	time.Sleep(500 * time.Millisecond)

	// Create processor
	processor, err := NewOrderProcessor()
	if err != nil {
		fmt.Printf("[ERROR] Failed to create processor: %v\n", err)
		return
	}

	// Setup signal handling for graceful shutdown
	ctx, cancel := context.WithCancel(context.Background())
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)

	// Handle shutdown in goroutine
	go func() {
		select {
		case sig := <-sigCh:
			fmt.Printf("\n[INFO] Received signal: %v\n", sig)
			cancel()
		case <-time.After(20 * time.Second):
			fmt.Println("\n[INFO] Timeout reached")
			cancel()
		}
	}()

	// Run processor
	fmt.Println("\n[INFO] Starting order processor...")
	fmt.Println("[INFO] Press Ctrl+C to shutdown gracefully\n")

	if err := processor.Run(ctx); err != nil {
		fmt.Printf("[ERROR] Processor error: %v\n", err)
	}

	// Cleanup
	fmt.Println("\n[INFO] Cleaning up...")
	processor.Close()

	// Print stats
	processed, errors := processor.Stats()
	fmt.Println("\n============================================================")
	fmt.Println("Service Statistics")
	fmt.Println("============================================================")
	fmt.Printf("  Orders processed: %d\n", processed)
	fmt.Printf("  Errors: %d\n", errors)
	fmt.Println("\n[INFO] Service shutdown complete")
}
