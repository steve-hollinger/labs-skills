// Exercise 1: Build a Message Router
//
// In this exercise, you will create a Kafka message router that reads
// messages from an input topic and routes them to different output topics
// based on message content.
//
// Requirements:
// 1. Consume messages from "events-input" topic
// 2. Parse the message to determine its type
// 3. Route to appropriate output topic:
//    - "user.*" events -> "user-events"
//    - "order.*" events -> "order-events"
//    - "payment.*" events -> "payment-events"
//    - Unknown events -> "unknown-events"
// 4. Maintain message ordering within each type
// 5. Handle errors gracefully
// 6. Implement graceful shutdown
//
// Run with: go run ./exercises/exercise1
// Test with: go test -v ./tests -run TestExercise1

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
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
	client *kgo.Client
	// TODO: Add any additional fields you need
}

// NewRouter creates a new message router
// TODO: Implement this function
// 1. Create a Kafka client configured for both consuming and producing
// 2. Subscribe to inputTopic
// 3. Configure consumer group
func NewRouter() (*Router, error) {
	// TODO: Implement
	return nil, fmt.Errorf("not implemented")
}

// Route determines the output topic for an event
// TODO: Implement this function
// Return the appropriate topic based on event type prefix
func (r *Router) Route(event *Event) string {
	// TODO: Implement routing logic
	// Hint: Use strings.HasPrefix or strings.Split

	return "unknown-events"
}

// Run starts the router
// TODO: Implement this function
// 1. Poll for messages
// 2. Parse each message as Event
// 3. Determine output topic using Route()
// 4. Produce to output topic
// 5. Commit offsets
// 6. Handle context cancellation for graceful shutdown
func (r *Router) Run(ctx context.Context) error {
	// TODO: Implement
	return fmt.Errorf("not implemented")
}

// Close cleans up resources
// TODO: Implement this function
func (r *Router) Close() {
	// TODO: Implement
}

func main() {
	fmt.Println("Exercise 1: Message Router")
	fmt.Println("==========================")
	fmt.Println()
	fmt.Println("This exercise is not yet implemented.")
	fmt.Println("See the TODO comments for implementation requirements.")
	fmt.Println()
	fmt.Println("Hint: Start by implementing NewRouter(), then Route(), then Run()")
}

// Helper function to produce test events
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
		{EventID: "5", EventType: "unknown.event", Data: map[string]interface{}{}},
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

// Hint: Use strings package for routing
var _ = strings.HasPrefix
