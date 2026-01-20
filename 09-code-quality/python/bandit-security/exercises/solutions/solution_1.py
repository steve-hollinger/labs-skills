"""Solution for Exercise 1: Find and Fix Security Vulnerabilities

This solution shows the secure versions of all vulnerable code.
"""

import hashlib
import os
import secrets
import subprocess

import yaml


# FIX 1: Command Injection
# Use list arguments instead of shell=True
def run_command(user_input: str) -> str:
    """Run a command with user input (SECURE)."""
    # Never pass user input directly to shell
    # Use list arguments which don't invoke shell
    result = subprocess.run(
        ["echo", user_input],  # List form - no shell injection
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


# FIX 2: Hardcoded Password
# Use environment variables for secrets
def connect_to_database() -> None:
    """Connect to database (SECURE)."""
    password = os.environ.get("DB_PASSWORD")
    if not password:
        raise ValueError("DB_PASSWORD environment variable is required")
    print(f"Connecting with password from environment...")


# FIX 3: Insecure Deserialization
# Use JSON instead of pickle for untrusted data
import json


def load_user_data(filename: str) -> dict:
    """Load user data from file (SECURE)."""
    # Option 1: Use JSON (safest for data interchange)
    with open(filename) as f:
        return json.load(f)

    # Option 2: If pickle is required, only use with TRUSTED sources
    # and consider signing the data
    # with open(filename, "rb") as f:
    #     return pickle.load(f)  # nosec B301 - trusted internal file only


# FIX 4: Unsafe YAML Loading
# Use safe_load instead of load
def load_config(filename: str) -> dict:
    """Load configuration from YAML (SECURE)."""
    with open(filename) as f:
        # safe_load doesn't execute arbitrary Python
        return yaml.safe_load(f)


# FIX 5: Weak Cryptography
# Use SHA-256 for general hashing, proper password hashing for passwords
def hash_password(password: str) -> str:
    """Hash a password (SECURE).

    For actual password storage, use argon2 or bcrypt!
    This is just for demonstration of SHA-256 vs MD5.
    """
    # For general hashing (not passwords)
    return hashlib.sha256(password.encode()).hexdigest()


# For actual password hashing, use:
# from passlib.hash import argon2
# def hash_password_secure(password: str) -> str:
#     return argon2.hash(password)


# FIX 6: Insecure Random
# Use secrets module for cryptographic randomness
def generate_token() -> str:
    """Generate a security token (SECURE)."""
    # secrets module is cryptographically secure
    return secrets.token_urlsafe(32)


# FIX 7: SQL Injection
# Use parameterized queries
def get_user(cursor, user_id: str) -> dict:
    """Get user from database (SECURE)."""
    # Parameterized query - SQL injection not possible
    cursor.execute(
        "SELECT * FROM users WHERE id = %s",
        (user_id,),
    )
    return cursor.fetchone()


# ============================================
# VERIFICATION
# ============================================

def main() -> None:
    """Demonstrate the secure functions."""
    print("Solution for Exercise 1: Security Vulnerability Fixes")
    print("=" * 60)

    print("\n1. Command Execution (safe):")
    try:
        result = run_command("Hello, World!")
        print(f"   Output: {result.strip()}")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n2. Database Connection (requires env var):")
    try:
        # Would need DB_PASSWORD environment variable
        # connect_to_database()
        print("   Would use DB_PASSWORD from environment")
    except ValueError as e:
        print(f"   {e}")

    print("\n3. Token Generation (cryptographically secure):")
    token = generate_token()
    print(f"   Token: {token}")

    print("\n4. Password Hashing (SHA-256):")
    hashed = hash_password("example_password")
    print(f"   Hash: {hashed[:32]}...")

    print("\nAll fixes demonstrated!")
    print("\nRun 'bandit exercises/solutions/solution_1.py' to verify no issues.")


if __name__ == "__main__":
    main()
