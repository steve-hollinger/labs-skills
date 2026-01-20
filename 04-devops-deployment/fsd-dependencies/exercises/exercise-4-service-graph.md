# Exercise 4: Design a Multi-Service Dependency Graph

## Objective

Design the complete dependency configuration for a microservices-based e-commerce order fulfillment system with multiple interconnected services.

## Scenario

You are designing the dependency configuration for an order fulfillment service that orchestrates the complete order lifecycle:

1. Receives orders from the order API
2. Validates inventory with the inventory service
3. Processes payment through the payment service
4. Creates shipping labels via the shipping service
5. Sends notifications through the notification service
6. Stores order state in DynamoDB
7. Publishes events to Kafka for analytics

## Starting Configuration

```yaml
name: order-fulfillment
platform: ecs
description: Orchestrates order fulfillment across multiple services

team: fulfillment-team
tags:
  environment: production
  tier: orchestration
  cost-center: orders

compute:
  cpu: 1024
  memory: 2048
  desired_count: 5

networking:
  port: 8080
  health_check:
    path: /health
    interval: 15

# TODO: Add comprehensive dependencies
dependencies: []

environment:
  LOG_LEVEL: info
```

## Requirements

### Service Dependencies

Add cross-service dependencies with appropriate circuit breaker and timeout configurations:

1. **inventory-service**:
   - Discovery: DNS in `production.internal` namespace
   - Timeout: 5000ms
   - Circuit breaker: threshold 3, recovery 30000ms

2. **payment-service**:
   - Discovery: DNS in `production.internal` namespace
   - Timeout: 30000ms (payments can be slow)
   - Circuit breaker: threshold 2, recovery 60000ms (sensitive)

3. **shipping-service**:
   - Discovery: DNS in `production.internal` namespace
   - Timeout: 10000ms
   - Circuit breaker: threshold 5, recovery 30000ms

4. **notification-service**:
   - Discovery: DNS in `production.internal` namespace
   - Timeout: 5000ms
   - Async mode (fire-and-forget)
   - No circuit breaker needed

### Data Dependencies

5. **orders** DynamoDB table:
   - Read/write access
   - GSI: `customer-index` (read)
   - GSI: `status-index` (read)
   - GSI: `created-at-index` (read)
   - Streams enabled (consumer mode)

6. **fulfillment-state** DynamoDB table:
   - Read/write access (saga state machine)

### Messaging Dependencies

7. **order-events** Kafka topic:
   - Producer mode
   - Acks: all
   - Bootstrap servers from SSM

8. **fulfillment-events** Kafka topic:
   - Producer mode
   - Acks: all

9. **analytics-events** Kafka topic:
   - Producer mode
   - Acks: 1 (fire-and-forget)

### Caching Dependencies

10. **fulfillment-cache** ElastiCache Redis:
    - Read/write access

### Environment Variables

Add environment variables for all service URLs, table names, topic references, and cache URL.

## Hints

- Service dependencies use `type: service` with `discovery.method` and `discovery.namespace`
- Circuit breakers have `failure_threshold` and `recovery_timeout` (ms)
- Async services don't need circuit breakers
- DynamoDB streams need `streams.enabled: true` and `streams.mode: consumer`
- Use `${service:name:url}` syntax for service URLs in environment

## Validation

Test your solution:

```bash
make validate YAML=exercises/solutions/solution-4.yml
```

## Expected Output

Your configuration should have:
- 4 service dependencies with appropriate resilience patterns
- 2 DynamoDB tables with indexes and streams
- 3 Kafka topics
- 1 ElastiCache cluster
- Comprehensive environment variables

## Architecture Diagram

```
                    +-------------------+
                    | order-fulfillment |
                    +-------------------+
                           |
           +---------------+---------------+
           |               |               |
           v               v               v
    +-----------+   +-----------+   +-----------+
    | inventory |   |  payment  |   | shipping  |
    |  service  |   |  service  |   |  service  |
    +-----------+   +-----------+   +-----------+
           |
           v
    +--------------+
    | notification |
    |   service    |
    +--------------+

    Data Flow:
    - DynamoDB: orders, fulfillment-state
    - Kafka: order-events, fulfillment-events, analytics-events
    - Redis: fulfillment-cache
```

## Bonus Challenge

Add a dead letter queue (SQS) for failed order processing and configure it as a producer dependency.

## Submit Your Solution

Save your solution to `exercises/solutions/solution-4.yml`
