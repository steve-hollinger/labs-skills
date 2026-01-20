//go:build integration

package tests

import (
	"context"
	"testing"
	"time"

	"github.com/segmentio/kafka-go"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go"
	tcKafka "github.com/testcontainers/testcontainers-go/modules/kafka"
)

// ============================================================================
// Example 3: Kafka Container
// ============================================================================

func TestExample3_KafkaBasic(t *testing.T) {
	ctx := context.Background()

	// Start Kafka container
	kafkaContainer, err := tcKafka.RunContainer(ctx,
		tcKafka.WithClusterID("test-cluster"),
		testcontainers.WithImage("confluentinc/cp-kafka:7.5.0"),
	)
	require.NoError(t, err)
	defer kafkaContainer.Terminate(ctx)

	// Get brokers
	brokers, err := kafkaContainer.Brokers(ctx)
	require.NoError(t, err)
	require.NotEmpty(t, brokers)

	t.Logf("Kafka container started with brokers: %v", brokers)
}

func TestExample3_ProduceConsume(t *testing.T) {
	ctx := context.Background()

	// Start Kafka container
	kafkaContainer, err := tcKafka.RunContainer(ctx,
		tcKafka.WithClusterID("test-cluster"),
		testcontainers.WithImage("confluentinc/cp-kafka:7.5.0"),
	)
	require.NoError(t, err)
	defer kafkaContainer.Terminate(ctx)

	brokers, err := kafkaContainer.Brokers(ctx)
	require.NoError(t, err)

	topic := "test-topic"

	// Create topic
	conn, err := kafka.Dial("tcp", brokers[0])
	require.NoError(t, err)
	defer conn.Close()

	controller, err := conn.Controller()
	require.NoError(t, err)

	controllerConn, err := kafka.Dial("tcp", controller.Host+":"+string(rune(controller.Port)))
	if err != nil {
		// Fallback to original connection for topic creation
		controllerConn = conn
	} else {
		defer controllerConn.Close()
	}

	err = controllerConn.CreateTopics(kafka.TopicConfig{
		Topic:             topic,
		NumPartitions:     1,
		ReplicationFactor: 1,
	})
	// Ignore error if topic already exists
	t.Logf("Topic creation result: %v", err)

	// Give Kafka time to set up the topic
	time.Sleep(2 * time.Second)

	// Write messages
	writer := &kafka.Writer{
		Addr:         kafka.TCP(brokers...),
		Topic:        topic,
		Balancer:     &kafka.LeastBytes{},
		BatchTimeout: 10 * time.Millisecond,
	}
	defer writer.Close()

	messages := []kafka.Message{
		{Key: []byte("key-1"), Value: []byte("Hello Kafka!")},
		{Key: []byte("key-2"), Value: []byte("Second message")},
		{Key: []byte("key-3"), Value: []byte("Third message")},
	}

	err = writer.WriteMessages(ctx, messages...)
	require.NoError(t, err)

	t.Log("Messages written successfully")

	// Read messages
	reader := kafka.NewReader(kafka.ReaderConfig{
		Brokers:     brokers,
		Topic:       topic,
		GroupID:     "test-group",
		StartOffset: kafka.FirstOffset,
		MaxWait:     1 * time.Second,
	})
	defer reader.Close()

	readCtx, cancel := context.WithTimeout(ctx, 30*time.Second)
	defer cancel()

	var receivedMessages []kafka.Message
	for i := 0; i < 3; i++ {
		msg, err := reader.ReadMessage(readCtx)
		if err != nil {
			t.Logf("Error reading message: %v", err)
			break
		}
		receivedMessages = append(receivedMessages, msg)
		t.Logf("Received: key=%s value=%s", msg.Key, msg.Value)
	}

	assert.GreaterOrEqual(t, len(receivedMessages), 1, "Should receive at least one message")
}

func TestExample3_MultipleConsumers(t *testing.T) {
	ctx := context.Background()

	// Start Kafka container
	kafkaContainer, err := tcKafka.RunContainer(ctx,
		tcKafka.WithClusterID("test-cluster"),
		testcontainers.WithImage("confluentinc/cp-kafka:7.5.0"),
	)
	require.NoError(t, err)
	defer kafkaContainer.Terminate(ctx)

	brokers, err := kafkaContainer.Brokers(ctx)
	require.NoError(t, err)

	topic := "multi-consumer-topic"

	// Create topic with multiple partitions
	conn, err := kafka.Dial("tcp", brokers[0])
	require.NoError(t, err)

	err = conn.CreateTopics(kafka.TopicConfig{
		Topic:             topic,
		NumPartitions:     3,
		ReplicationFactor: 1,
	})
	conn.Close()
	time.Sleep(2 * time.Second)

	// Write messages to different partitions
	writer := &kafka.Writer{
		Addr:         kafka.TCP(brokers...),
		Topic:        topic,
		Balancer:     &kafka.RoundRobin{},
		BatchTimeout: 10 * time.Millisecond,
	}

	for i := 0; i < 9; i++ {
		err := writer.WriteMessages(ctx, kafka.Message{
			Key:   []byte("key"),
			Value: []byte("message"),
		})
		require.NoError(t, err)
	}
	writer.Close()

	// Create readers for same consumer group
	reader1 := kafka.NewReader(kafka.ReaderConfig{
		Brokers:     brokers,
		Topic:       topic,
		GroupID:     "test-group-multi",
		StartOffset: kafka.FirstOffset,
		MaxWait:     1 * time.Second,
	})
	defer reader1.Close()

	reader2 := kafka.NewReader(kafka.ReaderConfig{
		Brokers:     brokers,
		Topic:       topic,
		GroupID:     "test-group-multi",
		StartOffset: kafka.FirstOffset,
		MaxWait:     1 * time.Second,
	})
	defer reader2.Close()

	// Both readers should be able to read from the group
	// (partitions are distributed among consumers in same group)
	readCtx, cancel := context.WithTimeout(ctx, 10*time.Second)
	defer cancel()

	msg, err := reader1.ReadMessage(readCtx)
	if err == nil {
		t.Logf("Reader 1 received message from partition %d", msg.Partition)
	}
}

// EventProcessor demonstrates testing event-driven systems
type EventProcessor struct {
	writer *kafka.Writer
	topic  string
}

func NewEventProcessor(brokers []string, topic string) *EventProcessor {
	return &EventProcessor{
		writer: &kafka.Writer{
			Addr:         kafka.TCP(brokers...),
			Topic:        topic,
			Balancer:     &kafka.LeastBytes{},
			BatchTimeout: 10 * time.Millisecond,
		},
		topic: topic,
	}
}

func (p *EventProcessor) PublishEvent(ctx context.Context, eventType string, payload []byte) error {
	return p.writer.WriteMessages(ctx, kafka.Message{
		Key:   []byte(eventType),
		Value: payload,
		Headers: []kafka.Header{
			{Key: "event-type", Value: []byte(eventType)},
			{Key: "timestamp", Value: []byte(time.Now().Format(time.RFC3339))},
		},
	})
}

func (p *EventProcessor) Close() error {
	return p.writer.Close()
}

func TestExample3_EventProcessor(t *testing.T) {
	ctx := context.Background()

	// Start Kafka container
	kafkaContainer, err := tcKafka.RunContainer(ctx,
		tcKafka.WithClusterID("test-cluster"),
		testcontainers.WithImage("confluentinc/cp-kafka:7.5.0"),
	)
	require.NoError(t, err)
	defer kafkaContainer.Terminate(ctx)

	brokers, err := kafkaContainer.Brokers(ctx)
	require.NoError(t, err)

	topic := "events"

	// Create topic
	conn, _ := kafka.Dial("tcp", brokers[0])
	conn.CreateTopics(kafka.TopicConfig{
		Topic:             topic,
		NumPartitions:     1,
		ReplicationFactor: 1,
	})
	conn.Close()
	time.Sleep(2 * time.Second)

	// Create event processor
	processor := NewEventProcessor(brokers, topic)
	defer processor.Close()

	// Publish events
	err = processor.PublishEvent(ctx, "user.created", []byte(`{"id": 1, "name": "Alice"}`))
	require.NoError(t, err)

	err = processor.PublishEvent(ctx, "user.updated", []byte(`{"id": 1, "name": "Alice Smith"}`))
	require.NoError(t, err)

	// Consume and verify events
	reader := kafka.NewReader(kafka.ReaderConfig{
		Brokers:     brokers,
		Topic:       topic,
		GroupID:     "event-test-group",
		StartOffset: kafka.FirstOffset,
		MaxWait:     1 * time.Second,
	})
	defer reader.Close()

	readCtx, cancel := context.WithTimeout(ctx, 10*time.Second)
	defer cancel()

	msg, err := reader.ReadMessage(readCtx)
	require.NoError(t, err)

	assert.Equal(t, "user.created", string(msg.Key))

	// Check headers
	var eventTypeHeader string
	for _, h := range msg.Headers {
		if h.Key == "event-type" {
			eventTypeHeader = string(h.Value)
		}
	}
	assert.Equal(t, "user.created", eventTypeHeader)
}
