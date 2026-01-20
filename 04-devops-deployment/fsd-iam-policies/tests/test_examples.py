"""Tests for FSD IAM policy examples."""

import yaml
import pytest


class TestPolicyStructure:
    """Tests for IAM policy structure validation."""

    def test_valid_policy_structure(self):
        """Test that a valid policy has required fields."""
        policy = """
        iam:
          policy_statements:
            - sid: TestStatement
              effect: Allow
              actions:
                - s3:GetObject
              resources:
                - arn:aws:s3:::my-bucket/*
        """
        config = yaml.safe_load(policy)

        assert 'iam' in config
        assert 'policy_statements' in config['iam']

        stmt = config['iam']['policy_statements'][0]
        assert 'effect' in stmt
        assert 'actions' in stmt
        assert 'resources' in stmt

    def test_effect_must_be_allow_or_deny(self):
        """Test that effect is either Allow or Deny."""
        valid_effects = ['Allow', 'Deny']

        for effect in valid_effects:
            policy = f"""
            iam:
              policy_statements:
                - effect: {effect}
                  actions:
                    - s3:GetObject
                  resources:
                    - "*"
            """
            config = yaml.safe_load(policy)
            stmt = config['iam']['policy_statements'][0]
            assert stmt['effect'] in valid_effects

    def test_actions_must_be_list(self):
        """Test that actions is a list."""
        policy = """
        iam:
          policy_statements:
            - effect: Allow
              actions:
                - s3:GetObject
                - s3:PutObject
              resources:
                - "*"
        """
        config = yaml.safe_load(policy)
        stmt = config['iam']['policy_statements'][0]

        assert isinstance(stmt['actions'], list)
        assert len(stmt['actions']) == 2


class TestResourceARNs:
    """Tests for resource ARN patterns."""

    def test_dynamodb_table_arn(self):
        """Test DynamoDB table ARN format."""
        arn = "arn:aws:dynamodb:us-east-1:123456789012:table/users"

        parts = arn.split(':')
        assert parts[0] == 'arn'
        assert parts[1] == 'aws'
        assert parts[2] == 'dynamodb'
        assert parts[3] == 'us-east-1'
        assert parts[4] == '123456789012'
        assert parts[5] == 'table/users'

    def test_s3_bucket_arn(self):
        """Test S3 bucket ARN format."""
        arn = "arn:aws:s3:::my-bucket"

        parts = arn.split(':')
        assert parts[2] == 's3'
        # S3 ARNs don't have region/account
        assert parts[3] == ''
        assert parts[4] == ''
        assert parts[5] == 'my-bucket'

    def test_s3_object_arn(self):
        """Test S3 object ARN format with path."""
        arn = "arn:aws:s3:::my-bucket/path/to/objects/*"

        assert arn.startswith('arn:aws:s3:::')
        assert 'my-bucket' in arn
        assert arn.endswith('/*')


class TestConditions:
    """Tests for IAM policy conditions."""

    def test_string_equals_condition(self):
        """Test StringEquals condition parsing."""
        policy = """
        iam:
          policy_statements:
            - effect: Allow
              actions:
                - s3:GetObject
              resources:
                - "*"
              conditions:
                StringEquals:
                  s3:ExistingObjectTag/status: approved
        """
        config = yaml.safe_load(policy)
        stmt = config['iam']['policy_statements'][0]

        assert 'conditions' in stmt
        assert 'StringEquals' in stmt['conditions']

    def test_null_condition(self):
        """Test Null condition for checking missing keys."""
        policy = """
        iam:
          policy_statements:
            - effect: Deny
              actions:
                - s3:PutObject
              resources:
                - "*"
              conditions:
                "Null":
                  s3:x-amz-server-side-encryption: "true"
        """
        config = yaml.safe_load(policy)
        stmt = config['iam']['policy_statements'][0]

        assert 'Null' in stmt['conditions']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
