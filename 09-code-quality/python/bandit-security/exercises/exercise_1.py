"""Exercise 1: Find and Fix Security Vulnerabilities

Goal: Identify and fix all security vulnerabilities in the code below.

Instructions:
1. Run Bandit on this file to find vulnerabilities
2. Fix each vulnerability using secure alternatives
3. Verify the fixes with another Bandit scan
4. Add comments explaining why the fix is secure

Run: bandit exercises/exercise_1.py

Expected: Fix all HIGH and MEDIUM severity issues
"""

import hashlib
import os
import pickle
import random
import subprocess

import yaml


# VULNERABILITY 1: Command Injection
# Find: B602, B605
def run_command(user_input: str) -> str:
    """Run a command with user input (VULNERABLE!)."""
    result = subprocess.run(
        f"echo {user_input}",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


# VULNERABILITY 2: Hardcoded Password
# Find: B105
def connect_to_database() -> None:
    """Connect to database (VULNERABLE!)."""
    password = "super_secret_password_123"
    print(f"Connecting with password: {password[:3]}...")


# VULNERABILITY 3: Insecure Deserialization
# Find: B301
def load_user_data(filename: str) -> dict:
    """Load user data from file (VULNERABLE!)."""
    with open(filename, "rb") as f:
        return pickle.load(f)


# VULNERABILITY 4: Unsafe YAML Loading
# Find: B506
def load_config(filename: str) -> dict:
    """Load configuration from YAML (VULNERABLE!)."""
    with open(filename) as f:
        return yaml.load(f, Loader=yaml.Loader)


# VULNERABILITY 5: Weak Cryptography
# Find: B303
def hash_password(password: str) -> str:
    """Hash a password (VULNERABLE!)."""
    return hashlib.md5(password.encode()).hexdigest()


# VULNERABILITY 6: Insecure Random
# Find: B311
def generate_token() -> str:
    """Generate a security token (VULNERABLE!)."""
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(random.choice(chars) for _ in range(32))


# VULNERABILITY 7: SQL Injection
# Find: B608
def get_user(cursor, user_id: str) -> dict:
    """Get user from database (VULNERABLE!)."""
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    return cursor.fetchone()


# ============================================
# VERIFICATION
# ============================================

def verify_fixes() -> None:
    """Run Bandit to verify all fixes."""
    result = subprocess.run(
        ["bandit", __file__, "-f", "json"],
        capture_output=True,
        text=True,
    )

    import json

    findings = json.loads(result.stdout)
    issues = findings.get("results", [])

    high_medium = [
        i for i in issues if i["issue_severity"] in ("HIGH", "MEDIUM")
    ]

    print(f"\nBandit Results:")
    print(f"  Total issues: {len(issues)}")
    print(f"  HIGH/MEDIUM: {len(high_medium)}")

    if high_medium:
        print("\nRemaining issues to fix:")
        for issue in high_medium:
            print(f"  Line {issue['line_number']}: {issue['test_id']} - {issue['issue_text']}")
    else:
        print("\nAll HIGH/MEDIUM vulnerabilities fixed!")


if __name__ == "__main__":
    print(__doc__)
    print("\nRun: bandit exercises/exercise_1.py")
    print("Then fix the vulnerabilities and run again.")
