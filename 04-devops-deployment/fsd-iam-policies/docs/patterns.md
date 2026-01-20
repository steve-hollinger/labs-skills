# IAM Policy Patterns

## Pattern 1: DynamoDB CRUD

```yaml
iam:
  policy_statements:
    - sid: DynamoDBFullAccess
      effect: Allow
      actions:
        - dynamodb:GetItem
        - dynamodb:BatchGetItem
        - dynamodb:Query
        - dynamodb:Scan
        - dynamodb:PutItem
        - dynamodb:UpdateItem
        - dynamodb:DeleteItem
        - dynamodb:BatchWriteItem
      resources:
        - arn:aws:dynamodb:${AWS_REGION}:${AWS_ACCOUNT}:table/${TABLE_NAME}
        - arn:aws:dynamodb:${AWS_REGION}:${AWS_ACCOUNT}:table/${TABLE_NAME}/index/*
```

## Pattern 2: S3 Read-Only with Prefix

```yaml
iam:
  policy_statements:
    - sid: S3ReadOnly
      effect: Allow
      actions:
        - s3:GetObject
        - s3:GetObjectVersion
      resources:
        - arn:aws:s3:::${BUCKET_NAME}/${PREFIX}/*

    - sid: S3ListBucket
      effect: Allow
      actions:
        - s3:ListBucket
      resources:
        - arn:aws:s3:::${BUCKET_NAME}
      conditions:
        StringLike:
          s3:prefix:
            - ${PREFIX}/*
```

## Pattern 3: SQS Consumer

```yaml
iam:
  policy_statements:
    - sid: SQSConsumer
      effect: Allow
      actions:
        - sqs:ReceiveMessage
        - sqs:DeleteMessage
        - sqs:ChangeMessageVisibility
        - sqs:GetQueueAttributes
      resources:
        - arn:aws:sqs:${AWS_REGION}:${AWS_ACCOUNT}:${QUEUE_NAME}
        - arn:aws:sqs:${AWS_REGION}:${AWS_ACCOUNT}:${QUEUE_NAME}-dlq
```

## Pattern 4: SNS Publisher

```yaml
iam:
  policy_statements:
    - sid: SNSPublish
      effect: Allow
      actions:
        - sns:Publish
      resources:
        - arn:aws:sns:${AWS_REGION}:${AWS_ACCOUNT}:${TOPIC_NAME}
```

## Pattern 5: Secrets Manager Read

```yaml
iam:
  policy_statements:
    - sid: SecretsRead
      effect: Allow
      actions:
        - secretsmanager:GetSecretValue
      resources:
        - arn:aws:secretsmanager:${AWS_REGION}:${AWS_ACCOUNT}:secret:${SERVICE_NAME}/*
      conditions:
        StringEquals:
          secretsmanager:VersionStage: AWSCURRENT
```

## Pattern 6: KMS for Service Integration

```yaml
iam:
  policy_statements:
    - sid: KMSForSecrets
      effect: Allow
      actions:
        - kms:Decrypt
        - kms:GenerateDataKey
      resources:
        - arn:aws:kms:${AWS_REGION}:${AWS_ACCOUNT}:key/${KMS_KEY_ID}
      conditions:
        StringEquals:
          kms:ViaService: secretsmanager.${AWS_REGION}.amazonaws.com
```

## Pattern 7: CloudWatch Logs

```yaml
iam:
  policy_statements:
    - sid: CloudWatchLogs
      effect: Allow
      actions:
        - logs:CreateLogStream
        - logs:PutLogEvents
      resources:
        - arn:aws:logs:${AWS_REGION}:${AWS_ACCOUNT}:log-group:/ecs/${SERVICE_NAME}:*
```

## Pattern 8: EventBridge Put Events

```yaml
iam:
  policy_statements:
    - sid: EventBridgePut
      effect: Allow
      actions:
        - events:PutEvents
      resources:
        - arn:aws:events:${AWS_REGION}:${AWS_ACCOUNT}:event-bus/default
```

## Pattern 9: Lambda Invoke

```yaml
iam:
  policy_statements:
    - sid: LambdaInvoke
      effect: Allow
      actions:
        - lambda:InvokeFunction
      resources:
        - arn:aws:lambda:${AWS_REGION}:${AWS_ACCOUNT}:function:${FUNCTION_NAME}
```

## Anti-Patterns to Avoid

### Don't: Use Wildcards for Actions

```yaml
# BAD
actions:
  - dynamodb:*

# GOOD
actions:
  - dynamodb:GetItem
  - dynamodb:PutItem
```

### Don't: Use * for Resources

```yaml
# BAD
resources:
  - "*"

# GOOD
resources:
  - arn:aws:dynamodb:us-east-1:123456789012:table/users
```

### Don't: Forget Index Permissions

```yaml
# BAD - Query on GSI will fail
resources:
  - arn:aws:dynamodb:*:*:table/users

# GOOD
resources:
  - arn:aws:dynamodb:*:*:table/users
  - arn:aws:dynamodb:*:*:table/users/index/*
```
