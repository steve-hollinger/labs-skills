"""Example 1: Common Security Vulnerabilities

This example demonstrates common security vulnerabilities that
Bandit can detect and how to fix them.

NOTE: This file contains intentionally vulnerable code for educational purposes.
DO NOT use this code in production!
"""


def demonstrate_command_injection() -> None:
    """Show command injection vulnerabilities."""
    print("\n" + "=" * 60)
    print("VULNERABILITY 1: Command Injection")
    print("=" * 60)

    vulnerable_code = '''
# B602: subprocess_popen_with_shell_equals_true
import subprocess
user_input = "file.txt; rm -rf /"  # Malicious input!
subprocess.Popen(f"cat {user_input}", shell=True)
# Attacker can execute arbitrary commands!

# B605: start_process_with_a_shell
import os
os.system(f"echo {user_input}")  # Same vulnerability

# B607: start_process_with_partial_path
subprocess.call(["bash", "-c", user_input])
'''

    secure_code = '''
# SECURE: Use list arguments, no shell
import subprocess

# Never pass user input to shell
subprocess.run(["cat", user_input], check=True)

# Validate against whitelist
allowed_files = {"report.txt", "data.csv", "log.txt"}
if user_input in allowed_files:
    subprocess.run(["cat", user_input], check=True)
else:
    raise ValueError("File not allowed")
'''

    print("VULNERABLE CODE:")
    print(vulnerable_code)
    print("\nSECURE CODE:")
    print(secure_code)


def demonstrate_hardcoded_secrets() -> None:
    """Show hardcoded secrets vulnerabilities."""
    print("\n" + "=" * 60)
    print("VULNERABILITY 2: Hardcoded Secrets")
    print("=" * 60)

    vulnerable_code = '''
# B105: hardcoded_password_string
password = "super_secret_password123"
api_key = "sk-1234567890abcdef"

# B106: hardcoded_password_funcarg
db.connect(
    host="localhost",
    password="admin123"  # Hardcoded!
)

# B107: hardcoded_password_default
def login(username, password="changeme"):
    ...
'''

    secure_code = '''
# SECURE: Use environment variables
import os

password = os.environ.get("DB_PASSWORD")
if not password:
    raise ValueError("DB_PASSWORD required")

api_key = os.environ.get("API_KEY")

# Or use a secrets manager
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_password: str
    api_key: str

    class Config:
        env_file = ".env"

settings = Settings()
db.connect(host="localhost", password=settings.db_password)
'''

    print("VULNERABLE CODE:")
    print(vulnerable_code)
    print("\nSECURE CODE:")
    print(secure_code)


def demonstrate_sql_injection() -> None:
    """Show SQL injection vulnerabilities."""
    print("\n" + "=" * 60)
    print("VULNERABILITY 3: SQL Injection")
    print("=" * 60)

    vulnerable_code = '''
# B608: hardcoded_sql_expressions
user_id = "1 OR 1=1"  # Malicious input!

# String formatting in SQL
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
# Returns ALL users!

# String concatenation
query = "SELECT * FROM users WHERE name = '" + username + "'"
cursor.execute(query)
'''

    secure_code = '''
# SECURE: Use parameterized queries
cursor.execute(
    "SELECT * FROM users WHERE id = %s",
    (user_id,)
)

# With SQLAlchemy ORM (safest)
user = session.query(User).filter(User.id == user_id).first()

# With SQLAlchemy Core
from sqlalchemy import text
result = session.execute(
    text("SELECT * FROM users WHERE id = :id"),
    {"id": user_id}
)
'''

    print("VULNERABLE CODE:")
    print(vulnerable_code)
    print("\nSECURE CODE:")
    print(secure_code)


def demonstrate_insecure_deserialization() -> None:
    """Show deserialization vulnerabilities."""
    print("\n" + "=" * 60)
    print("VULNERABILITY 4: Insecure Deserialization")
    print("=" * 60)

    vulnerable_code = '''
# B301: pickle - arbitrary code execution
import pickle
data = pickle.load(untrusted_file)  # Can execute ANY code!

# B506: yaml_load - similar risk
import yaml
config = yaml.load(untrusted_file)  # Can execute Python!

# B307: eval - direct code execution
result = eval(user_input)  # Never do this!
'''

    secure_code = '''
# SECURE: Use safe alternatives
import json
import yaml

# JSON is safe for data interchange
data = json.load(file)

# Use safe_load for YAML
config = yaml.safe_load(file)

# For Python literals, use ast.literal_eval
import ast
result = ast.literal_eval(string_of_python_literal)
# Only allows: strings, numbers, tuples, lists, dicts, bools, None

# If you must use pickle, only with TRUSTED sources
# and consider signing the data
'''

    print("VULNERABLE CODE:")
    print(vulnerable_code)
    print("\nSECURE CODE:")
    print(secure_code)


def demonstrate_weak_crypto() -> None:
    """Show weak cryptography vulnerabilities."""
    print("\n" + "=" * 60)
    print("VULNERABILITY 5: Weak Cryptography")
    print("=" * 60)

    vulnerable_code = '''
# B303: md5 - cryptographically broken
import hashlib
hashed = hashlib.md5(password.encode()).hexdigest()

# B311: random - not cryptographically secure
import random
token = ''.join(random.choices('abc123', k=32))

# B324: hashlib insecure functions
digest = hashlib.new('sha1')  # SHA1 is deprecated
'''

    secure_code = '''
# SECURE: Use strong algorithms
import hashlib
import secrets
from passlib.hash import argon2

# For cryptographic randomness
token = secrets.token_urlsafe(32)
api_key = secrets.token_hex(32)

# For password hashing (NEVER use MD5/SHA)
hashed = argon2.hash(password)
is_valid = argon2.verify(password, hashed)

# For general hashing, use SHA-256+
digest = hashlib.sha256(data).hexdigest()
'''

    print("VULNERABLE CODE:")
    print(vulnerable_code)
    print("\nSECURE CODE:")
    print(secure_code)


def show_bandit_commands() -> None:
    """Display common Bandit commands."""
    print("\n" + "=" * 60)
    print("BANDIT COMMANDS")
    print("=" * 60)

    print("""
Basic scanning:
    bandit -r src/                 # Scan recursively
    bandit -r src/ -ll             # Medium and High only
    bandit -r src/ -lll            # High only

Output formats:
    bandit -r src/ -f json         # JSON output
    bandit -r src/ -f csv          # CSV output
    bandit -r src/ -f html         # HTML report

Specific tests:
    bandit --list                  # List all tests
    bandit -r src/ -t B101,B102    # Run specific tests
    bandit -r src/ -s B101         # Skip specific tests

Configuration:
    bandit -r src/ -c .bandit      # Use config file
    bandit -r src/ -x tests        # Exclude directory
""")


def main() -> None:
    """Run the common vulnerabilities example."""
    print("Example 1: Common Security Vulnerabilities")
    print("=" * 60)

    print("""
This example covers common security vulnerabilities that Bandit detects.

IMPORTANT: The vulnerable code shown is for educational purposes only.
Never use these patterns in real applications!

Categories covered:
- Command Injection (B602, B605, B607)
- Hardcoded Secrets (B105, B106, B107)
- SQL Injection (B608)
- Insecure Deserialization (B301, B506, B307)
- Weak Cryptography (B303, B311, B324)
""")

    demonstrate_command_injection()
    demonstrate_hardcoded_secrets()
    demonstrate_sql_injection()
    demonstrate_insecure_deserialization()
    demonstrate_weak_crypto()
    show_bandit_commands()

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run 'bandit --list' to see all available tests")
    print("  2. Run 'make example-2' to learn about configuration")
    print("  3. Complete Exercise 1 to practice fixing vulnerabilities")


if __name__ == "__main__":
    main()
