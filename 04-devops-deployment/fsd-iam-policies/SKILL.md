---
name: creating-iam-policies
description: Creates IAM policies for FSD services using least-privilege principles. Use when defining service permissions for AWS resources.
---

# FSD IAM Policies

## Quick Start
```yaml
# In your FSD service YAML
iam:
  policy_statements:
    - sid: ReadDynamoDB
      effect: Allow
      actions:
        - dynamodb:GetItem
        - dynamodb:Query
        - dynamodb:Scan
      resources:
        - arn:aws:dynamodb:*:*:table/${TABLE_NAME}
        - arn:aws:dynamodb:*:*:table/${TABLE_NAME}/index/*
```

## Commands
```bash
make setup      # Install dependencies
make examples   # Show example policies
make validate   # Validate policy syntax
make test       # Run tests
```

## Key Points
- Always use least-privilege (minimum required permissions)
- Use resource ARNs instead of wildcards when possible
- Add conditions to restrict access scope

## Common Mistakes
1. **Using Action wildcards** - Specify exact actions needed
2. **Missing index permissions** - DynamoDB indexes need separate resource ARNs
3. **Forgetting condition keys** - Use conditions for fine-grained access control

## More Detail
- [docs/concepts.md](docs/concepts.md) - IAM policy structure and best practices
- [docs/patterns.md](docs/patterns.md) - Common policy patterns for FSD services
