"""Key management utilities for JWT validation.

This module provides utilities for working with RSA keys and JWKS.
"""

from __future__ import annotations

import json
from typing import Any

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from jwt_validation.validator import TokenValidationError


def generate_rsa_keypair(
    key_size: int = 2048,
) -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    """Generate an RSA key pair.

    Args:
        key_size: Key size in bits (default 2048)

    Returns:
        Tuple of (private_key, public_key)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend(),
    )
    public_key = private_key.public_key()
    return private_key, public_key


def get_private_key_pem(private_key: rsa.RSAPrivateKey) -> bytes:
    """Get PEM-encoded private key.

    Args:
        private_key: The RSA private key

    Returns:
        PEM-encoded private key bytes
    """
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def get_public_key_pem(public_key: rsa.RSAPublicKey) -> bytes:
    """Get PEM-encoded public key.

    Args:
        public_key: The RSA public key

    Returns:
        PEM-encoded public key bytes
    """
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def load_private_key(pem_data: bytes | str) -> rsa.RSAPrivateKey:
    """Load a private key from PEM data.

    Args:
        pem_data: PEM-encoded private key

    Returns:
        The loaded private key
    """
    if isinstance(pem_data, str):
        pem_data = pem_data.encode()

    return serialization.load_pem_private_key(
        pem_data,
        password=None,
        backend=default_backend(),
    )


def load_public_key(pem_data: bytes | str) -> rsa.RSAPublicKey:
    """Load a public key from PEM data.

    Args:
        pem_data: PEM-encoded public key

    Returns:
        The loaded public key
    """
    if isinstance(pem_data, str):
        pem_data = pem_data.encode()

    return serialization.load_pem_public_key(
        pem_data,
        backend=default_backend(),
    )


class JWKSValidator:
    """Validates JWTs using a JWKS endpoint.

    Example:
        validator = JWKSValidator(
            jwks_url="https://auth.example.com/.well-known/jwks.json",
            audience="my-api",
            issuer="https://auth.example.com"
        )
        payload = validator.validate(token)
    """

    def __init__(
        self,
        jwks_url: str,
        audience: str | list[str] | None = None,
        issuer: str | None = None,
        algorithms: list[str] | None = None,
        cache_keys: bool = True,
        cache_ttl: int = 300,
    ):
        """Initialize the JWKS validator.

        Args:
            jwks_url: URL to the JWKS endpoint
            audience: Expected audience claim
            issuer: Expected issuer claim
            algorithms: Allowed algorithms (default ["RS256"])
            cache_keys: Whether to cache JWKS (default True)
            cache_ttl: Cache TTL in seconds (default 300)
        """
        self.jwks_url = jwks_url
        self.audience = audience
        self.issuer = issuer
        self.algorithms = algorithms or ["RS256"]

        self.jwks_client = jwt.PyJWKClient(
            jwks_url,
            cache_jwk_set=cache_keys,
            lifespan=cache_ttl,
        )

    def validate(self, token: str) -> dict[str, Any]:
        """Validate a JWT using JWKS.

        Args:
            token: The JWT string

        Returns:
            The decoded payload

        Raises:
            TokenValidationError: If validation fails
        """
        try:
            # Get signing key from JWKS based on token's kid
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)

            return jwt.decode(
                token,
                signing_key.key,
                algorithms=self.algorithms,
                audience=self.audience,
                issuer=self.issuer,
            )
        except jwt.PyJWKClientError as e:
            raise TokenValidationError(f"Failed to fetch signing key: {e}") from e
        except jwt.ExpiredSignatureError as e:
            raise TokenValidationError("Token has expired") from e
        except jwt.InvalidTokenError as e:
            raise TokenValidationError(f"Invalid token: {e}") from e

    def get_signing_key(self, token: str) -> Any:
        """Get the signing key for a token.

        Args:
            token: The JWT string

        Returns:
            The signing key

        Raises:
            TokenValidationError: If key cannot be found
        """
        try:
            return self.jwks_client.get_signing_key_from_jwt(token)
        except jwt.PyJWKClientError as e:
            raise TokenValidationError(f"Failed to get signing key: {e}") from e


class LocalJWKS:
    """Local JWKS for testing and development.

    This class creates a local JWKS with generated keys for testing.
    """

    def __init__(self, key_id: str = "test-key"):
        """Initialize with a generated key pair.

        Args:
            key_id: The key ID to use
        """
        self.key_id = key_id
        self.private_key, self.public_key = generate_rsa_keypair()

    def sign_token(
        self,
        payload: dict[str, Any],
        algorithm: str = "RS256",
    ) -> str:
        """Sign a token with the private key.

        Args:
            payload: The claims to encode
            algorithm: The signing algorithm

        Returns:
            The signed JWT
        """
        headers = {"kid": self.key_id}
        return jwt.encode(
            payload,
            self.private_key,
            algorithm=algorithm,
            headers=headers,
        )

    def verify_token(
        self,
        token: str,
        audience: str | None = None,
        issuer: str | None = None,
    ) -> dict[str, Any]:
        """Verify a token with the public key.

        Args:
            token: The JWT to verify
            audience: Expected audience
            issuer: Expected issuer

        Returns:
            The decoded payload
        """
        return jwt.decode(
            token,
            self.public_key,
            algorithms=["RS256"],
            audience=audience,
            issuer=issuer,
        )

    def get_jwks(self) -> dict[str, Any]:
        """Get the JWKS representation.

        Returns:
            JWKS dictionary
        """
        # Get the public key numbers
        public_numbers = self.public_key.public_numbers()

        # Convert to base64url encoding
        import base64

        def int_to_base64url(n: int, length: int) -> str:
            data = n.to_bytes(length, byteorder="big")
            return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

        n_bytes = (public_numbers.n.bit_length() + 7) // 8
        e_bytes = (public_numbers.e.bit_length() + 7) // 8

        return {
            "keys": [
                {
                    "kty": "RSA",
                    "kid": self.key_id,
                    "use": "sig",
                    "alg": "RS256",
                    "n": int_to_base64url(public_numbers.n, n_bytes),
                    "e": int_to_base64url(public_numbers.e, e_bytes),
                }
            ]
        }

    def get_jwks_json(self) -> str:
        """Get the JWKS as a JSON string.

        Returns:
            JWKS JSON string
        """
        return json.dumps(self.get_jwks())
