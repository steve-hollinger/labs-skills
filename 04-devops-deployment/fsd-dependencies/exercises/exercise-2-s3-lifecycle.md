# Exercise 2: Configure S3 Bucket with Lifecycle Policies

## Objective

Configure S3 bucket dependencies with appropriate access modes, encryption, and lifecycle policies for a media processing service.

## Scenario

You are building a media processing service that handles user-uploaded images and videos. The service needs to:
- Read uploaded media from an input bucket
- Write processed media to an output bucket
- Store thumbnails in a public CDN bucket
- Archive original uploads for compliance

## Starting Configuration

```yaml
name: media-processor
platform: lambda
description: Processes uploaded media files

team: media-team
tags:
  environment: production
  tier: processing

compute:
  memory: 3008
  timeout: 300
  runtime: python3.11

triggers:
  - type: sqs
    queue_arn: arn:aws:sqs:us-east-1:123456789012:media-processing-queue
    batch_size: 1

# TODO: Add dependencies here
dependencies: []

environment:
  LOG_LEVEL: info
```

## Requirements

Add the following S3 bucket dependencies:

1. **media-uploads** bucket:
   - Read-only access
   - Prefix: `incoming/`
   - KMS encryption with key `${kms:media-key}`

2. **media-processed** bucket:
   - Write-only access
   - Prefix: `processed/`
   - KMS encryption with key `${kms:media-key}`
   - Lifecycle: transition to Infrequent Access after 30 days

3. **media-thumbnails** bucket:
   - Write-only access
   - Public read enabled (for CDN)
   - Prefix: `thumbnails/`

4. **media-archive** bucket:
   - Write-only access
   - KMS encryption with key `${kms:archive-key}`
   - Lifecycle: transition to Glacier after 7 days
   - Object lock enabled (GOVERNANCE mode, 365 days retention)

5. Add SQS dependencies:
   - **media-processing-queue**: consumer mode
   - **media-processing-dlq**: producer mode (for failed messages)

6. Add environment variables for all bucket names.

## Hints

- Use `encryption.kms_key` for custom KMS keys
- Lifecycle rules use `transition_to_ia` and `transition_to_glacier` (days)
- Object lock configuration uses `mode` (GOVERNANCE/COMPLIANCE) and `retention_days`
- Public buckets use `public_read: true`

## Validation

Test your solution:

```bash
make validate YAML=exercises/solutions/solution-2.yml
```

## Expected Output

Your configuration should have:
- 4 S3 bucket dependencies with varying access modes
- Encryption configuration on sensitive buckets
- Lifecycle policies for archival
- Object lock for compliance
- 2 SQS queue dependencies
- Environment variables for resource names

## Submit Your Solution

Save your solution to `exercises/solutions/solution-2.yml`
