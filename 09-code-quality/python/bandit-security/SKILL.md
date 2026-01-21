---
name: scanning-python-security
description: Security linting with Bandit to find vulnerabilities in Python code. Use when writing or improving tests.
---

# Bandit Security

## Quick Start
```python
# Bad - command injection vulnerability
import os
os.system(f"echo {user_input}")  # B605

# Good - use subprocess with list
import subprocess
subprocess.run(["echo", user_input], check=True)
```


## Key Points
- Security Linting
- Vulnerability Categories
- Severity Levels

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples