"""Tests for jwt_validation functionality."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from jwt_validation import (
    ClaimsValidator,
    InvalidClaimsError,
    InvalidSignatureError,
    TokenConfig,
    TokenExpiredError,
    TokenValidationError,
    TokenValidator,
    generate_rsa_keypair,
    get_claim,
    get_expiration,
    get_private_key_pem,
    get_public_key_pem,
    has_all_roles,
    has_any_role,
    has_role,
    is_expired,
    validate_claims,
)
from jwt_validation.claims import ClaimRule
from jwt_validation.keys import LocalJWKS


@pytest.fixture
def secret() -> str:
    """Generate a test secret."""
    return secrets.token_urlsafe(32)


@pytest.fixture
def valid_payload() -> dict:
    """Create a valid payload."""
    now = datetime.now(timezone.utc)
    return {
        "sub": "user123",
        "name": "Test User",
        "roles": ["user", "editor"],
        "iat": now,
        "exp": now + timedelta(hours=1),
        "iss": "https://auth.example.com",
        "aud": "my-api",
    }


@pytest.fixture
def valid_token(secret: str, valid_payload: dict) -> str:
    """Create a valid token."""
    return jwt.encode(valid_payload, secret, algorithm="HS256")


class TestTokenValidator:
    """Tests for TokenValidator class."""

    def test_validate_valid_token(self, secret: str, valid_token: str):
        """Test validating a valid token."""
        config = TokenConfig(secret=secret, algorithms=["HS256"])
        validator = TokenValidator(config)

        payload = validator.validate(valid_token)

        assert payload["sub"] == "user123"
        assert payload["name"] == "Test User"

    def test_validate_with_issuer(self, secret: str, valid_token: str):
        """Test validating with issuer check."""
        config = TokenConfig(
            secret=secret,
            algorithms=["HS256"],
            issuer="https://auth.example.com",
        )
        validator = TokenValidator(config)

        payload = validator.validate(valid_token)
        assert payload["iss"] == "https://auth.example.com"

    def test_validate_wrong_issuer(self, secret: str, valid_token: str):
        """Test validation fails with wrong issuer."""
        config = TokenConfig(
            secret=secret,
            algorithms=["HS256"],
            issuer="https://wrong.example.com",
        )
        validator = TokenValidator(config)

        with pytest.raises(InvalidClaimsError, match="Invalid issuer"):
            validator.validate(valid_token)

    def test_validate_with_audience(self, secret: str, valid_token: str):
        """Test validating with audience check."""
        config = TokenConfig(
            secret=secret,
            algorithms=["HS256"],
            audience="my-api",
        )
        validator = TokenValidator(config)

        payload = validator.validate(valid_token)
        assert payload["aud"] == "my-api"

    def test_validate_wrong_audience(self, secret: str, valid_token: str):
        """Test validation fails with wrong audience."""
        config = TokenConfig(
            secret=secret,
            algorithms=["HS256"],
            audience="wrong-api",
        )
        validator = TokenValidator(config)

        with pytest.raises(InvalidClaimsError, match="Invalid audience"):
            validator.validate(valid_token)

    def test_validate_expired_token(self, secret: str):
        """Test validation fails for expired token."""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "user123",
            "exp": now - timedelta(hours=1),  # Already expired
        }
        token = jwt.encode(payload, secret, algorithm="HS256")

        config = TokenConfig(secret=secret, algorithms=["HS256"])
        validator = TokenValidator(config)

        with pytest.raises(TokenExpiredError):
            validator.validate(token)

    def test_validate_wrong_secret(self, valid_token: str):
        """Test validation fails with wrong secret."""
        config = TokenConfig(secret="wrong-secret", algorithms=["HS256"])
        validator = TokenValidator(config)

        with pytest.raises(InvalidSignatureError):
            validator.validate(valid_token)

    def test_validate_required_claims(self, secret: str):
        """Test validation fails when required claims missing."""
        payload = {"name": "Test"}  # Missing 'sub'
        token = jwt.encode(payload, secret, algorithm="HS256")

        config = TokenConfig(
            secret=secret,
            algorithms=["HS256"],
            required_claims=["sub"],
        )
        validator = TokenValidator(config)

        with pytest.raises(InvalidClaimsError, match="Missing required claim"):
            validator.validate(token)

    def test_validate_with_leeway(self, secret: str):
        """Test validation with expiration leeway."""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "user123",
            "exp": now - timedelta(seconds=10),  # Expired 10 seconds ago
        }
        token = jwt.encode(payload, secret, algorithm="HS256")

        # Should fail without leeway
        config_no_leeway = TokenConfig(secret=secret, algorithms=["HS256"])
        validator_no_leeway = TokenValidator(config_no_leeway)

        with pytest.raises(TokenExpiredError):
            validator_no_leeway.validate(token)

        # Should pass with 30 second leeway
        config_leeway = TokenConfig(secret=secret, algorithms=["HS256"], leeway=30)
        validator_leeway = TokenValidator(config_leeway)

        payload = validator_leeway.validate(token)
        assert payload["sub"] == "user123"

    def test_decode_header(self, secret: str, valid_token: str):
        """Test decoding token header."""
        config = TokenConfig(secret=secret, algorithms=["HS256"])
        validator = TokenValidator(config)

        header = validator.decode_header(valid_token)
        assert header["alg"] == "HS256"
        assert header["typ"] == "JWT"


class TestRS256:
    """Tests for RS256 algorithm."""

    def test_rs256_validation(self):
        """Test RS256 token creation and validation."""
        private_key, public_key = generate_rsa_keypair()

        now = datetime.now(timezone.utc)
        payload = {
            "sub": "user123",
            "exp": now + timedelta(hours=1),
        }

        # Sign with private key
        token = jwt.encode(payload, private_key, algorithm="RS256")

        # Validate with public key
        config = TokenConfig(secret=public_key, algorithms=["RS256"])
        validator = TokenValidator(config)

        decoded = validator.validate(token)
        assert decoded["sub"] == "user123"

    def test_key_pem_conversion(self):
        """Test PEM encoding/decoding."""
        private_key, public_key = generate_rsa_keypair()

        private_pem = get_private_key_pem(private_key)
        public_pem = get_public_key_pem(public_key)

        assert b"BEGIN PRIVATE KEY" in private_pem
        assert b"BEGIN PUBLIC KEY" in public_pem


class TestLocalJWKS:
    """Tests for LocalJWKS class."""

    def test_sign_and_verify(self):
        """Test signing and verifying with LocalJWKS."""
        jwks = LocalJWKS(key_id="test-key")

        payload = {"sub": "user123", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}
        token = jwks.sign_token(payload)

        decoded = jwks.verify_token(token)
        assert decoded["sub"] == "user123"

    def test_jwks_format(self):
        """Test JWKS output format."""
        jwks = LocalJWKS(key_id="my-key")
        jwks_data = jwks.get_jwks()

        assert "keys" in jwks_data
        assert len(jwks_data["keys"]) == 1

        key = jwks_data["keys"][0]
        assert key["kty"] == "RSA"
        assert key["kid"] == "my-key"
        assert key["alg"] == "RS256"
        assert "n" in key
        assert "e" in key

    def test_token_has_kid(self):
        """Test that signed tokens include kid in header."""
        jwks = LocalJWKS(key_id="test-key-123")

        payload = {"sub": "user"}
        token = jwks.sign_token(payload)

        header = jwt.get_unverified_header(token)
        assert header["kid"] == "test-key-123"


class TestClaimsValidation:
    """Tests for claims validation utilities."""

    def test_validate_claims_success(self, valid_payload: dict):
        """Test successful claims validation."""
        is_valid, errors = validate_claims(
            valid_payload,
            required=["sub", "name"],
            issuer="https://auth.example.com",
            audience="my-api",
        )

        assert is_valid
        assert len(errors) == 0

    def test_validate_claims_missing_required(self):
        """Test validation fails for missing required claims."""
        payload = {"name": "Test"}

        is_valid, errors = validate_claims(
            payload,
            required=["sub", "email"],
        )

        assert not is_valid
        assert any("sub" in e for e in errors)
        assert any("email" in e for e in errors)

    def test_validate_claims_wrong_issuer(self, valid_payload: dict):
        """Test validation fails for wrong issuer."""
        is_valid, errors = validate_claims(
            valid_payload,
            issuer="https://wrong.example.com",
        )

        assert not is_valid
        assert any("issuer" in e.lower() for e in errors)

    def test_validate_claims_wrong_audience(self, valid_payload: dict):
        """Test validation fails for wrong audience."""
        is_valid, errors = validate_claims(
            valid_payload,
            audience="wrong-api",
        )

        assert not is_valid
        assert any("audience" in e.lower() for e in errors)


class TestClaimsValidator:
    """Tests for ClaimsValidator class."""

    def test_custom_validator(self):
        """Test custom claim validator."""
        validator = ClaimsValidator()
        validator.add_rule(ClaimRule(
            name="age",
            required=True,
            validator=lambda x: x >= 18,
        ))

        # Valid age
        is_valid, errors = validator.validate({"age": 25})
        assert is_valid

        # Invalid age
        is_valid, errors = validator.validate({"age": 16})
        assert not is_valid

    def test_allowed_values(self):
        """Test allowed values validation."""
        validator = ClaimsValidator()
        validator.add_rule(ClaimRule(
            name="role",
            required=True,
            allowed_values=["admin", "user"],
        ))

        # Valid role
        is_valid, errors = validator.validate({"role": "admin"})
        assert is_valid

        # Invalid role
        is_valid, errors = validator.validate({"role": "superuser"})
        assert not is_valid


class TestClaimUtilities:
    """Tests for claim utility functions."""

    def test_get_claim(self, valid_payload: dict):
        """Test get_claim function."""
        assert get_claim(valid_payload, "sub") == "user123"
        assert get_claim(valid_payload, "missing") is None
        assert get_claim(valid_payload, "missing", "default") == "default"

    def test_has_role(self, valid_payload: dict):
        """Test has_role function."""
        assert has_role(valid_payload, "user")
        assert has_role(valid_payload, "editor")
        assert not has_role(valid_payload, "admin")

    def test_has_any_role(self, valid_payload: dict):
        """Test has_any_role function."""
        assert has_any_role(valid_payload, ["admin", "user"])
        assert has_any_role(valid_payload, ["editor"])
        assert not has_any_role(valid_payload, ["admin", "superuser"])

    def test_has_all_roles(self, valid_payload: dict):
        """Test has_all_roles function."""
        assert has_all_roles(valid_payload, ["user", "editor"])
        assert not has_all_roles(valid_payload, ["user", "admin"])

    def test_get_expiration(self, valid_payload: dict):
        """Test get_expiration function."""
        # Convert to timestamp for the payload
        exp_dt = valid_payload["exp"]
        payload = {**valid_payload, "exp": exp_dt.timestamp()}

        exp = get_expiration(payload)
        assert exp is not None
        assert isinstance(exp, datetime)

    def test_is_expired(self):
        """Test is_expired function."""
        now = datetime.now(timezone.utc)

        # Not expired
        future_payload = {"exp": (now + timedelta(hours=1)).timestamp()}
        assert not is_expired(future_payload)

        # Expired
        past_payload = {"exp": (now - timedelta(hours=1)).timestamp()}
        assert is_expired(past_payload)

        # No exp claim
        no_exp_payload = {"sub": "user"}
        assert not is_expired(no_exp_payload)
