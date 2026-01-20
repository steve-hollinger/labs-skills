// Solution 1: Message Router
//
// This is the solution for Exercise 1: Build a Message Router

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"os/signal"
	"strings"
	"sync"
	"syscall"
	"time"

	"github.com/twmb/franz-go/pkg/kgo"
)

const (
	bootstrapServers = "localhost:9092"
	inputTopic       = "events-input"
)

// Event represents an incoming event
type Event struct {
	EventID   string                 `json:"event_id"`
	EventType string                 `json:"event_type"`
	Timestamp time.Time              `json:"timestamp"`
	Data      map[string]interface{} `json:"data"`
}

// Router handles message routing
type Router struct {
	client  *kgo.Client
	routed  map[string]int
	errors  int
	mu      sync.Mutex
}

// NewRouter creates a new message router
func NewRouter() (*Router, error) {
	client, err := kgo.NewClient(
		kgo.SeedBrokers(bootstrapServers),
		kgo.ConsumerGroup("message-router"),
		kgo.ConsumeTopics(inputTopic),
		kgo.ConsumeResetOffset(kgo.NewOffset().AtStart()),
		kgo.RequiredAcks(kgo.AllISRAcks()),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create client: %w", err)
	}

	return &Router{
		client: client,
		routed: make(map[string]int),
	}, nil
}

// Route determines the output topic for an event
func (r *Router) Route(event *Event) string {
	prefix := strings.Split(event.EventType, ".")[0]

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

// Run starts the router
func (r *Router) Run(ctx context.Context) error {
	fmt.Println("[INFO] Router started")

	for {
		fetches := r.client.PollFetches(ctx)

		// Check for shutdown
		if ctx.Err() != nil {
			break
		}

		// Handle errors
		if errs := fetches.Errors(); len(errs) > 0 {
			for _, fetchErr := range errs {
				fmt.Printf("[ERROR] Fetch: %v\n", fetchErr.Err)
			}
			continue
		}

		// Process and route each record
		fetches.EachRecord(func(record *kgo.Record) {
			r.routeRecord(ctx, record)
		})

		// Commit after processing
		if err := r.client.CommitUncommittedOffsets(ctx); err != nil {
			fmt.Printf("[ERROR] Commit: %v\n", err)
		}
	}

	return nil
}

func (r *Router) routeRecord(ctx context.Context, record *kgo.Record) {
	// Parse event
	var event Event
	if err := json.Unmarshal(record.Value, &event); err != nil {
		fmt.Printf("[ERROR] Parse event: %v\n", err)
		r.mu.Lock()
		r.errors++
		r.mu.Unlock()
		return
	}

	// Determine output topic
	outputTopic := r.Route(&event)

	// Produce to output topic
	r.client.Produce(ctx, &kgo.Record{
		Topic: outputTopic,
		Key:   record.Key,
		Value: record.Value,
	}, func(rec *kgo.Record, err error) {
		if err != nil {
			fmt.Printf("[ERROR] Route to %s: %v\n", outputTopic, err)
			r.mu.Lock()
			r.errors++
			r.mu.Unlock()
			return
		}

		r.mu.Lock()
		r.routed[outputTopic]++
		total := 0
		for _, v := range r.routed {
			total += v
		}
		r.mu.Unlock()

		fmt.Printf("[INFO] Routed %s -> %s (total: %d)\n",
			event.EventType, outputTopic, total)
	})
}

// Stats returns routing statistics
func (r *Router) Stats() (map[string]int, int) {
	r.mu.Lock()
	defer r.mu.Unlock()

	// Copy map
	stats := make(map[string]int)
	for k, v := range r.routed {
		stats[k] = v
	}
	return stats, r.errors
}

// Close cleans up resources
func (r *Router) Close() {
	r.client.Flush(context.Background())
	r.client.Close()
}

func produceTestEvents() error {
	client, err := kgo.NewClient(kgo.SeedBrokers(bootstrapServers))
	if err != nil {
		return err
	}
	defer client.Close()

	events := []Event{
		{EventID: "1", EventType: "user.created", Data: map[string]interface{}{"user_id": "u1"}},
		{EventID: "2", EventType: "order.placed", Data: map[string]interface{}{"order_id": "o1"}},
		{EventID: "3", EventType: "payment.completed", Data: map[string]interface{}{"payment_id": "p1"}},
		{EventID: "4", EventType: "user.updated", Data: map[string]interface{}{"user_id": "u1"}},
		{EventID: "5", EventType: "order.shipped", Data: map[string]interface{}{"order_id": "o1"}},
		{EventID: "6", EventType: "unknown.event", Data: map[string]interface{}{}},
		{EventID: "7", EventType: "user.deleted", Data: map[string]interface{}{"user_id": "u2"}},
		{EventID: "8", EventType: "payment.failed", Data: map[string]interface{}{"payment_id": "p2"}},
	}

	ctx := context.Background()
	for _, event := range events {
		event.Timestamp = time.Now()
		value, _ := json.Marshal(event)
		client.Produce(ctx, &kgo.Record{
			Topic: inputTopic,
			Key:   []byte(event.EventID),
			Value: value,
		}, nil)
	}

	return client.Flush(ctx)
}

func main() {
	fmt.Println("Solution 1: Message Router")
	fmt.Println("==========================")

	// Produce test events
	fmt.Println("\n[INFO] Producing test events...")
	if err := produceTestEvents(); err != nil {
		fmt.Printf("[ERROR] Failed to produce events: %v\n", err)
		fmt.Println("\nMake sure Kafka is running:")
		fmt.Println("  cd ../../../.. && make infra-up")
		return
	}

	time.Sleep(500 * time.Millisecond)

	// Create router
	router, err := NewRouter()
	if err != nil {
		fmt.Printf("[ERROR] Failed to create router: %v\n", err)
		return
	}

	// Setup signal handling
	ctx, cancel := context.WithCancel(context.Background())
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		select {
		case <-sigCh:
			fmt.Println("\n[INFO] Shutting down...")
			cancel()
		case <-time.After(10 * time.Second):
			cancel()
		}
	}()

	// Run router
	fmt.Println("\n[INFO] Starting router...")
	if err := router.Run(ctx); err != nil {
		fmt.Printf("[ERROR] Router error: %v\n", err)
	}

	// Cleanup
	router.Close()

	// Print stats
	stats, errors := router.Stats()
	fmt.Println("\n--- Routing Statistics ---")
	for topic, count := range stats {
		fmt.Printf("  %s: %d messages\n", topic, count)
	}
	fmt.Printf("  Errors: %d\n", errors)
}
