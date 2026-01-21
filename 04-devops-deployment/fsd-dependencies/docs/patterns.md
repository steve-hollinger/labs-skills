# Common Patterns

## Overview

This document covers common patterns for FSD dependency configurations using managed and unmanaged resources.

## Pattern 1: Service with Managed DynamoDB

### When to Use

Use this pattern when your service owns the DynamoDB table and FSD should create it.

### Implementation

```yaml
name: user-service
platform: ecs

compute:
  cpu: 512
  memory: 1024
  desired_count: 3

dependencies:
  # FSD creates this table
  - type: aws_dynamodb_table
    table_name: users
    key_schema:
      - attribute_name: id
        key_type: HASH
    attribute_definitions:
      - attribute_name: id
        attribute_type: S
    billing_mode: PAY_PER_REQUEST

environment:
  USERS_TABLE: users
```

### Pitfalls to Avoid

- Missing `key_schema` or `attribute_definitions` - both are required
- Using wrong `attribute_type` (S for string, N for number, B for binary)

## Pattern 2: Service with Unmanaged Dependencies

### When to Use

Use this pattern when your service needs access to resources owned by other services.

### Implementation

```yaml
name: analytics-service
platform: ecs

dependencies:
  # Read from existing table (owned by user-service)
  - type: aws_dynamodb_table
    table_name: users
    unmanaged:
      permissions: read

  # Write to existing bucket (owned by data-platform)
  - type: aws_s3_bucket
    bucket_name: analytics-output
    unmanaged:
      permissions: write
```

### Pitfalls to Avoid

- Using `read_write` when only `read` is needed
- Forgetting `unmanaged.permissions` for existing resources

## Pattern 3: DynamoDB with CDC Pipeline

### When to Use

Use this pattern when you need Change Data Capture streaming to Kafka/Snowflake.

### Implementation

```yaml
name: order-service
platform: ecs

dependencies:
  - type: fetch_msk_cluster
    name: cdc
  - type: aws_dynamodb_table
    table_name: orders
    key_schema:
      - attribute_name: id
        key_type: HASH
    attribute_definitions:
      - attribute_name: id
        attribute_type: S
    data_pipeline:
      enabled: true
      migrate: true
      snowflake:
        enabled: true
        optimized_merge: true
        dedupe_key: [id]
        timestamps:
          create: CreateTS
          update: UpdateTS
```

### Pitfalls to Avoid

- Forgetting `fetch_msk_cluster` dependency for CDC
- Missing `dedupe_key` for Snowflake merge

## Anti-Patterns

### Anti-Pattern 1: Over-Permissive Permissions

```yaml
# BAD - Full access when read-only needed
dependencies:
  - type: aws_dynamodb_table
    table_name: reference-data
    unmanaged:
      permissions: read_write  # Service only reads!

# GOOD - Minimal required access
dependencies:
  - type: aws_dynamodb_table
    table_name: reference-data
    unmanaged:
      permissions: read
```

### Anti-Pattern 2: Missing Schema for Managed Tables

```yaml
# BAD - Missing required fields
dependencies:
  - type: aws_dynamodb_table
    table_name: orders
    # Missing key_schema and attribute_definitions!

# GOOD - Complete schema
dependencies:
  - type: aws_dynamodb_table
    table_name: orders
    key_schema:
      - attribute_name: id
        key_type: HASH
    attribute_definitions:
      - attribute_name: id
        attribute_type: S
```

### Anti-Pattern 3: Using Managed When Unmanaged Needed

```yaml
# BAD - Trying to create table that already exists
dependencies:
  - type: aws_dynamodb_table
    table_name: shared-users  # Owned by another service!
    key_schema: ...

# GOOD - Reference existing table
dependencies:
  - type: aws_dynamodb_table
    table_name: shared-users
    unmanaged:
      permissions: read
```

## Choosing the Right Pattern

| Scenario | Pattern |
|----------|---------|
| Service owns the table | Managed DynamoDB |
| Access table from another service | Unmanaged with permissions |
| Need CDC streaming | DynamoDB with data_pipeline |
| Simple S3 access | Unmanaged S3 bucket |
