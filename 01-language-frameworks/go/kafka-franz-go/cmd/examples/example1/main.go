// Example 1: Basic Producer and Consumer
//
// This example demonstrates the fundamentals of producing and consuming
// messages with franz-go.
//
// Learning objectives:
// - Create a Kafka client with franz-go
// - Produce messages with delivery callbacks
// - Consume messages with PollFetches
// - Understand basic error handling
//
// Prerequisites:
// - Kafka running on localhost:9092
// - Start with: make infra-up (from repository root)

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"

	"github.com/twmb/franz-go/pkg/kgo"
)

const (
	bootstrapServers = "localhost:9092"
	topic            = "franz-go-basic"
)

// Event represents a simple event structure
type Event struct {
	ID        string    `json:"id"`
	Type      string    `json:"type"`
	Data      string    `json:"data"`
	Timestamp time.Time `json:"timestamp"`
}

func main() {
	fmt.Println("============================================================")
	fmt.Println("Example 1: Basic Producer and Consumer")
	fmt.Println("============================================================")

	// Run producer
	if err := runProducer(); err != nil {
		fmt.Printf("Producer error: %v\n", err)
		fmt.Println("\nMake sure Kafka is running:")
		fmt.Println("  cd ../../../.. && make infra-up")
		return
	}

	// Give Kafka a moment to persist messages
	time.Sleep(500 * time.Millisecond)

	// Run consumer
	if err := runConsumer(); err != nil {
		fmt.Printf("Consumer error: %v\n", err)
		return
	}

	fmt.Println("\n============================================================")
	fmt.Println("Example completed successfully!")
	fmt.Println("============================================================")
}

func runProducer() error {
	fmt.Println("\n--- PART 1: Basic Producer ---")

	// Create a client for producing
	client, err := kgo.NewClient(
		kgo.SeedBrokers(bootstrapServers),
		// Wait for all replicas to acknowledge
		kgo.RequiredAcks(kgo.AllISRAcks()),
	)
	if err != nil {
		return fmt.Errorf("failed to create client: %w", err)
	}
	defer client.Close()

	ctx := context.Background()

	// Create sample events
	events := []Event{
		{ID: "evt-001", Type: "user.login", Data: "User john logged in", Timestamp: time.Now()},
		{ID: "evt-002", Type: "user.action", Data: "User john viewed dashboard", Timestamp: time.Now()},
		{ID: "evt-003", Type: "user.logout", Data: "User john logged out", Timestamp: time.Now()},
	}

	fmt.Printf("\nProducing %d events to topic: %s\n\n", len(events), topic)

	var wg sync.WaitGroup
	var mu sync.Mutex
	produced := 0

	for _, event := range events {
		// Serialize event to JSON
		value, err := json.Marshal(event)
		if err != nil {
			return fmt.Errorf("failed to marshal event: %w", err)
		}

		// Create a Kafka record
		record := &kgo.Record{
			Topic: topic,
			Key:   []byte(event.ID),
			Value: value,
			Headers: []kgo.RecordHeader{
				{Key: "event-type", Value: []byte(event.Type)},
			},
		}

		wg.Add(1)

		// Produce asynchronously with callback
		client.Produce(ctx, record, func(r *kgo.Record, err error) {
			defer wg.Done()

			mu.Lock()
			defer mu.Unlock()

			if err != nil {
				fmt.Printf("  [ERROR] Failed to produce %s: %v\n", event.ID, err)
				return
			}

			produced++
			fmt.Printf("  [OK] Produced %s to partition %d at offset %d\n",
				event.ID, r.Partition, r.Offset)
		})
	}

	// Wait for all deliveries
	fmt.Println("\nWaiting for deliveries...")
	wg.Wait()

	// Alternative: use Flush instead of WaitGroup
	// client.Flush(ctx)

	fmt.Printf("\nProduced %d/%d events successfully\n", produced, len(events))

	return nil
}

func runConsumer() error {
	fmt.Println("\n--- PART 2: Basic Consumer ---")

	// Create a client for consuming
	client, err := kgo.NewClient(
		kgo.SeedBrokers(bootstrapServers),
		kgo.ConsumerGroup("franz-go-basic-consumer"),
		kgo.ConsumeTopics(topic),
		// Start from the earliest offset
		kgo.ConsumeResetOffset(kgo.NewOffset().AtStart()),
	)
	if err != nil {
		return fmt.Errorf("failed to create client: %w", err)
	}
	defer client.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	fmt.Printf("\nConsuming from topic: %s\n", topic)
	fmt.Println("(Will timeout after 10 seconds)\n")

	consumed := 0
	maxMessages := 10
	emptyPolls := 0

	for consumed < maxMessages && emptyPolls < 5 {
		// Poll for messages
		fetches := client.PollFetches(ctx)

		// Check for context cancellation
		if ctx.Err() != nil {
			break
		}

		// Check for errors
		if errs := fetches.Errors(); len(errs) > 0 {
			for _, fetchErr := range errs {
				fmt.Printf("  [ERROR] Fetch error: %v\n", fetchErr.Err)
			}
		}

		// Get records
		records := fetches.Records()
		if len(records) == 0 {
			emptyPolls++
			continue
		}

		emptyPolls = 0

		// Process each record
		for _, record := range records {
			consumed++

			// Deserialize the event
			var event Event
			if err := json.Unmarshal(record.Value, &event); err != nil {
				fmt.Printf("  [WARN] Failed to unmarshal record: %v\n", err)
				continue
			}

			// Get header value
			var eventType string
			for _, h := range record.Headers {
				if h.Key == "event-type" {
					eventType = string(h.Value)
					break
				}
			}

			fmt.Printf("  [MSG %d] Partition: %d, Offset: %d\n", consumed, record.Partition, record.Offset)
			fmt.Printf("          Key: %s\n", record.Key)
			fmt.Printf("          Type: %s\n", eventType)
			fmt.Printf("          Data: %s\n\n", event.Data)
		}

		// Commit offsets after processing
		if err := client.CommitUncommittedOffsets(ctx); err != nil {
			fmt.Printf("  [WARN] Commit error: %v\n", err)
		}
	}

	fmt.Printf("Consumed %d messages\n", consumed)

	return nil
}
