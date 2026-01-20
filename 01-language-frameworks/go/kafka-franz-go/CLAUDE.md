# CLAUDE.md - Kafka with franz-go

This skill teaches high-performance Kafka integration in Go using the franz-go library.

## Key Concepts

- **franz-go Client**: Pure Go Kafka client with modern API and high performance
- **Producing**: Asynchronous message production with callbacks
- **Consuming**: Efficient batch polling with PollFetches
- **Consumer Groups**: Coordinated consumption with automatic rebalancing
- **Batching**: Optimizing throughput with batch operations
- **Error Handling**: Proper error handling in async patterns

## Common Commands

```bash
make setup      # Download dependencies
make examples   # Run all examples
make example-1  # Run specific example
make test       # Run go test
make test-race  # Run tests with race detector
make lint       # Run golangci-lint
make clean      # Remove build artifacts
```

## Project Structure

```
kafka-franz-go/
├── cmd/examples/
│   ├── example1/main.go    # Basic producer/consumer
│   ├── example2/main.go    # Batch processing
│   ├── example3/main.go    # Consumer groups
│   └── example4/main.go    # Event-driven service
├── internal/
│   ├── producer/           # Producer utilities
│   └── consumer/           # Consumer utilities
├── exercises/
│   ├── exercise1/
│   └── solutions/
├── tests/
│   └── examples_test.go
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic Producer
```go
package main

import (
    "context"
    "github.com/twmb/franz-go/pkg/kgo"
)

func main() {
    client, err := kgo.NewClient(
        kgo.SeedBrokers("localhost:9092"),
    )
    if err != nil {
        panic(err)
    }
    defer client.Close()

    record := &kgo.Record{
        Topic: "events",
        Key:   []byte("key"),
        Value: []byte("value"),
    }

    // Async produce with callback
    client.Produce(context.Background(), record, func(r *kgo.Record, err error) {
        if err != nil {
            fmt.Printf("produce error: %v\n", err)
            return
        }
        fmt.Printf("produced to %s[%d]@%d\n", r.Topic, r.Partition, r.Offset)
    })

    // Wait for delivery
    client.Flush(context.Background())
}
```

### Pattern 2: Consumer Loop
```go
package main

import (
    "context"
    "github.com/twmb/franz-go/pkg/kgo"
)

func main() {
    client, err := kgo.NewClient(
        kgo.SeedBrokers("localhost:9092"),
        kgo.ConsumerGroup("my-group"),
        kgo.ConsumeTopics("events"),
    )
    if err != nil {
        panic(err)
    }
    defer client.Close()

    ctx := context.Background()
    for {
        fetches := client.PollFetches(ctx)

        // Check for errors
        if errs := fetches.Errors(); len(errs) > 0 {
            for _, err := range errs {
                fmt.Printf("fetch error: %v\n", err)
            }
        }

        // Process records
        fetches.EachRecord(func(r *kgo.Record) {
            fmt.Printf("topic=%s partition=%d offset=%d key=%s value=%s\n",
                r.Topic, r.Partition, r.Offset, r.Key, r.Value)
        })

        // Commit offsets
        client.CommitUncommittedOffsets(ctx)
    }
}
```

### Pattern 3: Graceful Shutdown
```go
ctx, cancel := context.WithCancel(context.Background())
defer cancel()

// Handle signals
sigCh := make(chan os.Signal, 1)
signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)

go func() {
    <-sigCh
    cancel()
}()

// Consumer loop with context
for {
    fetches := client.PollFetches(ctx)
    if ctx.Err() != nil {
        break // Context cancelled
    }
    // ... process fetches
}

// Commit final offsets
client.CommitUncommittedOffsets(context.Background())
```

## Common Mistakes

1. **Not handling produce errors in callbacks**
   - Always check the error parameter in produce callbacks
   - Log or handle errors appropriately

2. **Forgetting to flush before shutdown**
   - Call Flush() to ensure all messages are delivered
   - Use context with timeout for graceful shutdown

3. **Ignoring fetch errors**
   - Always check fetches.Errors() before processing
   - Some errors are recoverable, others require reconnection

4. **Blocking in callbacks**
   - Produce callbacks run in client goroutine
   - Use goroutines for heavy processing

5. **Not committing offsets**
   - With consumer groups, commit offsets to track progress
   - Use CommitUncommittedOffsets() or auto-commit

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make examples` and the README.md. Ensure Kafka is running via `make infra-up` from repo root.

### "How do I handle rebalances?"
Use the OnPartitionsAssigned and OnPartitionsRevoked callbacks:
```go
kgo.OnPartitionsAssigned(func(ctx context.Context, client *kgo.Client, assigned map[string][]int32) {
    // Handle assignment
})
```

### "How do I ensure ordering?"
- Same key = same partition = ordered
- Use key when producing for ordering guarantees
- Single partition = total ordering (but limits throughput)

### "What about exactly-once?"
franz-go supports idempotent producers and transactions. See docs/patterns.md for transactional patterns.

### "How do I tune performance?"
Key options:
- `kgo.ProducerBatchMaxBytes` - batch size
- `kgo.ProducerLinger` - wait time for batching
- `kgo.FetchMaxBytes` - fetch batch size
- `kgo.ProducerBatchCompression` - compression

## Testing Notes

- Use table-driven tests
- Run with race detector: `make test-race`
- Use testify for assertions
- Mock the Kafka client for unit tests
- Integration tests require running Kafka

## Dependencies

Key dependencies in go.mod:
- github.com/twmb/franz-go/pkg/kgo: Core Kafka client
- github.com/twmb/franz-go/pkg/kadm: Admin operations
- github.com/stretchr/testify: Testing assertions

## Infrastructure Requirements

Kafka must be running. Start from repo root:
```bash
make infra-up
```

This starts:
- Kafka broker on localhost:9092
- Kafka UI on localhost:8080
