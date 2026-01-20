# Kafka with franz-go

Master high-performance Kafka integration in Go using franz-go - the modern, high-throughput Kafka client library built from scratch with performance in mind.

## Learning Objectives

After completing this skill, you will be able to:
- Use franz-go for producing and consuming Kafka messages
- Implement efficient batch processing patterns
- Handle errors and retries gracefully
- Configure producers and consumers for optimal performance
- Build event-driven Go applications with Kafka
- Understand partitioning strategies and consumer groups

## Prerequisites

- Go 1.22+
- Docker (for local Kafka via shared infrastructure)
- Basic understanding of Kafka concepts (topics, partitions, offsets)
- Familiarity with Go concurrency patterns

## Quick Start

```bash
# Start shared infrastructure (includes Kafka)
cd ../../../..
make infra-up
cd 01-language-frameworks/go/kafka-franz-go

# Download dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Why franz-go?

franz-go was built from scratch as a modern Kafka client for Go, offering:

- **High Performance**: Zero-allocation design in critical paths
- **Pure Go**: No CGO dependencies, easy cross-compilation
- **Modern API**: Context-based cancellation, generics support
- **Complete Feature Set**: Full Kafka protocol support including transactions
- **Active Development**: Maintained by Redpanda and the community

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
    )
    defer client.Close()

    // Produce
    client.Produce(context.Background(),
        &kgo.Record{Topic: "events", Value: []byte("hello")},
        func(r *kgo.Record, err error) {
            fmt.Printf("Produced to partition %d\n", r.Partition)
        },
    )
    client.Flush(context.Background())
}
```

## Concepts

### Client Configuration

franz-go uses functional options for configuration:

```go
client, err := kgo.NewClient(
    kgo.SeedBrokers("localhost:9092"),
    kgo.ConsumerGroup("my-group"),
    kgo.ConsumeTopics("events"),
    kgo.ConsumeResetOffset(kgo.NewOffset().AtStart()),
)
```

### Producing Messages

Asynchronous production with callbacks:

```go
client.Produce(ctx, record, func(r *kgo.Record, err error) {
    if err != nil {
        log.Printf("produce failed: %v", err)
        return
    }
    log.Printf("produced to %s[%d]@%d", r.Topic, r.Partition, r.Offset)
})
```

### Consuming Messages

Polling for batches of records:

```go
for {
    fetches := client.PollFetches(ctx)
    if errs := fetches.Errors(); len(errs) > 0 {
        // handle errors
    }
    fetches.EachRecord(func(r *kgo.Record) {
        fmt.Printf("Got: %s\n", string(r.Value))
    })
}
```

## Examples

### Example 1: Basic Producer and Consumer

Learn the fundamentals of producing and consuming with franz-go.

```bash
make example-1
```

### Example 2: Batch Processing

Efficient batch production and consumption patterns.

```bash
make example-2
```

### Example 3: Consumer Groups and Rebalancing

Build scalable consumers with proper rebalance handling.

```bash
make example-3
```

### Example 4: Event-Driven Service

Complete event-driven service with error handling and graceful shutdown.

```bash
make example-4
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Build a Message Router - Route messages to different topics based on content
2. **Exercise 2**: Implement Exactly-Once Processing - Use idempotent producers and transactional consumers
3. **Exercise 3**: Build an Event Aggregator - Aggregate events over time windows

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Not Flushing Before Exit

Always flush to ensure all messages are delivered:

```go
// Wrong - may lose messages
client.Produce(ctx, record, nil)
// exit

// Correct
client.Produce(ctx, record, nil)
client.Flush(ctx)
```

### Ignoring Fetch Errors

Always check for errors in fetches:

```go
fetches := client.PollFetches(ctx)
// Wrong - ignoring errors
fetches.EachRecord(func(r *kgo.Record) { ... })

// Correct
if errs := fetches.Errors(); len(errs) > 0 {
    for _, err := range errs {
        log.Printf("fetch error: %v", err)
    }
}
fetches.EachRecord(func(r *kgo.Record) { ... })
```

### Blocking in Produce Callbacks

Callbacks run in the client's goroutine - don't block:

```go
// Wrong - blocking callback
client.Produce(ctx, record, func(r *kgo.Record, err error) {
    time.Sleep(time.Second) // blocks other callbacks
})

// Correct - async processing
client.Produce(ctx, record, func(r *kgo.Record, err error) {
    go processRecord(r) // handle asynchronously
})
```

## Performance Tips

1. **Batch Production**: Produce multiple records before flushing
2. **Prefetch**: Use `kgo.FetchMaxBytes` to control fetch sizes
3. **Compression**: Enable compression with `kgo.ProducerBatchCompression`
4. **Connection Pooling**: franz-go manages connections efficiently by default

## Infrastructure

This skill uses the shared Kafka infrastructure:

- **Bootstrap Server**: localhost:9092
- **Kafka UI**: localhost:8080

Start infrastructure from repository root:
```bash
make infra-up
```

## Further Reading

- [franz-go GitHub Repository](https://github.com/twmb/franz-go)
- [franz-go Documentation](https://pkg.go.dev/github.com/twmb/franz-go)
- [Kafka Protocol Specification](https://kafka.apache.org/protocol)
- Related skills in this repository:
  - [Kafka Event Streaming](../../../05-data-databases/kafka-event-streaming/) - Python Kafka patterns
  - [Go Concurrency](../concurrency/) - Go concurrency fundamentals
