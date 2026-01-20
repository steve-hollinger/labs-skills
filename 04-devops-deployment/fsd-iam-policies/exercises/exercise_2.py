"""Exercise 2: Create an S3 Policy with Encryption Requirement

Your task: Create an FSD IAM policy that:
1. Allows uploading objects to an S3 bucket
2. DENIES uploads without server-side encryption
3. Uses conditions to enforce encryption

Requirements:
- Allow PutObject to bucket 'data-uploads'
- Deny PutObject when encryption header is missing
"""

# TODO: Fill in the policy YAML
POLICY = """
iam:
  policy_statements:
    # Allow uploads
    - sid: # TODO: AllowUploads
      effect: # TODO
      actions:
        # TODO
      resources:
        # TODO

    # Deny unencrypted uploads
    - sid: # TODO: DenyUnencrypted
      effect: # TODO
      actions:
        # TODO
      resources:
        # TODO
      conditions:
        # TODO: Use Null condition
"""

if __name__ == "__main__":
    import yaml

    config = yaml.safe_load(POLICY)
    stmts = config['iam']['policy_statements']

    # Should have 2 statements
    assert len(stmts) == 2, "Should have Allow and Deny statements"

    # One Allow, one Deny
    effects = [s['effect'] for s in stmts]
    assert 'Allow' in effects, "Should have Allow statement"
    assert 'Deny' in effects, "Should have Deny statement"

    # Deny should have condition
    deny_stmt = next(s for s in stmts if s['effect'] == 'Deny')
    assert 'conditions' in deny_stmt, "Deny statement should have conditions"

    print("Policy structure looks good!")
