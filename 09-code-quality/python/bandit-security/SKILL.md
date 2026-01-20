---
name: scanning-python-security
description: This skill teaches security linting with Bandit to find vulnerabilities in Python code. Use when writing or improving tests.
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

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run specific example (common vulnerabilities)
make example-2  # Run specific example (configuration)
make example-3  # Run specific example (CI integration)
make test       # Run pytest
```

## Key Points
- Security Linting
- Vulnerability Categories
- Severity Levels

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples