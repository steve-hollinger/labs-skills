// Example 3: Consumer Groups and Rebalancing
//
// This example demonstrates consumer groups with proper rebalance
// handling using franz-go.
//
// Learning objectives:
// - Configure consumer groups
// - Handle partition assignment and revocation
// - Implement proper rebalance callbacks
// - Understand consumer group coordination
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
	topic            = "franz-go-groups"
	groupID          = "franz-go-consumer-group"
)

// Message represents a simple message
type Message struct {
	ID        int       `json:"id"`
	Content   string    `json:"content"`
	Timestamp time.Time `json:"timestamp"`
}

func main() {
	fmt.Println("============================================================")
	fmt.Println("Example 3: Consumer Groups and Rebalancing")
	fmt.Println("============================================================")

	// Produce test messages
	if err := produceMessages(50); err != nil {
		fmt.Printf("Producer error: %v\n", err)
		fmt.Println("\nMake sure Kafka is running:")
		fmt.Println("  cd ../../../.. && make infra-up")
		return
	}

	time.Sleep(500 * time.Millisecond)

	// Run multiple consumers in the same group
	if err := runConsumerGroup(); err != nil {
		fmt.Printf("Consumer error: %v\n", err)
		return
	}

	fmt.Println("\n============================================================")
	fmt.Println("Example completed successfully!")
	fmt.Println("============================================================")
}

func produceMessages(count int) error {
	fmt.Println("\n--- PART 1: Producing Test Messages ---")

	client, err := kgo.NewClient(
		kgo.SeedBrokers(bootstrapServers),
	)
	if err != nil {
		return err
	}
	defer client.Close()

	ctx := context.Background()

	fmt.Printf("\nProducing %d messages to topic: %s\n", count, topic)

	for i := 0; i < count; i++ {
		msg := Message{
			ID:        i,
			Content:   fmt.Sprintf("Message %d", i),
			Timestamp: time.Now(),
		}
		value, _ := json.Marshal(msg)

		// Use message ID as key to distribute across partitions
		key := fmt.Sprintf("key-%d", i%5)

		client.Produce(ctx, &kgo.Record{
			Topic: topic,
			Key:   []byte(key),
			Value: value,
		}, nil)
	}

	client.Flush(ctx)
	fmt.Printf("  Produced %d messages\n", count)

	return nil
}

// ConsumerWorker represents a consumer in the group
type ConsumerWorker struct {
	ID         string
	client     *kgo.Client
	partitions map[int32]bool
	mu         sync.Mutex
	processed  int
}

func (w *ConsumerWorker) onAssigned(ctx context.Context, client *kgo.Client, assigned map[string][]int32) {
	w.mu.Lock()
	defer w.mu.Unlock()

	for topic, partitions := range assigned {
		for _, p := range partitions {
			w.partitions[p] = true
		}
		fmt.Printf("  [%s] Assigned %s partitions: %v\n", w.ID, topic, partitions)
	}
}

func (w *ConsumerWorker) onRevoked(ctx context.Context, client *kgo.Client, revoked map[string][]int32) {
	w.mu.Lock()
	defer w.mu.Unlock()

	// Commit any pending offsets before losing partitions
	if err := client.CommitUncommittedOffsets(ctx); err != nil {
		fmt.Printf("  [%s] Commit on revoke error: %v\n", w.ID, err)
	}

	for topic, partitions := range revoked {
		for _, p := range partitions {
			delete(w.partitions, p)
		}
		fmt.Printf("  [%s] Revoked %s partitions: %v\n", w.ID, topic, partitions)
	}
}

func (w *ConsumerWorker) Run(ctx context.Context, wg *sync.WaitGroup) {
	defer wg.Done()

	for {
		fetches := w.client.PollFetches(ctx)

		if ctx.Err() != nil {
			break
		}

		if errs := fetches.Errors(); len(errs) > 0 {
			for _, fetchErr := range errs {
				fmt.Printf("  [%s] Fetch error: %v\n", w.ID, fetchErr.Err)
			}
		}

		records := fetches.Records()
		if len(records) > 0 {
			w.mu.Lock()
			for _, r := range records {
				w.processed++
				if w.processed <= 5 || w.processed%10 == 0 {
					fmt.Printf("  [%s] Processed message %d from partition %d\n",
						w.ID, w.processed, r.Partition)
				}
			}
			w.mu.Unlock()

			if err := w.client.CommitUncommittedOffsets(ctx); err != nil {
				fmt.Printf("  [%s] Commit error: %v\n", w.ID, err)
			}
		}
	}

	fmt.Printf("  [%s] Shutting down, processed %d messages\n", w.ID, w.processed)
}

func createConsumer(workerID string) (*ConsumerWorker, error) {
	worker := &ConsumerWorker{
		ID:         workerID,
		partitions: make(map[int32]bool),
	}

	client, err := kgo.NewClient(
		kgo.SeedBrokers(bootstrapServers),
		kgo.ConsumerGroup(groupID),
		kgo.ConsumeTopics(topic),
		kgo.ConsumeResetOffset(kgo.NewOffset().AtStart()),

		// Rebalance callbacks
		kgo.OnPartitionsAssigned(worker.onAssigned),
		kgo.OnPartitionsRevoked(worker.onRevoked),

		// Session timeout and heartbeat
		kgo.SessionTimeout(10*time.Second),
		kgo.HeartbeatInterval(3*time.Second),
	)
	if err != nil {
		return nil, err
	}

	worker.client = client
	return worker, nil
}

func runConsumerGroup() error {
	fmt.Println("\n--- PART 2: Consumer Group with Multiple Workers ---")

	fmt.Printf("\nStarting 2 consumers in group: %s\n", groupID)
	fmt.Println("Watch how partitions are distributed between consumers\n")

	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()

	var wg sync.WaitGroup
	workers := make([]*ConsumerWorker, 2)

	// Start first consumer
	worker1, err := createConsumer("worker-1")
	if err != nil {
		return fmt.Errorf("failed to create worker-1: %w", err)
	}
	workers[0] = worker1

	wg.Add(1)
	go worker1.Run(ctx, &wg)

	// Wait a bit, then start second consumer (triggers rebalance)
	time.Sleep(3 * time.Second)

	fmt.Println("\n  Starting second consumer (will trigger rebalance)...")

	worker2, err := createConsumer("worker-2")
	if err != nil {
		return fmt.Errorf("failed to create worker-2: %w", err)
	}
	workers[1] = worker2

	wg.Add(1)
	go worker2.Run(ctx, &wg)

	// Wait for consumers to finish
	wg.Wait()

	// Cleanup
	for _, w := range workers {
		if w != nil && w.client != nil {
			w.client.Close()
		}
	}

	// Print summary
	fmt.Println("\n--- Summary ---")
	total := 0
	for _, w := range workers {
		if w != nil {
			fmt.Printf("  %s processed: %d messages\n", w.ID, w.processed)
			total += w.processed
		}
	}
	fmt.Printf("  Total processed: %d messages\n", total)
	fmt.Println("\nNote: Partitions were rebalanced when worker-2 joined")

	return nil
}
