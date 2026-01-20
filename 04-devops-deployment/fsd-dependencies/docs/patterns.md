# Common Patterns

## Overview

This document covers common patterns and best practices for FSD dependency configurations across different service architectures.

## Pattern 1: CRUD Service with DynamoDB

### When to Use

Use this pattern for services that need to create, read, update, and delete items in a DynamoDB table with optional secondary indexes for queries.

### Implementation

```yaml
name: user-service
platform: ecs
description: User management service with full CRUD operations

compute:
  cpu: 512
  memory: 1024
  desired_count: 3

dependencies:
  # Main table with full access
  - type: aws_dynamodb_table
    name: users
    mode: read_write
    indexes:
      - name: email-index
        mode: read
      - name: created-at-index
        mode: read

  # Audit log table (write-only for this service)
  - type: aws_dynamodb_table
    name: user-audit-log
    mode: write

environment:
  USERS_TABLE: users
  AUDIT_TABLE: user-audit-log
```

### Example Use Case

```yaml
# E-commerce product catalog
dependencies:
  - type: aws_dynamodb_table
    name: products
    mode: read_write
    indexes:
      - name: category-index
        mode: read
      - name: brand-index
        mode: read
      - name: price-range-index
        mode: read
```

### Pitfalls to Avoid

- Granting write access to audit/log tables that should be append-only
- Forgetting to include index permissions for query patterns
- Not considering eventual consistency for read-after-write scenarios

## Pattern 2: File Processing Pipeline

### When to Use

Use this pattern for services that process files uploaded to S3, with SQS for job queuing and dead letter handling.

### Implementation

```yaml
name: document-processor
platform: lambda
description: Processes uploaded documents and extracts metadata

compute:
  memory: 2048
  timeout: 300
  runtime: python3.11

dependencies:
  # Source bucket (read uploaded files)
  - type: aws_s3_bucket
    name: document-uploads
    mode: read
    prefix: incoming/
    event_notifications:
      - event: s3:ObjectCreated:*
        destination: ${sqs:document-queue}

  # Destination bucket (write processed files)
  - type: aws_s3_bucket
    name: document-processed
    mode: write
    prefix: processed/
    encryption:
      enabled: true
      kms_key: ${kms:documents-key}

  # Processing queue
  - type: aws_sqs_queue
    name: document-queue
    mode: consumer
    batch_size: 1
    visibility_timeout: 360

  # Dead letter queue for failed processing
  - type: aws_sqs_queue
    name: document-dlq
    mode: producer

  # Metadata storage
  - type: aws_dynamodb_table
    name: document-metadata
    mode: write

triggers:
  - type: sqs
    queue: document-queue
    batch_size: 1
```

### Example Use Case

```yaml
# Image thumbnail generation pipeline
dependencies:
  - type: aws_s3_bucket
    name: user-uploads
    mode: read
    prefix: images/

  - type: aws_s3_bucket
    name: thumbnails
    mode: write

  - type: aws_sqs_queue
    name: thumbnail-queue
    mode: consumer
```

### Pitfalls to Avoid

- Setting visibility_timeout shorter than function timeout
- Not handling S3 eventual consistency (retry on 404)
- Missing dead letter queue configuration

## Pattern 3: Event-Driven Microservice

### When to Use

Use this pattern for services that consume events from Kafka or Kinesis and produce events for downstream services.

### Implementation

```yaml
name: order-processor
platform: eks
description: Processes order events and updates inventory

compute:
  replicas: 3
  resources:
    requests:
      cpu: "500m"
      memory: "512Mi"

dependencies:
  # Consume order events
  - type: kafka_topic
    name: order-events
    mode: consumer
    consumer_group: order-processor
    bootstrap_servers: ${ssm:/kafka/bootstrap}
    auto_offset_reset: earliest
    enable_auto_commit: false

  # Produce inventory updates
  - type: kafka_topic
    name: inventory-events
    mode: producer
    bootstrap_servers: ${ssm:/kafka/bootstrap}

  # Produce shipping events
  - type: kafka_topic
    name: shipping-events
    mode: producer
    bootstrap_servers: ${ssm:/kafka/bootstrap}

  # Store order state
  - type: aws_dynamodb_table
    name: orders
    mode: read_write

  # Cache for frequently accessed data
  - type: aws_elasticache
    name: order-cache
    engine: redis
    mode: read_write

environment:
  KAFKA_BOOTSTRAP: ${ssm:/kafka/bootstrap}
  REDIS_URL: ${elasticache:order-cache:url}
```

### Example Use Case

```yaml
# Real-time analytics processor
dependencies:
  - type: aws_kinesis_stream
    name: clickstream
    mode: consumer
    enhanced_fan_out:
      enabled: true
      consumer_name: analytics

  - type: aws_dynamodb_table
    name: session-aggregates
    mode: read_write
    streams:
      enabled: true
```

### Pitfalls to Avoid

- Using auto-commit with at-least-once processing requirements
- Not handling consumer group rebalancing
- Missing idempotency for event processing

## Pattern 4: API Gateway with Multiple Backends

### When to Use

Use this pattern for API services that aggregate data from multiple backend services and data sources.

### Implementation

```yaml
name: api-gateway
platform: ecs
description: GraphQL API aggregating multiple backend services

compute:
  cpu: 1024
  memory: 2048
  desired_count: 5

dependencies:
  # Backend service dependencies
  - type: service
    name: user-service
    mode: client
    discovery:
      method: dns
      namespace: production
    timeout: 5000

  - type: service
    name: product-service
    mode: client
    discovery:
      method: dns
      namespace: production
    timeout: 3000

  - type: service
    name: order-service
    mode: client
    discovery:
      method: dns
      namespace: production
    timeout: 10000

  # Caching layer
  - type: aws_elasticache
    name: api-cache
    engine: redis
    mode: read_write

  # Rate limiting data
  - type: aws_dynamodb_table
    name: rate-limits
    mode: read_write

environment:
  USER_SERVICE_URL: ${service:user-service:url}
  PRODUCT_SERVICE_URL: ${service:product-service:url}
  ORDER_SERVICE_URL: ${service:order-service:url}
  REDIS_URL: ${elasticache:api-cache:url}
```

### Example Use Case

```yaml
# BFF (Backend for Frontend) pattern
dependencies:
  - type: service
    name: auth-service
    mode: client

  - type: service
    name: content-service
    mode: client

  - type: service
    name: recommendation-service
    mode: client

  - type: aws_elasticache
    name: session-store
    mode: read_write
```

### Pitfalls to Avoid

- Not setting appropriate timeouts for each backend
- Missing circuit breaker configuration
- Over-caching stale data

## Pattern 5: Data Lake Ingestion

### When to Use

Use this pattern for batch jobs that ingest data from various sources into a data lake with proper partitioning.

### Implementation

```yaml
name: data-lake-ingestion
platform: batch
description: Daily ingestion of transaction data into data lake

compute:
  vcpus: 4
  memory: 16384

job:
  type: array
  array_properties:
    size: 24
  timeout: 14400

dependencies:
  # Source database (read-only)
  - type: aws_rds_instance
    name: transactions-db
    database: transactions
    credentials: ${secrets:ingestion/db-creds}
    mode: read

  # Raw data landing zone
  - type: aws_s3_bucket
    name: data-lake-raw
    mode: write
    prefix: transactions/
    encryption:
      enabled: true
      kms_key: ${kms:data-lake-key}

  # Processed data zone
  - type: aws_s3_bucket
    name: data-lake-curated
    mode: write
    prefix: transactions/
    encryption:
      enabled: true
      kms_key: ${kms:data-lake-key}

  # Metadata catalog
  - type: aws_dynamodb_table
    name: ingestion-metadata
    mode: read_write

  # Glue catalog for schema management
  - type: aws_glue_catalog
    name: data-lake-catalog
    mode: read_write

environment:
  SOURCE_DB: ${rds:transactions-db:endpoint}
  RAW_BUCKET: data-lake-raw
  CURATED_BUCKET: data-lake-curated
```

### Pitfalls to Avoid

- Not handling incremental loads properly
- Missing data validation before writing to curated zone
- Insufficient error handling for partial failures

## Anti-Patterns

### Anti-Pattern 1: Over-Permissive Dependencies

Never grant more access than required.

```yaml
# BAD - Full access when read-only needed
dependencies:
  - type: aws_dynamodb_table
    name: reference-data
    mode: read_write  # Service only reads this table!
```

### Better Approach

```yaml
# GOOD - Minimal required access
dependencies:
  - type: aws_dynamodb_table
    name: reference-data
    mode: read
```

### Anti-Pattern 2: Missing Index Declarations

Forgetting to declare index access for DynamoDB queries.

```yaml
# BAD - Will fail GSI queries at runtime
dependencies:
  - type: aws_dynamodb_table
    name: orders
    mode: read_write
    # Missing: indexes configuration
```

### Better Approach

```yaml
# GOOD - Explicit index access
dependencies:
  - type: aws_dynamodb_table
    name: orders
    mode: read_write
    indexes:
      - name: status-date-index
        mode: read
      - name: customer-index
        mode: read
```

### Anti-Pattern 3: Hardcoded Resource References

Using environment-specific names directly.

```yaml
# BAD - Environment baked in
dependencies:
  - type: aws_s3_bucket
    name: prod-user-uploads
```

### Better Approach

```yaml
# GOOD - Environment-agnostic
dependencies:
  - type: aws_s3_bucket
    name: user-uploads  # Let FSD add environment prefix
```

### Anti-Pattern 4: Circular Dependencies

Creating dependency cycles between services.

```yaml
# BAD - Circular dependency
# service-a.yml
dependencies:
  - type: service
    name: service-b
    mode: client

# service-b.yml
dependencies:
  - type: service
    name: service-a  # Creates circular dependency!
    mode: client
```

### Better Approach

```yaml
# GOOD - Use async messaging to break cycle
# service-a.yml
dependencies:
  - type: aws_sqs_queue
    name: service-b-requests
    mode: producer

# service-b.yml
dependencies:
  - type: aws_sqs_queue
    name: service-b-requests
    mode: consumer
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| REST API with database | CRUD Service with DynamoDB |
| Background file processing | File Processing Pipeline |
| Event-driven architecture | Event-Driven Microservice |
| API aggregation layer | API Gateway with Multiple Backends |
| ETL/Data pipeline | Data Lake Ingestion |
| High-throughput streaming | Event-Driven with Kinesis |
| Cache-heavy workload | API Gateway pattern with ElastiCache |
| Scheduled batch job | Data Lake Ingestion pattern |
