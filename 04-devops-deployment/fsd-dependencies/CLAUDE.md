# CLAUDE.md - FSD Dependencies

This skill teaches FSD dependency configuration for AWS services (DynamoDB, S3, SQS, RDS) and cross-service integrations.

## Key Concepts

- **Dependency Types**: DynamoDB, S3, SQS, SNS, Kinesis, RDS, ElastiCache, Kafka, Service
- **Access Modes**: read, write, read_write, consumer, producer
- **IAM Policy Generation**: Automatic least-privilege policies from declarations
- **Cross-Service Dependencies**: Service discovery and inter-service communication

## Common Commands

```bash
make validate-all        # Validate all dependency examples
make validate YAML=file  # Validate a specific file
make exercises           # List available exercises
make check-solutions     # Validate exercise solutions
make lint               # Run YAML linting
make clean              # Remove temporary files
```

## Project Structure

```
fsd-dependencies/
├── README.md
├── CLAUDE.md
├── Makefile
├── docs/
│   ├── concepts.md          # Dependency concepts
│   └── patterns.md          # Configuration patterns
├── examples/
│   ├── 01-dynamodb-dependency.yml
│   ├── 02-s3-sqs-dependencies.yml
│   ├── 03-kafka-dependencies.yml
│   ├── 04-rds-dependency.yml
│   └── 05-cross-service-dependencies.yml
└── exercises/
    ├── exercise-1-dynamodb-tables.md
    ├── exercise-2-s3-lifecycle.md
    ├── exercise-3-kafka-setup.md
    ├── exercise-4-service-graph.md
    └── solutions/
        ├── solution-1.yml
        ├── solution-2.yml
        ├── solution-3.yml
        └── solution-4.yml
```

## Dependency Schema Reference

### DynamoDB Table

```yaml
dependencies:
  - type: aws_dynamodb_table
    name: table-name
    mode: read | write | read_write
    indexes:
      - name: gsi-name
        mode: read | write | read_write
    streams:
      enabled: true
      mode: consumer
```

### S3 Bucket

```yaml
dependencies:
  - type: aws_s3_bucket
    name: bucket-name
    mode: read | write | read_write
    prefix: optional/prefix/    # Limit access to prefix
    encryption:
      enabled: true
      kms_key: ${kms:key-alias}
```

### SQS Queue

```yaml
dependencies:
  - type: aws_sqs_queue
    name: queue-name
    mode: consumer | producer
    batch_size: 10              # For consumers
    visibility_timeout: 30      # Seconds
```

### SNS Topic

```yaml
dependencies:
  - type: aws_sns_topic
    name: topic-name
    mode: producer | subscriber
```

### Kinesis Stream

```yaml
dependencies:
  - type: aws_kinesis_stream
    name: stream-name
    mode: consumer | producer
    shard_iterator_type: LATEST | TRIM_HORIZON
```

### RDS Instance

```yaml
dependencies:
  - type: aws_rds_instance
    name: database-identifier
    database: database-name
    credentials: ${secrets:db-credentials}
    ssl_mode: require
```

### ElastiCache

```yaml
dependencies:
  - type: aws_elasticache
    name: cache-cluster
    engine: redis | memcached
    mode: read | write | read_write
```

### Kafka Topic

```yaml
dependencies:
  - type: kafka_topic
    name: topic-name
    mode: consumer | producer
    consumer_group: my-consumer-group
    bootstrap_servers: ${ssm:/kafka/bootstrap-servers}
```

### Cross-Service

```yaml
dependencies:
  - type: service
    name: other-service-name
    mode: client
    discovery:
      method: dns | service_mesh
      namespace: production
```

## Access Mode to IAM Actions Mapping

### DynamoDB

| Mode | IAM Actions |
|------|-------------|
| read | GetItem, Query, Scan, BatchGetItem |
| write | PutItem, UpdateItem, DeleteItem, BatchWriteItem |
| read_write | All of the above |

### S3

| Mode | IAM Actions |
|------|-------------|
| read | GetObject, GetObjectVersion, ListBucket |
| write | PutObject, DeleteObject, AbortMultipartUpload |
| read_write | All of the above |

### SQS

| Mode | IAM Actions |
|------|-------------|
| consumer | ReceiveMessage, DeleteMessage, GetQueueAttributes |
| producer | SendMessage, GetQueueUrl |

## Common Mistakes

1. **Over-permissive modes**
   - Using `read_write` when only `read` needed
   - Fix: Always use the minimum required mode

2. **Missing GSI/LSI permissions**
   - Forgetting to include index permissions for queries
   - Fix: Explicitly list all indexes used by the service

3. **Hardcoded bucket/table names**
   - Using environment-specific names directly
   - Fix: Use logical names or environment variables

4. **Missing encryption configuration**
   - Not specifying KMS keys for encrypted resources
   - Fix: Always include encryption config for sensitive data

5. **Circular dependencies**
   - Service A depends on B, B depends on A
   - Fix: Use async messaging to break cycles

## When Users Ask About...

### "How do I add a DynamoDB table?"
```yaml
dependencies:
  - type: aws_dynamodb_table
    name: my-table
    mode: read_write
```

### "What mode should I use for SQS?"
- `consumer` for services reading from queue
- `producer` for services sending to queue
- You can have both if service does both

### "How do I connect to another service?"
```yaml
dependencies:
  - type: service
    name: other-service
    mode: client
```
Then use `${service:other-service:url}` in environment variables.

### "How do I use the same table in multiple services?"
Each service declares its own dependency with appropriate mode. FSD coordinates to prevent conflicts.

### "How do I add encryption?"
```yaml
dependencies:
  - type: aws_s3_bucket
    name: sensitive-data
    encryption:
      enabled: true
      kms_key: ${kms:my-key}
```

## Testing Notes

- Validate YAML syntax with `make validate`
- Check for circular dependencies manually
- Verify IAM policies are least-privilege
- Test access patterns match declared modes

## Dependencies

Key tools used:
- `yamllint`: YAML syntax validation
- `yq`: YAML processing
- FSD CLI: Full validation (if available)

## Related Skills

- [FSD YAML Config](../fsd-yaml-config/) - Basic service configuration
- [FSD IAM Policies](../fsd-iam-policies/) - Advanced IAM patterns
- [DynamoDB Schema](../../05-data-databases/dynamodb-schema/) - Table design
- [Kafka Event Streaming](../../05-data-databases/kafka-event-streaming/) - Kafka patterns
