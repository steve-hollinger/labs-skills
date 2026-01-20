# Core Concepts

## Overview

Bandit is a security-focused static analysis tool for Python. It scans your code for common security issues and potential vulnerabilities before they reach production.

## Concept 1: Static Security Analysis

### What It Is

Static analysis examines code without running it, looking for patterns that indicate security vulnerabilities.

### Why It Matters

- Catches issues during development, not after deployment
- Automated, consistent security checks
- Integrates with CI/CD for continuous security
- Educates developers about secure coding

### How It Works

```bash
# Basic scan of a directory
bandit -r src/

# Output shows:
# - File and line number
# - Issue severity (LOW/MEDIUM/HIGH)
# - Confidence level (LOW/MEDIUM/HIGH)
# - Description and CWE reference
```

## Concept 2: Vulnerability Categories

### What They Are

Bandit tests are grouped by the type of vulnerability they detect.

### Why They Matter

- Understanding categories helps prioritize fixes
- Different projects have different risk profiles
- Enables targeted scanning for specific risks

### Categories

| Category | Tests | Description |
|----------|-------|-------------|
| Injection | B102, B307, B601-B608 | Code/command injection |
| Crypto | B303-B305, B311, B324 | Weak cryptography |
| Secrets | B105-B107 | Hardcoded secrets |
| Network | B104, B501-B509 | Network security |
| Dangerous | B101, B102, B307 | Dangerous function calls |
| Deserialize | B301-B303 | Insecure deserialization |

### How It Works

```bash
# Run specific test categories
bandit -r src/ -t B101,B102,B103  # Specific tests
bandit -r src/ --profile django   # Django-specific profile

# Skip certain tests
bandit -r src/ -s B101  # Skip assert check
```

## Concept 3: Severity and Confidence

### What They Are

Each finding has two ratings:
- **Severity**: How dangerous the issue is (LOW/MEDIUM/HIGH)
- **Confidence**: How certain Bandit is about the finding (LOW/MEDIUM/HIGH)

### Why They Matter

- Prioritize fixes by severity
- Filter false positives by confidence
- Set appropriate CI gates

### How It Works

```bash
# Filter by severity
bandit -r src/ -l      # LOW and above (all)
bandit -r src/ -ll     # MEDIUM and above
bandit -r src/ -lll    # HIGH only

# In reports, look for:
# >> Issue: [B105:hardcoded_password_string]
#    Severity: Medium   Confidence: Medium
```

## Concept 4: Baselines

### What They Are

A baseline is a snapshot of existing issues that you've reviewed and accepted. New scans report only new issues.

### Why They Matter

- Adopt Bandit in legacy projects without overwhelming results
- Track security improvements over time
- Fail CI only on new vulnerabilities

### How It Works

```bash
# Create baseline
bandit -r src/ -f json -o .bandit_baseline.json

# Scan with baseline (only reports new issues)
bandit -r src/ -b .bandit_baseline.json

# Update baseline after fixing issues
bandit -r src/ -f json -o .bandit_baseline.json
```

Baseline workflow:
1. Create initial baseline
2. Review and fix HIGH severity issues
3. Update baseline with remaining accepted issues
4. CI uses baseline to catch new issues

## Concept 5: Inline Ignores

### What They Are

Comments that tell Bandit to skip specific lines or blocks.

### Why They Matter

- Handle false positives
- Document security decisions
- Keep CI green without hiding real issues

### How It Works

```python
# Skip one line with nosec
password = "not-a-real-password"  # nosec B105 - test data

# Skip with specific test
eval(trusted_input)  # nosec B307

# Skip entire block
# nosec
dangerous_function(
    arg1,
    arg2,
)

# Best practice: always explain why
os.system(safe_command)  # nosec B605 - validated input
```

## Concept 6: CI Integration

### What It Is

Running Bandit automatically in your CI/CD pipeline to catch security issues before merge.

### Why It Matters

- Security gate for all code changes
- Consistent enforcement across team
- Catches issues early in development

### How It Works

```yaml
# GitHub Actions example
- name: Security Scan
  run: |
    pip install bandit
    bandit -r src/ -f json -o bandit-report.json --exit-zero
    # Parse report and fail on HIGH severity

# With baseline
- name: Security Scan
  run: |
    bandit -r src/ -b .bandit_baseline.json -ll
    # Fails if new MEDIUM+ issues found
```

## Summary

Key takeaways:

1. **Static Analysis**: Catch security issues without running code
2. **Categories**: Different tests for different vulnerability types
3. **Severity/Confidence**: Prioritize findings by risk
4. **Baselines**: Manage legacy code and track improvements
5. **Inline Ignores**: Handle false positives with documentation
6. **CI Integration**: Automate security checks in your pipeline
