# Common Patterns

## Overview

This document covers common patterns and best practices for building Kafka applications with franz-go.

## Pattern 1: Graceful Shutdown

### When to Use

Always implement graceful shutdown to ensure messages are delivered and offsets are committed before the application exits.

### Implementation

```go
package main

import (
    "context"
    "fmt"
    "os"
    "os/signal"
    "syscall"
    "time"
    "github.com/twmb/franz-go/pkg/kgo"
)

func main() {
    client, _ := kgo.NewClient(
        kgo.SeedBrokers("localhost:9092"),
        kgo.ConsumerGroup("graceful-shutdown"),
        kgo.ConsumeTopics("events"),
    )

    // Create cancellable context
    ctx, cancel := context.WithCancel(context.Background())

    // Handle shutdown signals
    sigCh := make(chan os.Signal, 1)
    signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)

    go func() {
        sig := <-sigCh
        fmt.Printf("Received signal: %v\n", sig)
        cancel()
    }()

    // Consumer loop
    for {
        fetches := client.PollFetches(ctx)

        // Check for context cancellation
        if ctx.Err() != nil {
            fmt.Println("Shutting down...")
            break
        }

        fetches.EachRecord(func(r *kgo.Record) {
            fmt.Printf("Processing: %s\n", r.Value)
        })

        client.CommitUncommittedOffsets(ctx)
    }

    // Final commit with fresh context
    shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer shutdownCancel()

    if err := client.CommitUncommittedOffsets(shutdownCtx); err != nil {
        fmt.Printf("Final commit error: %v\n", err)
    }

    client.Close()
    fmt.Println("Shutdown complete")
}
```

### Pitfalls to Avoid

- Don't use the cancelled context for final operations
- Set reasonable timeout for shutdown operations
- Close client after all operations complete

## Pattern 2: Idempotent Producer

### When to Use

When you need exactly-once production semantics to prevent duplicate messages on retries.

### Implementation

```go
package main

import (
    "context"
    "fmt"
    "github.com/twmb/franz-go/pkg/kgo"
)

func main() {
    client, err := kgo.NewClient(
        kgo.SeedBrokers("localhost:9092"),

        // Enable idempotent producer
        kgo.RequiredAcks(kgo.AllISRAcks()),
        kgo.MaxProduceRequestsInflightPerBroker(1),
        kgo.ProducerOnDataLossDetected(func(topic string, partition int32) {
            fmt.Printf("Data loss detected: %s[%d]\n", topic, partition)
        }),
    )
    if err != nil {
        panic(err)
    }
    defer client.Close()

    ctx := context.Background()

    // Produce with idempotency
    for i := 0; i < 10; i++ {
        client.Produce(ctx, &kgo.Record{
            Topic: "events",
            Value: []byte(fmt.Sprintf("idempotent-message-%d", i)),
        }, func(r *kgo.Record, err error) {
            if err != nil {
                fmt.Printf("Error: %v\n", err)
                return
            }
            fmt.Printf("Delivered to %s[%d]@%d\n", r.Topic, r.Partition, r.Offset)
        })
    }

    client.Flush(ctx)
}
```

### Pitfalls to Avoid

- Idempotency is per-producer-session
- Requires acks=all and max.in.flight=1
- Only prevents duplicates from retries, not application resends

## Pattern 3: Batch Processing

### When to Use

When processing messages in batches improves efficiency, such as bulk database inserts or API calls.

### Implementation

```go
package main

import (
    "context"
    "fmt"
    "time"
    "github.com/twmb/franz-go/pkg/kgo"
)

type BatchProcessor struct {
    client    *kgo.Client
    batchSize int
    timeout   time.Duration
}

func (bp *BatchProcessor) Run(ctx context.Context) error {
    for {
        batch := make([]*kgo.Record, 0, bp.batchSize)
        startTime := time.Now()

        // Collect batch
        for len(batch) < bp.batchSize {
            // Check timeout
            if time.Since(startTime) > bp.timeout && len(batch) > 0 {
                break
            }

            // Calculate remaining timeout
            remaining := bp.timeout - time.Since(startTime)
            if remaining < 0 {
                remaining = 0
            }

            pollCtx, cancel := context.WithTimeout(ctx, remaining)
            fetches := bp.client.PollFetches(pollCtx)
            cancel()

            if ctx.Err() != nil {
                return ctx.Err()
            }

            fetches.EachRecord(func(r *kgo.Record) {
                batch = append(batch, r)
            })
        }

        if len(batch) == 0 {
            continue
        }

        // Process batch
        fmt.Printf("Processing batch of %d records\n", len(batch))
        if err := bp.processBatch(batch); err != nil {
            fmt.Printf("Batch processing error: %v\n", err)
            // Don't commit on error
            continue
        }

        // Commit after successful processing
        bp.client.CommitUncommittedOffsets(ctx)
    }
}

func (bp *BatchProcessor) processBatch(batch []*kgo.Record) error {
    // Simulate batch processing
    for _, r := range batch {
        fmt.Printf("  - %s: %s\n", r.Key, r.Value)
    }
    return nil
}

func main() {
    client, _ := kgo.NewClient(
        kgo.SeedBrokers("localhost:9092"),
        kgo.ConsumerGroup("batch-processor"),
        kgo.ConsumeTopics("events"),
    )
    defer client.Close()

    processor := &BatchProcessor{
        client:    client,
        batchSize: 100,
        timeout:   5 * time.Second,
    }

    processor.Run(context.Background())
}
```

### Pitfalls to Avoid

- Handle partial batch failures appropriately
- Consider memory limits for batch size
- Implement timeout to avoid waiting forever

## Pattern 4: Parallel Partition Processing

### When to Use

When you want to process partitions in parallel within a single consumer for maximum throughput.

### Implementation

```go
package main

import (
    "context"
    "fmt"
    "sync"
    "github.com/twmb/franz-go/pkg/kgo"
)

func main() {
    client, _ := kgo.NewClient(
        kgo.SeedBrokers("localhost:9092"),
        kgo.ConsumerGroup("parallel-processor"),
        kgo.ConsumeTopics("events"),
    )
    defer client.Close()

    ctx := context.Background()

    for {
        fetches := client.PollFetches(ctx)

        if ctx.Err() != nil {
            break
        }

        // Group records by partition
        byPartition := make(map[int32][]*kgo.Record)
        fetches.EachRecord(func(r *kgo.Record) {
            byPartition[r.Partition] = append(byPartition[r.Partition], r)
        })

        // Process each partition in parallel
        var wg sync.WaitGroup
        for partition, records := range byPartition {
            wg.Add(1)
            go func(p int32, recs []*kgo.Record) {
                defer wg.Done()
                for _, r := range recs {
                    fmt.Printf("Partition %d: %s\n", p, r.Value)
                }
            }(partition, records)
        }
        wg.Wait()

        // Commit after all partitions processed
        client.CommitUncommittedOffsets(ctx)
    }
}
```

### Pitfalls to Avoid

- Maintain ordering within partition if required
- Handle errors from all goroutines
- Don't commit until all partitions are processed

## Pattern 5: Dead Letter Queue

### When to Use

When you need to handle messages that fail processing repeatedly without blocking the consumer.

### Implementation

```go
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "time"
    "github.com/twmb/franz-go/pkg/kgo"
)

type DLQMessage struct {
    OriginalTopic     string `json:"original_topic"`
    OriginalPartition int32  `json:"original_partition"`
    OriginalOffset    int64  `json:"original_offset"`
    OriginalKey       []byte `json:"original_key"`
    OriginalValue     []byte `json:"original_value"`
    Error             string `json:"error"`
    Timestamp         string `json:"timestamp"`
    RetryCount        int    `json:"retry_count"`
}

type ConsumerWithDLQ struct {
    client     *kgo.Client
    dlqTopic   string
    maxRetries int
    retries    map[string]int // key: topic-partition-offset
}

func (c *ConsumerWithDLQ) Process(ctx context.Context, handler func(*kgo.Record) error) {
    for {
        fetches := c.client.PollFetches(ctx)
        if ctx.Err() != nil {
            break
        }

        fetches.EachRecord(func(r *kgo.Record) {
            key := fmt.Sprintf("%s-%d-%d", r.Topic, r.Partition, r.Offset)

            if err := handler(r); err != nil {
                c.retries[key]++

                if c.retries[key] >= c.maxRetries {
                    c.sendToDLQ(ctx, r, err)
                    delete(c.retries, key)
                } else {
                    fmt.Printf("Retry %d/%d for %s\n",
                        c.retries[key], c.maxRetries, key)
                }
            } else {
                delete(c.retries, key)
            }
        })

        c.client.CommitUncommittedOffsets(ctx)
    }
}

func (c *ConsumerWithDLQ) sendToDLQ(ctx context.Context, r *kgo.Record, err error) {
    dlqMsg := DLQMessage{
        OriginalTopic:     r.Topic,
        OriginalPartition: r.Partition,
        OriginalOffset:    r.Offset,
        OriginalKey:       r.Key,
        OriginalValue:     r.Value,
        Error:             err.Error(),
        Timestamp:         time.Now().Format(time.RFC3339),
        RetryCount:        c.maxRetries,
    }

    value, _ := json.Marshal(dlqMsg)

    c.client.Produce(ctx, &kgo.Record{
        Topic: c.dlqTopic,
        Key:   r.Key,
        Value: value,
    }, func(r *kgo.Record, err error) {
        if err != nil {
            fmt.Printf("DLQ send failed: %v\n", err)
        } else {
            fmt.Printf("Sent to DLQ: %s[%d]@%d\n", r.Topic, r.Partition, r.Offset)
        }
    })
}

func main() {
    client, _ := kgo.NewClient(
        kgo.SeedBrokers("localhost:9092"),
        kgo.ConsumerGroup("dlq-consumer"),
        kgo.ConsumeTopics("events"),
    )
    defer client.Close()

    consumer := &ConsumerWithDLQ{
        client:     client,
        dlqTopic:   "events-dlq",
        maxRetries: 3,
        retries:    make(map[string]int),
    }

    consumer.Process(context.Background(), func(r *kgo.Record) error {
        // Your processing logic
        return nil
    })
}
```

### Pitfalls to Avoid

- Ensure DLQ production succeeds before committing
- Monitor DLQ for growing backlogs
- Implement tooling to replay from DLQ

## Anti-Patterns

### Anti-Pattern 1: Synchronous Processing in Callback

Don't do heavy work in produce callbacks - they run in the client's goroutine.

```go
// Bad: Blocking callback
client.Produce(ctx, record, func(r *kgo.Record, err error) {
    time.Sleep(time.Second)  // Blocks other callbacks
    http.Post("http://api/notify", ...)  // Network call in callback
})

// Good: Offload to worker
results := make(chan *kgo.Record, 100)
go worker(results)

client.Produce(ctx, record, func(r *kgo.Record, err error) {
    if err == nil {
        results <- r  // Non-blocking send
    }
})
```

### Anti-Pattern 2: Not Handling Context Cancellation

Always check for context cancellation in loops.

```go
// Bad: Ignores cancellation
for {
    fetches := client.PollFetches(ctx)
    // Continues even if ctx is cancelled
}

// Good: Check and exit
for {
    fetches := client.PollFetches(ctx)
    if ctx.Err() != nil {
        break
    }
    // Process
}
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Application shutdown | Graceful Shutdown |
| Prevent duplicate production | Idempotent Producer |
| Bulk database inserts | Batch Processing |
| Maximum throughput | Parallel Partition Processing |
| Handle poison messages | Dead Letter Queue |
| Need total ordering | Single partition per key |
| Cross-partition transactions | Kafka Transactions (not covered) |
