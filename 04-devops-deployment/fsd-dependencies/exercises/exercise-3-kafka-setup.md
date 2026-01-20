# Exercise 3: Set Up Kafka Consumer and Producer

## Objective

Configure Kafka topic dependencies for an event-driven service that consumes events from multiple topics and produces events to downstream topics.

## Scenario

You are building a fraud detection service that:
- Consumes transaction events as they occur
- Consumes user activity events for behavioral analysis
- Produces fraud alerts when suspicious activity is detected
- Produces analytics events for reporting
- Needs idempotency tracking in DynamoDB
- Uses Redis for real-time feature caching

## Starting Configuration

```yaml
name: fraud-detector
platform: eks
description: Real-time fraud detection service

team: security-team
tags:
  environment: production
  tier: critical
  compliance: sox

compute:
  replicas: 5
  resources:
    requests:
      cpu: "1000m"
      memory: "2Gi"
    limits:
      cpu: "2000m"
      memory: "4Gi"

# TODO: Add dependencies here
dependencies: []

environment:
  LOG_LEVEL: info
  LOG_FORMAT: json
```

## Requirements

Add the following Kafka topic dependencies:

1. **transaction-events** topic (consumer):
   - Consumer group: `fraud-detector`
   - Auto offset reset: `earliest` (process all events)
   - Disable auto commit (manual commits for exactly-once)
   - Max poll records: 50
   - Bootstrap servers from SSM: `/kafka/bootstrap-servers`

2. **user-activity-events** topic (consumer):
   - Consumer group: `fraud-detector`
   - Auto offset reset: `latest` (only new events)
   - Bootstrap servers from SSM: `/kafka/bootstrap-servers`

3. **fraud-alerts** topic (producer):
   - Acks: `all` (wait for all replicas)
   - Retries: 5
   - Compression: `lz4`
   - Bootstrap servers from SSM: `/kafka/bootstrap-servers`

4. **analytics-events** topic (producer):
   - Acks: `1` (leader only, fire-and-forget)
   - Bootstrap servers from SSM: `/kafka/bootstrap-servers`

Add supporting dependencies:

5. **fraud-detection-results** DynamoDB table:
   - Read/write access
   - GSI: `user-id-index` (read)
   - GSI: `timestamp-index` (read)

6. **fraud-feature-cache** ElastiCache Redis:
   - Read/write access
   - Cluster mode enabled

Add environment variables for:
- Kafka bootstrap servers
- Consumer group name
- DynamoDB table name
- Redis URL

## Hints

- Kafka consumer configuration includes: `auto_offset_reset`, `enable_auto_commit`, `max_poll_records`
- Kafka producer configuration includes: `acks`, `retries`, `compression_type`
- Use `${ssm:path}` syntax for SSM Parameter Store references
- Use `${elasticache:name:url}` for Redis URL reference

## Validation

Test your solution:

```bash
make validate YAML=exercises/solutions/solution-3.yml
```

## Expected Output

Your configuration should have:
- 2 Kafka consumer dependencies with different configurations
- 2 Kafka producer dependencies with different reliability levels
- 1 DynamoDB table with indexes
- 1 ElastiCache cluster
- All necessary environment variables

## Bonus Challenge

Add HPA (Horizontal Pod Autoscaler) configuration that scales based on Kafka consumer lag metric.

## Submit Your Solution

Save your solution to `exercises/solutions/solution-3.yml`
