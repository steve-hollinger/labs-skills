"""Example 2: S3 bucket access with conditions.

This example shows how to create IAM policies with conditions
for S3 bucket access, demonstrating fine-grained access control.
"""

import yaml


S3_POLICY = """
# FSD service with S3 access and conditions
service:
  name: document-service
  platform: ecs

iam:
  policy_statements:
    # Read objects from specific prefix
    - sid: S3ReadDocuments
      effect: Allow
      actions:
        - s3:GetObject
        - s3:GetObjectVersion
        - s3:GetObjectTagging
      resources:
        - arn:aws:s3:::my-bucket/documents/*
      conditions:
        StringEquals:
          s3:ExistingObjectTag/status: approved

    # Write objects with required encryption
    - sid: S3WriteDocuments
      effect: Allow
      actions:
        - s3:PutObject
        - s3:PutObjectTagging
      resources:
        - arn:aws:s3:::my-bucket/documents/*
      conditions:
        StringEquals:
          s3:x-amz-server-side-encryption: aws:kms
        StringLike:
          s3:x-amz-server-side-encryption-aws-kms-key-id:
            - arn:aws:kms:*:*:key/my-kms-key-id

    # List bucket with prefix restriction
    - sid: S3ListBucket
      effect: Allow
      actions:
        - s3:ListBucket
      resources:
        - arn:aws:s3:::my-bucket
      conditions:
        StringLike:
          s3:prefix:
            - documents/*

    # Deny unencrypted uploads
    - sid: DenyUnencryptedUploads
      effect: Deny
      actions:
        - s3:PutObject
      resources:
        - arn:aws:s3:::my-bucket/*
      conditions:
        "Null":
          s3:x-amz-server-side-encryption: "true"
"""


def main() -> None:
    """Demonstrate S3 IAM policy patterns with conditions."""
    print("S3 IAM Policy with Conditions Example")
    print("=" * 60)

    config = yaml.safe_load(S3_POLICY)

    print(f"\nService: {config['service']['name']}")

    print("\nPolicy Statements:")
    for stmt in config['iam']['policy_statements']:
        print(f"\n  {stmt['sid']}:")
        print(f"    Effect: {stmt['effect']}")
        print(f"    Actions: {', '.join(stmt['actions'])}")

        if 'conditions' in stmt:
            print("    Conditions:")
            for cond_type, cond_values in stmt['conditions'].items():
                print(f"      {cond_type}:")
                for key, val in cond_values.items():
                    print(f"        {key}: {val}")

    print("\n" + "=" * 60)
    print("Condition Patterns Demonstrated:")
    print("1. StringEquals - Exact match on object tags")
    print("2. StringLike - Pattern matching for KMS key ARNs")
    print("3. Null condition - Check if header is absent")
    print("4. Deny statement - Explicit denial for security")


if __name__ == "__main__":
    main()
