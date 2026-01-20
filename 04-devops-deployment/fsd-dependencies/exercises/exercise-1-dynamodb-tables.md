# Exercise 1: Add DynamoDB Tables to a Service

## Objective

Add DynamoDB table dependencies to an existing FSD service configuration with appropriate access modes and index permissions.

## Scenario

You have an inventory management service that needs to store and query product inventory data. The service needs to:
- Read and write inventory levels
- Query by product ID (primary key)
- Query by warehouse location
- Query by low stock threshold for alerts
- Write to an inventory changes audit log

## Starting Configuration

```yaml
name: inventory-service
platform: ecs
description: Inventory management service

team: warehouse-team
tags:
  environment: production
  tier: backend

compute:
  cpu: 512
  memory: 1024
  desired_count: 3

networking:
  port: 8080
  health_check:
    path: /health
    interval: 30

# TODO: Add dependencies here
dependencies: []

environment:
  LOG_LEVEL: info
  AWS_REGION: us-east-1
```

## Requirements

Add the following DynamoDB dependencies:

1. **inventory** table:
   - Full read/write access (CRUD operations)
   - GSI: `warehouse-index` for querying by warehouse (read-only)
   - GSI: `low-stock-index` for querying items below threshold (read-only)

2. **inventory-audit-log** table:
   - Write-only access (service appends logs, never reads)

3. **product-catalog** table:
   - Read-only access (managed by a different service)
   - GSI: `category-index` for product lookup by category (read-only)

4. Add environment variables for table names.

## Hints

- Use the `indexes` array within a DynamoDB dependency
- Audit logs should only have `write` mode
- Reference tables should only have `read` mode
- Index mode should match the query pattern (usually read-only)

## Validation

Test your solution:

```bash
make validate YAML=exercises/solutions/solution-1.yml
```

## Expected Output

Your configuration should have:
- 3 DynamoDB table dependencies
- Appropriate access modes for each table
- Index configurations where needed
- Environment variables for table names

## Submit Your Solution

Save your solution to `exercises/solutions/solution-1.yml`
