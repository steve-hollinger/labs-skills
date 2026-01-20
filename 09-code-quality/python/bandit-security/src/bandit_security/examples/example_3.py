"""Example 3: CI/CD Integration

This example demonstrates integrating Bandit into CI/CD pipelines
for automated security scanning.
"""


def demonstrate_github_actions() -> None:
    """Show GitHub Actions integration."""
    print("\n" + "=" * 60)
    print("STEP 1: GitHub Actions Integration")
    print("=" * 60)

    basic_workflow = '''
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Bandit
        run: pip install bandit

      - name: Run Bandit
        run: bandit -r src/ -f json -o bandit-report.json

      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: bandit-report
          path: bandit-report.json
'''
    print("Basic workflow:")
    print(basic_workflow)

    advanced_workflow = '''
# Advanced workflow with baseline and severity gate
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: uv sync --all-extras

      # Fail on HIGH severity issues
      - name: Security Gate (HIGH)
        run: uv run bandit -r src/ -lll
        continue-on-error: false

      # Report MEDIUM issues (don't fail)
      - name: Security Audit (MEDIUM+)
        run: |
          uv run bandit -r src/ -ll -f json -o report.json
          echo "::notice::Security findings saved to report.json"
        continue-on-error: true

      # Use baseline for existing issues
      - name: Check New Issues
        run: uv run bandit -r src/ -b .bandit_baseline.json -ll
'''
    print("\nAdvanced workflow:")
    print(advanced_workflow)


def demonstrate_gitlab_ci() -> None:
    """Show GitLab CI integration."""
    print("\n" + "=" * 60)
    print("STEP 2: GitLab CI Integration")
    print("=" * 60)

    gitlab_ci = '''
# .gitlab-ci.yml
security:
  stage: test
  image: python:3.11
  script:
    - pip install bandit
    - bandit -r src/ -f json -o gl-sast-report.json
  artifacts:
    reports:
      sast: gl-sast-report.json
    paths:
      - gl-sast-report.json
    when: always

# With baseline
security:baseline:
  stage: test
  image: python:3.11
  script:
    - pip install bandit
    - bandit -r src/ -b .bandit_baseline.json -ll
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
'''
    print(gitlab_ci)


def demonstrate_precommit_hook() -> None:
    """Show pre-commit hook integration."""
    print("\n" + "=" * 60)
    print("STEP 3: Pre-commit Hook")
    print("=" * 60)

    precommit = '''
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.7
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml", "-r", "src/"]
        exclude: tests/

# Or with local hook for custom config
repos:
  - repo: local
    hooks:
      - id: bandit
        name: Security Scan
        entry: uv run bandit
        args: ["-r", "src/", "-ll"]
        language: system
        types: [python]
        pass_filenames: false

# Minimal (only HIGH severity blocks commit)
repos:
  - repo: local
    hooks:
      - id: bandit-critical
        name: Critical Security Check
        entry: uv run bandit
        args: ["-r", "src/", "-lll"]
        language: system
        types: [python]
        pass_filenames: false
'''
    print(precommit)


def demonstrate_sarif_output() -> None:
    """Show SARIF output for GitHub Security tab."""
    print("\n" + "=" * 60)
    print("STEP 4: SARIF Output for Security Tab")
    print("=" * 60)

    sarif_workflow = '''
# GitHub Code Scanning with Bandit
name: Code Scanning

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: "0 0 * * *"  # Daily

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      contents: read

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Bandit with SARIF
        run: pip install bandit bandit-sarif-formatter

      - name: Run Bandit
        run: |
          bandit -r src/ -f sarif -o results.sarif

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
          category: bandit
'''
    print(sarif_workflow)

    print("""
This enables:
- Security findings in GitHub Security tab
- Alerts on new vulnerabilities
- Integration with GitHub Security Overview
- PR annotations for security issues
""")


def demonstrate_multiple_tools() -> None:
    """Show integration with other security tools."""
    print("\n" + "=" * 60)
    print("STEP 5: Combining Security Tools")
    print("=" * 60)

    multi_tool = '''
# Comprehensive security workflow
name: Security

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v4

      - name: Install tools
        run: |
          uv sync --all-extras
          uv add --dev safety pip-audit

      # 1. Bandit - Code security
      - name: Bandit (Code Security)
        run: uv run bandit -r src/ -ll

      # 2. Safety - Dependency vulnerabilities
      - name: Safety (Dependencies)
        run: uv run safety check

      # 3. pip-audit - Another dep scanner
      - name: pip-audit (Dependencies)
        run: uv run pip-audit

      # 4. Ruff with security rules
      - name: Ruff Security Rules
        run: uv run ruff check --select S src/

      # 5. Generate combined report
      - name: Generate Report
        run: |
          echo "# Security Report" > security-report.md
          echo "## Bandit Findings" >> security-report.md
          uv run bandit -r src/ -f json | jq '.results | length' >> security-report.md
'''
    print(multi_tool)


def demonstrate_policy_enforcement() -> None:
    """Show security policy enforcement."""
    print("\n" + "=" * 60)
    print("STEP 6: Security Policy Enforcement")
    print("=" * 60)

    print("""
Define and enforce security policies in CI:

POLICY LEVELS:

1. CRITICAL (blocks merge immediately):
   - HIGH severity + HIGH confidence
   - Hardcoded secrets (B105, B106, B107)
   - SQL injection (B608)
   - Command injection (B602, B605)

2. HIGH (must fix before release):
   - HIGH severity
   - Pickle/YAML unsafe loading (B301, B506)
   - Weak cryptography (B303, B311)

3. MEDIUM (track in baseline):
   - MEDIUM severity
   - Use of assert (B101)
   - Binding to all interfaces (B104)

4. LOW (informational):
   - LOW severity findings
   - Review periodically

IMPLEMENTATION:
""")

    policy_script = '''
#!/usr/bin/env python3
"""Security policy enforcement script."""
import json
import subprocess
import sys

# Define policy
CRITICAL_TESTS = {"B105", "B106", "B107", "B602", "B605", "B608"}
BLOCK_SEVERITY = {"HIGH"}
BLOCK_CONFIDENCE = {"HIGH", "MEDIUM"}

def check_security():
    result = subprocess.run(
        ["bandit", "-r", "src/", "-f", "json"],
        capture_output=True,
        text=True,
    )

    findings = json.loads(result.stdout)
    critical_issues = []

    for issue in findings.get("results", []):
        test_id = issue["test_id"]
        severity = issue["issue_severity"]
        confidence = issue["issue_confidence"]

        # Check against policy
        if test_id in CRITICAL_TESTS:
            critical_issues.append(issue)
        elif severity in BLOCK_SEVERITY and confidence in BLOCK_CONFIDENCE:
            critical_issues.append(issue)

    if critical_issues:
        print(f"BLOCKED: {len(critical_issues)} critical security issues")
        for issue in critical_issues:
            print(f"  {issue['test_id']}: {issue['issue_text']}")
            print(f"    {issue['filename']}:{issue['line_number']}")
        sys.exit(1)

    print("Security policy check passed")

if __name__ == "__main__":
    check_security()
'''
    print(policy_script)


def main() -> None:
    """Run the CI integration example."""
    print("Example 3: CI/CD Integration")
    print("=" * 60)

    print("""
This example covers integrating Bandit into CI/CD pipelines:
- GitHub Actions workflows
- GitLab CI configuration
- Pre-commit hooks
- SARIF output for GitHub Security
- Combining multiple security tools
- Security policy enforcement
""")

    demonstrate_github_actions()
    demonstrate_gitlab_ci()
    demonstrate_precommit_hook()
    demonstrate_sarif_output()
    demonstrate_multiple_tools()
    demonstrate_policy_enforcement()

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Set up Bandit in your project's CI pipeline")
    print("  2. Create a security baseline for your project")
    print("  3. Complete Exercise 3 to implement a security gate")


if __name__ == "__main__":
    main()
