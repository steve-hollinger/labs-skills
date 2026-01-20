# Exercise 4: Batch Processing Pipeline

## Objective

Design an FSD YAML configuration for a data processing batch job that handles large-scale ETL operations.

## Scenario

Your data team needs a batch processing job that:
- Runs daily to process transaction logs from the previous day
- Processes files in parallel using array jobs
- Transforms and aggregates data for the analytics warehouse
- Must complete within a 4-hour window
- Needs retry logic for transient failures

## Requirements

Create an FSD YAML file for `transaction-etl` that:

1. **Platform**: Batch

2. **Compute**:
   - vCPUs: 4
   - Memory: 16384 MB (16 GB)
   - Compute environment: FARGATE

3. **Job Configuration**:
   - Type: array (parallel processing)
   - Array size: 24 (one job per hour of data)
   - Retry attempts: 3
   - Timeout: 14400 seconds (4 hours)

4. **Retry Strategy**:
   - Retry on exit codes: 1 (general error), 137 (OOM)
   - Retry on status reason containing "Host EC2"
   - Exit (don't retry) on exit code 2 (validation error)

5. **Scheduling**:
   - Type: cron
   - Expression: 5 AM UTC daily (`0 5 * * *`)
   - Timezone: UTC

6. **Container Configuration**:
   - Image from ECR: `transaction-etl` repository
   - Command: `python -m etl.main --date ${batch:scheduled_date} --partition ${batch:array_index}`

7. **Environment Variables**:
   - `SOURCE_BUCKET`: raw-transaction-logs
   - `OUTPUT_BUCKET`: processed-transactions
   - `REDSHIFT_CLUSTER`: from SSM at `/etl/redshift-cluster`
   - `DATABASE_URL`: from Secrets Manager at `transaction-etl/database-url`
   - `LOG_LEVEL`: info
   - `PARALLELISM`: 4

8. **Metadata**:
   - Team: data-engineering
   - Tags:
     - environment: production
     - schedule: daily
     - tier: data-pipeline
     - cost-center: analytics

## Template

```yaml
name: transaction-etl
platform: batch
description: # Add description

team: # Add team
tags:
  # Add tags

compute:
  # Add compute configuration

job:
  type: # Add job type
  # Add array configuration
  # Add retry configuration
  # Add timeout
  # Add scheduling

  retry_strategy:
    # Add retry rules

container:
  # Add container configuration

environment:
  # Add environment variables
```

## Validation

Test your solution:

```bash
make validate YAML=exercises/solutions/solution-4.yml
```

## Hints

- Array jobs use `${batch:array_index}` to get the current index (0-23 for 24 items)
- Retry strategy `evaluate_on_exit` allows fine-grained retry control
- Exit code 137 typically indicates the container was killed due to memory limits
- Cron expressions in AWS use 5 fields (minute, hour, day-of-month, month, day-of-week)

## Bonus Challenge

Add a dependent job that runs after all array jobs complete:
- Name: `transaction-etl-summary`
- Single job type
- Generates a summary report
- Depends on the array job completing successfully

## Submit Your Solution

Save your solution to `exercises/solutions/solution-4.yml`
