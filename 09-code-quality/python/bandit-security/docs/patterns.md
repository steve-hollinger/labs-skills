# Common Patterns

## Overview

This document covers common patterns and best practices for using Bandit and writing secure Python code.

## Pattern 1: Command Execution Safety

### When to Use

When your code needs to execute system commands.

### Vulnerable Code

```python
import os
import subprocess

# B602: subprocess_popen_with_shell_equals_true
subprocess.Popen(f"echo {user_input}", shell=True)

# B605: start_process_with_partial_path
os.system(f"rm {filename}")

# B607: start_process_with_partial_path
subprocess.call(["bash", "-c", user_command])
```

### Secure Implementation

```python
import subprocess
import shlex

# Use list arguments instead of shell=True
subprocess.run(["echo", user_input], check=True)

# For complex commands, use shlex.split
command = shlex.split("ls -la /path/to/dir")
subprocess.run(command, check=True)

# If you must use shell, validate input strictly
allowed_files = {"report.txt", "data.csv"}
if filename in allowed_files:
    subprocess.run(["rm", filename], check=True)
```

### Pitfalls to Avoid

- Never pass user input directly to shell commands
- Always use absolute paths when possible
- Validate and whitelist allowed inputs

## Pattern 2: Secure Secrets Management

### When to Use

Whenever your code needs passwords, API keys, or tokens.

### Vulnerable Code

```python
# B105: hardcoded_password_string
password = "mysecretpassword"

# B106: hardcoded_password_funcarg
connect(password="secretpass123")

# B107: hardcoded_password_default
def login(user, password="admin123"):
    ...
```

### Secure Implementation

```python
import os
from functools import lru_cache

# Use environment variables
password = os.environ.get("DB_PASSWORD")
if not password:
    raise ValueError("DB_PASSWORD environment variable required")

# Use secrets management
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_password: str
    api_key: str

    class Config:
        env_file = ".env"

settings = Settings()

# For AWS, use secrets manager
import boto3

def get_secret(name: str) -> str:
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=name)
    return response["SecretString"]
```

### Pitfalls to Avoid

- Never commit secrets to version control
- Don't log secrets
- Use `.env` files for local development only

## Pattern 3: Safe Deserialization

### When to Use

When loading data from files or network sources.

### Vulnerable Code

```python
import pickle
import yaml

# B301: pickle
data = pickle.load(file)  # Arbitrary code execution!

# B506: yaml_load
data = yaml.load(file)  # Can execute arbitrary Python
```

### Secure Implementation

```python
import json
import yaml

# Use JSON for data interchange
data = json.load(file)

# Use safe_load for YAML
data = yaml.safe_load(file)

# If you must use pickle, only with trusted sources
import pickle
import hmac

def load_verified_pickle(file, key: bytes):
    """Load pickle only if signature matches."""
    data = file.read()
    signature = file.read(32)
    expected = hmac.digest(key, data, "sha256")
    if not hmac.compare_digest(signature, expected):
        raise ValueError("Invalid signature")
    return pickle.loads(data)
```

### Pitfalls to Avoid

- Never unpickle data from untrusted sources
- Prefer JSON for data exchange
- If using YAML, always use safe_load

## Pattern 4: SQL Injection Prevention

### When to Use

Whenever working with SQL databases.

### Vulnerable Code

```python
# B608: hardcoded_sql_expressions
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# String formatting is also vulnerable
query = "SELECT * FROM users WHERE name = '%s'" % username
cursor.execute(query)
```

### Secure Implementation

```python
# Use parameterized queries
cursor.execute(
    "SELECT * FROM users WHERE id = %s",
    (user_id,)
)

# With SQLAlchemy
from sqlalchemy import select, text

# ORM (safest)
users = session.query(User).filter(User.id == user_id).all()

# Raw SQL with bound parameters
result = session.execute(
    text("SELECT * FROM users WHERE id = :id"),
    {"id": user_id}
)

# With asyncpg
await conn.fetch(
    "SELECT * FROM users WHERE id = $1",
    user_id
)
```

### Pitfalls to Avoid

- Never use string formatting for SQL
- Always use parameterized queries
- Use ORM when possible

## Pattern 5: Cryptography Best Practices

### When to Use

When implementing authentication, encryption, or hashing.

### Vulnerable Code

```python
import hashlib
import random

# B303: md5
hashed = hashlib.md5(password.encode()).hexdigest()

# B311: random - not cryptographically secure
token = ''.join(random.choices('abc123', k=32))

# B324: hashlib_new_insecure_functions
digest = hashlib.new('sha1')
```

### Secure Implementation

```python
import hashlib
import secrets
from passlib.hash import argon2

# Use secrets for cryptographic randomness
token = secrets.token_urlsafe(32)

# Use strong hashing for passwords
hashed = argon2.hash(password)
verified = argon2.verify(password, hashed)

# Use SHA-256 or better for general hashing
digest = hashlib.sha256(data).hexdigest()

# For HMAC
import hmac
signature = hmac.new(key, message, "sha256").hexdigest()
```

### Pitfalls to Avoid

- Never use MD5 or SHA1 for security purposes
- Never use `random` for security-sensitive values
- Always use proper password hashing (argon2, bcrypt)

## Pattern 6: Network Security

### When to Use

When making HTTP requests or accepting network connections.

### Vulnerable Code

```python
import ssl
import requests

# B104: bind to all interfaces
socket.bind(("0.0.0.0", 8080))

# B501: request without certificate verification
requests.get(url, verify=False)

# B503: ssl_with_no_version
ssl.wrap_socket(sock)  # Uses outdated defaults
```

### Secure Implementation

```python
import ssl
import socket
import requests

# Bind to specific interface in production
socket.bind(("127.0.0.1", 8080))  # Localhost only
# or use environment config
host = os.environ.get("BIND_HOST", "127.0.0.1")
socket.bind((host, 8080))

# Always verify SSL certificates
response = requests.get(url)  # verify=True is default

# Use modern SSL context
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.minimum_version = ssl.TLSVersion.TLSv1_2

# For self-signed certs in dev, use custom CA
response = requests.get(url, verify="/path/to/ca-bundle.crt")
```

### Pitfalls to Avoid

- Never disable SSL verification in production
- Don't bind to 0.0.0.0 unless necessary
- Always use TLS 1.2 or higher

## Anti-Patterns

### Anti-Pattern 1: Blanket nosec

```python
# Bad - hiding all issues
import subprocess
subprocess.call(user_input, shell=True)  # nosec
```

### Better Approach

```python
# Good - specific ignore with justification
# nosec B602 - input validated against whitelist in validate_command()
subprocess.call(validated_command, shell=True)
```

### Anti-Pattern 2: Ignoring in CI

```yaml
# Bad - all security issues ignored
- run: bandit -r src/ --exit-zero
```

### Better Approach

```yaml
# Good - fail on HIGH, track others
- run: bandit -r src/ -lll  # Fail on HIGH
- run: bandit -r src/ -b .baseline.json  # Track new issues
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| User input in commands | Command Execution Safety |
| Credentials in code | Secrets Management |
| Loading external data | Safe Deserialization |
| Database queries | SQL Injection Prevention |
| Auth/Encryption | Cryptography Best Practices |
| Network services | Network Security |
