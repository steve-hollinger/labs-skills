"""Example 3: Advanced Pattern Detection.

This example demonstrates advanced secret detection:
- Custom pattern definitions
- Entropy-based detection
- Comprehensive scanning
- Building a secrets scanner

Run with: make example-3
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from token_masking import (
    SECRET_PATTERNS,
    SecretDetector,
    TokenMasker,
    calculate_entropy,
    looks_like_secret,
)


def demo_entropy_analysis() -> None:
    """Demonstrate entropy-based secret detection."""
    print("\n1. Entropy Analysis")
    print("-" * 40)

    test_values = [
        ("password", "Low entropy - common word"),
        ("Password123!", "Medium entropy - simple password"),
        ("aB3$kL9#mN2@pQ5", "High entropy - random password"),
        ("AKIAIOSFODNN7EXAMPLE", "AWS Access Key"),
        ("wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", "AWS Secret Key"),
        ("hello world", "Normal text"),
        ("aaaaaaaaaaaaaaaa", "Repeated characters"),
    ]

    print(f"{'Value':<45} {'Entropy':>8} {'Looks like secret?':>20}")
    print("-" * 75)

    for value, description in test_values:
        entropy = calculate_entropy(value)
        is_secret = looks_like_secret(value)
        display_value = value[:42] + "..." if len(value) > 45 else value
        print(f"{display_value:<45} {entropy:>8.2f} {str(is_secret):>20}")

    print(f"\nNote: Values with entropy > 3.5 and length > 8 are flagged as potential secrets")


def demo_custom_patterns() -> None:
    """Demonstrate custom pattern definitions."""
    print("\n2. Custom Pattern Definitions")
    print("-" * 40)

    # Define custom patterns for your organization
    custom_patterns = {
        # Internal API keys
        "internal_api_key": r"int_[a-f0-9]{32}",
        "internal_secret": r"sec_[a-f0-9]{64}",

        # Service tokens
        "service_token": r"svc_[A-Za-z0-9]{24}",

        # Database IDs that might be sensitive
        "sensitive_id": r"usr_[0-9]{8}",

        # Custom JWT with specific issuer
        "custom_jwt": r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]*\"iss\":\"mycompany\"[A-Za-z0-9_-]*\.[A-Za-z0-9_-]+",
    }

    detector = SecretDetector(patterns=custom_patterns, use_entropy=False)

    test_text = """
    Configuration:
    - Internal API Key: int_abc123def456abc123def456abc123de
    - Service Token: svc_abcdefghijklmnopqrstuvwx
    - User ID: usr_12345678
    - Public ID: pub_12345678 (not matched)
    """

    print("Test text:")
    print(test_text)

    print("\nDetected secrets:")
    for match in detector.detect(test_text):
        print(f"  - Type: {match.secret_type}")
        print(f"    Value: {match.value}")
        print(f"    Masked: {match.masked}")
        print()


def demo_comprehensive_scanner() -> None:
    """Demonstrate a comprehensive secrets scanner."""
    print("\n3. Comprehensive Secrets Scanner")
    print("-" * 40)

    @dataclass
    class ScanResult:
        """Result from scanning a file or text."""
        source: str
        line_number: int
        secret_type: str
        masked_value: str
        severity: str

    class SecretsScanner:
        """Comprehensive secrets scanner."""

        def __init__(self):
            self.detector = SecretDetector(use_entropy=True)
            self.severity_map = {
                "aws_access_key": "CRITICAL",
                "aws_secret_key": "CRITICAL",
                "github_pat": "HIGH",
                "stripe_secret": "CRITICAL",
                "postgres_url": "HIGH",
                "generic_secret": "MEDIUM",
                "high_entropy": "LOW",
            }

        def scan_text(self, text: str, source: str = "input") -> list[ScanResult]:
            """Scan text for secrets."""
            results = []
            lines = text.split("\n")

            for line_num, line in enumerate(lines, 1):
                matches = self.detector.detect(line)
                for match in matches:
                    severity = self.severity_map.get(match.secret_type, "MEDIUM")
                    results.append(ScanResult(
                        source=source,
                        line_number=line_num,
                        secret_type=match.secret_type,
                        masked_value=match.masked,
                        severity=severity,
                    ))

            return results

        def scan_config(self, config: dict, path: str = "") -> list[ScanResult]:
            """Recursively scan a configuration dictionary."""
            results = []

            for key, value in config.items():
                current_path = f"{path}.{key}" if path else key

                if isinstance(value, dict):
                    results.extend(self.scan_config(value, current_path))
                elif isinstance(value, str):
                    matches = self.detector.detect(value)
                    for match in matches:
                        severity = self.severity_map.get(match.secret_type, "MEDIUM")
                        results.append(ScanResult(
                            source=current_path,
                            line_number=0,
                            secret_type=match.secret_type,
                            masked_value=match.masked,
                            severity=severity,
                        ))

            return results

    # Demo the scanner
    scanner = SecretsScanner()

    # Scan code snippet
    code_snippet = '''
    import boto3

    # Configuration
    AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
    AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

    def connect():
        db_url = "postgres://admin:secretpass@db.example.com/mydb"
        return create_connection(db_url)

    # GitHub integration
    GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    '''

    print("Scanning code snippet:")
    print("-" * 40)
    results = scanner.scan_text(code_snippet, "example.py")

    for result in sorted(results, key=lambda r: (r.severity != "CRITICAL", r.line_number)):
        print(f"[{result.severity}] Line {result.line_number}: {result.secret_type}")
        print(f"         Masked: {result.masked_value}")

    # Scan configuration
    print("\n" + "-" * 40)
    print("Scanning configuration:")
    print("-" * 40)

    config = {
        "database": {
            "url": "postgres://user:pass123@localhost/db",
        },
        "services": {
            "stripe": {
                "api_key": "sk_example_FAKE24CHARSTRING12",
            },
            "aws": {
                "access_key": "AKIAIOSFODNN7EXAMPLE",
            },
        },
    }

    results = scanner.scan_config(config)
    for result in results:
        print(f"[{result.severity}] {result.source}: {result.secret_type}")
        print(f"         Masked: {result.masked_value}")


def demo_pattern_testing() -> None:
    """Demonstrate testing patterns for accuracy."""
    print("\n4. Pattern Testing")
    print("-" * 40)

    # Test patterns against known values
    test_cases = [
        # (pattern_name, test_value, should_match)
        ("aws_access_key", "AKIAIOSFODNN7EXAMPLE", True),
        ("aws_access_key", "AKIA1234567890123456", True),
        ("aws_access_key", "NOTANAWSKEY123456789", False),
        ("github_pat", "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", True),
        ("github_pat", "ghp_short", False),
        ("stripe_secret", "sk_example_FAKE24CHARSTRING12", True),
        ("stripe_secret", "sk_example_FAKE24CHARSTRING12", False),  # Test key, not live
        ("jwt", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U", True),
        ("email", "user@example.com", True),
        ("email", "not-an-email", False),
    ]

    print(f"{'Pattern':<20} {'Test Value':<50} {'Expected':>8} {'Actual':>8} {'Pass':>6}")
    print("-" * 95)

    passed = 0
    failed = 0

    for pattern_name, test_value, should_match in test_cases:
        if pattern_name not in SECRET_PATTERNS:
            print(f"Pattern '{pattern_name}' not found")
            continue

        pattern = re.compile(SECRET_PATTERNS[pattern_name])
        matches = bool(pattern.search(test_value))

        is_pass = matches == should_match
        if is_pass:
            passed += 1
        else:
            failed += 1

        display_value = test_value[:47] + "..." if len(test_value) > 50 else test_value
        status = "OK" if is_pass else "FAIL"
        print(f"{pattern_name:<20} {display_value:<50} {str(should_match):>8} {str(matches):>8} {status:>6}")

    print(f"\nResults: {passed} passed, {failed} failed")


def main() -> None:
    """Demonstrate advanced pattern detection."""
    print("=" * 60)
    print("Example 3: Advanced Pattern Detection")
    print("=" * 60)

    demo_entropy_analysis()
    demo_custom_patterns()
    demo_comprehensive_scanner()
    demo_pattern_testing()

    print("\n" + "=" * 60)
    print("Example 3 Complete!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("- Combine pattern matching with entropy analysis")
    print("- Create custom patterns for your organization's secrets")
    print("- Build scanners for automated secret detection")
    print("- Test patterns to ensure accuracy")


if __name__ == "__main__":
    main()
