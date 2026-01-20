# FSD IAM Policies

Learn to create secure, least-privilege IAM policies for FSD-deployed services.

## Quick Start

```bash
make setup      # Install dependencies
make examples   # View example policies
```

## What You'll Learn

1. **IAM Policy Structure** - Statements, effects, actions, resources, conditions
2. **Least Privilege** - Granting minimum required permissions
3. **Resource ARNs** - Properly scoping resources instead of using wildcards
4. **Condition Keys** - Fine-grained access control with conditions

## Prerequisites

- Familiarity with AWS IAM concepts
- Understanding of FSD YAML configuration
- Knowledge of AWS resource ARN formats

## Examples

| Example | Description |
|---------|-------------|
| `example_1.py` | Basic DynamoDB read/write policy |
| `example_2.py` | S3 bucket access with conditions |
| `example_3.py` | Cross-service permissions (SQS, SNS) |

## FSD Policy Integration

FSD services define IAM permissions in the `iam` section:

```yaml
service:
  name: my-service

iam:
  policy_statements:
    - sid: AllowDynamoDBAccess
      effect: Allow
      actions:
        - dynamodb:GetItem
        - dynamodb:PutItem
      resources:
        - arn:aws:dynamodb:${AWS_REGION}:${AWS_ACCOUNT}:table/my-table
```

## Documentation

- [docs/concepts.md](docs/concepts.md) - IAM policy fundamentals
- [docs/patterns.md](docs/patterns.md) - Common policy patterns

## Related Skills

- [fsd-yaml-config](../fsd-yaml-config/) - FSD service configuration
- [fsd-dependencies](../fsd-dependencies/) - FSD dependency definitions
- [secrets-manager](../../07-security/secrets-manager/) - Secure credential management
