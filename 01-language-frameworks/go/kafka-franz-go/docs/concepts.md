# Core Concepts

## Overview

This document covers the fundamental concepts of using franz-go, a high-performance Kafka client for Go. franz-go provides a modern, pure-Go implementation with excellent performance characteristics.

## Concept 1: The franz-go Client

### What It Is

The franz-go client (`kgo.Client`) is the central component for all Kafka operations. It handles connections, produces messages, consumes messages, and manages consumer groups - all through a single client instance.

### Why It Matters

- **Unified Interface**: One client for both producing and consuming
- **Connection Management**: Automatic connection pooling and reconnection
- **High Performance**: Zero-allocation design in critical paths
- **Context Support**: Full context.Context integration for cancellation

### How It Works

```go
package main

import (
    "context"
    "fmt"
    "github.com/twmb/franz-go/pkg/kgo"
)

func main() {
    // Create a client with functional options
    client, err := kgo.NewClient(
        kgo.SeedBrokers("localhost:9092"),
        kgo.ConsumerGroup("my-group"),
        kgo.ConsumeTopics("events"),
    )
    if err != nil {
        panic(err)
    }
    defer client.Close()

    // The same client can produce and consume
    ctx := context.Background()

    // Produce
    client.Produce(ctx, &kgo.Record{
        Topic: "events",
        Value: []byte("hello"),
    }, nil)
    client.Flush(ctx)

    // Consume
    fetches := client.PollFetches(ctx)
    fetches.EachRecord(func(r *kgo.Record) {
        fmt.Printf("Got: %s\n", r.Value)
    })
}
```

## Concept 2: Asynchronous Production

### What It Is

franz-go uses an asynchronous production model where `Produce` returns immediately and delivery confirmation happens via callbacks. This enables high throughput by batching messages.

### Why It Matters

- **High Throughput**: Messages are batched automatically
- **Non-Blocking**: Application continues while messages queue
- **Delivery Confirmation**: Callbacks provide delivery status
- **Backpressure**: Built-in handling when broker is slow

### How It Works

```go
package main

import (
    "context"
    "fmt"
    "sync"
    "github.com/twmb/franz-go/pkg/kgo"
)

func main() {
    client, _ := kgo.NewClient(kgo.SeedBrokers("localhost:9092"))
    defer client.Close()

    ctx := context.Background()
    var wg sync.WaitGroup

    // Produce multiple messages asynchronously
    for i := 0; i < 100; i++ {
        wg.Add(1)
        record := &kgo.Record{
            Topic: "events",
            Value: []byte(fmt.Sprintf("message-%d", i)),
        }

        client.Produce(ctx, record, func(r *kgo.Record, err error) {
            defer wg.Done()
            if err != nil {
                fmt.Printf("produce error: %v\n", err)
                return
            }
            fmt.Printf("delivered to partition %d at offset %d\n",
                r.Partition, r.Offset)
        })
    }

    // Wait for all deliveries
    wg.Wait()
    // Or use Flush:
    // client.Flush(ctx)
}
```

## Concept 3: Batch Consumption with PollFetches

### What It Is

`PollFetches` returns a batch of records from subscribed topics. This is more efficient than processing one record at a time and allows for batch processing patterns.

### Why It Matters

- **Efficiency**: Process multiple records per poll
- **Reduced Overhead**: Fewer network round-trips
- **Batch Processing**: Enable aggregation patterns
- **Error Aggregation**: Errors collected per fetch batch

### How It Works

```go
package main

import (
    "context"
    "fmt"
    "github.com/twmb/franz-go/pkg/kgo"
)

func main() {
    client, _ := kgo.NewClient(
        kgo.SeedBrokers("localhost:9092"),
        kgo.ConsumerGroup("batch-processor"),
        kgo.ConsumeTopics("events"),
        kgo.FetchMaxWait(time.Second),      // Max wait for batch
        kgo.FetchMaxBytes(1 * 1024 * 1024), // 1MB max batch
    )
    defer client.Close()

    ctx := context.Background()

    for {
        // Poll returns a batch of fetches
        fetches := client.PollFetches(ctx)

        // Check for errors first
        if errs := fetches.Errors(); len(errs) > 0 {
            for _, err := range errs {
                fmt.Printf("fetch error: %v\n", err)
            }
        }

        // Get all records from all partitions
        records := fetches.Records()
        fmt.Printf("Got batch of %d records\n", len(records))

        // Process batch
        for _, record := range records {
            processRecord(record)
        }

        // Or use iterator pattern
        fetches.EachRecord(func(r *kgo.Record) {
            processRecord(r)
        })

        // Commit after processing
        client.CommitUncommittedOffsets(ctx)
    }
}
```

## Concept 4: Consumer Groups

### What It Is

Consumer groups coordinate multiple consumers to share the work of consuming from a topic. Partitions are distributed among group members, and rebalancing happens automatically when members join or leave.

### Why It Matters

- **Scalability**: Add consumers to increase throughput
- **Fault Tolerance**: Failed consumers' partitions reassigned
- **Exactly-Once Semantics**: With proper offset management
- **Automatic Rebalancing**: Handled transparently

### How It Works

```go
package main

import (
    "context"
    "fmt"
    "github.com/twmb/franz-go/pkg/kgo"
)

func main() {
    client, _ := kgo.NewClient(
        kgo.SeedBrokers("localhost:9092"),
        kgo.ConsumerGroup("order-processors"),
        kgo.ConsumeTopics("orders"),

        // Rebalance callbacks
        kgo.OnPartitionsAssigned(func(ctx context.Context, c *kgo.Client, assigned map[string][]int32) {
            for topic, partitions := range assigned {
                fmt.Printf("Assigned %s: %v\n", topic, partitions)
            }
        }),
        kgo.OnPartitionsRevoked(func(ctx context.Context, c *kgo.Client, revoked map[string][]int32) {
            // Commit any pending work before losing partitions
            c.CommitUncommittedOffsets(ctx)
            for topic, partitions := range revoked {
                fmt.Printf("Revoked %s: %v\n", topic, partitions)
            }
        }),
    )
    defer client.Close()

    ctx := context.Background()
    for {
        fetches := client.PollFetches(ctx)
        // ... process records
        client.CommitUncommittedOffsets(ctx)
    }
}
```

## Concept 5: Records and Metadata

### What It Is

A `kgo.Record` represents a Kafka message with key, value, headers, and metadata. After production or consumption, records contain additional information like partition and offset.

### Why It Matters

- **Structured Data**: Key, value, and headers
- **Partitioning**: Key determines partition assignment
- **Metadata**: Topic, partition, offset, timestamp
- **Headers**: Additional key-value metadata

### How It Works

```go
package main

import (
    "context"
    "encoding/json"
    "time"
    "github.com/twmb/franz-go/pkg/kgo"
)

type OrderEvent struct {
    OrderID   string  `json:"order_id"`
    Customer  string  `json:"customer"`
    Amount    float64 `json:"amount"`
}

func main() {
    client, _ := kgo.NewClient(kgo.SeedBrokers("localhost:9092"))
    defer client.Close()

    ctx := context.Background()

    // Create a record with full metadata
    event := OrderEvent{
        OrderID:  "ord-123",
        Customer: "cust-456",
        Amount:   99.99,
    }
    value, _ := json.Marshal(event)

    record := &kgo.Record{
        Topic: "orders",
        Key:   []byte(event.OrderID),  // Key for partitioning
        Value: value,
        Headers: []kgo.RecordHeader{
            {Key: "event-type", Value: []byte("order.created")},
            {Key: "content-type", Value: []byte("application/json")},
        },
        Timestamp: time.Now(),
    }

    // After production, record has partition and offset
    client.Produce(ctx, record, func(r *kgo.Record, err error) {
        if err == nil {
            fmt.Printf("Produced to %s[%d]@%d\n",
                r.Topic, r.Partition, r.Offset)
        }
    })
    client.Flush(ctx)
}
```

## Concept 6: Error Handling

### What It Is

franz-go provides comprehensive error handling through callbacks, fetch errors, and context cancellation. Understanding error types helps build resilient applications.

### Why It Matters

- **Reliability**: Handle transient and permanent failures
- **Observability**: Log and monitor errors
- **Recovery**: Implement retry logic appropriately
- **Graceful Degradation**: Continue operating despite errors

### How It Works

```go
package main

import (
    "context"
    "errors"
    "fmt"
    "github.com/twmb/franz-go/pkg/kgo"
    "github.com/twmb/franz-go/pkg/kerr"
)

func main() {
    client, _ := kgo.NewClient(
        kgo.SeedBrokers("localhost:9092"),
        kgo.ConsumerGroup("error-demo"),
        kgo.ConsumeTopics("events"),
    )
    defer client.Close()

    ctx := context.Background()

    // Production errors via callback
    client.Produce(ctx, &kgo.Record{
        Topic: "events",
        Value: []byte("test"),
    }, func(r *kgo.Record, err error) {
        if err != nil {
            // Check for specific Kafka errors
            if errors.Is(err, kerr.UnknownTopicOrPartition) {
                fmt.Println("Topic doesn't exist")
            } else if errors.Is(err, context.DeadlineExceeded) {
                fmt.Println("Production timed out")
            } else {
                fmt.Printf("Production error: %v\n", err)
            }
            return
        }
        fmt.Println("Produced successfully")
    })

    // Consumption errors
    fetches := client.PollFetches(ctx)

    // Check fetch-level errors
    if errs := fetches.Errors(); len(errs) > 0 {
        for _, fetchErr := range errs {
            fmt.Printf("Fetch error on %s[%d]: %v\n",
                fetchErr.Topic, fetchErr.Partition, fetchErr.Err)

            // Check for authorization errors
            if errors.Is(fetchErr.Err, kerr.TopicAuthorizationFailed) {
                fmt.Println("Not authorized to read topic")
            }
        }
    }

    // Context cancellation
    ctx, cancel := context.WithCancel(context.Background())
    go func() {
        time.Sleep(5 * time.Second)
        cancel()
    }()

    fetches = client.PollFetches(ctx)
    if ctx.Err() != nil {
        fmt.Println("Polling cancelled")
    }
}
```

## Summary

Key takeaways from these concepts:

1. **Single Client**: Use one client instance for both producing and consuming
2. **Async Production**: Leverage callbacks for high-throughput production
3. **Batch Consumption**: Use PollFetches for efficient batch processing
4. **Consumer Groups**: Scale consumption with automatic rebalancing
5. **Rich Records**: Use keys for partitioning, headers for metadata
6. **Error Handling**: Handle errors appropriately at each stage

These concepts form the foundation for building robust, high-performance Kafka applications in Go with franz-go.
