# Core Concepts

## Overview

FSD Dependencies define the external resources your service needs to function. This includes databases, storage, messaging systems, and other services. By declaring dependencies explicitly, FSD can automatically provision resources, generate IAM policies, and ensure proper connectivity.

## Concept 1: Dependency Declaration

### What It Is

Dependencies are declared as an array in your FSD YAML file. Each dependency has a type, name, and access mode that determines how your service interacts with the resource.

### Why It Matters

Explicit dependency declaration enables:
- Automatic IAM policy generation with least-privilege access
- Resource provisioning and lifecycle management
- Service topology visualization and validation
- Consistent configuration across environments

### How It Works

```yaml
name: order-service
platform: ecs

dependencies:
  # Database for storing orders
  - type: aws_dynamodb_table
    name: orders
    mode: read_write

  # Bucket for order attachments
  - type: aws_s3_bucket
    name: order-attachments
    mode: read_write

  # Queue for async notifications
  - type: aws_sqs_queue
    name: order-notifications
    mode: producer
```

**Dependency Structure:**
- `type`: The kind of resource (aws_dynamodb_table, aws_s3_bucket, etc.)
- `name`: The logical name of the resource
- `mode`: How your service accesses the resource (read, write, consumer, etc.)

## Concept 2: Access Modes

### What It Is

Access modes define the operations your service can perform on a dependency. FSD uses these to generate appropriate IAM policies.

### Why It Matters

Using correct access modes ensures:
- Least-privilege security principle
- Clear documentation of service capabilities
- Automatic IAM policy generation
- Prevention of accidental destructive operations

### How It Works

#### Storage Access Modes

```yaml
# Read-only access
dependencies:
  - type: aws_dynamodb_table
    name: config
    mode: read          # GetItem, Query, Scan only

# Write-only access
dependencies:
  - type: aws_s3_bucket
    name: logs
    mode: write         # PutObject, DeleteObject only

# Full access
dependencies:
  - type: aws_dynamodb_table
    name: users
    mode: read_write    # All operations
```

#### Messaging Access Modes

```yaml
# Consumer reads from queue
dependencies:
  - type: aws_sqs_queue
    name: tasks
    mode: consumer      # ReceiveMessage, DeleteMessage

# Producer sends to queue
dependencies:
  - type: aws_sqs_queue
    name: notifications
    mode: producer      # SendMessage

# Publisher sends to topic
dependencies:
  - type: aws_sns_topic
    name: events
    mode: producer      # Publish
```

**Mode Reference Table:**

| Resource Type | read | write | read_write | consumer | producer |
|--------------|------|-------|------------|----------|----------|
| DynamoDB | Get, Query, Scan | Put, Update, Delete | All | - | - |
| S3 | Get, List | Put, Delete | All | - | - |
| SQS | - | - | - | Receive, Delete | Send |
| SNS | - | - | - | - | Publish |
| Kinesis | - | - | - | GetRecords | PutRecord |

## Concept 3: IAM Policy Generation

### What It Is

FSD automatically generates IAM policies based on your dependency declarations, ensuring your service has exactly the permissions it needs.

### Why It Matters

Automatic policy generation provides:
- Consistent security across all services
- Reduced human error in policy creation
- Easy auditing of permissions
- Compliance with least-privilege principles

### How It Works

```yaml
# This dependency declaration...
dependencies:
  - type: aws_dynamodb_table
    name: users
    mode: read

# Generates this IAM policy statement:
# {
#   "Effect": "Allow",
#   "Action": [
#     "dynamodb:GetItem",
#     "dynamodb:Query",
#     "dynamodb:Scan",
#     "dynamodb:BatchGetItem"
#   ],
#   "Resource": [
#     "arn:aws:dynamodb:*:*:table/users",
#     "arn:aws:dynamodb:*:*:table/users/index/*"
#   ]
# }
```

**Complex Example:**

```yaml
dependencies:
  - type: aws_s3_bucket
    name: documents
    mode: read_write
    prefix: uploads/        # Restricts access to prefix
    encryption:
      enabled: true
      kms_key: ${kms:documents-key}

# Generates:
# {
#   "Effect": "Allow",
#   "Action": [
#     "s3:GetObject",
#     "s3:PutObject",
#     "s3:DeleteObject",
#     "s3:ListBucket"
#   ],
#   "Resource": [
#     "arn:aws:s3:::documents/uploads/*",
#     "arn:aws:s3:::documents"
#   ],
#   "Condition": {
#     "StringLike": {
#       "s3:prefix": ["uploads/*"]
#     }
#   }
# }
# Plus KMS permissions for the specified key
```

## Concept 4: Database Dependencies

### What It Is

Database dependencies include DynamoDB tables, RDS instances, and ElastiCache clusters. Each has specific configuration options for access patterns, encryption, and connectivity.

### Why It Matters

Proper database dependency configuration ensures:
- Correct network connectivity
- Appropriate credential management
- Optimized query permissions
- Data encryption compliance

### How It Works

#### DynamoDB Tables

```yaml
dependencies:
  - type: aws_dynamodb_table
    name: orders
    mode: read_write

    # Specific index access
    indexes:
      - name: status-index
        mode: read
      - name: customer-index
        mode: read

    # DynamoDB Streams access
    streams:
      enabled: true
      mode: consumer
```

#### RDS Databases

```yaml
dependencies:
  - type: aws_rds_instance
    name: postgres-main
    database: orders_db
    credentials: ${secrets:orders/db-credentials}
    ssl_mode: verify-full

    # Connection pooling
    connection:
      max_connections: 10
      idle_timeout: 300
```

#### ElastiCache

```yaml
dependencies:
  - type: aws_elasticache
    name: session-cache
    engine: redis
    mode: read_write

    # Cluster configuration
    cluster:
      mode: cluster
      node_type: cache.t3.micro
```

## Concept 5: Messaging Dependencies

### What It Is

Messaging dependencies include SQS queues, SNS topics, Kinesis streams, and Kafka topics. These enable asynchronous communication between services.

### Why It Matters

Proper messaging configuration ensures:
- Reliable message delivery
- Appropriate batch processing
- Dead letter queue handling
- Consumer group management

### How It Works

#### SQS Queues

```yaml
dependencies:
  # Consumer configuration
  - type: aws_sqs_queue
    name: order-tasks
    mode: consumer
    batch_size: 10
    visibility_timeout: 300
    wait_time_seconds: 20

  # Producer configuration
  - type: aws_sqs_queue
    name: notifications
    mode: producer
    message_group_id: orders    # For FIFO queues
```

#### Kafka Topics

```yaml
dependencies:
  - type: kafka_topic
    name: order-events
    mode: consumer
    consumer_group: order-processor
    bootstrap_servers: ${ssm:/kafka/bootstrap}

    # Consumer configuration
    auto_offset_reset: earliest
    enable_auto_commit: false

  - type: kafka_topic
    name: shipping-events
    mode: producer
    bootstrap_servers: ${ssm:/kafka/bootstrap}
```

#### Kinesis Streams

```yaml
dependencies:
  - type: aws_kinesis_stream
    name: clickstream
    mode: consumer
    shard_iterator_type: LATEST

    # Enhanced fan-out for high-throughput
    enhanced_fan_out:
      enabled: true
      consumer_name: analytics-processor
```

## Concept 6: Cross-Service Dependencies

### What It Is

Cross-service dependencies define how your service communicates with other FSD services, enabling microservice architectures with proper service discovery.

### Why It Matters

Service dependencies enable:
- Automatic service discovery
- Network policy configuration
- Dependency graph visualization
- Deployment ordering

### How It Works

```yaml
name: checkout-service
platform: ecs

dependencies:
  # Depends on user service for authentication
  - type: service
    name: user-service
    mode: client
    discovery:
      method: dns
      namespace: production

  # Depends on inventory service for stock checks
  - type: service
    name: inventory-service
    mode: client
    discovery:
      method: service_mesh
      timeout: 5000

  # Depends on payment service (external)
  - type: service
    name: payment-gateway
    mode: client
    external: true
    endpoint: ${ssm:/checkout/payment-gateway-url}
```

**Service URL Access:**

```yaml
# In environment variables, reference discovered service
environment:
  USER_SERVICE_URL: ${service:user-service:url}
  INVENTORY_SERVICE_URL: ${service:inventory-service:url}
  PAYMENT_GATEWAY_URL: ${service:payment-gateway:url}
```

## Summary

Key takeaways from these concepts:

1. **Dependency Declaration**: Explicitly declare all external resources in the `dependencies` array
2. **Access Modes**: Use the minimum required mode (read over read_write when possible)
3. **IAM Generation**: FSD automatically creates least-privilege IAM policies
4. **Database Dependencies**: Configure indexes, streams, and connection settings appropriately
5. **Messaging Dependencies**: Set batch sizes, timeouts, and consumer groups correctly
6. **Service Dependencies**: Enable service discovery for microservice communication

Well-configured dependencies are the foundation of secure, maintainable cloud services. Always prefer explicit declarations over implicit access.
