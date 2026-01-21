---
name: creating-iam-policies
description: IAM permissions for FSD services via dependencies and custom policy statements. Use when configuring service permissions for AWS resources.
---

# FSD IAM Policies

## Quick Start
```yaml
# Preferred: Use dependencies - FSD auto-generates IAM
dependencies:
  - type: aws_dynamodb_table
    table_name: users
    unmanaged:
      permissions: read  # Generates GetItem, Query, Scan permissions

# Advanced: Custom policy statements for edge cases
iam:
  policy_statements:
    - sid: CrossAccountAccess
      effect: Allow
      actions:
        - s3:GetObject
      resources:
        - arn:aws:s3:::external-bucket/*
```

## Key Points
- **Dependencies first**: Declare AWS resources as dependencies and FSD generates IAM policies
- **Unmanaged permissions**: Use `unmanaged.permissions` (read, write, read_write) for existing resources
- **Custom statements**: Use `iam.policy_statements` only for cross-account or special cases

## Common Mistakes
1. **Manual policies for managed deps** - Use dependencies instead of writing IAM manually
2. **Wrong permission level** - Use `read` not `read_write` when only reading
3. **Missing resource specificity** - Always use specific ARNs, not wildcards

## More Detail
- docs/concepts.md - How FSD generates IAM from dependencies
- docs/patterns.md - Dependency patterns and custom policy examples

## MCP Integration
The FSD MCP server (`fsd-docs`) can validate FSD YAML and look up dependency schemas. Use `get_dependency_docs` to see what permissions each dependency type supports.
