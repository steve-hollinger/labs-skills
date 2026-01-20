# Exercise 3: Lambda Function with Multiple Triggers

## Objective

Create an FSD YAML configuration for a Lambda function that responds to multiple event sources.

## Scenario

You're building a document processing service that:
- Accepts document uploads via API
- Processes documents automatically when uploaded to S3
- Handles batch processing requests from an SQS queue
- Runs daily cleanup via a scheduled event

## Requirements

Create an FSD YAML file for `document-processor` that:

1. **Platform**: Lambda

2. **Compute**:
   - Memory: 2048 MB (documents can be large)
   - Timeout: 120 seconds
   - Runtime: python3.11
   - Architecture: arm64 (cost optimization)

3. **Triggers** (all four required):

   a. **API Gateway** trigger:
      - Path: `/documents/process`
      - Method: POST
      - Authorization: AWS_IAM

   b. **S3** trigger:
      - Bucket: `document-uploads-bucket`
      - Events: `s3:ObjectCreated:*`
      - Filter prefix: `incoming/`
      - Filter suffix: `.pdf`

   c. **SQS** trigger:
      - Queue ARN: `arn:aws:sqs:us-east-1:123456789012:document-batch-queue`
      - Batch size: 5
      - Batch window: 10 seconds

   d. **Schedule** trigger:
      - Rate: Daily at 2 AM UTC
      - Expression: `cron(0 2 * * ? *)`
      - Description: "Daily cleanup of temporary files"

4. **Concurrency**:
   - Reserved concurrency: 50
   - Provisioned concurrency: 3 (for API latency)

5. **Dead Letter Queue**:
   - Target: `arn:aws:sqs:us-east-1:123456789012:document-processor-dlq`

6. **Environment Variables**:
   - `OUTPUT_BUCKET`: processed-documents
   - `OCR_ENABLED`: true
   - `MAX_FILE_SIZE_MB`: 50
   - `TEMP_STORAGE`: /tmp
   - `API_KEY`: from Secrets Manager at `document-processor/api-key`

7. **Metadata**:
   - Team: document-team
   - Tags: environment=production, data-classification=confidential

## Template

```yaml
name: document-processor
platform: lambda
description: # Add description

team: # Add team
tags:
  # Add tags

compute:
  # Add compute configuration

triggers:
  # Add API Gateway trigger

  # Add S3 trigger

  # Add SQS trigger

  # Add Schedule trigger

dead_letter:
  # Add DLQ configuration

environment:
  # Add environment variables
```

## Validation

Test your solution:

```bash
make validate YAML=exercises/solutions/solution-3.yml
```

## Hints

- Lambda triggers are an array - each trigger type has different required fields
- S3 filter uses `prefix` and `suffix` fields
- Schedule expressions can use `rate()` or `cron()` syntax
- Secrets Manager references use `${secrets:path}` syntax

## Bonus Challenge

Add VPC configuration to allow the Lambda to access resources in a private subnet:
- Security Group: `sg-lambda-processor`
- Subnets: `subnet-private-1a`, `subnet-private-1b`

## Submit Your Solution

Save your solution to `exercises/solutions/solution-3.yml`
