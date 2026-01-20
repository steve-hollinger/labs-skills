"""Tests for token_masking functionality."""

from __future__ import annotations

import logging
import pytest

from token_masking import (
    MaskingFilter,
    SECRET_PATTERNS,
    SecretDetector,
    TokenMasker,
    calculate_entropy,
    full_mask,
    looks_like_secret,
    mask_email,
    mask_json,
    mask_url_credentials,
    partial_mask,
)


class TestFullMask:
    """Tests for full_mask function."""

    def test_default_placeholder(self):
        """Test default masking placeholder."""
        result = full_mask("secret")
        assert result == "***MASKED***"

    def test_custom_placeholder(self):
        """Test custom placeholder."""
        result = full_mask("secret", placeholder="[REDACTED]")
        assert result == "[REDACTED]"

    def test_empty_string(self):
        """Test masking empty string."""
        result = full_mask("")
        assert result == "***MASKED***"


class TestPartialMask:
    """Tests for partial_mask function."""

    def test_default_settings(self):
        """Test with default show_start and show_end."""
        result = partial_mask("sk_example_FAKE")
        assert result == "sk_l***z789"
        assert "abc123" not in result

    def test_custom_settings(self):
        """Test with custom show_start and show_end."""
        result = partial_mask("my_secret_value", show_start=3, show_end=2)
        assert result == "my_***ue"

    def test_short_value(self):
        """Test that short values are fully masked."""
        result = partial_mask("abc", show_start=4, show_end=4)
        assert result == "***"

    def test_exact_length(self):
        """Test value exactly at threshold length."""
        result = partial_mask("12345678", show_start=4, show_end=4)
        assert result == "***"

    def test_just_over_threshold(self):
        """Test value just over threshold."""
        result = partial_mask("123456789", show_start=4, show_end=4)
        assert result == "1234***6789"

    def test_show_only_start(self):
        """Test showing only start characters."""
        result = partial_mask("sk_example_FAKE", show_start=7, show_end=0)
        assert result == "sk_live***"

    def test_show_only_end(self):
        """Test showing only end characters."""
        result = partial_mask("secret_key_123", show_start=0, show_end=4)
        assert result == "***_123"


class TestMaskEmail:
    """Tests for mask_email function."""

    def test_normal_email(self):
        """Test masking a normal email."""
        result = mask_email("john.doe@example.com")
        assert result == "j********@example.com"
        assert "@example.com" in result

    def test_short_local_part(self):
        """Test email with single character local part."""
        result = mask_email("a@b.com")
        assert result == "*@b.com"

    def test_preserves_domain(self):
        """Test that domain is preserved."""
        result = mask_email("user@subdomain.example.org")
        assert "@subdomain.example.org" in result

    def test_invalid_email(self):
        """Test handling invalid email format."""
        result = mask_email("not-an-email")
        assert result == "***@***"


class TestMaskUrlCredentials:
    """Tests for mask_url_credentials function."""

    def test_postgres_url(self):
        """Test masking postgres connection string."""
        url = "postgres://admin:secret123@db.example.com:5432/mydb"
        result = mask_url_credentials(url)
        assert "admin" in result
        assert "secret123" not in result
        assert "***" in result
        assert "db.example.com" in result

    def test_url_without_credentials(self):
        """Test URL without credentials is unchanged."""
        url = "https://api.example.com/v1/data"
        result = mask_url_credentials(url)
        assert result == url

    def test_url_with_port(self):
        """Test URL with port is preserved."""
        url = "redis://default:pass@cache.example.com:6379"
        result = mask_url_credentials(url)
        assert ":6379" in result
        assert "pass" not in result

    def test_special_characters_in_password(self):
        """Test password with special characters."""
        url = "postgres://user:p@ss%23word@host/db"
        result = mask_url_credentials(url)
        assert "p@ss" not in result


class TestMaskJson:
    """Tests for mask_json function."""

    def test_simple_dict(self):
        """Test masking simple dictionary."""
        data = {"username": "john", "password": "secret123"}
        result = mask_json(data)
        assert result["username"] == "john"
        assert result["password"] == "***MASKED***"

    def test_nested_dict(self):
        """Test masking nested dictionary."""
        data = {
            "config": {
                "api_key": "sk_example_FAKE",
                "timeout": 30,
            }
        }
        result = mask_json(data)
        assert result["config"]["api_key"] == "***MASKED***"
        assert result["config"]["timeout"] == 30

    def test_list_of_dicts(self):
        """Test masking list of dictionaries."""
        data = [
            {"name": "service1", "token": "token1"},
            {"name": "service2", "token": "token2"},
        ]
        result = mask_json(data)
        assert result[0]["name"] == "service1"
        assert result[0]["token"] == "***MASKED***"
        assert result[1]["token"] == "***MASKED***"

    def test_case_insensitive(self):
        """Test case-insensitive field matching."""
        data = {"PASSWORD": "secret", "Api_Key": "key123"}
        result = mask_json(data, case_insensitive=True)
        assert result["PASSWORD"] == "***MASKED***"
        assert result["Api_Key"] == "***MASKED***"

    def test_custom_fields(self):
        """Test custom sensitive fields."""
        data = {"custom_secret": "value", "password": "pass"}
        result = mask_json(data, sensitive_fields={"custom_secret"})
        assert result["custom_secret"] == "***MASKED***"
        assert result["password"] == "pass"  # Not in custom fields

    def test_custom_mask_func(self):
        """Test custom masking function."""
        data = {"password": "secret123"}
        result = mask_json(data, mask_func=lambda x: "[HIDDEN]")
        assert result["password"] == "[HIDDEN]"

    def test_preserves_original(self):
        """Test that original data is not modified."""
        data = {"password": "secret"}
        _ = mask_json(data)
        assert data["password"] == "secret"


class TestEntropy:
    """Tests for entropy-based detection."""

    def test_low_entropy(self):
        """Test low entropy values."""
        assert calculate_entropy("aaaaaaaaaa") < 1.0
        assert not looks_like_secret("password")

    def test_high_entropy(self):
        """Test high entropy values."""
        assert calculate_entropy("aB3$kL9#mN2@pQ5") > 3.5
        assert looks_like_secret("aB3$kL9#mN2@pQ5abcdef")

    def test_empty_string(self):
        """Test empty string entropy."""
        assert calculate_entropy("") == 0.0

    def test_min_length_requirement(self):
        """Test minimum length for secret detection."""
        assert not looks_like_secret("aB3$", min_length=8)


class TestSecretDetector:
    """Tests for SecretDetector class."""

    def test_detect_aws_key(self):
        """Test detecting AWS access key."""
        detector = SecretDetector()
        text = "AWS Key: AKIAIOSFODNN7EXAMPLE"
        matches = detector.detect(text)
        assert len(matches) >= 1
        assert any(m.secret_type == "aws_access_key" for m in matches)

    def test_detect_github_token(self):
        """Test detecting GitHub token."""
        detector = SecretDetector()
        text = "Token: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        matches = detector.detect(text)
        assert len(matches) >= 1
        assert any(m.secret_type == "github_pat" for m in matches)

    def test_detect_jwt(self):
        """Test detecting JWT."""
        detector = SecretDetector()
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        matches = detector.detect(jwt)
        assert len(matches) >= 1
        assert any(m.secret_type == "jwt" for m in matches)

    def test_mask_all(self):
        """Test mask_all method."""
        detector = SecretDetector()
        text = "Key: AKIAIOSFODNN7EXAMPLE"
        result = detector.mask_all(text)
        assert "AKIAIOSFODNN7EXAMPLE" not in result
        assert "***" in result

    def test_has_secrets(self):
        """Test has_secrets method."""
        detector = SecretDetector()
        assert detector.has_secrets("Key: AKIAIOSFODNN7EXAMPLE")
        assert not detector.has_secrets("Just normal text")

    def test_entropy_detection(self):
        """Test entropy-based detection."""
        detector = SecretDetector(patterns={}, use_entropy=True)
        # High-entropy random string
        text = "Secret: xK9mP2nL5qR8tY3wE6uI0oA4sD7fG1hJ"
        matches = detector.detect(text)
        # Should detect as high_entropy
        assert len(matches) >= 1

    def test_disable_entropy(self):
        """Test disabling entropy detection."""
        detector = SecretDetector(patterns={}, use_entropy=False)
        text = "xK9mP2nL5qR8tY3wE6uI0oA4sD7fG1hJ"
        matches = detector.detect(text)
        assert len(matches) == 0


class TestTokenMasker:
    """Tests for TokenMasker class."""

    def test_mask_text(self):
        """Test masking text with secrets."""
        masker = TokenMasker()
        text = "API key: sk_example_FAKE"
        result = masker.mask_text(text)
        assert "abc123xyz789" not in result

    def test_mask_data(self):
        """Test masking structured data."""
        masker = TokenMasker()
        data = {"api_key": "secret123", "name": "test"}
        result = masker.mask_data(data)
        assert "secret123" not in str(result)
        assert result["name"] == "test"

    def test_mask_url(self):
        """Test URL masking."""
        masker = TokenMasker()
        url = "postgres://user:pass@host/db"
        result = masker.mask_url(url)
        assert "pass" not in result

    def test_detect_secrets(self):
        """Test secret detection."""
        masker = TokenMasker()
        text = "Key: AKIAIOSFODNN7EXAMPLE"
        secrets = masker.detect_secrets(text)
        assert len(secrets) >= 1
        assert "type" in secrets[0]
        assert "masked" in secrets[0]


class TestMaskingFilter:
    """Tests for logging MaskingFilter."""

    def test_filter_masks_message(self):
        """Test that filter masks secrets in message."""
        masker = TokenMasker()
        filter = MaskingFilter(masker)

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="API key: AKIAIOSFODNN7EXAMPLE",
            args=(),
            exc_info=None,
        )

        filter.filter(record)
        assert "AKIAIOSFODNN7EXAMPLE" not in record.msg
        assert "***" in record.msg

    def test_filter_masks_args(self):
        """Test that filter masks secrets in args."""
        masker = TokenMasker()
        filter = MaskingFilter(masker)

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Key: %s",
            args=("AKIAIOSFODNN7EXAMPLE",),
            exc_info=None,
        )

        filter.filter(record)
        assert "AKIAIOSFODNN7EXAMPLE" not in str(record.args)

    def test_filter_returns_true(self):
        """Test that filter always returns True (doesn't block)."""
        masker = TokenMasker()
        filter = MaskingFilter(masker)

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Normal message",
            args=(),
            exc_info=None,
        )

        assert filter.filter(record) is True


class TestPatterns:
    """Tests for secret patterns."""

    @pytest.mark.parametrize("pattern_name,test_value,should_match", [
        ("aws_access_key", "AKIAIOSFODNN7EXAMPLE", True),
        ("aws_access_key", "NOTANAWSKEY123456789", False),
        ("github_pat", "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", True),
        ("github_pat", "ghp_short", False),
        ("stripe_secret", "sk_example_FAKE24CHARSTRING12", True),
        ("email", "user@example.com", True),
        ("email", "not-an-email", False),
        ("ssn", "123-45-6789", True),
        ("ssn", "12345-6789", False),
    ])
    def test_pattern_accuracy(self, pattern_name, test_value, should_match):
        """Test that patterns match expected values."""
        import re
        if pattern_name not in SECRET_PATTERNS:
            pytest.skip(f"Pattern {pattern_name} not found")

        pattern = re.compile(SECRET_PATTERNS[pattern_name])
        matches = bool(pattern.search(test_value))
        assert matches == should_match, f"Pattern {pattern_name} {'should' if should_match else 'should not'} match {test_value}"
