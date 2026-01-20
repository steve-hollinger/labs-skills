# Bandit Security

Learn security linting with Bandit, a tool designed to find common security issues in Python code. Bandit scans your code for potential vulnerabilities and reports them with severity levels.

## Learning Objectives

After completing this skill, you will be able to:
- Identify common security vulnerabilities in Python code
- Configure Bandit with baselines and ignore patterns
- Integrate Bandit into CI/CD pipelines
- Fix security issues with secure alternatives
- Use Bandit with other security tools

## Prerequisites

- Python 3.11+
- UV package manager
- Basic Python development experience

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Concepts

### Running Bandit

Scan your code for security issues:

```bash
# Basic scan
bandit -r src/

# With severity filter
bandit -r src/ -ll  # Medium and High only

# JSON output for CI
bandit -r src/ -f json -o report.json

# Specific tests
bandit -r src/ -t B101,B102
```

### Common Vulnerabilities

Bandit detects issues like:
- **B101**: Use of assert (removed in optimized mode)
- **B102**: exec() usage
- **B103**: set_bad_file_permissions
- **B104**: Binding to all interfaces
- **B105-B107**: Hardcoded passwords
- **B301-B303**: Pickle usage (deserialization attacks)
- **B501-B503**: SSL/TLS issues

### Configuration

Configure Bandit in pyproject.toml:

```toml
[tool.bandit]
exclude_dirs = ["tests", "venv"]
skips = ["B101"]  # Skip assert warnings in app code

[tool.bandit.assert_used]
skips = ["*_test.py", "*test_*.py"]
```

## Examples

### Example 1: Common Vulnerabilities

Learn to identify and understand security issues.

```bash
make example-1
```

### Example 2: Configuration and Baselines

Set up Bandit for your project.

```bash
make example-2
```

### Example 3: CI Integration

Integrate Bandit into your pipeline.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Find and fix vulnerabilities in sample code
2. **Exercise 2**: Configure Bandit for a web application
3. **Exercise 3**: Set up a security gate in CI

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Severity Levels

Bandit reports issues with severity and confidence:

| Level | Meaning |
|-------|---------|
| HIGH | Critical security issue, fix immediately |
| MEDIUM | Moderate risk, should be addressed |
| LOW | Minor issue, consider fixing |

Confidence levels (HIGH/MEDIUM/LOW) indicate how certain Bandit is about the finding.

## Common Mistakes

### Mistake 1: Ignoring all warnings

```python
# Wrong - hiding real issues
# nosec B101

# Correct - only ignore with justification
# nosec B101 - Using assert for type narrowing, not security
```

### Mistake 2: Not using baselines for legacy code

```bash
# Wrong - too many false positives
bandit -r legacy_code/

# Correct - baseline existing issues, catch new ones
bandit -r src/ -b .bandit_baseline.json
```

## Further Reading

- [Bandit Documentation](https://bandit.readthedocs.io/)
- [OWASP Python Security](https://owasp.org/www-project-python-security/)
- [CWE Database](https://cwe.mitre.org/)
- Related skills in this repository:
  - [Ruff Linting](../ruff-linting/)
  - [Security Best Practices](../../../07-security/)
