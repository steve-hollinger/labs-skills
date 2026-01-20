"""Exercise 3: Set Up a Security Gate in CI

Goal: Create a GitHub Actions workflow that enforces security policies.

Instructions:
1. Create a .github/workflows/security.yml file
2. Configure Bandit to fail on HIGH severity issues
3. Report MEDIUM issues without failing the build
4. Upload security reports as artifacts
5. Add SARIF output for GitHub Security tab

Requirements:
- Block merges on HIGH severity + HIGH confidence
- Report MEDIUM+ severity in PR comments
- Use baseline for existing issues
- Generate SARIF report for GitHub Security

Expected Files:
    .github/
    └── workflows/
        └── security.yml

Hints:
- Use 'bandit -lll' for HIGH only
- Use 'bandit -ll' for MEDIUM and above
- Use 'bandit -f sarif' for GitHub Security tab
- Use 'continue-on-error' for non-blocking steps
"""

# GitHub Actions workflow template
WORKFLOW_TEMPLATE = '''
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:

jobs:
  security:
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

      # TODO: Add steps to:
      # 1. Install Bandit
      # 2. Run security gate (HIGH severity - blocks merge)
      # 3. Run security audit (MEDIUM+ - reports only)
      # 4. Generate SARIF report
      # 5. Upload artifacts
'''

# Expected completed workflow
EXPECTED_WORKFLOW = '''
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:

jobs:
  security:
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

      - name: Install Bandit
        run: pip install bandit bandit-sarif-formatter

      # GATE: Block on HIGH severity
      - name: Security Gate (Critical)
        run: bandit -r src/ -lll -f json -o critical.json

      # AUDIT: Report MEDIUM+ (don't fail)
      - name: Security Audit (All)
        run: bandit -r src/ -ll -f json -o audit.json
        continue-on-error: true

      # SARIF for GitHub Security tab
      - name: Generate SARIF
        run: bandit -r src/ -f sarif -o results.sarif
        continue-on-error: true

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
          category: bandit

      - name: Upload Reports
        uses: actions/upload-artifact@v4
        with:
          name: security-reports
          path: |
            critical.json
            audit.json
            results.sarif
'''

# Policy enforcement script
POLICY_SCRIPT = '''
#!/usr/bin/env python3
"""Security policy enforcement for CI."""
import json
import subprocess
import sys
from pathlib import Path

# Policy: Block on these issues
CRITICAL_TESTS = {
    "B105",  # hardcoded_password_string
    "B106",  # hardcoded_password_funcarg
    "B107",  # hardcoded_password_default
    "B602",  # subprocess_popen_with_shell_equals_true
    "B605",  # start_process_with_a_shell
    "B608",  # hardcoded_sql_expressions
    "B301",  # pickle
}

def main():
    result = subprocess.run(
        ["bandit", "-r", "src/", "-f", "json"],
        capture_output=True,
        text=True,
    )

    report = json.loads(result.stdout)
    critical = []

    for issue in report.get("results", []):
        if issue["test_id"] in CRITICAL_TESTS:
            critical.append(issue)
        elif (
            issue["issue_severity"] == "HIGH"
            and issue["issue_confidence"] == "HIGH"
        ):
            critical.append(issue)

    if critical:
        print(f"BLOCKED: {len(critical)} critical security issues")
        for issue in critical:
            print(f"  {issue['test_id']}: {issue['issue_text']}")
            print(f"    {issue['filename']}:{issue['line_number']}")
        sys.exit(1)

    print("Security policy check passed")

if __name__ == "__main__":
    main()
'''


def verify_exercise() -> bool:
    """Verify the exercise was completed correctly."""
    from pathlib import Path

    workflow = Path(".github/workflows/security.yml")

    checks = [
        ("Workflow file exists", workflow.exists()),
    ]

    if workflow.exists():
        content = workflow.read_text()
        checks.append(("Uses bandit", "bandit" in content))
        checks.append(("Has security gate", "lll" in content or "HIGH" in content.upper()))
        checks.append(("Has SARIF output", "sarif" in content.lower()))
        checks.append(("Uploads artifacts", "upload-artifact" in content))

    print("\nExercise Verification:")
    print("-" * 40)

    all_passed = True
    for name, passed in checks:
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False

    print("-" * 40)
    if all_passed:
        print("Exercise 3 completed successfully!")
    else:
        print("Exercise 3 not yet complete. See instructions above.")

    return all_passed


if __name__ == "__main__":
    print(__doc__)
    print("\nWorkflow template to complete:")
    print(WORKFLOW_TEMPLATE)
    print("\n\nExpected completed workflow:")
    print(EXPECTED_WORKFLOW)
