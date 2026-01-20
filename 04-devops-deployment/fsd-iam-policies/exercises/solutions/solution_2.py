"""Solution 2: S3 Policy with Encryption Requirement"""

import yaml

POLICY = """
iam:
  policy_statements:
    # Allow uploads
    - sid: AllowUploads
      effect: Allow
      actions:
        - s3:PutObject
      resources:
        - arn:aws:s3:::data-uploads/*

    # Deny unencrypted uploads
    - sid: DenyUnencrypted
      effect: Deny
      actions:
        - s3:PutObject
      resources:
        - arn:aws:s3:::data-uploads/*
      conditions:
        "Null":
          s3:x-amz-server-side-encryption: "true"
"""

if __name__ == "__main__":
    config = yaml.safe_load(POLICY)
    stmts = config['iam']['policy_statements']

    # Should have 2 statements
    assert len(stmts) == 2, "Should have Allow and Deny statements"

    # One Allow, one Deny
    effects = [s['effect'] for s in stmts]
    assert 'Allow' in effects, "Should have Allow statement"
    assert 'Deny' in effects, "Should have Deny statement"

    # Deny should have Null condition
    deny_stmt = next(s for s in stmts if s['effect'] == 'Deny')
    assert 'conditions' in deny_stmt, "Deny statement should have conditions"
    assert 'Null' in deny_stmt['conditions'], "Should use Null condition"

    print("Solution 2: All tests passed!")
