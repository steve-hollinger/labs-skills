"""Tests for OAuth 2.1 and OIDC examples."""

import hashlib
import base64
import pytest

from oauth_oidc.examples.example_1 import (
    PKCEChallenge,
    generate_pkce_challenge,
    build_authorization_url,
)
from oauth_oidc.examples.example_3 import TokenSet


class TestPKCE:
    """Tests for PKCE challenge generation."""

    def test_generate_pkce_challenge(self):
        """Test PKCE challenge generation."""
        pkce = generate_pkce_challenge()

        assert pkce.verifier is not None
        assert pkce.challenge is not None
        assert pkce.method == "S256"
        assert len(pkce.verifier) >= 43

    def test_pkce_challenge_is_valid_s256(self):
        """Test that challenge is valid S256 hash of verifier."""
        pkce = generate_pkce_challenge()

        # Verify the challenge is correct S256 of verifier
        expected_digest = hashlib.sha256(pkce.verifier.encode()).digest()
        expected_challenge = base64.urlsafe_b64encode(expected_digest).decode().rstrip("=")

        assert pkce.challenge == expected_challenge

    def test_pkce_challenges_are_unique(self):
        """Test that each call generates unique values."""
        pkce1 = generate_pkce_challenge()
        pkce2 = generate_pkce_challenge()

        assert pkce1.verifier != pkce2.verifier
        assert pkce1.challenge != pkce2.challenge


class TestAuthorizationURL:
    """Tests for authorization URL building."""

    def test_build_authorization_url(self):
        """Test building authorization URL with all parameters."""
        pkce = PKCEChallenge(
            verifier="test-verifier",
            challenge="test-challenge",
            method="S256",
        )

        url = build_authorization_url(
            authorize_endpoint="https://auth.example.com/authorize",
            client_id="test-client",
            redirect_uri="http://localhost:8000/callback",
            scope="openid profile",
            state="test-state",
            pkce=pkce,
        )

        assert "https://auth.example.com/authorize?" in url
        assert "response_type=code" in url
        assert "client_id=test-client" in url
        assert "redirect_uri=http" in url
        assert "scope=openid+profile" in url
        assert "state=test-state" in url
        assert "code_challenge=test-challenge" in url
        assert "code_challenge_method=S256" in url


class TestTokenSet:
    """Tests for TokenSet functionality."""

    def test_token_set_creation(self):
        """Test creating a token set."""
        tokens = TokenSet(
            access_token="access-123",
            token_type="Bearer",
            expires_in=3600,
            refresh_token="refresh-456",
            scope="openid profile",
        )

        assert tokens.access_token == "access-123"
        assert tokens.token_type == "Bearer"
        assert tokens.refresh_token == "refresh-456"
        assert tokens.scope == "openid profile"

    def test_token_set_expiry_calculation(self):
        """Test that expiry is calculated correctly."""
        tokens = TokenSet(
            access_token="access-123",
            token_type="Bearer",
            expires_in=3600,
        )

        assert tokens.expires_at > 0
        assert not tokens.is_expired()

    def test_token_set_is_expired_with_buffer(self):
        """Test expiry check with buffer time."""
        # Token that expires in 30 seconds
        tokens = TokenSet(
            access_token="access-123",
            token_type="Bearer",
            expires_in=30,
        )

        # With default 60 second buffer, should be considered expired
        assert tokens.is_expired(buffer_seconds=60)

        # With 10 second buffer, should not be expired
        assert not tokens.is_expired(buffer_seconds=10)

    def test_token_set_without_refresh_token(self):
        """Test token set without refresh token."""
        tokens = TokenSet(
            access_token="access-123",
            token_type="Bearer",
            expires_in=3600,
        )

        assert tokens.refresh_token is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
