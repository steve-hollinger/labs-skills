// Example 2: Batch Processing
//
// This example demonstrates efficient batch production and consumption
// patterns with franz-go.
//
// Learning objectives:
// - Produce messages in batches for better throughput
// - Configure batching parameters
// - Consume and process messages in batches
// - Understand the performance implications
//
// Prerequisites:
// - Kafka running on localhost:9092
// - Start with: make infra-up (from repository root)

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"sync/atomic"
	"time"

	"github.com/twmb/franz-go/pkg/kgo"
)

const (
	bootstrapServers = "localhost:9092"
	topic            = "franz-go-batch"
)

// Order represents an order event
type Order struct {
	OrderID    string    `json:"order_id"`
	CustomerID string    `json:"customer_id"`
	Amount     float64   `json:"amount"`
	Items      int       `json:"items"`
	CreatedAt  time.Time `json:"created_at"`
}

func main() {
	fmt.Println("============================================================")
	fmt.Println("Example 2: Batch Processing")
	fmt.Println("============================================================")

	// Run batch producer
	if err := runBatchProducer(); err != nil {
		fmt.Printf("Producer error: %v\n", err)
		fmt.Println("\nMake sure Kafka is running:")
		fmt.Println("  cd ../../../.. && make infra-up")
		return
	}

	time.Sleep(500 * time.Millisecond)

	// Run batch consumer
	if err := runBatchConsumer(); err != nil {
		fmt.Printf("Consumer error: %v\n", err)
		return
	}

	fmt.Println("\n============================================================")
	fmt.Println("Example completed successfully!")
	fmt.Println("============================================================")
}

func runBatchProducer() error {
	fmt.Println("\n--- PART 1: Batch Producer ---")

	// Create client with batching configuration
	client, err := kgo.NewClient(
		kgo.SeedBrokers(bootstrapServers),
		// Batching configuration
		kgo.ProducerLinger(10*time.Millisecond),      // Wait up to 10ms to batch
		kgo.ProducerBatchMaxBytes(1024*1024),         // 1MB max batch size
		kgo.ProducerBatchCompression(kgo.Lz4Compression()), // Compress batches
		kgo.RequiredAcks(kgo.AllISRAcks()),
	)
	if err != nil {
		return fmt.Errorf("failed to create client: %w", err)
	}
	defer client.Close()

	ctx := context.Background()
	numOrders := 1000

	fmt.Printf("\nProducing %d orders in batches to topic: %s\n", numOrders, topic)

	startTime := time.Now()
	var produced int64

	// Produce many messages - they will be batched automatically
	for i := 0; i < numOrders; i++ {
		order := Order{
			OrderID:    fmt.Sprintf("ord-%05d", i),
			CustomerID: fmt.Sprintf("cust-%03d", i%100),
			Amount:     float64(i%1000) + 0.99,
			Items:      (i % 10) + 1,
			CreatedAt:  time.Now(),
		}

		value, _ := json.Marshal(order)

		record := &kgo.Record{
			Topic: topic,
			Key:   []byte(order.CustomerID), // Partition by customer
			Value: value,
		}

		client.Produce(ctx, record, func(r *kgo.Record, err error) {
			if err == nil {
				atomic.AddInt64(&produced, 1)
			}
		})
	}

	// Flush all pending messages
	fmt.Println("\nFlushing batched messages...")
	if err := client.Flush(ctx); err != nil {
		return fmt.Errorf("flush failed: %w", err)
	}

	duration := time.Since(startTime)
	rate := float64(produced) / duration.Seconds()

	fmt.Printf("\nBatch Production Results:\n")
	fmt.Printf("  Messages: %d\n", produced)
	fmt.Printf("  Duration: %v\n", duration)
	fmt.Printf("  Rate: %.0f msgs/sec\n", rate)

	return nil
}

func runBatchConsumer() error {
	fmt.Println("\n--- PART 2: Batch Consumer ---")

	// Create client for consuming
	client, err := kgo.NewClient(
		kgo.SeedBrokers(bootstrapServers),
		kgo.ConsumerGroup("franz-go-batch-consumer"),
		kgo.ConsumeTopics(topic),
		kgo.ConsumeResetOffset(kgo.NewOffset().AtStart()),
		// Fetch configuration
		kgo.FetchMaxWait(time.Second),       // Max wait for batch
		kgo.FetchMaxBytes(5*1024*1024),      // 5MB max fetch
		kgo.FetchMaxPartitionBytes(1*1024*1024), // 1MB per partition
	)
	if err != nil {
		return fmt.Errorf("failed to create client: %w", err)
	}
	defer client.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	fmt.Printf("\nConsuming batches from topic: %s\n", topic)

	var totalConsumed int
	var totalBatches int
	var totalAmount float64
	emptyPolls := 0

	startTime := time.Now()

	for emptyPolls < 3 {
		// Poll for a batch of messages
		fetches := client.PollFetches(ctx)

		if ctx.Err() != nil {
			break
		}

		// Check for errors
		if errs := fetches.Errors(); len(errs) > 0 {
			for _, fetchErr := range errs {
				fmt.Printf("  [ERROR] %v\n", fetchErr.Err)
			}
		}

		// Get all records from this fetch
		records := fetches.Records()
		if len(records) == 0 {
			emptyPolls++
			continue
		}

		emptyPolls = 0
		totalBatches++
		batchAmount := 0.0

		// Process batch
		for _, record := range records {
			var order Order
			if err := json.Unmarshal(record.Value, &order); err != nil {
				continue
			}
			batchAmount += order.Amount
			totalConsumed++
		}

		totalAmount += batchAmount

		fmt.Printf("  Batch %d: %d records, total amount: $%.2f\n",
			totalBatches, len(records), batchAmount)

		// Commit after processing batch
		if err := client.CommitUncommittedOffsets(ctx); err != nil {
			fmt.Printf("  [WARN] Commit error: %v\n", err)
		}
	}

	duration := time.Since(startTime)
	rate := float64(totalConsumed) / duration.Seconds()

	fmt.Printf("\nBatch Consumption Results:\n")
	fmt.Printf("  Messages: %d\n", totalConsumed)
	fmt.Printf("  Batches: %d\n", totalBatches)
	fmt.Printf("  Avg batch size: %.0f\n", float64(totalConsumed)/float64(totalBatches))
	fmt.Printf("  Total amount: $%.2f\n", totalAmount)
	fmt.Printf("  Duration: %v\n", duration)
	fmt.Printf("  Rate: %.0f msgs/sec\n", rate)

	return nil
}
