# IAM Policy Concepts

## IAM Policy Structure

Every IAM policy consists of statements with these elements:

| Element | Required | Description |
|---------|----------|-------------|
| `sid` | No | Statement identifier (for documentation) |
| `effect` | Yes | `Allow` or `Deny` |
| `actions` | Yes | List of API actions |
| `resources` | Yes | ARNs of resources to access |
| `conditions` | No | Additional constraints |

## FSD IAM Configuration

In FSD YAML files, IAM policies are defined under the `iam` key:

```yaml
iam:
  policy_statements:
    - sid: StatementName
      effect: Allow
      actions:
        - service:Action
      resources:
        - arn:aws:service:region:account:resource
      conditions:
        ConditionOperator:
          ConditionKey: ConditionValue
```

## Least Privilege Principle

Always grant the minimum permissions needed:

1. **Specific Actions** - List exact actions, not wildcards
2. **Specific Resources** - Use full ARNs, not `*`
3. **Conditions** - Add constraints when possible
4. **Separate Read/Write** - Different SIDs for different access levels

## Resource ARN Patterns

```
arn:aws:service:region:account:resource-type/resource-id

Examples:
- DynamoDB table: arn:aws:dynamodb:us-east-1:123456789012:table/users
- DynamoDB index: arn:aws:dynamodb:us-east-1:123456789012:table/users/index/email-index
- S3 bucket:      arn:aws:s3:::my-bucket
- S3 objects:     arn:aws:s3:::my-bucket/path/*
- SQS queue:      arn:aws:sqs:us-east-1:123456789012:my-queue
- SNS topic:      arn:aws:sns:us-east-1:123456789012:my-topic
```

## Condition Operators

| Operator | Use Case |
|----------|----------|
| `StringEquals` | Exact string match |
| `StringLike` | Pattern match with wildcards |
| `StringNotEquals` | Negated exact match |
| `ArnLike` | ARN pattern match |
| `Null` | Check if key exists |
| `Bool` | Boolean conditions |
| `NumericEquals` | Numeric comparisons |
| `DateLessThan` | Date comparisons |

## Common Condition Keys

| Service | Key | Description |
|---------|-----|-------------|
| Global | `aws:SourceIp` | Request source IP |
| Global | `aws:RequestTag/key` | Tags in request |
| S3 | `s3:prefix` | Object key prefix |
| S3 | `s3:x-amz-server-side-encryption` | Encryption method |
| DynamoDB | `dynamodb:LeadingKeys` | Partition key values |
| KMS | `kms:ViaService` | Service making request |
| Secrets | `secretsmanager:VersionStage` | Secret version |

## Deny Statements

Use explicit deny for security controls:

```yaml
- sid: DenyUnencrypted
  effect: Deny
  actions:
    - s3:PutObject
  resources:
    - arn:aws:s3:::my-bucket/*
  conditions:
    "Null":
      s3:x-amz-server-side-encryption: "true"
```

Deny always overrides Allow (except for resource-based policies).
