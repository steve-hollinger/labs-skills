"""Solution 3: Configuration File Scanner.

This solution demonstrates a comprehensive configuration scanner with:
- Multi-format support (JSON, YAML, .env, INI)
- Pattern and key-based detection
- Severity classification
- Remediation suggestions
"""

from __future__ import annotations

import configparser
import json
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from io import StringIO
from pathlib import Path
from typing import Any

# Import YAML if available
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class Severity(Enum):
    """Severity levels for findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FileFormat(Enum):
    """Supported file formats."""
    JSON = "json"
    YAML = "yaml"
    ENV = "env"
    INI = "ini"
    UNKNOWN = "unknown"


@dataclass
class Finding:
    """A security finding in a configuration file."""
    severity: Severity
    description: str
    location: str
    value_masked: str
    remediation: str
    secret_type: str


@dataclass
class ScanResult:
    """Result of scanning a file."""
    file_path: str
    file_format: FileFormat
    findings: list[Finding] = field(default_factory=list)
    scan_duration_ms: float = 0.0

    @property
    def has_critical(self) -> bool:
        return any(f.severity == Severity.CRITICAL for f in self.findings)

    @property
    def finding_count(self) -> dict[Severity, int]:
        counts = {s: 0 for s in Severity}
        for f in self.findings:
            counts[f.severity] += 1
        return counts


class ConfigScanner:
    """Scanner for detecting secrets in configuration files."""

    # Secret patterns with severity
    SECRET_PATTERNS = {
        "aws_access_key": (r"AKIA[0-9A-Z]{16}", Severity.CRITICAL),
        "aws_secret_key": (r"[A-Za-z0-9/+=]{40}", Severity.CRITICAL),
        "github_token": (r"gh[ps]_[A-Za-z0-9]{36}", Severity.HIGH),
        "stripe_key": (r"sk_example_FAKE[A-Za-z0-9]{24,}", Severity.CRITICAL),
        "jwt": (r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", Severity.HIGH),
        "private_key": (r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----", Severity.CRITICAL),
    }

    # Key patterns that indicate sensitive data
    SENSITIVE_KEYS = {
        Severity.CRITICAL: [
            r"(?i)^(aws_)?secret(_?key)?$",
            r"(?i)^private_?key$",
            r"(?i)^(db_)?password$",
        ],
        Severity.HIGH: [
            r"(?i)^api_?(key|secret)$",
            r"(?i)^(access_?)?token$",
            r"(?i)^auth(orization)?$",
            r"(?i)^credentials?$",
        ],
        Severity.MEDIUM: [
            r"(?i)^secret$",
            r"(?i)^passwd$",
            r"(?i)^pwd$",
            r"(?i)^key$",
        ],
    }

    # Extension to format mapping
    FORMAT_MAP = {
        ".json": FileFormat.JSON,
        ".yaml": FileFormat.YAML,
        ".yml": FileFormat.YAML,
        ".env": FileFormat.ENV,
        ".ini": FileFormat.INI,
        ".cfg": FileFormat.INI,
        ".conf": FileFormat.INI,
    }

    def __init__(
        self,
        custom_patterns: dict[str, str] | None = None,
        sensitive_key_patterns: list[str] | None = None,
    ):
        """Initialize the scanner."""
        self.patterns = dict(self.SECRET_PATTERNS)
        if custom_patterns:
            for name, pattern in custom_patterns.items():
                self.patterns[name] = (pattern, Severity.MEDIUM)

        self.sensitive_keys = dict(self.SENSITIVE_KEYS)
        if sensitive_key_patterns:
            self.sensitive_keys[Severity.MEDIUM].extend(sensitive_key_patterns)

        # Compile patterns
        self._compiled_patterns = {
            name: (re.compile(pattern), severity)
            for name, (pattern, severity) in self.patterns.items()
        }

        self._compiled_keys: dict[Severity, list[re.Pattern]] = {
            severity: [re.compile(p) for p in patterns]
            for severity, patterns in self.sensitive_keys.items()
        }

    def _detect_format(self, path: Path) -> FileFormat:
        """Detect file format from extension."""
        suffix = path.suffix.lower()
        return self.FORMAT_MAP.get(suffix, FileFormat.UNKNOWN)

    def _parse_json(self, content: str) -> dict[str, Any]:
        """Parse JSON content."""
        return json.loads(content)

    def _parse_yaml(self, content: str) -> dict[str, Any]:
        """Parse YAML content."""
        if not HAS_YAML:
            raise ImportError("PyYAML not installed. Install with: pip install pyyaml")
        return yaml.safe_load(content) or {}

    def _parse_env(self, content: str) -> dict[str, str]:
        """Parse .env file content."""
        result = {}
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                result[key] = value
        return result

    def _parse_ini(self, content: str) -> dict[str, dict[str, str]]:
        """Parse INI file content."""
        parser = configparser.ConfigParser()
        parser.read_string(content)

        result = {}
        for section in parser.sections():
            result[section] = dict(parser[section])

        # Include DEFAULT section if not empty
        if parser.defaults():
            result["DEFAULT"] = dict(parser.defaults())

        return result

    def _mask_value(self, value: str) -> str:
        """Mask a sensitive value."""
        if len(value) <= 8:
            return "***"
        return f"{value[:4]}***{value[-4:]}"

    def _check_key_sensitivity(self, key: str) -> Severity | None:
        """Check if a key name indicates sensitive data."""
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM]:
            for pattern in self._compiled_keys.get(severity, []):
                if pattern.match(key):
                    return severity
        return None

    def _check_value_patterns(self, value: str) -> tuple[str, Severity] | None:
        """Check if a value matches known secret patterns."""
        for name, (pattern, severity) in self._compiled_patterns.items():
            if pattern.search(value):
                return name, severity
        return None

    def _get_remediation(self, secret_type: str, key: str) -> str:
        """Get remediation suggestion for a finding."""
        remediation_map = {
            "aws_access_key": "Use IAM roles or store in AWS Secrets Manager",
            "aws_secret_key": "Use IAM roles or store in AWS Secrets Manager",
            "github_token": "Use GitHub's encrypted secrets or a secrets manager",
            "stripe_key": "Store in environment variables or secrets manager",
            "jwt": "JWTs should be dynamically generated, not stored in config",
            "private_key": "Store in a secure key vault or secrets manager",
            "password": f"Use environment variable: ${{{key.upper()}}}",
            "api_key": f"Use environment variable: ${{{key.upper()}}}",
            "token": f"Use environment variable: ${{{key.upper()}}}",
            "secret": f"Use environment variable: ${{{key.upper()}}}",
        }

        for pattern_name, suggestion in remediation_map.items():
            if pattern_name in secret_type.lower() or pattern_name in key.lower():
                return suggestion

        return f"Move to environment variable: ${{{key.upper()}}}"

    def _scan_value(
        self,
        key: str,
        value: Any,
        path: str,
    ) -> list[Finding]:
        """Scan a single value for secrets."""
        findings = []

        if not isinstance(value, str) or not value:
            return findings

        # Check key name
        key_severity = self._check_key_sensitivity(key)

        # Check value patterns
        pattern_match = self._check_value_patterns(value)

        if pattern_match:
            secret_type, severity = pattern_match
            findings.append(Finding(
                severity=severity,
                description=f"Detected {secret_type} in configuration",
                location=path,
                value_masked=self._mask_value(value),
                remediation=self._get_remediation(secret_type, key),
                secret_type=secret_type,
            ))
        elif key_severity:
            # Key suggests sensitivity but no pattern match
            findings.append(Finding(
                severity=key_severity,
                description=f"Sensitive key '{key}' contains a value",
                location=path,
                value_masked=self._mask_value(value),
                remediation=self._get_remediation(key, key),
                secret_type=f"sensitive_key:{key}",
            ))

        return findings

    def _scan_dict(
        self,
        data: dict[str, Any],
        base_path: str = "",
    ) -> list[Finding]:
        """Recursively scan a dictionary."""
        findings = []

        for key, value in data.items():
            current_path = f"{base_path}.{key}" if base_path else key

            if isinstance(value, dict):
                findings.extend(self._scan_dict(value, current_path))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        findings.extend(self._scan_dict(item, f"{current_path}[{i}]"))
                    else:
                        findings.extend(self._scan_value(key, item, f"{current_path}[{i}]"))
            else:
                findings.extend(self._scan_value(key, value, current_path))

        return findings

    def scan_file(self, path: str | Path) -> ScanResult:
        """Scan a configuration file for secrets."""
        path = Path(path)
        start_time = time.time()

        file_format = self._detect_format(path)
        findings: list[Finding] = []

        try:
            content = path.read_text()
            findings = self.scan_content(content, file_format, str(path))
        except Exception as e:
            findings.append(Finding(
                severity=Severity.INFO,
                description=f"Error scanning file: {e}",
                location=str(path),
                value_masked="",
                remediation="Check file format and permissions",
                secret_type="scan_error",
            ))

        duration_ms = (time.time() - start_time) * 1000

        return ScanResult(
            file_path=str(path),
            file_format=file_format,
            findings=findings,
            scan_duration_ms=duration_ms,
        )

    def scan_content(
        self,
        content: str,
        format: FileFormat,
        source: str = "input",
    ) -> list[Finding]:
        """Scan content string for secrets."""
        findings = []

        try:
            if format == FileFormat.JSON:
                data = self._parse_json(content)
                findings = self._scan_dict(data, source)

            elif format == FileFormat.YAML:
                data = self._parse_yaml(content)
                if isinstance(data, dict):
                    findings = self._scan_dict(data, source)

            elif format == FileFormat.ENV:
                data = self._parse_env(content)
                findings = self._scan_dict(data, source)

            elif format == FileFormat.INI:
                data = self._parse_ini(content)
                for section, values in data.items():
                    section_path = f"{source}[{section}]"
                    findings.extend(self._scan_dict(values, section_path))

            else:
                # Unknown format - scan as plain text
                for i, line in enumerate(content.splitlines(), 1):
                    for name, (pattern, severity) in self._compiled_patterns.items():
                        if pattern.search(line):
                            findings.append(Finding(
                                severity=severity,
                                description=f"Detected {name} in content",
                                location=f"{source}:{i}",
                                value_masked=self._mask_value(line.strip()[:50]),
                                remediation=self._get_remediation(name, "value"),
                                secret_type=name,
                            ))

        except Exception as e:
            findings.append(Finding(
                severity=Severity.INFO,
                description=f"Parse error: {e}",
                location=source,
                value_masked="",
                remediation="Check content format",
                secret_type="parse_error",
            ))

        return findings

    def scan_directory(
        self,
        path: str | Path,
        recursive: bool = True,
        patterns: list[str] | None = None,
    ) -> list[ScanResult]:
        """Scan all configuration files in a directory."""
        path = Path(path)
        results = []

        if patterns is None:
            patterns = ["*.json", "*.yaml", "*.yml", "*.env", "*.ini", "*.cfg"]

        for pattern in patterns:
            if recursive:
                files = path.rglob(pattern)
            else:
                files = path.glob(pattern)

            for file_path in files:
                if file_path.is_file():
                    results.append(self.scan_file(file_path))

        return results


def main() -> None:
    """Demonstrate the configuration scanner."""
    print("=" * 60)
    print("Solution 3: Configuration File Scanner")
    print("=" * 60)

    scanner = ConfigScanner()

    # Test JSON content
    json_content = '''
    {
        "database": {
            "host": "localhost",
            "port": 5432,
            "password": "super_secret_123"
        },
        "api": {
            "endpoint": "https://api.example.com",
            "api_key": "sk_example_FAKE",
            "timeout": 30
        },
        "aws": {
            "access_key": "AKIAIOSFODNN7EXAMPLE",
            "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        }
    }
    '''

    print("\n1. Scanning JSON Content")
    print("-" * 40)
    findings = scanner.scan_content(json_content, FileFormat.JSON, "config.json")

    for finding in sorted(findings, key=lambda f: (f.severity.value != "critical", f.severity.value)):
        print(f"\n[{finding.severity.value.upper()}] {finding.description}")
        print(f"  Location: {finding.location}")
        print(f"  Value: {finding.value_masked}")
        print(f"  Remediation: {finding.remediation}")

    # Test .env content
    env_content = '''
    # Database configuration
    DB_HOST=localhost
    DB_PASSWORD=my-secret-password

    # API Keys
    STRIPE_API_KEY=sk_example_FAKE24CHARSTRING12
    GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    '''

    print("\n2. Scanning .env Content")
    print("-" * 40)
    findings = scanner.scan_content(env_content, FileFormat.ENV, ".env")

    for finding in findings:
        print(f"[{finding.severity.value.upper()}] {finding.location}: {finding.secret_type}")

    # Summary
    print("\n3. Scan Summary")
    print("-" * 40)
    all_findings = scanner.scan_content(json_content, FileFormat.JSON)
    all_findings.extend(scanner.scan_content(env_content, FileFormat.ENV))

    severity_counts = {s: 0 for s in Severity}
    for f in all_findings:
        severity_counts[f.severity] += 1

    print(f"Total findings: {len(all_findings)}")
    for severity, count in severity_counts.items():
        if count > 0:
            print(f"  {severity.value.upper()}: {count}")

    print("\n" + "=" * 60)
    print("Solution 3 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
