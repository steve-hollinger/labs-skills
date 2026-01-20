# FSD Dependencies

Learn to configure external dependencies for FSD services including databases, storage, messaging, and cross-service integrations.

## Learning Objectives

After completing this skill, you will be able to:
- Define DynamoDB, S3, Kafka, and RDS dependencies in FSD YAML
- Configure appropriate IAM policies for each dependency type
- Set up cross-service dependencies and service discovery
- Apply best practices for secure and efficient dependency configuration
- Troubleshoot common dependency configuration issues

## Prerequisites

- [FSD YAML Config](../fsd-yaml-config/) - Understanding of basic FSD structure
- Familiarity with AWS services (DynamoDB, S3, SQS, RDS)
- Basic understanding of IAM policies

## Quick Start

```bash
# Validate example configurations
make validate-all

# Validate a specific example
make validate YAML=examples/01-dynamodb-dependency.yml

# Run exercises
make exercises

# Check your solutions
make check-solutions
```

## Dependency Types

FSD supports multiple dependency types for AWS and third-party services:

| Type | Description | Common Use Cases |
|------|-------------|------------------|
| `aws_dynamodb_table` | NoSQL database tables | User data, sessions, caches |
| `aws_s3_bucket` | Object storage | Files, images, backups |
| `aws_sqs_queue` | Message queues | Async processing, decoupling |
| `aws_sns_topic` | Pub/sub messaging | Notifications, fan-out |
| `aws_kinesis_stream` | Real-time streaming | Event streaming, analytics |
| `aws_rds_instance` | Relational databases | Transactions, complex queries |
| `aws_elasticache` | In-memory cache | Session storage, caching |
| `kafka_topic` | Kafka messaging | Event sourcing, streaming |
| `service` | Cross-service dependency | Microservice communication |

## Concepts

### Dependency Declaration

Dependencies are declared in the `dependencies` block of your FSD YAML:

```yaml
name: order-service
platform: ecs

dependencies:
  - type: aws_dynamodb_table
    name: orders
    mode: read_write

  - type: aws_s3_bucket
    name: order-attachments
    mode: read_write

  - type: aws_sqs_queue
    name: order-notifications
    mode: producer
```

### Access Modes

Each dependency supports different access modes that determine IAM permissions:

| Mode | DynamoDB | S3 | SQS | SNS |
|------|----------|-----|-----|-----|
| `read` | GetItem, Query, Scan | GetObject, ListBucket | - | - |
| `write` | PutItem, UpdateItem, DeleteItem | PutObject, DeleteObject | - | - |
| `read_write` | All read + write | All read + write | - | - |
| `consumer` | - | - | ReceiveMessage, DeleteMessage | - |
| `producer` | - | - | SendMessage | Publish |

### IAM Policy Generation

FSD automatically generates least-privilege IAM policies based on your dependency declarations:

```yaml
# This declaration...
dependencies:
  - type: aws_dynamodb_table
    name: users
    mode: read

# ...generates this IAM policy
# {
#   "Effect": "Allow",
#   "Action": [
#     "dynamodb:GetItem",
#     "dynamodb:Query",
#     "dynamodb:Scan"
#   ],
#   "Resource": "arn:aws:dynamodb:*:*:table/users"
# }
```

## Examples

### Example 1: DynamoDB Dependency

A service with DynamoDB tables for data storage.

```bash
make validate YAML=examples/01-dynamodb-dependency.yml
```

See [examples/01-dynamodb-dependency.yml](./examples/01-dynamodb-dependency.yml)

### Example 2: S3 and SQS Dependencies

A file processing service with S3 storage and SQS queues.

```bash
make validate YAML=examples/02-s3-sqs-dependencies.yml
```

See [examples/02-s3-sqs-dependencies.yml](./examples/02-s3-sqs-dependencies.yml)

### Example 3: Kafka Dependencies

An event-driven service using Kafka topics.

```bash
make validate YAML=examples/03-kafka-dependencies.yml
```

See [examples/03-kafka-dependencies.yml](./examples/03-kafka-dependencies.yml)

### Example 4: RDS Database

A service connecting to an RDS PostgreSQL database.

```bash
make validate YAML=examples/04-rds-dependency.yml
```

See [examples/04-rds-dependency.yml](./examples/04-rds-dependency.yml)

### Example 5: Cross-Service Dependencies

Microservices with inter-service communication.

```bash
make validate YAML=examples/05-cross-service-dependencies.yml
```

See [examples/05-cross-service-dependencies.yml](./examples/05-cross-service-dependencies.yml)

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Add DynamoDB tables to an existing service
2. **Exercise 2**: Configure S3 bucket with lifecycle policies
3. **Exercise 3**: Set up Kafka consumer and producer
4. **Exercise 4**: Design a multi-service dependency graph

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Mistake 1: Over-Permissive Access Modes

Granting `read_write` when only `read` is needed violates least-privilege.

```yaml
# Bad - too permissive
dependencies:
  - type: aws_dynamodb_table
    name: audit-logs
    mode: read_write  # Service only reads logs

# Good - appropriate permissions
dependencies:
  - type: aws_dynamodb_table
    name: audit-logs
    mode: read
```

### Mistake 2: Missing Table Indexes

Forgetting to include GSI/LSI permissions for DynamoDB queries.

```yaml
# Include index access for query patterns
dependencies:
  - type: aws_dynamodb_table
    name: orders
    mode: read_write
    indexes:
      - name: status-created-index
        mode: read
      - name: customer-id-index
        mode: read
```

### Mistake 3: Hardcoded Resource Names

Using environment-specific names instead of references.

```yaml
# Bad - hardcoded environment
dependencies:
  - type: aws_s3_bucket
    name: prod-user-uploads

# Good - environment-agnostic with naming convention
dependencies:
  - type: aws_s3_bucket
    name: ${environment}-user-uploads
    # Or use the logical name and let FSD handle naming
    name: user-uploads
```

## Further Reading

- [FSD YAML Config](../fsd-yaml-config/) - Basic FSD service configuration
- [FSD IAM Policies](../fsd-iam-policies/) - Advanced IAM policy patterns
- [DynamoDB Schema](../../05-data-databases/dynamodb-schema/) - DynamoDB design patterns
- [Kafka Event Streaming](../../05-data-databases/kafka-event-streaming/) - Kafka integration patterns
