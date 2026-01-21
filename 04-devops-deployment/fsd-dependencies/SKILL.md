---
name: defining-fsd-dependencies
description: FSD dependency configuration for AWS services (DynamoDB, S3, SQS, Kafka) with automatic IAM policy generation. Use when deploying services that need AWS resources.
---

# FSD Dependencies

## Quick Start
```yaml
# Managed dependency - FSD creates the resource
dependencies:
  - type: aws_dynamodb_table
    table_name: orders
    key_schema:
      - attribute_name: id
        key_type: HASH
    attribute_definitions:
      - attribute_name: id
        attribute_type: S

# Unmanaged dependency - FSD grants permissions to existing resource
dependencies:
  - type: aws_dynamodb_table
    table_name: existing-table
    unmanaged:
      permissions: write  # read, write, or read_write
```

## Key Points
- **Managed vs Unmanaged**: Managed dependencies are created by FSD; unmanaged grant permissions to existing resources
- **Auto IAM**: FSD generates least-privilege IAM policies based on dependency declarations
- **Supported Types**: aws_dynamodb_table, aws_s3_bucket, aws_sqs_queue, kafka_topic, and more

## Common Mistakes
1. **Using managed when unmanaged needed** - If the resource exists elsewhere, use `unmanaged.permissions`
2. **Missing key_schema for managed tables** - Managed DynamoDB tables require full schema definition
3. **Over-permissive access** - Use `read` instead of `read_write` when only reading

## More Detail
- docs/concepts.md - Managed vs unmanaged dependencies, access modes
- docs/patterns.md - Common dependency patterns by service type

## MCP Integration
The FSD MCP server (`fsd-docs`) provides `get_dependency_docs` for looking up dependency schemas (e.g., `aws_dynamodb_table`, `aws_s3_bucket`). Use it when available to get accurate field definitions.