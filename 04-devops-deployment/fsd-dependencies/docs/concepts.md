# Core Concepts

## Overview

FSD Dependencies define the external resources your service needs. There are two types:

- **Managed**: FSD creates and manages the resource (requires full schema)
- **Unmanaged**: FSD grants permissions to an existing resource (requires `unmanaged.permissions`)

## Concept 1: Managed Dependencies

### What It Is

Managed dependencies are AWS resources that FSD creates and manages for your service. You define the full resource schema and FSD provisions it.

### When to Use

Use managed dependencies when:
- Your service owns the resource
- The resource doesn't exist yet
- You want FSD to handle the resource lifecycle

### How It Works

```yaml
dependencies:
  # FSD creates this DynamoDB table
  - type: aws_dynamodb_table
    table_name: orders
    key_schema:
      - attribute_name: id
        key_type: HASH
    attribute_definitions:
      - attribute_name: id
        attribute_type: S
    billing_mode: PAY_PER_REQUEST
```

**Required Fields (DynamoDB):**
- `type`: Must be `aws_dynamodb_table`
- `table_name`: The table name
- `key_schema`: Primary key definition (HASH, optionally RANGE)
- `attribute_definitions`: Attribute types (S, N, B)

## Concept 2: Unmanaged Dependencies

### What It Is

Unmanaged dependencies reference existing AWS resources. FSD grants your service IAM permissions to access them without creating or modifying the resource.

### When to Use

Use unmanaged dependencies when:
- The resource is owned by another service
- The resource was created outside FSD
- You only need access permissions, not ownership

### How It Works

```yaml
dependencies:
  # Grant read access to existing table
  - type: aws_dynamodb_table
    table_name: shared-config
    unmanaged:
      permissions: read    # read, write, or read_write

  # Grant write access to existing S3 bucket
  - type: aws_s3_bucket
    bucket_name: shared-uploads
    unmanaged:
      permissions: write
```

**Permission Levels:**

| Permission | DynamoDB | S3 |
|------------|----------|-----|
| `read` | GetItem, Query, Scan, BatchGetItem | GetObject, ListBucket |
| `write` | PutItem, UpdateItem, DeleteItem, BatchWriteItem | PutObject, DeleteObject |
| `read_write` | All read + write operations | All read + write operations |

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
# This unmanaged dependency declaration...
dependencies:
  - type: aws_dynamodb_table
    table_name: users
    unmanaged:
      permissions: read

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

**Managed dependencies** also generate IAM permissions automatically - you don't need to specify permissions separately when FSD creates the resource.

## Concept 4: DynamoDB Dependencies

### Managed DynamoDB Table

FSD creates and manages the table:

```yaml
dependencies:
  - type: aws_dynamodb_table
    table_name: orders
    key_schema:
      - attribute_name: id
        key_type: HASH
      - attribute_name: created_at
        key_type: RANGE
    attribute_definitions:
      - attribute_name: id
        attribute_type: S
      - attribute_name: created_at
        attribute_type: N
    billing_mode: PAY_PER_REQUEST
```

### Unmanaged DynamoDB Table

Grant permissions to an existing table:

```yaml
dependencies:
  - type: aws_dynamodb_table
    table_name: shared-config
    unmanaged:
      permissions: read  # or write, read_write
```

### DynamoDB with Data Pipeline (CDC)

Enable Change Data Capture streaming to Kafka:

```yaml
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
      snowflake:
        enabled: true
        dedupe_key: [id]
```

## Concept 5: S3 Dependencies

### Managed S3 Bucket

FSD creates the bucket:

```yaml
dependencies:
  - type: aws_s3_bucket
    bucket_name: my-uploads
```

### Unmanaged S3 Bucket

Grant permissions to existing bucket:

```yaml
dependencies:
  - type: aws_s3_bucket
    bucket_name: shared-assets
    unmanaged:
      permissions: read  # or write, read_write
```

## Summary

Key takeaways:

1. **Managed vs Unmanaged**: Use managed when FSD should create the resource; use unmanaged for existing resources
2. **Permission Levels**: Use the minimum required (read over read_write when possible)
3. **IAM Generation**: FSD automatically creates least-privilege IAM policies from dependencies
4. **Schema Requirements**: Managed DynamoDB tables require key_schema and attribute_definitions

Well-configured dependencies are the foundation of secure, maintainable cloud services.
