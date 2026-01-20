"""Example 2: Bandit Configuration and Baselines

This example demonstrates how to configure Bandit for your project
and use baselines for managing existing issues.
"""

import subprocess
import tempfile
from pathlib import Path


def demonstrate_pyproject_config() -> None:
    """Show pyproject.toml configuration for Bandit."""
    print("\n" + "=" * 60)
    print("STEP 1: Configuration in pyproject.toml")
    print("=" * 60)

    config = '''
# pyproject.toml

[tool.bandit]
# Directories to exclude from scanning
exclude_dirs = [
    "tests",
    ".venv",
    "venv",
    "migrations",
    "node_modules",
]

# Tests to skip globally (use sparingly!)
skips = [
    # Skip assert check (usually OK in non-security code)
    # "B101",
]

# Targets to scan (alternative to command line)
targets = ["src"]

# Recursive scanning
recursive = true

# Severity threshold for reporting
# severity = "medium"  # Only report medium and high

# Per-plugin configuration
[tool.bandit.assert_used]
skips = [
    "*_test.py",
    "test_*.py",
    "**/tests/**",
]
'''
    print(config)


def demonstrate_bandit_yaml_config() -> None:
    """Show .bandit.yaml configuration file."""
    print("\n" + "=" * 60)
    print("STEP 2: Configuration in .bandit.yaml")
    print("=" * 60)

    config = '''
# .bandit.yaml (alternative to pyproject.toml)

# Directories to exclude
exclude_dirs:
  - tests
  - .venv
  - migrations

# Tests to skip
skips:
  - B101  # assert_used
  - B601  # paramiko_calls (if not using paramiko)

# Custom test configurations
assert_used:
  skips:
    - "*_test.py"
    - "test_*.py"

# Profile for web applications
profiles:
  web:
    include:
      - B301  # pickle
      - B302  # marshal
      - B303  # md5
      - B501  # request_with_no_cert_validation
      - B502  # ssl_with_bad_version
      - B506  # yaml_load
      - B608  # hardcoded_sql_expressions
'''
    print(config)


def demonstrate_baseline_workflow() -> None:
    """Show how to use baselines for legacy code."""
    print("\n" + "=" * 60)
    print("STEP 3: Baseline Workflow")
    print("=" * 60)

    print("""
Baselines help manage existing security issues in legacy code.

1. CREATE BASELINE (snapshot current issues):
    bandit -r src/ -f json -o .bandit_baseline.json

2. SCAN WITH BASELINE (only report NEW issues):
    bandit -r src/ -b .bandit_baseline.json

3. UPDATE BASELINE (after fixing issues):
    bandit -r src/ -f json -o .bandit_baseline.json

The baseline file contains:
{
    "results": [
        {
            "filename": "src/legacy.py",
            "test_id": "B105",
            "line_number": 42,
            "issue_text": "Possible hardcoded password"
        }
    ]
}

Benefits:
- CI passes on existing code
- New vulnerabilities still fail CI
- Track security debt over time
- Fix incrementally without blocking development
""")


def demonstrate_inline_ignores() -> None:
    """Show how to use inline ignores correctly."""
    print("\n" + "=" * 60)
    print("STEP 4: Inline Ignores (# nosec)")
    print("=" * 60)

    print("""
Use # nosec to ignore specific findings. Always include justification!

BASIC USAGE:
    # nosec B105 - this is a placeholder for tests
    password = "test_password"

SPECIFIC TEST:
    # nosec B602
    subprocess.call(validated_cmd, shell=True)

MULTIPLE TESTS:
    # nosec B602,B607
    dangerous_call()

WITH EXPLANATION (recommended):
    # nosec B105 - Default value, overridden by env var
    password = os.environ.get("PASSWORD", "changeme")

BLOCK IGNORE (use sparingly):
    # nosec
    legacy_code_block(
        with_multiple,
        arguments,
    )

BEST PRACTICES:
1. Always specify the test ID (B105, not just nosec)
2. Always explain WHY it's safe
3. Review nosec comments during code review
4. Consider if there's a better fix
""")


def demonstrate_severity_filtering() -> None:
    """Show severity and confidence filtering."""
    print("\n" + "=" * 60)
    print("STEP 5: Severity and Confidence Filtering")
    print("=" * 60)

    print("""
Filter findings by severity and confidence:

SEVERITY LEVELS:
    -l   or --level     LOW and above (all findings)
    -ll                 MEDIUM and above
    -lll                HIGH only

CONFIDENCE LEVELS:
    -i LOW              Include LOW confidence
    -i MEDIUM           Include MEDIUM confidence (default)
    -i HIGH             HIGH confidence only

EXAMPLES:
    # Production CI: Only HIGH severity with HIGH confidence
    bandit -r src/ -lll -i HIGH

    # Development: All findings
    bandit -r src/ -l

    # Security review: MEDIUM+ severity
    bandit -r src/ -ll

RECOMMENDED CI CONFIGURATION:
    # Fail on HIGH severity (block merge)
    bandit -r src/ -lll --exit-zero || exit 1

    # Report MEDIUM as warnings
    bandit -r src/ -ll -f json > security-report.json
""")


def demonstrate_custom_profile() -> None:
    """Show how to create custom profiles."""
    print("\n" + "=" * 60)
    print("STEP 6: Custom Profiles")
    print("=" * 60)

    print("""
Custom profiles allow you to define test sets for different contexts.

WEB APPLICATION PROFILE:
    profiles:
      web:
        include:
          - B101  # assert_used
          - B102  # exec_used
          - B301  # pickle
          - B303  # md5
          - B501  # request_with_no_cert_validation
          - B506  # yaml_load
          - B608  # hardcoded_sql_expressions

API SERVICE PROFILE:
    profiles:
      api:
        include:
          - B105  # hardcoded_password_string
          - B106  # hardcoded_password_funcarg
          - B501  # request_with_no_cert_validation
          - B608  # hardcoded_sql_expressions
        exclude:
          - B101  # assert_used (OK in data validation)

USAGE:
    bandit -r src/ --profile web
    bandit -r src/ --profile api
""")


def run_config_demo() -> None:
    """Run a demonstration of Bandit with configuration."""
    print("\n" + "=" * 60)
    print("STEP 7: Live Configuration Demo")
    print("=" * 60)

    # Create sample files
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = Path(tmpdir) / "src"
        src_dir.mkdir()

        # Create sample file with issues
        sample_file = src_dir / "sample.py"
        sample_file.write_text('''
import pickle

def load_data(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)  # B301

password = "secret123"  # B105

def process(data):
    assert data is not None  # B101
    return data
''')

        # Create pyproject.toml
        pyproject = Path(tmpdir) / "pyproject.toml"
        pyproject.write_text('''
[tool.bandit]
exclude_dirs = ["tests"]
skips = ["B101"]  # Skip assert check
''')

        print("Sample code with vulnerabilities:")
        print(sample_file.read_text())

        print("\nRunning Bandit WITHOUT config:")
        result = subprocess.run(
            ["bandit", str(sample_file)],
            capture_output=True,
            text=True,
        )
        print(result.stdout or result.stderr)

        print("\nRunning Bandit WITH config (skips B101):")
        result = subprocess.run(
            ["bandit", "-r", str(src_dir), "-c", str(pyproject)],
            capture_output=True,
            text=True,
        )
        print(result.stdout or result.stderr)


def main() -> None:
    """Run the configuration and baselines example."""
    print("Example 2: Bandit Configuration and Baselines")
    print("=" * 60)

    print("""
This example covers Bandit configuration options:
- pyproject.toml configuration
- .bandit.yaml configuration
- Baseline workflow for legacy code
- Inline ignores with nosec
- Severity and confidence filtering
- Custom profiles
""")

    demonstrate_pyproject_config()
    demonstrate_bandit_yaml_config()
    demonstrate_baseline_workflow()
    demonstrate_inline_ignores()
    demonstrate_severity_filtering()
    demonstrate_custom_profile()
    run_config_demo()

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Create a Bandit configuration for your project")
    print("  2. Run 'make example-3' to learn about CI integration")
    print("  3. Complete Exercise 2 to configure for a web application")


if __name__ == "__main__":
    main()
