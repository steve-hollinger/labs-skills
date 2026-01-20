# CLAUDE.md - Bandit Security

This skill teaches security linting with Bandit to find vulnerabilities in Python code.

## Key Concepts

- **Security Linting**: Static analysis to find potential security issues
- **Vulnerability Categories**: Code injection, crypto issues, hardcoded secrets
- **Severity Levels**: HIGH/MEDIUM/LOW for impact and confidence
- **Baselines**: Track existing issues, only fail on new ones
- **CI Integration**: Block PRs with security issues

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run specific example (common vulnerabilities)
make example-2  # Run specific example (configuration)
make example-3  # Run specific example (CI integration)
make test       # Run pytest
make security   # Run bandit scan
make baseline   # Create/update baseline
make clean      # Remove build artifacts
```

## Project Structure

```
bandit-security/
├── src/bandit_security/
│   ├── __init__.py
│   └── examples/
│       ├── example_1.py    # Common vulnerabilities
│       ├── example_2.py    # Configuration
│       └── example_3.py    # CI integration
├── exercises/
│   ├── exercise_1.py       # Find and fix vulns
│   ├── exercise_2.py       # Configure for web app
│   ├── exercise_3.py       # CI security gate
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Avoiding Command Injection
```python
# Bad - command injection vulnerability
import os
os.system(f"echo {user_input}")  # B605

# Good - use subprocess with list
import subprocess
subprocess.run(["echo", user_input], check=True)
```

### Pattern 2: Avoiding Hardcoded Secrets
```python
# Bad - hardcoded password
password = "secret123"  # B105

# Good - use environment variables
import os
password = os.environ.get("PASSWORD")
```

### Pattern 3: Safe YAML Loading
```python
# Bad - arbitrary code execution
import yaml
data = yaml.load(file)  # B506

# Good - safe loading
data = yaml.safe_load(file)
```

## Common Mistakes

1. **Disabling all warnings with # nosec**
   - Why it happens: Quick fix for CI
   - How to fix it: Use specific test codes, add justification

2. **Not using baselines for legacy code**
   - Why it happens: Too many existing issues
   - How to fix it: Create baseline, fix incrementally

3. **Ignoring MEDIUM severity**
   - Why it happens: Only looking at HIGH
   - How to fix it: Review MEDIUM with HIGH confidence

4. **Not scanning dependencies**
   - Why it happens: Only scanning own code
   - How to fix it: Use safety or pip-audit for dependencies

## When Users Ask About...

### "How do I get started?"
Point them to:
```bash
uv run bandit -r src/       # Basic scan
uv run bandit -r src/ -ll   # Medium+ only
```

### "What does B101 mean?"
B101 is "use of assert detected". Asserts are removed in optimized Python (`-O` flag), so they shouldn't be used for security checks. However, they're fine in tests.

### "How do I ignore a false positive?"
```python
# Inline ignore with justification
eval(trusted_code)  # nosec B307 - trusted input only

# Or in pyproject.toml
[tool.bandit]
skips = ["B101"]
```

### "How do I fix a command injection issue?"
Replace string interpolation with subprocess:
```python
# Instead of
os.system(f"cmd {user_input}")

# Use
subprocess.run(["cmd", user_input], check=True)
```

### "Should I use Bandit with Ruff?"
Yes! They complement each other:
- Ruff: Style, formatting, some security (S rules)
- Bandit: Deep security analysis
- Both: Use together for comprehensive coverage

## Testing Notes

- Tests verify Bandit catches expected vulnerabilities
- Run specific tests: `pytest -k "test_name"`
- Check coverage: `make coverage`
- Vulnerable example code is intentionally insecure for teaching

## Dependencies

Key dependencies in pyproject.toml:
- bandit: The security linter
- pytest: Testing framework
- ruff: Style linting (complementary)
- mypy: Type checking
